"""Reuse authenticated source support for bounded advanced graph queries."""

import hashlib
import json

from app.agent.tools import RetrievalTools
from app.ingestion.documents import PROTOTYPE_IDS
from app.ingestion.graph import HUMAN_POLICY
from app.analytics import queries

MAX_PAPERS = 16
MAX_CLAIMS = 128
KINDS = {'USES': 'Method', 'EVALUATED_ON': 'Dataset', 'ADDRESSES': 'Task'}


class UnknownPaper(ValueError):
    """A validly shaped ID is outside the selected existing corpus."""


class GraphUnavailable(ValueError):
    """Invalid evidence or a missing/stale analytical snapshot."""


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), default=str)


def approved(claim):
    return (claim.get('status') == 'SOURCE_VERIFIED' and claim.get('human_reviewed') is True
            and claim.get('student_review_status') == 'approved'
            and claim.get('review_policy') == HUMAN_POLICY
            and bool(str(claim.get('reviewer', '')).strip()) and bool(claim.get('reviewed_at')))


def accepted_entity(entity):
    """Identity acceptance is scoped; unresolved/rejected equivalences add no identity."""
    try:
        decision = json.loads(entity.get('alias_review_json', '{}'))
    except (ValueError, TypeError):
        return False
    return (entity.get('resolution_status') == 'STUDENT_APPROVED_SCOPED'
            and isinstance(decision, dict) and decision.get('outcome') == 'ACCEPT'
            and decision.get('decision') == 'APPROVED'
            and decision.get('canonical_id') == entity.get('id'))


class GraphService:
    """Only reviewed read templates; no importer, database writes or model dependency."""

    def __init__(self, driver, settings, papers=None):
        self.tools = RetrievalTools(driver, None, settings)
        self.paper_ids = sorted(PROTOTYPE_IDS if papers is None else papers)
        if not 1 <= len(self.paper_ids) <= MAX_PAPERS or len(set(self.paper_ids)) != len(self.paper_ids):
            raise ValueError('Select between one and sixteen distinct Papers')

    def require_paper(self, ident):
        if ident not in self.paper_ids:
            raise UnknownPaper('Paper ID is not in the selected corpus')

    async def records(self):
        rows = await self.tools.read(queries.SNAPSHOT, papers=self.paper_ids)
        if [r['paper']['id'] for r in rows] != self.paper_ids:
            raise GraphUnavailable('Selected Paper missing from database')
        if any(len(r['assertions']) >= 129 for r in rows):
            raise GraphUnavailable('Paper assertion budget exceeded')
        return rows

    async def snapshot(self):
        """Validate approval, scoped identity and complete evidence, then fingerprint it."""
        rows = await self.records()
        claims, entities, excluded = {}, {}, []
        seen = set()
        for row in rows:
            for assertion in row['assertions']:
                c, e = assertion['claim'], assertion['entity']
                if c['id'] in seen:
                    raise GraphUnavailable('Non-unique Claim subject/object association')
                seen.add(c['id'])
                if c.get('predicate') not in KINDS:
                    continue
                if not approved(c):
                    excluded.append(c['id'])
                    continue
                if not e or not accepted_entity(e):
                    excluded.append(c['id'])
                    continue
                if (c.get('paper_id') != row['paper']['id'] or c.get('subject_id') != c['paper_id']
                        or c.get('object_id') != e['id'] or e.get('kind') != KINDS[c['predicate']]):
                    raise GraphUnavailable('Scientific assertion endpoint/type mismatch')
                claims[c['id']] = c
                entities[e['id']] = e
        if len(claims) > MAX_CLAIMS:
            raise GraphUnavailable('Approved assertion budget exceeded')
        evidence, supports = {}, []
        ids = sorted(claims)
        for start in range(0, len(ids), 16):
            chunks, parts = await self.tools.claim_supports(ids[start:start + 16])
            evidence.update({c['chunk_id']: c for c in chunks})
            supports.extend(parts)
        if {s['claim_id'] for s in supports} != set(claims):
            raise GraphUnavailable('Approved source support missing or changed')
        if canonical(rows) != canonical(await self.records()):
            raise GraphUnavailable('Review state changed during source validation')
        digest = hashlib.sha256(canonical({
            'policy': 'scientific-similarity-v1', 'records': rows,
            'evidence': sorted(evidence.values(), key=lambda c: c['chunk_id']),
            'supports': sorted(supports, key=canonical),
        }).encode()).hexdigest()
        pairs = await self.tools.read(queries.PAIRS, papers=self.paper_ids, claims=ids, limit=121)
        if len(pairs) > 120:
            raise GraphUnavailable('Similarity edge budget exceeded')
        for pair in pairs:
            for side in ('source', 'target'):
                pair[side + '_claim_ids'] = sorted(c['id'] for c in claims.values()
                    if c['paper_id'] == pair[side] and c['object_id'] in pair['shared'])
        # Recheck the exact validated allowlist after executing the analytical query.
        if canonical(rows) != canonical(await self.records()):
            raise GraphUnavailable('Review state changed during graph computation')
        return dict(fingerprint=digest, papers=[dict(id=r['paper']['id'], title=r['paper']['title']) for r in rows],
                    claims=claims, entities=entities, pairs=pairs, evidence=evidence,
                    supports=supports, excluded_claim_ids=sorted(excluded), review_state=canonical(rows))

    async def ensure_review_unchanged(self, snapshot):
        if canonical(await self.records()) != snapshot['review_state']:
            raise GraphUnavailable('Review state changed during exploration')

    @staticmethod
    def support_subset(snapshot, ids):
        parts = [p for p in snapshot['supports'] if p['claim_id'] in ids]
        chunks = sorted({p['chunk_id'] for p in parts})
        return dict(supports=parts, evidence=[snapshot['evidence'][c] for c in chunks])

    async def path(self, source, target, hops):
        self.require_paper(source)
        self.require_paper(target)
        if source == target:
            raise ValueError('Citation endpoints must be distinct')
        return await self.tools.execute('find_citation_path',
            dict(source_id=source, target_id=target, max_hops=hops))

    async def shared(self, source, target, kind=None, limit=20, offset=0):
        self.require_paper(source)
        self.require_paper(target)
        if source == target:
            raise ValueError('Exploration endpoints must be distinct')
        snap = await self.snapshot()
        rows = await self.tools.read(queries.SHARED, source=source, target=target, kind=kind,
                                     claims=sorted(snap['claims']), limit=limit, offset=offset)
        await self.ensure_review_unchanged(snap)
        ids = {c for row in rows for key in ('source_claim_ids', 'target_claim_ids') for c in row[key]}
        return dict(source=source, target=target, entities=rows, limit=limit, offset=offset,
                    **self.support_subset(snap, ids))

    async def related(self, source, limit=20, offset=0):
        self.require_paper(source)
        snap = await self.snapshot()
        rows = await self.tools.read(queries.RELATED, source=source, papers=self.paper_ids,
                                     claims=sorted(snap['claims']), limit=limit, offset=offset)
        await self.ensure_review_unchanged(snap)
        titles = {p['id']: p['title'] for p in snap['papers']}
        ids = set()
        for row in rows:
            row['title'] = titles[row['paper_id']]
            for key, paper in [('source_claim_ids', source), ('target_claim_ids', row['paper_id'])]:
                row[key] = sorted(c['id'] for c in snap['claims'].values()
                                  if c['paper_id'] == paper and c['object_id'] in row['entity_ids'])
                ids.update(row[key])
        return dict(source=source, papers=rows, limit=limit, offset=offset,
                    interpretation='Scoped shared-entity Jaccard similarity; experimental settings may differ.',
                    **self.support_subset(snap, ids))

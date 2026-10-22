"""Read the merged student sign-off, never infer approval from unsigned CSV rows."""

import csv
import json
import re

from app.ingestion.documents import digest
from app.ingestion.research import require

REVIEW_PATH = 'docs/GRAPH_EVIDENCE_REVIEW.md'
REVIEW_SHA256 = 'e26ad12f038131f99d739c2ffbd778c55d8b2a3f911bb5738d9f62acfa631404'
DECISIONS_PATH = 'corpus/review_decisions.json'
INPUTS = (REVIEW_PATH, 'corpus/GRAPH_EVIDENCE_CANDIDATES.csv',
          'corpus/citation_evidence.csv', 'corpus/corpus_manifest.json')
INPUT_HASHES = dict(zip(INPUTS, (REVIEW_SHA256,
    '6154df1342a92133a18425d4ed5152f38f37b5754ae14c4f9534deffc7d81b10',
    '296396fe74c1d452ab283fd79f486791ad2e1a4ff9d7f69f6fe12332a7959cb2',
    'c6eb6199b0a48433df7de25226587e08baf6e31c277017b6d2a6f41ef1463a75')))
ALIAS_ENTITIES = dict(zip((f'A{i:02}' for i in range(1, 15)), (
    'dataset:natural-questions', 'dataset:triviaqa', 'dataset:webquestions',
    'dataset:curatedtrec', 'method:bert-base', 'task:open-domain-question-answering',
    'method:dpr', 'method:bart-large', 'method:leiden', 'method:map-reduce-summarization',
    'task:query-focused-summarization', 'dataset:graphrag-v1-behind-the-tech-transcripts',
    'dataset:multihop-rag-news-corpus', 'dataset:hotpotqa')))


def table_rows(text):
    """Read the simple, unescaped Markdown tables in this pinned review format."""
    for line in text.splitlines():
        if line.startswith('| '):
            yield [cell.strip() for cell in line.strip().strip('|').split('|')]


def decision_snapshot(root):
    """Mechanical transcription; this derived manifest is not new authorization."""
    text = (root / REVIEW_PATH).read_text()
    signed = text.split('## 9. Student sign-off:', 1)[1].split('## 10.', 1)[0]
    scope = text.split('## 6. Alias recommendations', 1)[0]
    alias_section = text.split('## 6. Alias recommendations', 1)[1].split('## 7.', 1)[0]
    definitions = {r[0]: r for r in table_rows(alias_section) if re.fullmatch(r'A\d{2}', r[0])}
    with (root / INPUTS[1]).open(newline='') as handle:
        candidates = {r['candidate_id']: r for r in csv.DictReader(handle)}
    claims, aliases = {}, {}
    for row in table_rows(signed):
        ident = row[0]
        if re.fullmatch(r'(GE\d{2}|C03|C09)', ident):
            require(len(row) == 7 and ident not in claims, 'Malformed/duplicate claim decision')
            contexts = [r for r in table_rows(scope) if ident in re.findall(r'(?:GE|C)\d{2}', r[0])]
            claims[ident] = dict(decision=row[3], reviewer=row[4], signoff_recorded_date=row[5],
                                 accepted_scope=row[6], inspected_sources=row[2],
                                 review_context=contexts)
            if ident in candidates:
                r = candidates[ident]
                claims[ident]['assertion'] = {k: r[k] for k in
                    ('source_paper_id', 'predicate', 'object_proposed_id', 'object_kind')}
        elif re.fullmatch(r'A\d{2}', ident):
            require(len(row) == 6 and ident not in aliases, 'Malformed/duplicate alias decision')
            definition = definitions[ident]
            aliases[ident] = dict(outcome=definition[2], mapping=definition[1], boundary=definition[3],
                decision=row[2], reviewer=row[3], signoff_recorded_date=row[4].split()[0],
                accepted_scope=row[5], canonical_id=ALIAS_ENTITIES.get(ident))
            require(row[1].split()[0] == definition[2], 'Conflicting alias recommendation')
    require(set(claims) == {'C03', 'C09'} | {f'GE{i:02}' for i in range(1, 21)},
            'Missing student claim decisions')
    require(set(aliases) == {f'A{i:02}' for i in range(1, 22)}, 'Missing student alias decisions')
    for row in [*claims.values(), *aliases.values()]:
        require(row['decision'] == 'APPROVED' and row['reviewer'] == 'fabrice12345C'
                and row['signoff_recorded_date'] == '2026-10-21', 'Missing/incompatible student decision')
    return {'policy': 'documented-student-review-v1', 'source_document': REVIEW_PATH,
            'source_section': '9', 'signoff_timezone': 'Europe/Paris',
            'source_inspection_timestamp': None,
            'inputs_sha256': {p: digest((root / p).read_bytes()) for p in INPUTS},
            'claims': claims, 'aliases': aliases}


def load_decisions(root):
    """Require the reviewable snapshot to agree with every signed source decision."""
    require(digest((root / REVIEW_PATH).read_bytes()) == REVIEW_SHA256,
            'Merged PR #5 review document changed; explicit review migration required')
    saved = json.loads((root / DECISIONS_PATH).read_text())
    require(saved['inputs_sha256'] == INPUT_HASHES, 'Unreviewed source artifact revision')
    require(saved == decision_snapshot(root), 'Review decision manifest/source mismatch')
    return saved


def resolve_alias(decisions, row):
    """Only resolve the exact reviewed typed entity and source-specific assertion."""
    decision = decisions['claims'].get(row['candidate_id'])
    require(decision is not None and decision['decision'] == 'APPROVED', 'Missing student decision')
    require(decision['assertion'] == {k: row[k] for k in decision['assertion']},
            'Reviewed assertion/predicate/entity kind mismatch')
    kind = {'USES': 'Method', 'EVALUATED_ON': 'Dataset', 'ADDRESSES': 'Task'}.get(row['predicate'])
    require(kind is not None and row['object_kind'] == kind, 'Wrong predicate/entity kind')
    matches = [(key, alias) for key, alias in decisions['aliases'].items()
               if alias['canonical_id'] == row['object_proposed_id']]
    require(len(matches) == 1, 'Ambiguous or missing alias resolution')
    ident, alias = matches[0]
    require(alias['outcome'] == 'ACCEPT' and alias['decision'] == 'APPROVED',
            'Rejected or unresolved alias cannot be applied')
    return ident, alias

"""Snapshot-bound GDS reads; catalog mutation is confined to the operator class."""

from collections import Counter
import hashlib
import re
from time import perf_counter

from app.analytics.queries import PROJECT
from app.analytics.service import GraphService, GraphUnavailable

MEMORY_BUDGET = 64 * 1024 * 1024
NAME = re.compile(r'^research_sim_[a-f0-9]{12}_[a-f0-9]{64}$')
CONFIGS = {
    'pagerank': dict(relationshipWeightProperty='weight', concurrency=1, logProgress=False,
                     dampingFactor=0.85, maxIterations=100, tolerance=1e-7),
    'louvain': dict(relationshipWeightProperty='weight', concurrency=1, logProgress=False,
                    maxLevels=10, maxIterations=10, tolerance=0.0001),
}
# Finite procedure registry. An API argument is never interpolated into Cypher.
ALGORITHMS = {
    'pagerank': (
        'CALL gds.pageRank.stream.estimate($name,$config) YIELD bytesMin,bytesMax,requiredMemory RETURN bytesMin,bytesMax,requiredMemory',
        'CALL gds.pageRank.stats($name,$config) YIELD ranIterations,didConverge,computeMillis,preProcessingMillis,postProcessingMillis RETURN ranIterations,didConverge,computeMillis,preProcessingMillis,postProcessingMillis',
        'CALL gds.pageRank.stream($name,$config) YIELD nodeId,score RETURN nodeId,score'),
    'louvain': (
        'CALL gds.louvain.stream.estimate($name,$config) YIELD bytesMin,bytesMax,requiredMemory RETURN bytesMin,bytesMax,requiredMemory',
        'CALL gds.louvain.stats($name,$config) YIELD modularity,modularities,ranLevels,communityCount,computeMillis,preProcessingMillis,postProcessingMillis RETURN modularity,modularities,ranLevels,communityCount,computeMillis,preProcessingMillis,postProcessingMillis',
        'CALL gds.louvain.stream($name,$config) YIELD nodeId,communityId RETURN nodeId,communityId'),
}


def modularity(pairs, communities):
    """Weighted undirected modularity of the actual streamed partition; isolates add zero."""
    mass = sum(p['weight'] for p in pairs)
    if not mass:
        return 0.0
    internal, degree = Counter(), Counter()
    for pair in pairs:
        left, right, weight = communities[pair['source']], communities[pair['target']], pair['weight']
        degree[left] += weight
        degree[right] += weight
        if left == right:
            internal[left] += weight
    return sum(internal[c] / mass - (degree[c] / (2 * mass)) ** 2 for c in set(communities.values()))


class Analytics(GraphService):
    """API capability: validate and stream existing projections, never create/drop them."""

    @property
    def prefix(self):
        scope = hashlib.sha256('\n'.join(self.paper_ids).encode()).hexdigest()[:12]
        return 'research_sim_' + scope + '_'

    def name(self, snapshot):
        return self.prefix + snapshot['fingerprint']

    async def projection(self, snapshot):
        name = self.name(snapshot)
        exists = await self.tools.read('RETURN gds.graph.exists($name) AS exists', name=name)
        if not exists[0]['exists']:
            raise GraphUnavailable('Projection missing or stale; run the explicit analytics refresh CLI')
        rows = await self.tools.read(
            'CALL gds.graph.list($name) YIELD nodeCount,relationshipCount,sizeInBytes,schemaWithOrientation '
            'RETURN nodeCount,relationshipCount,sizeInBytes,schemaWithOrientation', name=name)
        record = rows[0]
        if (record['nodeCount'] != len(snapshot['papers'])
                or record['relationshipCount'] != 2 * len(snapshot['pairs'])
                or record['sizeInBytes'] > MEMORY_BUDGET):
            raise GraphUnavailable('Projection size differs from validated snapshot or exceeds budget')
        nodes = await self.tools.read(
            'CALL gds.graph.nodeProperty.stream($name,"paperIndex") YIELD nodeId,propertyValue '
            'RETURN nodeId,propertyValue ORDER BY nodeId', name=name)
        if [(r['nodeId'], r['propertyValue']) for r in nodes] != [(i, i) for i in range(len(snapshot['papers']))]:
            raise GraphUnavailable('Projection Paper identities differ from snapshot')
        if snapshot['pairs']:
            schema = record['schemaWithOrientation']['relationships'].get('SHARES_ENTITY', {})
            if schema.get('direction') != 'UNDIRECTED':
                raise GraphUnavailable('Expected undirected scientific similarity projection')
            edges = await self.tools.read(
                'CALL gds.graph.relationshipProperty.stream($name,"weight") '
                'YIELD sourceNodeId,targetNodeId,propertyValue RETURN sourceNodeId,targetNodeId,propertyValue', name=name)
            indexes = {p['id']: i for i, p in enumerate(snapshot['papers'])}
            expected = sorted((indexes[p[a]], indexes[p[b]], p['weight']) for p in snapshot['pairs']
                              for a, b in [('source', 'target'), ('target', 'source')])
            if sorted((r['sourceNodeId'], r['targetNodeId'], r['propertyValue']) for r in edges) != expected:
                raise GraphUnavailable('Projection adjacency or weight differs from snapshot')
        return record

    async def run(self, algorithm, limit=20, offset=0):
        if algorithm not in ALGORITHMS:
            raise ValueError('Unsupported analytical operation')
        started = perf_counter()
        snap = await self.snapshot()
        catalog = await self.projection(snap)
        name, config = self.name(snap), dict(CONFIGS[algorithm])
        # An edgeless projection has no relationship weight schema; unweighted and
        # weighted algorithms are equivalent there. Preserve all isolated vertices.
        if not snap['pairs']:
            config.pop('relationshipWeightProperty')
        estimate_q, stats_q, stream_q = ALGORITHMS[algorithm]
        estimate = (await self.tools.read(estimate_q, name=name, config=config))[0]
        if estimate['bytesMax'] > MEMORY_BUDGET:
            raise GraphUnavailable('GDS memory estimate exceeds 64 MiB algorithm budget')
        stats = (await self.tools.read(stats_q, name=name, config=config))[0]
        stream_start = perf_counter()
        rows = await self.tools.read(stream_q, name=name, config=config)
        stream_millis = (perf_counter() - stream_start) * 1000
        if sorted(r['nodeId'] for r in rows) != list(range(len(snap['papers']))):
            raise GraphUnavailable('Algorithm omitted or duplicated a Paper')
        if (await self.snapshot())['fingerprint'] != snap['fingerprint']:
            raise GraphUnavailable('Review/source snapshot changed while running algorithm')
        degree = {p['id']: 0.0 for p in snap['papers']}
        for pair in snap['pairs']:
            degree[pair['source']] += pair['weight']
            degree[pair['target']] += pair['weight']
        result = dict(algorithm=algorithm, projection=name, snapshot=snap['fingerprint'],
            node_count=catalog['nodeCount'], logical_edge_count=len(snap['pairs']),
            projected_relationship_count=catalog['relationshipCount'],
            isolated_papers=sorted(p for p, d in degree.items() if d == 0), adjacencies=snap['pairs'],
            configuration=config, memory_estimate=estimate, stats=stats, stream_millis=stream_millis,
            offset=offset, limit=limit)
        if algorithm == 'pagerank':
            ranked = [dict(paper_id=snap['papers'][r['nodeId']]['id'],
                           title=snap['papers'][r['nodeId']]['title'], score=r['score'],
                           weighted_degree=degree[snap['papers'][r['nodeId']]['id']]) for r in rows]
            result['ranks'] = sorted(ranked, key=lambda r: (-r['score'], r['paper_id']))[offset:offset + limit]
            result['interpretation'] = ('Navigation prominence in scoped scientific similarity, not scientific quality or citation impact. '
                                        'Convergence statistics come from a separate stats execution with identical settings.')
        else:
            sizes = Counter(r['communityId'] for r in rows)
            memberships = [dict(paper_id=snap['papers'][r['nodeId']]['id'],
                title=snap['papers'][r['nodeId']]['title'], community_id=r['communityId'],
                community_size=sizes[r['communityId']]) for r in rows]
            result['memberships'] = sorted(memberships, key=lambda r: (r['community_id'], r['paper_id']))[offset:offset + limit]
            result['stream_modularity'] = modularity(snap['pairs'], {m['paper_id']: m['community_id'] for m in memberships})
            result['interpretation'] = ('Community IDs are arbitrary; a tiny partition may only reflect disconnected components. '
                'stats is a separate execution; stream_modularity is independently computed from the returned full partition. '
                'GraphRAG uses Leiden; this project independently selects Louvain.')
        result['elapsed_millis'] = (perf_counter() - started) * 1000
        return result


class ProjectionManager(Analytics):
    """Local operator only: explicit bounded catalog refresh/drop, no persisted writes."""

    async def drop(self, name):
        if not NAME.fullmatch(name) or not name.startswith(self.prefix):
            raise ValueError('Projection name is outside this selected corpus scope')
        return await self.tools.read('CALL gds.graph.drop($name,false) YIELD graphName RETURN graphName', name=name)

    async def refresh(self):
        snap = await self.snapshot()
        name = self.name(snap)
        exists = (await self.tools.read('RETURN gds.graph.exists($name) AS exists', name=name))[0]['exists']
        if exists:
            return dict(action='REUSED', name=name, snapshot=snap['fingerprint'],
                        catalog=await self.projection(snap), adjacencies=snap['pairs'])
        indexes = {p['id']: i for i, p in enumerate(snap['papers'])}
        rows = [dict(source=indexes[p['source']], target=indexes[p['target']], weight=p['weight']) for p in snap['pairs']]
        connected = {r[k] for r in rows for k in ('source', 'target')}
        rows += [dict(source=i, target=None, weight=0.0) for i in indexes.values() if i not in connected]
        created = False
        try:
            projection = (await self.tools.read(
                PROJECT, name=name, rows=rows,
                undirected_types=['SHARES_ENTITY'] if snap['pairs'] else []))[0]
            created = True
            catalog = await self.projection(snap)
            if (await self.snapshot())['fingerprint'] != snap['fingerprint']:
                raise GraphUnavailable('Review changed during projection; refresh again explicitly')
        except Exception:
            if created:
                await self.drop(name)
            raise
        # Replace only this corpus's obsolete analytical cache, never other GDS graphs.
        old = await self.tools.read('CALL gds.graph.list() YIELD graphName '
                                   'WHERE graphName STARTS WITH $prefix RETURN graphName LIMIT 33', prefix=self.prefix)
        if len(old) > 32:
            await self.drop(name)
            raise GraphUnavailable('Too many projections for this scope; explicitly clean up')
        for row in old:
            if row['graphName'] != name:
                await self.drop(row['graphName'])
        return dict(action='CREATED', name=name, snapshot=snap['fingerprint'], projection=projection,
                    catalog=catalog, adjacencies=snap['pairs'], excluded_claim_ids=snap['excluded_claim_ids'])

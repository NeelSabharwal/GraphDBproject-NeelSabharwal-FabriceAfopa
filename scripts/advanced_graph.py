"""Local analytics operator: explicit refresh/drop, real runs and bounded benchmarks.

No command imports papers or changes persisted scientific evidence. Use --help.
"""

import argparse
import asyncio
import json
from statistics import median
from time import perf_counter

from neo4j import AsyncGraphDatabase, Query

from app.analytics.gds import ProjectionManager
from app.analytics.models import AnalyticsResponse
from app.analytics.queries import PAIRS, PAIR_BASELINE, SHARED
from app.agent.tools import PATH_QUERY
from app.config import Settings
from app.ingestion.graph import HUMAN_POLICY


def plan_summary(plan):
    """Flatten actual EXPLAIN/PROFILE operators and sum reported operator DB hits."""
    entries = []
    def visit(node):
        if not node:
            return
        entries.append({k: node.get(k) for k in ('operatorType', 'dbHits', 'rows', 'arguments')})
        for child in node.get('children', []):
            visit(child)
    visit(plan)
    return dict(operators=entries, db_hits=sum(e['dbHits'] or 0 for e in entries))


def normalized(rows):
    return sorted(json.dumps({k: sorted(v) if isinstance(v, list) else v for k,v in r.items()}, sort_keys=True) for r in rows)


async def benchmark(service):
    """Five warmups, thirty interleaved real-corpus timings; unchanged outputs required."""
    snap = await service.snapshot()
    params = dict(papers=service.paper_ids, claims=sorted(snap['claims']), limit=121)
    queries = dict(baseline=PAIR_BASELINE, optimized=PAIRS)
    outputs = {name: await service.tools.read(query, **params) for name, query in queries.items()}
    if normalized(outputs['baseline']) != normalized(outputs['optimized']):
        raise ValueError('Benchmark queries return different results')
    samples = {name: [] for name in queries}
    for i in range(35):
        # Alternate which query runs first to reduce simple order/warm-cache bias.
        for name in list(queries)[::1 if i % 2 == 0 else -1]:
            start = perf_counter()
            result = await service.tools.read(queries[name], **params)
            elapsed = (perf_counter() - start) * 1000
            if normalized(result) != normalized(outputs[name]):
                raise ValueError('Benchmark source results changed')
            if i >= 5:
                samples[name].append(elapsed)
    plans = {}
    cases = [(name, query, params) for name, query in queries.items()]
    cases += [('citation_path', PATH_QUERY, dict(source=service.paper_ids[2],target=service.paper_ids[0],hops=3,policy=HUMAN_POLICY)),
              ('shared_datasets', SHARED,dict(source=service.paper_ids[0],target=service.paper_ids[1],kind='Dataset',claims=sorted(snap['claims']),limit=20,offset=0))]
    for name, query, parameters in cases:
        plans[name] = {}
        for mode in ('EXPLAIN', 'PROFILE'):
            async with service.tools.driver.session(default_access_mode='READ') as session:
                result = await session.run(Query(mode + ' ' + query, timeout=5), **parameters)
                await result.data()
                summary = await result.consume()
                if summary.counters.contains_updates:
                    raise ValueError('Unexpected persisted mutation in read-only benchmark')
                plans[name][mode.lower()] = plan_summary(summary.profile if mode == 'PROFILE' else summary.plan)
    if (await service.snapshot())['fingerprint'] != snap['fingerprint']:
        raise ValueError('Snapshot changed during benchmark')
    return dict(snapshot=snap['fingerprint'], paper_count=len(snap['papers']),
        approved_scientific_claim_count=len(snap['claims']), logical_pairs=snap['pairs'],
        setup='One local async driver/client; five warmups per query; thirty alternating-order samples; no LLM; end-to-end Bolt query latency.',
        timings={name:dict(samples_ms=values,p50_ms=median(values),p95_ms=sorted(values)[28],min_ms=min(values),max_ms=max(values)) for name,values in samples.items()},
        identical_results=True, plans=plans,
        limitations='Three papers, warm cache and tiny results; latency noise can outweigh the reduction in database work.')


async def execute(command, name=None):
    config = Settings.from_environment()
    async with AsyncGraphDatabase.driver(config.neo4j_uri,
            auth=(config.neo4j_user,config.neo4j_password.get_secret_value()),
            connection_timeout=5,max_transaction_retry_time=0,max_connection_pool_size=4) as driver:
        service = ProjectionManager(driver, config)
        if command == 'refresh':
            return await service.refresh()
        if command == 'drop':
            if not name:
                raise ValueError('drop requires --name with the exact managed projection name')
            return await service.drop(name)
        if command in ('pagerank', 'louvain'):
            return AnalyticsResponse.model_validate(await service.run(command)).model_dump()
        if command == 'benchmark':
            return await benchmark(service)
        snap = await service.snapshot()
        return dict(name=service.name(snap),snapshot=snap['fingerprint'],catalog=await service.projection(snap),
                    papers=snap['papers'],adjacencies=snap['pairs'],excluded_claim_ids=snap['excluded_claim_ids'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['status','refresh','drop','pagerank','louvain','benchmark'])
    parser.add_argument('--name',help='Exact managed projection name for explicit drop')
    args = parser.parse_args()
    result = asyncio.run(execute(args.command,args.name))
    print(json.dumps(result,ensure_ascii=False,indent=2,default=str))


if __name__ == '__main__':
    main()

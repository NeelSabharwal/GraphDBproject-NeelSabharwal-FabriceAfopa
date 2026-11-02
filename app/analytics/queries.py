"""Fixed analytical Cypher; all values are parameters, never executable user text."""

SNAPSHOT = """
UNWIND $papers AS paper_id
MATCH (p:Paper {id:paper_id}) USING INDEX p:Paper(id)
CALL (p) {
 MATCH (c:Claim)-[:SUBJECT]->(p)
 OPTIONAL MATCH (c)-[:OBJECT]->(e:Entity)
 WITH c,e ORDER BY c.id,e.id LIMIT 129
 RETURN collect({claim:properties(c),entity:properties(e)}) AS assertions
}
RETURN properties(p) AS paper, assertions ORDER BY p.id
"""

# Collapse claim multiplicity once per paper BEFORE enumerating unordered pairs.
PAIR_SETS = """
UNWIND $papers AS paper_id
MATCH (p:Paper {id:paper_id}) USING INDEX p:Paper(id)
CALL (p) {
 MATCH (c:Claim)-[:SUBJECT]->(p), (c)-[:OBJECT]->(e:Entity)
 WHERE c.id IN $claims
 WITH DISTINCT e.id AS entity_id ORDER BY entity_id
 RETURN collect(entity_id) AS entities
}
WITH collect({id:p.id, entities:entities}) AS papers
UNWIND papers AS a
UNWIND papers AS b
WITH a,b WHERE a.id<b.id
WITH a.id AS source,b.id AS target,a.entities AS left_entities,b.entities AS right_entities
"""
PAIR_SCORE = """
WITH source,target,left_entities,right_entities,
     [e IN left_entities WHERE e IN right_entities] AS shared
WITH source,target,shared,size(left_entities)+size(right_entities)-size(shared) AS union_size
WHERE size(shared)>0
RETURN source,target,shared,union_size,toFloat(size(shared))/union_size AS weight
ORDER BY weight DESC,source,target LIMIT $limit
"""
PAIRS = PAIR_SETS + PAIR_SCORE

# Benchmark-only baseline: repeated per-pair claim joins multiply intermediate rows.
PAIR_BASELINE = (
    """
UNWIND $papers AS source_id
MATCH (a:Paper {id:source_id})
UNWIND $papers AS target_id
MATCH (b:Paper {id:target_id}) WHERE a.id<b.id
OPTIONAL MATCH (ca:Claim)-[:SUBJECT]->(a), (ca)-[:OBJECT]->(ea:Entity)
WHERE ca.id IN $claims
OPTIONAL MATCH (cb:Claim)-[:SUBJECT]->(b), (cb)-[:OBJECT]->(eb:Entity)
WHERE cb.id IN $claims
WITH a.id AS source,b.id AS target,collect(DISTINCT ea.id) AS left_entities,
     collect(DISTINCT eb.id) AS right_entities
"""
    + PAIR_SCORE
)

SHARED = """
MATCH (a:Paper {id:$source})<-[:SUBJECT]-(ca:Claim)-[:OBJECT]->(e:Entity)
      <-[:OBJECT]-(cb:Claim)-[:SUBJECT]->(b:Paper {id:$target})
WHERE ca.id IN $claims AND cb.id IN $claims AND ($kind IS NULL OR e.kind=$kind)
WITH e,collect(DISTINCT ca.id) AS source_claim_ids,collect(DISTINCT cb.id) AS target_claim_ids
RETURN e.id AS entity_id,e.canonical_name AS name,e.kind AS kind,source_claim_ids,target_claim_ids
ORDER BY entity_id SKIP $offset LIMIT $limit
"""

RELATED = (
    PAIR_SETS
    + """
WITH source,target,left_entities,right_entities,
     [e IN left_entities WHERE e IN right_entities] AS shared
WITH source,target,shared,size(left_entities)+size(right_entities)-size(shared) AS union_size
WHERE size(shared)>0 AND $source IN [source,target]
RETURN CASE WHEN source=$source THEN target ELSE source END AS paper_id,
       shared AS entity_ids,toFloat(size(shared))/union_size AS similarity
ORDER BY similarity DESC,paper_id SKIP $offset LIMIT $limit
"""
)

PROJECT = """
UNWIND $rows AS row
WITH gds.graph.project($name,row.source,row.target,
 {sourceNodeProperties:{paperIndex:row.source},
  targetNodeProperties:{paperIndex:coalesce(row.target,row.source)},
  relationshipType:'SHARES_ENTITY',relationshipProperties:{weight:row.weight}},
 {undirectedRelationshipTypes:$undirected_types,readConcurrency:1,logProgress:false}) AS g
RETURN g.graphName AS name,g.nodeCount AS nodes,g.relationshipCount AS relationships,
       g.projectMillis AS project_millis
"""

# syntax=docker/dockerfile:1
FROM neo4j:5.26.32-community@sha256:0a6e7aedf54a531f76286032d4365ead65b11cca05e4a15cdf23b8e53d6db02b

# Community-compatible release; never use runtime NEO4J_PLUGINS/latest resolution.
ADD --checksum=sha256:edb7ce2ae1642449073ed2fd72b8438ce312fefee0b3ae04dbb0854eaecbd16f https://github.com/neo4j/graph-data-science/releases/download/2.13.2/neo4j-graph-data-science-2.13.2.jar /plugins/neo4j-graph-data-science-2.13.2.jar
RUN chmod 644 /plugins/neo4j-graph-data-science-2.13.2.jar

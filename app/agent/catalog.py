"""Bounded exact paper-name resolution; no scientific alias merging or graph writes."""

import re

from pydantic import Field

from app.agent.models import StrictModel


class PaperReference(StrictModel):
    """Only identity metadata is exposed to the agent."""

    id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=500)
    aliases: list[str] = Field(default_factory=list, max_length=32)


def names(paper):
    """Existing aliases plus conservative title forms, never an ID/result lookup table."""
    title = paper["title"]
    result = {paper["id"], title, *paper["aliases"]}
    # E.g. a leading noun phrase before "for" can supply its initialism.
    prefix = re.split(r"\bfor\b|:", title, maxsplit=1, flags=re.I)[0]
    words = re.findall(r"[A-Za-z]+", prefix)
    if 2 <= len(words) <= 6 and all(w[0].isupper() for w in words):
        result.add("".join(w[0] for w in words))
    # Preserve explicitly capitalized title phrases such as "Graph RAG".
    result.update(re.findall(r"\b[A-Z][a-z]+\s+[A-Z]{2,}\b", title))
    version = re.search(r"v\d+$", paper["id"])
    if version:
        result.update(n + " " + version.group() for n in tuple(result))
    return sorted(n for n in result if 1 <= len(n) <= 500)


def key(name):
    """Whitespace/punctuation-insensitive exact comparison, not fuzzy matching."""
    return re.sub(r"[\W_]+", "", name.casefold())


def resolve_name(name, catalog):
    """Resolve each endpoint independently; duplicate aliases fail closed."""
    matches = [p["id"] for p in catalog if key(name.strip(" '\"")) in {key(n) for n in names(p)}]
    if len(matches) != 1:
        raise ValueError("Paper name is ambiguous" if matches else "Paper name is unsupported")
    return matches[0]


def mentioned_papers(question, catalog):
    """Longest bounded name matches avoid treating RAG within GraphRAG as another paper."""
    matches = []
    for paper in catalog:
        for name in names(paper):
            parts = re.findall(r"\w+", name)
            pattern = r"(?<!\w)" + r"[\s-]*".join(map(re.escape, parts)) + r"(?!\w)"
            for match in re.finditer(pattern, question, re.I):
                matches.append((match.start(), match.end(), paper["id"]))
    maximal = [m for m in matches if not any(
        n[0] <= m[0] and n[1] >= m[1] and n[1]-n[0] > m[1]-m[0] for n in matches)]
    for start, end, _ in maximal:
        if len({pid for a, b, pid in maximal if a == start and b == end}) > 1:
            raise ValueError("Paper name is ambiguous")
    return sorted({m[2] for m in maximal})


def resolve_direction(question, catalog):
    """Support explicit 'from X to Y', standalone 'X to Y', and arrows; no guessed direction."""
    pattern = r"(.+?)\s+(to|→|->|←|<-)\s+(.+?)(?=[.!?;](?:\s|$)|$)"
    match = (re.search(r"\bfrom\s+" + pattern, question, re.I)
             or re.search("^" + pattern, question, re.I))
    if not match:
        if re.search(r"\bbetween\b", question, re.I):
            raise ValueError("Citation direction is ambiguous; specify from source to target")
        return None
    left, direction, right = match.groups()
    source, target = resolve_name(left, catalog), resolve_name(right, catalog)
    if direction in ("←", "<-"):
        source, target = target, source
    if source == target:
        raise ValueError("Citation endpoints must be different papers")
    return {"source_id": source, "target_id": target}

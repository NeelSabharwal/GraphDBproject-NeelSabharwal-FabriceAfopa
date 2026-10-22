"""Shared source-coordinate validation; no evaluation labels or database writes."""

from app.ingestion.documents import digest


def require(condition, message):
    """Fail a source-location check without silently changing its inputs."""
    if not condition:
        raise ValueError(message)


def map_supports(chunks, pages, paper_id, page_number, raw_start, raw_end):
    """Cover a raw span using actual normalized chunks and original offset mappings."""
    page = pages[paper_id][page_number - 1]
    start = next(i for i, raw_limit in enumerate(page['raw_ends']) if raw_limit > raw_start)
    end = max(i for i, raw_origin in enumerate(page['raw_starts']) if raw_origin < raw_end) + 1
    candidates = [c for c in chunks if c['paper'] == paper_id and c['page'] == page_number
                  and c['start'] < end and c['end'] > start]
    cursor, selected = start, []
    while cursor < end:
        reachable = [c for c in candidates if c['start'] <= cursor < c['end']]
        require(reachable, 'No live chunks cover full source interval')
        chosen = max(reachable, key=lambda c: (c['end'], c['id']))
        finish = min(end, chosen['end'])
        selected.append({'chunk_id': chosen['id'], 'normalized_page_start': cursor,
                         'normalized_page_end': finish, 'chunk_start': cursor - chosen['start'],
                         'chunk_end': finish - chosen['start']})
        cursor = finish
    return selected


def verify_record(record, kind, pages, chunks):
    """Verify original page/context hashes and quotes before resolving chunk supports."""
    ident = record['candidate_id'] if kind == 'candidate' else record['evidence_id']
    paper = record['source_paper_id'] if kind == 'candidate' else record['paper_id']
    number = int(record['pdf_page_1based'])
    require(1 <= number <= len(pages[paper]), 'Invalid PDF page')
    page = pages[paper][number - 1]
    require(page['raw_sha256'] == record['page_text_sha256'], 'Raw page hash mismatch')
    a, b, c, d = (int(record[key]) for key in (
        'excerpt_start_char_0based', 'excerpt_end_char_exclusive',
        'context_start_char_0based', 'context_end_char_exclusive'))
    require(0 <= c <= a < b <= d <= len(page['raw_text']), 'Invalid raw offsets')
    require(page['raw_text'][a:b] == record['supporting_excerpt'], 'Exact excerpt mismatch')
    require(digest(page['raw_text'][c:d]) == record['context_text_sha256'], 'Context hash mismatch')
    return {'kind': kind, 'id': ident, 'paper_id': paper, 'pdf_page': number,
            'raw_excerpt': [a, b], 'raw_context': [c, d],
            'excerpt_supports': map_supports(chunks, pages, paper, number, a, b),
            'context_supports': map_supports(chunks, pages, paper, number, c, d),
            'student_review_status': 'PENDING',
            'alias_resolution': 'PENDING' if kind == 'candidate' else 'NOT_APPLICABLE'}

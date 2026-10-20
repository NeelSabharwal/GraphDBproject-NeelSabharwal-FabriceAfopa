"""Offline acceptance requests, not answer scoring (reserved for teammate tooling).

Reads only selected question strings from gold. The HTTP service never receives
gold labels, evidence registries or expected answers. Full responses stay ignored.
"""

import argparse
import json
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import ProxyHandler, build_opener


def main():
    """Save actual API responses, including refusals and failed requests."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=Path("data/evaluation/evaluation_gold.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/agent/smoke.json"))
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--ids", nargs="+", default=["Q01", "Q04", "Q08", "Q14"])
    args = parser.parse_args()
    questions = json.loads(args.gold.read_text())["questions"]
    results = []
    # Standard library client runs on the host: no extra container or gold mount.
    client = build_opener(ProxyHandler({}))
    for row in questions:
        if row["id"] not in args.ids:
            continue
        start = time.perf_counter()
        try:
            response = client.open(args.url.rstrip("/") + "/api/ask?" +
                                   urlencode({"q": row["question"]}), timeout=310)
        except HTTPError as error:
            response = error
        with response:
            payload = json.load(response)
        entry = {"id": row["id"], "question": row["question"], "http_status": response.code,
                 "seconds": round(time.perf_counter()-start, 3), "response": payload}
        results.append(entry)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2)+"\n")
        print(json.dumps({**{k: v for k, v in entry.items() if k != "response"},
            "status": payload.get("status"), "answer": payload.get("answer", payload.get("detail")),
            "citations": [{k: c[k] for k in ("paper_id", "page", "chunk_id", "quote")}
                          for c in payload.get("citations", [])],
            "tools": [{"tool": e["tool"], "outcome": e["outcome"],
                       "duration_ms": round(e["duration_ms"], 2)} for e in payload.get("trace", [])]}),
            flush=True)


if __name__ == "__main__":
    main()

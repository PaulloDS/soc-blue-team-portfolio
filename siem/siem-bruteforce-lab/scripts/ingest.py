#!/usr/bin/env python3
"""Cria o índice lab-winlogs (com mapeamento ECS) e ingere data/events.ndjson. Só stdlib."""
import argparse, base64, json, os, sys, urllib.request, urllib.error

MAPPING = {"mappings": {"properties": {
    "@timestamp": {"type": "date"},
    "event": {"properties": {k: {"type": "keyword"} for k in ("category", "action", "outcome", "code")}},
    "user": {"properties": {"name": {"type": "keyword"}}},
    "source": {"properties": {"ip": {"type": "ip"}}},
    "host": {"properties": {"name": {"type": "keyword"}}},
    "winlog": {"properties": {"logon": {"properties": {"type": {"type": "keyword"}}}}},
    "lab": {"properties": {"scenario": {"type": "keyword"}}}}}}


def call(url, method="GET", body=None, ctype="application/json", auth=None):
    req = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": ctype})
    if auth:
        req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        if e.code == 404 and method == "DELETE":
            return {}
        sys.exit(f"HTTP {e.code} em {method} {url}: {e.read().decode()[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"Não consegui conectar em {url}: {e.reason}. O Elasticsearch está de pé? (./lab.sh up)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--es", default=os.getenv("ES_URL", "http://localhost:9200"))
    ap.add_argument("--index", default="lab-winlogs")
    ap.add_argument("--file", default="data/events.ndjson")
    ap.add_argument("--reset", action="store_true", help="apaga e recria o índice")
    a = ap.parse_args()
    auth = f"elastic:{os.getenv('ELASTIC_PASSWORD', 'changeme-lab-only')}"
    if a.reset:
        call(f"{a.es}/{a.index}", "DELETE", auth=auth)
    exists = False
    try:
        urllib.request.urlopen(urllib.request.Request(f"{a.es}/{a.index}", method="HEAD", headers={
            "Authorization": "Basic " + base64.b64encode(auth.encode()).decode()}), timeout=30)
        exists = True
    except urllib.error.HTTPError:
        pass
    except urllib.error.URLError as e:
        sys.exit(f"Não consegui conectar em {a.es}: {e.reason}. O Elasticsearch está de pé? (./lab.sh up)")
    if not exists:
        call(f"{a.es}/{a.index}", "PUT", json.dumps(MAPPING).encode(), auth=auth)
    lines = []
    for line in open(a.file, encoding="utf-8"):
        lines += [json.dumps({"index": {"_index": a.index}}), line.strip()]
    res = call(f"{a.es}/_bulk?refresh=true", "POST", ("\n".join(lines) + "\n").encode(), "application/x-ndjson", auth)
    if res.get("errors"):
        sys.exit("Erros na ingestão: " + json.dumps(res["items"][:3])[:500])
    print(f"{len(lines)//2} eventos ingeridos em '{a.index}'")


if __name__ == "__main__":
    main()

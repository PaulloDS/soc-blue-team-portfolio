#!/usr/bin/env python3
"""Valida a detecção contra os dados que estão no Elasticsearch.

1) Agregações nativas do ES (equivalem às regras de limiar e spraying)
2) detector.py (sequência) sobre os documentos buscados
3) Compara com o gabarito (lab.scenario) e sai com código 1 se algo falhar.
"""
import base64, json, os, sys, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from detections import detector as d

ES = os.getenv("ES_URL", "http://localhost:9200")
IDX = os.getenv("LAB_INDEX", "lab-winlogs")
AUTH = base64.b64encode(f"elastic:{os.getenv('ELASTIC_PASSWORD', 'changeme-lab-only')}".encode()).decode()
FAIL = {"bool": {"filter": [{"term": {"event.category": "authentication"}}, {"term": {"event.outcome": "failure"}}]}}


def es(path, body):
    req = urllib.request.Request(f"{ES}/{path}", json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": "Basic " + AUTH})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def main():
    ok = True
    def check(label, cond):
        nonlocal ok
        ok &= bool(cond)
        print(("[OK]   " if cond else "[FALHA]"), label)

    r = es(f"{IDX}/_search", {"size": 0, "query": FAIL, "aggs": {"g": {"composite": {"size": 1000, "sources": [
        {"ip": {"terms": {"field": "source.ip"}}}, {"user": {"terms": {"field": "user.name"}}}]}}}})
    thr = {(b["key"]["ip"], b["key"]["user"]): b["doc_count"] for b in r["aggregations"]["g"]["buckets"] if b["doc_count"] >= 5}
    print("\nLimiar (>=5 falhas por IP+usuário, toda a janela do lab):")
    for k, v in thr.items():
        print(f"   {k[0]:>15} -> {k[1]:<14} {v} falhas")
    check("brute force detectado (203.0.113.45 -> administrator)", ("203.0.113.45", "administrator") in thr)
    check("falso positivo visível SEM tuning (svc_backup)", ("10.0.5.20", "svc_backup") in thr)
    tuned = {k for k in thr if k != ("10.0.5.20", "svc_backup")}
    check("com tuning, só o ataque permanece", tuned == {("203.0.113.45", "administrator")})

    r = es(f"{IDX}/_search", {"size": 0, "query": FAIL, "aggs": {"ip": {"terms": {"field": "source.ip", "size": 100},
          "aggs": {"users": {"cardinality": {"field": "user.name"}}}}}})
    spray = {b["key"]: (b["doc_count"], b["users"]["value"]) for b in r["aggregations"]["ip"]["buckets"]
             if b["doc_count"] >= 10 and b["users"]["value"] >= 5}
    print("\nSpraying (>=10 falhas e >=5 contas por IP):")
    for ip, (n, u) in spray.items():
        print(f"   {ip:>15} -> {n} falhas em {u} contas")
    check("password spraying detectado (198.51.100.77)", "198.51.100.77" in spray)
    check("spraying não confunde o ataque dirigido nem o serviço", set(spray) == {"198.51.100.77"})

    docs = es(f"{IDX}/_search", {"size": 10000, "sort": ["@timestamp"], "query": {"term": {"event.category": "authentication"}}})
    events = [h["_source"] for h in docs["hits"]["hits"]]
    seq = d.sequence_alerts(events)
    print("\nSequência (>=5 falhas e depois sucesso):")
    for a in seq:
        print(f"   {a['source.ip']} -> {a['user.name']}: {a['failures_before_success']} falhas antes do sucesso")
    check("sequência falha->sucesso detectada", [(a["source.ip"], a["user.name"]) for a in seq] == [("203.0.113.45", "administrator")])

    print("\nResultado:", "TUDO CERTO" if ok else "HÁ FALHAS")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

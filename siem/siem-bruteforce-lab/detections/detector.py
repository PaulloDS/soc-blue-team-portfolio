"""Lógica de detecção em Python espelhando as regras do Kibana.

Serve para testar a lógica offline (pytest) e para o verify.py comparar
com os dados que estão no Elasticsearch.
"""
from collections import Counter, defaultdict
from datetime import datetime, timedelta

TUNED_ALLOWLIST = [{"user.name": "svc_backup", "source.ip": "10.0.5.20"}]


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _get(ev, path):
    cur = ev
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def is_auth(ev, outcome):
    ev_ = ev.get("event", {})
    return "authentication" in ev_.get("category", []) and ev_.get("outcome") == outcome


def _excluded(ev, allowlist):
    return any(all(_get(ev, k) == v for k, v in rule.items()) for rule in (allowlist or []))


def threshold_alerts(events, threshold=5, window=timedelta(minutes=5), allowlist=None):
    """>= threshold falhas do mesmo (source.ip, user.name) dentro de 'window'."""
    groups = defaultdict(list)
    for e in events:
        if is_auth(e, "failure") and not _excluded(e, allowlist):
            groups[(_get(e, "source.ip"), _get(e, "user.name"))].append(parse_ts(e["@timestamp"]))
    alerts = []
    for (ip, user), ts in groups.items():
        ts.sort()
        best, lo, best_span = 0, 0, None
        for hi in range(len(ts)):
            while ts[hi] - ts[lo] > window:
                lo += 1
            if hi - lo + 1 > best:
                best, best_span = hi - lo + 1, (ts[lo], ts[hi])
        if best >= threshold:
            alerts.append({"rule": "threshold", "source.ip": ip, "user.name": user,
                           "count": best, "first_seen": best_span[0], "last_seen": best_span[1]})
    return sorted(alerts, key=lambda a: a["first_seen"])


def spray_alerts(events, min_failures=10, min_users=5, window=timedelta(minutes=10)):
    """Mesmo IP falhando contra >= min_users contas distintas na janela."""
    groups = defaultdict(list)
    for e in events:
        if is_auth(e, "failure"):
            groups[_get(e, "source.ip")].append((parse_ts(e["@timestamp"]), _get(e, "user.name")))
    alerts = []
    for ip, items in groups.items():
        items.sort()
        users, lo, hit = Counter(), 0, None
        for hi in range(len(items)):
            users[items[hi][1]] += 1
            while items[hi][0] - items[lo][0] > window:
                users[items[lo][1]] -= 1
                if users[items[lo][1]] == 0:
                    del users[items[lo][1]]
                lo += 1
            if hi - lo + 1 >= min_failures and len(users) >= min_users:
                hit = {"rule": "spray", "source.ip": ip, "failures": hi - lo + 1,
                       "distinct_users": len(users), "first_seen": items[lo][0], "last_seen": items[hi][0]}
                break
        if hit:
            alerts.append(hit)
    return sorted(alerts, key=lambda a: a["first_seen"])


def sequence_alerts(events, min_failures=5, maxspan=timedelta(minutes=10)):
    """>= min_failures falhas seguidas de sucesso (mesmo IP e usuário) em 'maxspan'."""
    fails, alerts = defaultdict(list), []
    auth = [e for e in events if is_auth(e, "failure") or is_auth(e, "success")]
    for e in sorted(auth, key=lambda x: x["@timestamp"]):
        key, t = (_get(e, "source.ip"), _get(e, "user.name")), parse_ts(e["@timestamp"])
        if is_auth(e, "failure"):
            fails[key].append(t)
        else:
            recent = [x for x in fails[key] if t - x <= maxspan]
            if len(recent) >= min_failures:
                alerts.append({"rule": "sequence", "source.ip": key[0], "user.name": key[1],
                               "failures_before_success": len(recent),
                               "first_seen": recent[0], "last_seen": t})
    return sorted(alerts, key=lambda a: a["first_seen"])

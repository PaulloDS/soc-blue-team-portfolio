#!/usr/bin/env bash
# Adiciona IPs secundários na MESMA interface/sub-rede do atacante, para que
# cada "perfil" de ataque saia de um IP de origem diferente de verdade.
# Uso: sudo ./add_ips.sh <interface> <ip-base> <quantidade>
# Ex.:  sudo ./add_ips.sh eth0 192.168.56.200 3    -> cria .200, .201, .202
set -euo pipefail
IFACE="${1:?informe a interface, ex: eth0 (veja com: ip a)}"
BASE="${2:?informe o IP base, ex: 192.168.56.200}"
N="${3:-3}"
IFS='.' read -r a b c d <<< "$BASE"
for i in $(seq 0 $((N-1))); do
  ip="$a.$b.$c.$((d+i))"
  sudo ip addr add "$ip/24" dev "$IFACE" label "${IFACE}:lab$i" 2>/dev/null \
    && echo "adicionado: $ip" || echo "(já existia ou falhou): $ip"
done
echo
echo "Para remover depois:"
for i in $(seq 0 $((N-1))); do
  echo "  sudo ip addr del $a.$b.$c.$((d+i))/24 dev $IFACE"
done

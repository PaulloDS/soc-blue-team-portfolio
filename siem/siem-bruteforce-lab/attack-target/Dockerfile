# Alvo de LABORATÓRIO: SSH com senha fraca de propósito, para treinar brute force
# e observar logs reais de autenticação sendo detectados pelo SIEM.
# Nunca exponha esta imagem fora da rede do Docker Compose.
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends openssh-server \
 && mkdir -p /var/run/sshd \
 && useradd -m -s /bin/bash labuser && echo 'labuser:123456' | chpasswd \
 && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
 && rm -rf /var/lib/apt/lists/*
EXPOSE 22
# -D: foreground, -e: log no stderr -> aparece em 'docker compose logs'
CMD ["/usr/sbin/sshd", "-D", "-e"]

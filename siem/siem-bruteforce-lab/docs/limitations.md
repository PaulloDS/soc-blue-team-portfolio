# Limitações (leia antes de divulgar)

- **Cenário principal é sintético.** Os 4 cenários do `./lab.sh demo` vêm de um gerador no formato ECS/Windows 4624-4625. Isso valida a lógica de detecção, não a coleta real.
- **Ataque com SSH/Linux:** `./lab.sh attack` é um fluxo disponível para executar autenticações contra um alvo local e converter logs reais em ECS. A execução desse fluxo e o disparo de alertas no Kibana devem ser verificados com evidências da máquina em que o lab foi executado; a presença do script não equivale a execução comprovada. Telemetria Windows com Sysmon/Elastic Agent permanece uma etapa futura.
- **Janela de lab.** As regras usam `from: now-1h` para encontrar dados gerados pouco antes. Em produção a janela deve ser `interval` + sobreposição pequena.
- **Limiar do Kibana não é deslizante.** O Python usa janela deslizante; o Kibana conta na janela da regra. Por isso os números podem diferir levemente.
- **Alertas repetidos.** Como os eventos continuam dentro da janela, a regra pode alertar de novo a cada execução.
- **Segurança.** Senha do lab e chaves de criptografia do Kibana são apenas para uso local e não são adequadas a produção. As portas agora usam `127.0.0.1` por padrão. Para coleta de VMs em rede Host-only, vincule `ES_BIND_IP` e, se necessário, `KIBANA_BIND_IP` ao IP específico da interface isolada. Nunca exponha a stack à internet.
- **Níveis de evidência:** testes automatizados validam funções Python; `verify.py` valida agregações no Elasticsearch e a lógica Python. A importação, agendamento e emissão de alertas nativos do Kibana precisam de evidência independente.
- **Dados ilustrativos:** a base sintética contém eventos em formato ECS com códigos Windows 4624/4625, mas não é telemetria capturada de um Windows real. Screenshots externos devem ser contextualizados e preferencialmente acompanhados de artefatos locais versionados, expurgados de segredos.

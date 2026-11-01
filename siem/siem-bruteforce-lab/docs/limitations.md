# Limitações (leia antes de divulgar)

- **Cenário principal é sintético.** Os 4 cenários do `./lab.sh demo` vêm de um gerador no formato ECS/Windows 4624-4625. Isso valida a lógica de detecção, não a coleta real.
- **O ataque real (`./lab.sh attack`) é Linux/SSH, não Windows.** Ele prova a detecção contra tráfego real, mas a telemetria Windows com Sysmon/Elastic Agent continua no roadmap.
- **Janela de lab.** As regras usam `from: now-1h` para encontrar dados gerados pouco antes. Em produção a janela deve ser `interval` + sobreposição pequena.
- **Limiar do Kibana não é deslizante.** O Python usa janela deslizante; o Kibana conta na janela da regra. Por isso os números podem diferir levemente.
- **Alertas repetidos.** Como os eventos continuam dentro da janela, a regra pode alertar de novo a cada execução.
- **Segurança.** Senha do lab e chaves de criptografia do Kibana são só para uso local. Nunca exponha essa stack na internet.

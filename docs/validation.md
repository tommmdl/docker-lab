# Validação — 17/10/2026

[English](validation.en.md)

Execução real em Linux/WSL com Docker Engine 29.1.3 e Compose 5.6.0. Os 23 testes terminaram às 18:53:48 no fuso America/Sao_Paulo (21:53:48 UTC). Execução realizada pelo assistente com autorização do proprietário.

## Resultados

| Cenário | Resultado observado |
| --- | --- |
| Inicialização com Compose | API e banco healthy |
| Página web | HTML servido com textos em português e inglês |
| API | Criar, listar e excluir notas; 404 ao excluir ID ausente |
| Validação | 400 para títulos inválidos; 413 para corpo excessivo |
| SQL parametrizado | Texto semelhante a SQL armazenado literalmente; tabela preservada |
| Recriação dos containers | Nota preservada no volume |
| Banco interrompido | Liveness 200; readiness e listagem 503 |
| Banco religado | API recuperou acesso sem reiniciar |
| Limpeza dos testes | Notas criadas pelos testes excluídas |
| Configuração em execução | API UID 10001, rootfs somente leitura; banco sem porta publicada |

## Evidências

- [Resultados dos 23 testes](../evidence/integration-results.json)
- [Versões e propriedades selecionadas dos containers](../evidence/runtime.json)
- [Logs da aplicação durante o cenário de falha e recuperação](../evidence/api.log)
- [Código dos testes](../tests/integration.py)

Python 3.13.16, Flask 3.1.2, Gunicorn 23.0.0, Psycopg 3.3.6 e PostgreSQL 17.11. Imagens base fixadas por digest e dependências Python fixadas em `requirements.lock`. Segredos locais não foram incluídos nos arquivos publicados.

## Limites

A página foi verificada por HTTP, sem teste visual ou automação dos cliques no navegador. Os testes exercitam indisponibilidade controlada e persistência do volume, sem cobrir carga, perda do volume, backup/restauração, TLS ou autenticação. A entrada semelhante a SQL é um teste pontual do uso de parâmetros, não uma auditoria completa de segurança. As imagens ficaram em execução para exploração local. O Jenkins de outro laboratório não foi alterado.

Neste ambiente, comandos Docker exigem autorização fora do sandbox. O Compose oficial já verificado no laboratório anterior foi reutilizado localmente; em um clone novo, `prepare.sh` faz a instalação com checksum quando necessário. Buildx estava ausente, então o Docker utilizou o builder clássico.

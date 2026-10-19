# Docker: uma aplicação, um banco e algumas falhas

[English](README.en.md) · Português

## Banco atual: Alpine, com rollback testado

Os labs agora usam a imagem PostgreSQL Alpine testada, fixada por digest. A adoção usou backup lógico e volumes novos; os volumes Debian originais continuam guardados. O rollback real da API preservou uma nota criada depois da troca. Veja o [procedimento de migração, backup e recuperação](docs/postgres-adoption.md). Os relatórios de segurança anteriores continuam disponíveis.

Uma aplicação de notas é simples o bastante para deixar o foco no que acontece ao redor dela. Aqui, a API e o PostgreSQL rodam em containers separados, e o Compose cuida de conectá-los.

O exercício fica mais interessante quando os containers são recriados ou o banco para: as notas continuam lá? A API sabe dizer que não está pronta? Ela se recupera quando o banco volta?

## Para começar

Linux/WSL, Docker, Bash, Python 3, curl e porta 8000 livre. O preparo pode instalar o Compose localmente em Linux x86_64.

Na raiz deste repositório:

```bash
bash scripts/prepare.sh
bash scripts/compose.sh up -d --build --wait --wait-timeout 180
```

Abra http://localhost:8000 e crie uma nota. O seletor no topo alterna a interface entre português e inglês.

## Experimente

1. Crie, liste e exclua notas pela interface ou pela API.
2. Recrie os containers e confira o que o volume preservou.
3. Pare o banco e compare `/healthz` com `/readyz`.
4. Religue o banco e observe a recuperação da API.

## O que já foi testado

Os 23 testes de integração passaram. Eles incluem persistência após recriar os containers, respostas 503 durante a parada do banco e recuperação sem reiniciar a API.

Os [resultados e seus limites](docs/validation.md) estão registrados com os comandos e evidências da execução. Eles se referem às revisões indicadas nos relatórios.

## Quando terminar

```bash
bash scripts/compose.sh down
```

As notas ficam no volume. Adicionar `-v` apaga esses dados. A API fica acessível apenas em localhost e não tem autenticação de usuários; este é um ambiente de estudo.

## Para ir além

O [guia de uso](docs/guide.md) reúne arquitetura, configuração, testes, limitações e ajuda para investigar problemas. O [portfólio](https://github.com/tommmdl/devops-portfolio) conecta este projeto aos outros laboratórios.

[Sobre a revisão do histórico](docs/history.md)

Veja as [correções nas imagens e os achados restantes](docs/remediation.md).

Validação das correções: 23 testes do Compose, restauração controlada de três notas da imagem original do PostgreSQL para a recompilada e 19 testes locais de tracing. A aplicação do Argo CD está Synced/Healthy e mantém o mesmo PVC. As evidências completas e as pendências estão no link acima.

A [análise dos críticos do PostgreSQL e o endurecimento do banco](docs/database-hardening.md) explica a imagem menor, as contas da aplicação/manutenção e os testes com volumes existentes.

A [alternativa PostgreSQL Alpine](docs/postgres-alternative.md) testa a libxml2 corrigida em outro volume, com restauração e retorno lógico. Esse teste foi seguido pela adoção documentada acima.

A [análise dos HIGH da API](https://github.com/tommmdl/security-lab/blob/main/docs/api-high-review.md) agrupa 44 ocorrências em oito CVEs e confere os pré-requisitos reais. Limites de recursos e restrições de privilégio mitigam a exposição; a imagem da API continua bloqueada e os achados completos permanecem visíveis.

O [ensaio da API Alpine](https://github.com/tommmdl/security-lab/blob/main/docs/api-alpine.md) testa as imagens básica e instrumentada com scans completos, aplicação e tracing real por Collector/Tempo/Grafana/Loki. Usa workloads e bancos separados; os pins da API principal continuam iguais.

# Docker: uma aplicação, um banco e algumas falhas

[English](README.en.md) · Português

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

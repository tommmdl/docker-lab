# Testando outra imagem do PostgreSQL sem reaproveitar o diretório de dados

Português · [English](postgres-alternative.en.md)

A alternativa mantém PostgreSQL 17.11 e passa para Alpine 3.24.2, com libxml2 2.13.9-r2. O achado CVE-2026-6653 desaparece. A imagem oficial trouxe de volta um Go antigo no gosu, então o Dockerfile copia apenas o auxiliar estático já corrigido da derivada Bookworm fixada por digest. As bibliotecas Debian não entram no sistema de arquivos final. A zlib recebe a atualização disponível 1.3.2-r1.

O scan completo registra zero achados nessa fotografia da base do Trivy, com inventário de pacotes e a mesma política. Isso não garante ausência de vulnerabilidades. Os relatórios intermediários preservam os achados do Go original e da zlib antes da atualização. [Comparação completa e fontes](https://github.com/tommmdl/security-lab/blob/main/docs/postgres-alternative.md).

## Uma aplicação separada

O Compose padrão, os volumes existentes e a aplicação Kubernetes continuam com a imagem Bookworm. A alternativa usa outro projeto, outra porta e outro volume. Depois da publicação, seu overlay fixa API e banco por digest.

```bash
bash scripts/prepare.sh
bash scripts/alternative.sh up
bash scripts/alternative.sh status
```

Abra http://localhost:8015. A demonstração local validada contém sete notas Unicode controladas; ela não substitui o banco em execução. `bash scripts/alternative.sh down` preserva o volume dessa alternativa.

## Restauração lógica, sem trocar a imagem sobre o PGDATA

O Alpine usa musl e UID 70; o Bookworm usa glibc e UID 999. O comportamento de locale pode mudar. O destino é inicializado com ICU/en-US e UTF8 em um volume novo. A origem usa libc/en_US.utf8. Os provedores e suas versões ficam registrados; a aplicação ordena por ID numérico, então o caminho testado não depende da ordenação dos títulos. Isso não certifica índices de texto arbitrários, extensões ou aplicações dependentes de locale.

O teste exporta um pg_dump em formato custom, restaura em um destino vazio com a conta comum e compara todos os campos das notas, propriedades das colunas, índices e estado da sequência de IDs. Exercita novos IDs, XPath/XML inofensivo, API e persistência após recriar containers. Depois exporta o destino de volta para outro banco Debian, verificando um retorno lógico. As linhas e a sequência da origem permanecem iguais. Nenhum diretório de dados original é montado no Alpine.

```bash
bash scripts/alternative.sh test
```

O teste reproduzível tem 17 verificações de migração, 23 da API e 20 de privilégios/recursos. A execução local também restaurou backups privados dos três labs existentes em outros bancos no destino e comparou os campos das notas. Esses bancos estavam vazios; as sete notas controladas são o teste de preservação com dados. Backups e conteúdo das notas ficam no `.local/` ignorado; apenas os JSONs de resultado são públicos.

As contas e a autenticação são criadas pelo hook de endurecimento existente, em vez de restaurar todos os objetos globais. A aplicação continua sem superusuário e as contas de manutenção rejeitam TCP. Os dumps usam no-owner/no-acl e a propriedade no destino fica com lab. O escopo é o esquema de notas, não todas as permissões ou extensões de um cluster compartilhado. Os serviços originais continuam disponíveis para retorno; escritas feitas apenas na alternativa exigiriam nova exportação reversa e troca controlada antes de voltar à origem.

Para desenvolvimento, construa a aplicação e o `images/postgres-alpine/Dockerfile` como imagens locais e execute `python3 tests/postgres_alternative.py`. `ALTERNATIVE_API_IMAGE` e `POSTGRES_ALTERNATIVE_IMAGE` permitem escolher imagens já publicadas. `KEEP_ALTERNATIVE=1` mantém apenas o destino bem-sucedido; ambientes de testes com falha são removidos. `ALTERNATIVE_LIVE_MANIFEST` é um manifesto local opcional de dumps e registros privados para comparação, nunca um artefato do CI.

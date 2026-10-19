# Um banco menor e uma conta separada para a aplicação

Português · [English](database-hardening.en.md)

A análise dos críticos remove libsqlite3-0 junto das ferramentas de gerenciamento de chaves GPG que não são usadas para servir o banco. O PostgreSQL não se liga ao SQLite, e a simulação de dependências do apt preserva os pacotes do servidor e do cliente. O gpgv e os chaveiros do Debian continuam disponíveis para verificar assinaturas dos pacotes. É remoção de pacotes, não uma exceção no scanner.

A aplicação continua conectando como `lab`, com a mesma senha, mas deixa de receber uma conta de superusuário. O PostgreSQL exige que o usuário bootstrap (OID 10) continue sendo superusuário. Na inicialização ou atualização explícita, o `lab-db-harden` renomeia esse usuário para `notes_bootstrap`, limpa sua senha, cria um novo `lab` comum com o verificador de senha existente e atribui a ele o banco e a tabela de notas. A sequência de identidade acompanha a tabela. O script não transfere a propriedade dos catálogos do sistema.

O `notes_admin` é a conta de manutenção local, não tem senha e é rejeitado explicitamente por TCP junto do `notes_bootstrap`, incluindo loopback e conexões de replicação. A administração por socket Unix ainda confia nos usuários dentro do container do banco. O acesso ao container/host continua sendo uma fronteira administrativa. A aplicação permanece dona do banco e da tabela para as migrações existentes do lab funcionarem; não é uma conta limitada estritamente a DML.

O Compose limita o banco a 384 MiB, uma CPU e 256 PIDs, ativa no-new-privileges e mantém a porta do banco sem publicação no host. Os padrões da conta acrescentam timeout de 5 segundos por comando e 10 segundos para uma transação ociosa. Isso reduz privilégios e limita recursos; não corrige a libxml2 nem desativa o parser XML. Um usuário SQL pode alterar esses padrões da sessão. Os dois achados críticos restantes continuam bloqueando o gate.

## Bancos novos e existentes

Bancos novos executam o hook durante a inicialização pelo entrypoint oficial. Trocar a imagem não repete os hooks em volumes já inicializados.

Em uma instância existente, salve antes backups privados dos dados, dos objetos globais e do pg_hba.conf. Depois de trocar para a imagem testada do banco, aplique a migração explícita:

```bash
bash scripts/compose.sh exec -T --user postgres db lab-db-harden
```

A operação foi feita para `notes`/`lab` e recusa outras configurações. Ela preserva o login da API, transfere apenas os objetos conhecidos do lab e desconecta as sessões antigas do bootstrap na primeira migração. Use uma janela de manutenção. Não é uma migração genérica para um cluster compartilhado.

Para manutenção depois:

```bash
bash scripts/compose.sh exec -T --user postgres db psql -U notes_admin -d notes
```

Voltar a imagem não desfaz os usuários persistidos nem o pg_hba.conf. Preserve a conta local de manutenção e use os backups para uma recuperação deliberada; evite restaurar os objetos globais às cegas sobre o cluster em execução.

## Repetir as verificações

```bash
python3 tests/database_security.py
python3 tests/integration.py
python3 tests/database_upgrade.py
```

Os 20 testes de segurança exercitam negações de privilégios, rejeição dos administradores por TCP, timeouts, texto parecido com XML e limites de recursos. Uma análise XML SQL inofensiva deve continuar funcionando: isso registra a exposição restante. Os 23 testes de integração continuam cobrindo a API e a persistência. O teste de atualização cria outro banco com três notas na imagem original, troca a imagem no mesmo volume, migra as contas, confere o encerramento de uma sessão privilegiada antiga e compara todos os campos das notas. Ele remove apenas o projeto e o volume temporários que criou.

Achados completos, fontes dos fornecedores e scans de antes/depois: [security-lab](https://github.com/tommmdl/security-lab/blob/main/docs/postgresql-critical.md).

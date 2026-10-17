# Sobre o histórico / About the history

Em 17/10/2026, as mensagens dos commits da branch `main` foram encurtadas para facilitar a leitura. Essa etapa preservou os arquivos de cada commit, seus autores e suas datas. Depois vieram as alterações de documentação. Os backups do histórico anterior foram salvos localmente antes do force push.

Os relatórios, logs e metadados de imagens continuam mostrando os SHAs usados nas execuções originais. Eles são registros históricos e não foram alterados para aparentar novas execuções. A tabela relaciona esses commits com os commits equivalentes do histórico revisado. O pipeline passa a usar uma revisão acessível do histórico novo em `source.json`.

On 2026-10-17, commit messages on `main` were shortened for readability. This step preserved each commit's files, authors and dates; documentation edits came afterward. Local backups were saved before the force push.

Reports, logs and image metadata still show the SHAs used by their original runs. They are historical records, not rewritten test results. The table maps those commits to their equivalents in the revised history. The pipeline's `source.json` uses an accessible revision from the new history.

| SHA anterior / Previous SHA | SHA equivalente / Equivalent SHA | Mensagem / Message |
| --- | --- | --- |
| `9879bdba2a695e42236e7cec97c48e072cabe954` | `b763cd682351b440d32a13f73e5a0493b1746c16` | Cria a aplicação de notas com Docker e PostgreSQL |
| `2c04e97d892796659bb2fc716f7ff18cc55d7305` | `59d4931a2edb5febd1635d4f50cedf9257aea6e5` | Corrige a leitura da senha no container Linux |

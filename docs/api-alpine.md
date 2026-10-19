# Uma API Alpine separada para experimentar

Execute `bash scripts/api-alpine.sh up -d --no-build --wait` e abra http://localhost:8016. O projeto e o volume do banco são próprios; a API padrão não é substituída. Para parar, use `bash scripts/api-alpine.sh down`; o volume fica guardado. Faça o build explícito com `images/api-alpine/Dockerfile`, ou use o digest publicado fixado no overlay. `python3 tests/api_alpine.py` verifica as imagens básica e instrumentada em projetos temporários únicos; somente os volumes desses testes são removidos.

[Análise completa nos dois idiomas, tracing e scans integrais](https://github.com/tommmdl/security-lab/blob/main/docs/api-alpine.md).

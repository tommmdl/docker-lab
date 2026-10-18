# Atualizando as imagens sem perder os achados de vista

O primeiro scan encontrou cópias vulneráveis de msgpack, setuptools e urllib3 dentro do pip. A API não usa essas cópias para atender requisições. Instalamos as dependências durante o build e depois removemos pip e ensurepip da imagem final. A remoção é das ferramentas de instalação; os metadados dos pacotes e o scanner continuam intactos. Para adicionar uma dependência da aplicação, agora é preciso reconstruir a imagem.

O Flask passa de 3.1.2 para 3.1.3. O pacote Debian liblzma5 passa para 5.8.1-1+deb13u2. As duas mudanças tratam achados com correção publicada, incluindo severidades baixa e desconhecida.

O PostgreSQL continua na versão 17.11 e no Debian Bookworm. A imagem oficial ainda distribui o gosu compilado com Go 1.24.6. Nossa imagem derivada compila a mesma revisão do gosu 1.19 com Go 1.27.2, github.com/moby/sys/user 0.4.1 e golang.org/x/sys 0.44.0. O Dockerfile registra o commit da fonte e os digests das duas imagens base. Ele substitui o executável, preservando o entrypoint original e a organização dos dados.

O Compose constrói as duas imagens. Use API_PORT e API_BASE_URL para testar em outra porta e COMPOSE_PROJECT_NAME para separar o volume de testes. Não use `down -v` em um banco cujos dados você precisa preservar.

A comparação dos scans, as vulnerabilidades restantes e a política de bloqueio mantida estão no [security-lab](https://github.com/tommmdl/security-lab). Menos achados não significa que as imagens passaram pelo gate de segurança.

# ✈️ TVTOP PBCS - Procedimento Operacional Padrão de Atualização e Deploy

Este documento detalha o ciclo completo de atualização do sistema **TVTOP PBCS**, cobrindo as alterações locais, o versionamento, o empacotamento da imagem Docker via arquivo `.tar`, a transferência para o servidor **Gort** e a subida limpa do container em produção.

---

## 📋 1. Controle de Versão e Alteração Local

Antes de gerar os artefatos de deploy, o versionamento da aplicação precisa ser atualizado para garantir a rastreabilidade da release na TIOp. Vale destacar que o versionamento prático da imagem é centralizado no arquivo de orquestração (`tvtop.yml`) no servidor de produção.

### Commit e Push para o GitHub
Na máquina local, certifique-se de que todas as alterações feitas na branch `versao-intraer` estão salvas e enviadas para o repositório remoto:

```bash
git status
git add .
git commit -m "feat: atualização de rotinas e melhorias na versao-intraer"
git push origin versao-intraer
```

---

## 📦 2. Empacotamento do Container (Na Máquina de Desenvolvimento)

Como o servidor de produção (**Gort**, IP `10.80.8.54`) opera em ambiente restrito e isolado da rede externa, a imagem Docker compilada na máquina local precisa ser exportada manualmente através de um arquivo compactado (`.tar`).

### Construir a Nova Imagem Docker Localmente
Garanta que a tag reflita exatamente a nova versão (ex: `1.1`), utilizando a mesma nomenclatura que será configurada posteriormente no arquivo `tvtop.yml` do servidor:

```bash
docker build -t tvtop_pbcs:1.1 .
```

> **Nota:** Se você utilizava uma tag anterior como `tvtop_pbcs:1.0`, lembre-se de incrementar o identificador para a nova versão que está sendo lançada.

### Exportar e Salvar a Imagem em um Arquivo `.tar`

```bash
docker save -o tvtop_pbcs_v1.1.tar tvtop_pbcs:1.1
```

---

## 🚀 3. Transferência e Deploy no Servidor Gort (`10.80.8.54`)

Com o arquivo `.tar` gerado na sua máquina de desenvolvimento, siga a ordem lógica abaixo no servidor de produção:

### A. Enviar o Arquivo `.tar` para a Home do Servidor
Transfira o arquivo compactado para a pasta do usuário root no servidor Gort (via `scp`):

```bash
scp tvtop_pbcs_v1.1.tar root@10.80.8.54:~/
```

### B. Acessar o Servidor Gort via SSH e Carregar a Nova Imagem

```bash
ssh root@10.80.8.54
docker load -i ~/tvtop_pbcs_v1.1.tar
```

### C. Desativar o Container Atual
Navegue até o diretório oficial de configuração e encerre o container em execução:

```bash
cd /tiop/dados-containers/tvtop
docker-compose -f tvtop.yml down
```

### D. Atualizar a Versão no Arquivo de Configuração (`tvtop.yml`)
Abra o arquivo de orquestração do container e atualize o parâmetro `image` para apontar para a nova versão carregada:

```yaml
version: '3.3'
services:
  tvtop:
    image: tvtop_pbcs:1.1  # <-- Atualizado para a nova versão
    container_name: tvtop_app
    environment:
      - VIRTUAL_HOST=tvtop.cindacta3.intraer
      - VIRTUAL_PORT=8501
      - HTTPS_METHOD=nohttps
      - STREAMLIT_SERVER_ENABLE_CORS=false
      - STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
    ports:
      - "8501:8501"
    networks:
      - rdecntrs-gort
    restart: always

networks:
  rdecntrs-gort:
    external: true
```

### E. Subir o Novo Container
Com o arquivo `tvtop.yml` atualizado e na mesma pasta, suba o container limpo:

```bash
docker-compose -f tvtop.yml up -d
```

### F. Limpeza de Imagens Órfãs e Arquivos Temporários
Remova a versão antiga da imagem para liberar espaço em disco e apague o `.tar` temporário da home:

```bash
# Listar imagens para identificar o ID/tag anterior
docker images

# Remover a imagem antiga obsoleta (substitua pela tag anterior)
docker rmi tvtop_pbcs:1.0  

# Remover o arquivo .tar temporário
rm ~/tvtop_pbcs_v1.1.tar
```

---

## 🔍 4. Validação Pós-Deploy

* Acesse o navegador e valide a aplicação através do endereço interno: `https://tvtop.cindacta3.intraer`
* Confirme se os dados e rascunhos em JSON continuam preservados no volume persistente e se a nova versão responde normalmente sem bloqueios de WebSocket pelo firewall.
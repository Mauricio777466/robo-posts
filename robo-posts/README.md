# Robô de posts: @mauricio__oficialll

Este robô **cria a arte e publica sozinho** um post de tecnologia no seu Instagram, **toda segunda, quarta e sexta às 19h** (horário de Brasília). Ele roda de graça no GitHub Actions.

- `content/posts.json`: o banco com 36 posts (12 semanas). Cada post tem tema, texto da arte, legenda e hashtags.
- `content/state.json`: guarda qual é o próximo post da fila. Não precisa mexer.
- `src/`: o código que gera as artes (`render.js`), prepara o post (`prepare.js`) e publica (`publish.js`).
- `docs/img/`: onde o robô salva as artes publicadas. É isso que cria o link público que o Instagram exige.

---

## Configuração: só uma vez, uns 30 minutos

### Parte 1: subir o projeto para o GitHub (GitHub Desktop)

1. Descompacte o arquivo `robo-posts.zip` numa pasta do seu computador.
2. No **GitHub Desktop**, vá em **File > Add local repository** e escolha a pasta `robo-posts`.
   - Se aparecer "this directory does not appear to be a Git repository", clique em **create a repository** e depois em **Create repository**.
3. Clique em **Publish repository**.
   - **Desmarque** a opção **"Keep this code private"**. O repositório precisa ser **público** para o Instagram conseguir ler a imagem.
4. Pronto: o projeto está em `github.com/SEU-USUARIO/robo-posts`.

### Parte 2: pegar as chaves do Instagram (Meta for Developers)

Pré-requisito: o Instagram **@mauricio__oficialll** precisa ser **conta profissional** (já é) e estar **vinculado a uma Página do Facebook**. Para conferir, vá no Instagram em **Configurações > Central de Contas** e veja se aparece uma página do Facebook ligada.

1. Acesse **developers.facebook.com** e entre com o seu Facebook.
2. Clique em **Meus apps > Criar app**.
   - Nome: `Robo Posts`.
   - Caso de uso: escolha a opção de **gerenciar/publicar no Instagram** (se aparecer "Outro", escolha **Outro** e depois tipo **Empresa**).
3. Abra o **Explorador da API do Graph** (developers.facebook.com/tools/explorer):
   - Em **App da Meta**, escolha `Robo Posts`.
   - Em **Permissões**, adicione:
     - `instagram_basic`
     - `instagram_content_publish`
     - `pages_show_list`
     - `pages_read_engagement`
     - `business_management`
   - Clique em **Generate Access Token** e autorize. Na tela de autorização, marque a sua página e o seu Instagram.
4. Transforme a chave em uma de longa duração:
   - Clique no **ⓘ** ao lado da chave e depois em **Abrir na Ferramenta de Token de Acesso**.
   - Clique em **Estender token de acesso** e copie a nova chave.
5. Volte ao Explorador, cole essa chave nova no campo **Token de acesso** e consulte:

   ```
   me/accounts?fields=name,access_token,instagram_business_account
   ```

   Na resposta, procure a sua página e anote dois valores:
   - `access_token` **da página**. Esse é o `IG_ACCESS_TOKEN`, e essa chave não expira.
   - `instagram_business_account.id`. Esse é o `IG_USER_ID`.

> A Meta muda as telas de vez em quando. Se algum nome estiver diferente, tire um print e peça ajuda ao Claude.

### Parte 3: guardar as chaves no GitHub (secretas)

1. No seu repositório no GitHub, vá em **Settings > Secrets and variables > Actions**.
2. Clique em **New repository secret** e crie:
   - Nome `IG_USER_ID`, com o valor do `instagram_business_account.id`.
   - Nome `IG_ACCESS_TOKEN`, com o valor do `access_token` da página.

As chaves ficam escondidas. Nem quem vê o repositório público consegue ler.

### Parte 4: testar

1. No GitHub, abra a aba **Actions**. Se pedir, clique em **I understand... enable workflows**.
2. Clique em **Robô de posts > Run workflow**, deixe marcado **Modo teste** e clique em **Run workflow**.
3. Quando terminar (✅ verde), a arte aparece em `docs/img/`. Nada foi publicado ainda.
4. Para publicar o primeiro post de verdade, rode de novo **desmarcando** o Modo teste. Confira no Instagram.

A partir daí ele publica sozinho **seg, qua e sex às 19h**. O GitHub pode atrasar alguns minutos em horários de pico.

---

## Dia a dia

- **Ver o que foi publicado:** aba **Actions** (cada execução) ou `content/state.json`.
- **Pausar:** **Actions > Robô de posts > ⋯ > Disable workflow**.
- **Quando os 36 posts acabarem:** a execução falha com o aviso "adicione novos posts". Peça ao Claude: *"cria mais 36 posts para o content/posts.json"*.
- **Ver todas as artes antes** (no seu PC, com Node instalado): `npm install`, depois `npx playwright install chromium`, depois `npm run preview`. As artes aparecem na pasta `preview/`.

## Formato de um post (`content/posts.json`)

Layouts disponíveis: `list`, `cards`, `terminal`, `versus` e `big`. Palavras entre `*asteriscos*` ficam destacadas na cor da paleta. As cores mudam sozinhas a cada post (ciano, roxo, verde, laranja, vermelho, amarelo).

---

Fonte Poppins © Indian Type Foundry, licença SIL Open Font License 1.1 (openfontlicense.org).

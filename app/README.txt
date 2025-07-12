# Quiosque Online IFMS

Sistema de exibição de informações em modo quiosque para TVs, computadores da instituição, com painel administrativo web para cadastro e gerenciamento de conteúdos, dispositivos e regras de exibição.

## Funcionalidades

- **Painel administrativo** protegido por login para:
  - Cadastro e edição de usuários.
  - Cadastro e gerenciamento de conteúdos (imagens e banners)
  - Cadastro e edição de dispositivos (por IP).
  - Criação de regras de exibição: vincule conteúdos a dispositivos, defina ordem e duração de exibição.
  - Configuração de modo escuro (dark mode).

- **Display (Quiosque)**:
  - Pode ser acessado de qualquer navegador (PC, notebook, tablet, celular etc..).
  - Exibição rotativa dos conteúdos conforme regras definidas para cada dispositivo/IP.
  - Acesso restrito por IP cadastrado.

## Requisitos para rodar o sistema

- Python 3.7+
- Flask
- Flask-SQLAlchemy
- Flask-Bcrypt
- pip install -r requirements.txt(para baixar todas os imports restantes)


## Instalação

1. **Clone o repositório ou copie/baixe os arquivos do projeto**

2. **Estrutura as pastas do projeto:**

quiosque/
└── app/
    ├── instance/
    │   └── quiosque.db
    ├── static/
    │   └── Imagens do projeto
    ├── templates/
    │   ├── login.html
    │   ├── register.html
    │   ├── dashPainelADM.html
    │   ├── dashAvisoConteudo.html
    │   ├── dashConfig.html
    │   ├── dashDispositivos.html
    │   ├── dashregrasNegocio.html
    │   ├── editarConteudo.html
    │   ├── editarDispositivo.html
    │   ├── display.html
    │   └── 403.html
    ├── venv(sera criado com comando)/
    ├── conteudos.db
    ├── app.py
    ├── init_db.py
    └── README.txt

3. **No terminal do VSCODE:**
   -> vai criar/ativar o ambiente virtual
   python -m venv venv
   -> Ative o ambiente virtual:
   para Windows: venv\Scripts\activate
   para Linux: source venv/bin/activate
   -> Vai instalar as dependências com: 
   pip install -r requirements.txt

4. **Executando o projeto:**
-> flask init_db.py (para inicializar o banco de dados)
-> app.py           (lembrando de navegar até a pasta app do projeto utilizando o 'cd app')

5. **Uso:**
-> http://localhost:5000/login (acessando pelo navegador do servidor)
voce vai registrar o usuario e fazer login
-> voce vai ser redirecionado para o painel (http://localhost:5000/painel)
aqui voce vera uma sidebar mostrando o nome do projeto, junto com as demais página do projeto, no meio da página voce vera um contador referente aos conteudos(imagens), dispositivos conectados(todos pelo ip) e as regras de exibição que estao cadastradas no sistema, no canto superior direito voce um icone que mostrará que ao clicar te mostrará o nome e o usuario da sua sessão atual

-> Agora seguindo na ordem da sidebar, a página de conteudos (http://localhost:5000/conteudos)
voce terá um formulario para preencher, o primeiro input é referente ao titulo(é bom colocar um titulo que te ajude a identificar o conteudo porque te ajudará mais para frente), outro para url da imagem(nome.png já o suficiente para renderizar a imagem dentro do sistema) e outro para o grupo de exibição(aqui a idéia é para referenciar um lugar que seria o foco deste conteudo, nao sera usado pelo sistema é mais para ajudar o usuario), a cada conteudo cadastrado voce vera um card com o nome, grupo selecionado e uma miniatura da imagem, junto com o botao de editar/excluir se o usuario quuiser

-> Nos dispositivos (http://localhost:5000/dispositivos)
Sera onde o projeto permitirá que o ip cadastrado exiba o quiosque, aqui voce tera um formulario para preencher com o nome do dispositivo e o seu ip(jogando o comando ipconfig no terminal voce pegara o numero que sera referente ao ipv4), clicando em cadastrar será gerado um card abaixo do formulário com o nome e ip cadastrados, além do botao de editar e de excluir para caso o usuario queira.

-> Exibição (http://localhost:5000/regras)
Vai ser aqui que o usuario vai definir onde e qual conteudo vai ser exibido no quiosque, voce terá um formulário com 4 campos, o primeiro será para voce selecionar o conteudo(classificado pelo titulo entao lembre-se de por um bom titulo), o proximo campo será para selecionar o dispositivo(classificado pelo nome e ip), o proximo será para decidir a ordem que as imagens vao ser exibidas, cada imagem vai ser pega de 2 em 2(por conta do layout do quiosque), entao as primeiras 2 imagens a serem exibidas serao a 1 e 2, 3 e 4, etc.. e por fim a duração que cada par de imagens ficará sendo exibida, para quando os segundos acabarem ela mudará para o proximo par de imagem(assim dando uma rotatividade para as imagens)

-> Configuração (http://localhost:5000/regras)
Aqui basicamente serivá apenas se voce quiser ativar o dark mode para usar o sistema, este dark mode te acompanhará para as outras páginas assim que ativado(se quiser também pode desativar)

-> Sair 
Basicamente o logout do usuario

-> Display (ip:porta/display ex:http://192.168.1.14:5000/display )
Não é uma area apresentada na sidebar, porque a ideia é que voce apenas configure o quiosque por esse painel e depois já deixe rodando no ip/maquina que voce quiser com a regra que voce montou e aqui basicamente ao lado direito voce terá 2 espaços para banners que ficarão rotacionando com os demais banners que foram registrados no sistema e na regra de negocio(lembrando que o segundo que essas imagens ficarão para mudar também será decidido na regra de negocio do sistema), abaixo destas imagens terá um quadro para os avisos da escola/faculdade e um outro referente aos eventos do mes(sao campos auto explicativos), ao lado esquerdo, voce tera um horario com a data e o dia de hoje. 










Para usar o Script é necessário que você siga o passo a passo desta documentação. E caso surja alguma dúvida sobre a instalação das bibliotecas e ferramentas necessárias
use o Google e a Inteligência Artificial ao seu favor. Use para tirar dúvidas sobre a instalação no seu sistema operacional.

Este script foi criado no desktop usando o sistema operacional GNU/Linux. Nos testes apresentados ele se saiu muito bem em vários ambientes operacionais incluindo o Termux (Aplicativo 
do celular usado no Android), GNU/Linux e Windows. Em sistemas como MacOS e Iphone não foram testados.

Vamos para a Instalação e configuração do script.


TERMUX

1° - No termux de autorização para ele ter acesso aos seus diretórios no seu dispositivo com o seguinte comando: termux-setup-storage

2° - No termux atualize seu sistema com o comando: pkg update && pkg upgrade -y

3° - No termux instale as seguintes ferramentas: pkg install python git curl -y

4° - Instale o telethon: pip install telethon

5° - Copie o link do script que estar aqui no github.

6° - Depois de copiado entre no termux e vá para a seguinte pasta: cd storage/downloads

7° - Após entrar na pasta, clone o ou baixe o script: git clone https://linkdoscriptcopiado

8° - Para listar diretórios "pastas" o comando é: ls

9° - Para entrar na pasta do script escreva: cd Clonador  e depois aperte tab para ele completar automaticamente.

10° - Após clonar o repositório rode o script com: python main.py

11° - Caso o arquivo que contém o script venha compactado, descompacte com um aplicatvo como o ZArchive

12° - Após seguir estes passos e o script já estiver rodando vá para seção telegram nesta documentação.


LINUX | DEBIAN

1° - Abra o terminal e instale as seguintes ferramentas:  sudo apt install git curl wget

2° - Instale as seguintes bibliotecas: sudo apt update && sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

3° - Instale o pyenv para não "danificar ou alterar" o python já nativo na sua máquina : curl https://pyenv.run | bash

4° - Copie o texto que irá aparecer: 
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

5° - Cole o texto que você copiou e adicione na última linha do arquivo: sudo nano ~/.bashrc

6° - Dê CTRL+O para salvar o arquivo e CTRL+X para sair do arquivo. Feche e abra o terminal.

7° - Com o terminal aberto faça o comando: pyenv install -l

8° - Escolha a versão do python mais recente e estável, por exemplo: pyenv install 3.12.12

9° - Coloque o python que foi instalado pelo pyenv como global: pyenv global 3.12.12

10° - Após a instalação rode o comando: pip install --upgrade pip  #Vai atualizar o pip para a versão mais recente.

11° - Depois de atualizar o pip instale o telethon: pip install telethon

12° - Depois de instalado vá até a pasta que estar o script baixado e rode ele com o comando: python main.py.

13° - O script já estar rodando, falta apenas configurar a API do telegram.


WINDOWS

1° - Vá no google e digite download python. Depois instale.

2° - Não tenho tanta familiaridade com o Windows mas recomendo assistir este tutorial para setar a variável do python: https://youtu.be/nM1QSFT4QR4?si=pUpJOLajcfC0gtcM

3° - Após intalação do python instale o telethon com o comando: pip install telethon

4° - Após instalar o python, baixe o arquivo do script que estar neste repositório, descompacte ele e com a tecla SHIFT+BOTÃO DIREITO DO MOUSE abra com o powershell.

5° - Após abri a pasta no powershell escreva o comando: python main.py  #Rode o script

6° - Para ter acesso à API do telegram, veja a seção telegram aqui da documentação.


TELEGRAM

1° - Para conseguir a API Hash é necessário acessar o telegram pelo navegador, no site https://my.telegram.org

2° - Siga as instruções apresentadas no site e após o código de confirmação clique em API Development

3° - Em CREATE NEW APPLICATION no APP TITLE coloque algo como Meu Bot, ou algo relacionado a isso.

4° - Em SHORT NAME escolha algo como MyBotapp9283

5° - Na URL pode deixar em branco.

6° - A plataforma você escolhe, se você estiver em notebook ou PC, escolha o DESKTOP. Se você estiver no TERMUX escolha a opção ANDROID.

7° - Na descrição deixe em branco e crie a aplicação.

8° - Em seguida, aparecerá o seu App api_id e o seu App api_hash. ⚠️ ATENÇÃO: NÃO COMPARTILHE ISSO PARA NINGUÉM! ISSO É SUA CONTA DE ACESSO!! ⚠️


Após a conclusão destas etapas coloque o seu número no script e coloque o seu código de confirmação. Pronto, o script estar todo instruido para sua compreensão.
Faça um bom proveito!

✝️ VIVA CRISTO REI! ✝️

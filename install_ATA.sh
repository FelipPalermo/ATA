#!/bin/bash

sudo install python3 
sudo install git 

echo "python3 instalado"
echo "continuando com instalacao do bot..."

REPO_URL="https://github.com/FelipPalermo/ATA.git"
DIR_NAME="ATA"

git clone $REPO_URL
cd $DIR_NAME

source venv/bin/activate

pip3 install -r requirements.txt
pip3 install discord.py pymongo

# Rodar o código Python
if [ -f src/Alan_the_Alarm.py ]; then
    echo "Rodando o código Python..."
    ./run.sh
else
    echo "Nenhum arquivo Alan_the_Alarm.py encontrado."
fi

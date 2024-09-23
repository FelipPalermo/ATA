#!/bin/bash

# Funcao que vai ser usada no trap 
stop_bot(){
	echo "\n"
	echo "Finalizando bot..." 
	echo "Interrompido pelo usuario" 
	exit 1
}

# SIGINT : comando CTRL + C 
trap stop_bot SIGINT

source venv/bin/activate

if [ -f src/Main.py ]; then
	echo "Iniciando Bot" 
	python3 src/Main.py

else 
	echo "Arquivo nao encontrado" 

fi

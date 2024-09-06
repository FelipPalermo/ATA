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

if [ -f src/Alan_the_alarm.py ]; then
	echo "Iniciando Bot" 
	python3 src/Alan_the_alarm.py

else 
	echo "Arquivo nao encontrado" 

fi

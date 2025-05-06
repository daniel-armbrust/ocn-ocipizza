#!/bin/bash
#
# functions/deploy-fn.sh
#

OCIPIZZA_APP_NAME="ocipizza-app"
FN_PORT=8090

function start_fnserver() {
    # Inicia o servidor local Fn server. Um loop é utilizado para monitorar 
    # a conclusão do processo de inicialização.

    local max_tries=3
    local count=0

    fn use context default &>/dev/null

    # Inicia o servidor local Fn server em background.
    fn start --log-level debug \
             --port "$FN_PORT" &>/dev/null &

    # Aguarda a inicialização completa do servidor.
    while [ $count -lt $max_tries ]; do
        fn list app &>/dev/null

        if [ $? -eq 0 ]; then
           return    
        fi

       sleep 3

    done

    echo "[ERRO] Não foi possível iniciar o servidor Fn-Project."
    exit 1    
}

function create_app() {    
    # Verifica se uma aplicação já foi criada anteriormente. Se não 
    # existir, a aplicação definida pela variável $OCIPIZZA_APP_NAME 
    # será criada.
    
    fn list app 2>/dev/null | grep -v "^NAME" | awk '{print $1}' | while read app_name; do
        if [ "$app_name" == "$OCIPIZZA_APP_NAME" ]; then
            return
        else
            fn create app "$OCIPIZZA_APP_NAME" &>/dev/null

            if [ $? -ne 0 ]; then
                echo "[ERRO] Não foi possível criar a aplicação: $OCIPIZZA_APP_NAME"
                exit 1
            fi
        fi
    done
}

function fn_deploy() {
    # Executa a implantação das funções presentes neste diretório.    
    fn deploy --all --local --no-bump

    ls -1 | while read funcname; do

        if [ -d "$funcname" ]; then        
            echo -e "\n[INFO] Criando a trigger para a função: $funcname"
            fn create trigger --type http \
                              --source "$funcname" "$OCIPIZZA_APP_NAME" "$funcname" "trigger-$funcname" &>/dev/null
        fi

    done
}


echo -e "\n[INFO] Iniciando servidor Fn-Project."
start_fnserver

echo -e "\n[INFO] Criando a aplicação: $OCIPIZZA_APP_NAME"
create_app

echo -e "\n[INFO] Iniciando o deployment das Funções ..."
fn_deploy

exit 0

#!/usr/bin/env python3

import re

def verifica_entrega(localidade: str):
    print('Localidade Encontrada!')
    
frase = 'É possível entregar uma pizza grande na Rua Aparecida n123?'

# Retorna a string rua ou avenida, se presentes na frase.
palavra_chave = ', '.join(re.findall(r'\b(rua|avenida)\b', frase, re.IGNORECASE)).lower()

if palavra_chave:
    # Encontra a posição numérica da palavra chave na frase (rua ou avenida).
    posicao = frase.lower().index(palavra_chave)

    # Extrai o texto após a palavra chave. O resultado será "Rua Aparecida n123?".
    texto_apos_palvra_chave = frase[posicao + len(palavra_chave):].strip()

    # Remove todos os caracteres especiais. O resultado será "Rua Aparecida n123".
    localidade = re.sub(r'[^\w\s]', '', texto_apos_palvra_chave)

    # Chama uma função para verificar se é possível entregar uma pizza 
    # no endereço solicitado.
    verifica_entrega(localidade)

else:
    print('Desculpe, não consegui entender ou não é possível entregar no endereço solicitado.')

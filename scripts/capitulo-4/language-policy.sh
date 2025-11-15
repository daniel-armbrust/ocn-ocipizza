#!/bin/bash
#
# scripts/capitulo-4/language-policy.sh
#
# Copyright (C) 2005-2024 by Daniel Armbrust <darmbrust@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# Importa funções externas.
source functions.sh

# Variáveis Globais.
tenancy_ocid="$(get_tenancy_compartmet_ocid "ocipizza")"

# Grupo dinâmico que faz referência ao serviço OCI Language.
oci iam dynamic-group create \
    --compartment-id "$tenancy_ocid" \
    --name "language-dyngrp" \
    --description "Grupo dinâmico para o serviço OCI Language." \
    --matching-rule "ALL {resource.type='ailanguagemodel'}" \
    --wait-for-state "ACTIVE"

# Política IAM que concede acesso ao bucket privado "chatbot-data" ao serviço OCI Language.
oci iam policy create \
    --compartment-id "$tenancy_ocid" \
    --name "language-policy" \
    --description "Políticas de Acesso para o Grupo Dinâmico \"language-dyngrp\" acessar os objetos do bucket \"chatbot-data\"." \
    --statements '["Allow dynamic-group language-dyngrp to manage objects in tenancy where target.bucket.name='chatbot-data'"]' \
    --wait-for-state "ACTIVE"

exit 0
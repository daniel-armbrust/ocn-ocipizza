#!/bin/bash
#
# scripts/capitulo-4/language-model-logs.sh
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

function get_latest_project_model_ocid() {
    # Retorna o OCID do último modelo de Classificação de Texto.

    local compartment_ocid="$1"
    local region="$2"

    oci ai language model list \
        --region "$region" \
        --compartment-id "$compartment_ocid" \
        --display-name "model-text-classification" \
        --all \
        --sort-order 'desc' \
        --query 'data.items[0].id' | tr -d '[]" \n'
}

function get_lang_project_model_workreq_ocid() {
    # Retorna o OCID da Work Request do projeto do OCI Language.

    local compartment_ocid="$1"
    local region="$2"
    local project_ocid="$3"

    oci ai language work-request list \
        --region "$region" \
        --compartment-id "$compartment_ocid" \
        --resource-id "$project_ocid" \
        --all \
        --query 'data.items[].id' | tr -d '[]" \n'
}

# OCID do compartimento do ambiente de produção (cmp-prd).
cmp_prd_ocid="$(get_compartmet_ocid "cmp-prd")"

# OCID do compartimento de aplicação do ambiente de produção (cmp-prd/cmp-appl).
cmp_appl_ocid="$(get_compartmet_ocid "$cmp_prd_ocid" "cmp-appl")"

# OCID do Modelo de Classificação de Texto da região "sa-saopaulo-1".
lang_project_model_ocid="$(get_latest_project_model_ocid "$cmp_appl_ocid" "sa-saopaulo-1")"

# OCID do Work Request do Modelo de Classificação de Texto da região "sa-saopaulo-1".
lang_project_model_workreq_ocid="$(get_lang_project_model_workreq_ocid "$cmp_appl_ocid" "sa-saopaulo-1" "$lang_project_model_ocid")"

# Exibe os logs do processo de treinamento do modelo de Classificação de Texto da região "sa-saopaulo-1".
oci ai language work-request log list \
    --region "sa-saopaulo-1" \
    --work-request-id "$lang_project_model_workreq_ocid" \
    --all \
    --query "data.items[].{log:message,hora:timestamp}" \
    --output table

exit 0
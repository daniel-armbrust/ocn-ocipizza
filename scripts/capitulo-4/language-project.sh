#!/bin/bash
#
# scripts/capitulo-4/language-project.sh
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

# OCID do compartimento do ambiente de produção (cmp-prd).
cmp_prd_ocid="$(get_compartmet_ocid "cmp-prd")"

# OCID do compartimento de aplicação do ambiente de produção (cmp-prd/cmp-appl).
cmp_appl_ocid="$(get_compartmet_ocid "$cmp_prd_ocid" "cmp-appl")"

# Criação do Projeto OCI Language na região "sa-saopaulo-1".
oci ai language project create \
    --region "sa-saopaulo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --display-name "chatbot-project" \
    --description "Projeto OCI Language para Chatbot da região \"sa-saopaulo-1\"." \
    --wait-for-state "SUCCEEDED"

# Criação do Projeto OCI Language na região "sa-vinhedo-1".
oci ai language project create \
    --region "sa-vinhedo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --display-name "chatbot-project" \
    --description "Projeto OCI Language para Chatbot da região \"sa-vinhedo-1\"." \
    --wait-for-state "SUCCEEDED"

exit 0
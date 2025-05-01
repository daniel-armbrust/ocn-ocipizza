#!/bin/bash
#
# scripts/chapter-2/compartment.sh
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

# Obtém funções externas.
source functions.sh

# Variáveis Globais.
tenancy_ocid="$(get_tenancy_compartmet_ocid "ocipizza")"

#
# Ambiente de Produção (cmp-prd).
#
oci iam compartment create \
    --compartment-id "$tenancy_ocid" \
    --name "cmp-prd" \
    --description "Compartimento para os recursos de produção (cmp-prd)." \
    --wait-for-state "ACTIVE"

prd_compartment_ocid="$(get_compartmet_ocid "cmp-prd")"

# Network (cmp-network).
oci iam compartment create \
    --compartment-id "$prd_compartment_ocid" \
    --name "cmp-network" \
    --description "Compartimento para os recursos de redes do ambiente de produção." \
    --wait-for-state "ACTIVE"

# Appl (cmp-appl).
oci iam compartment create \
    --compartment-id "$prd_compartment_ocid" \
    --name "cmp-appl" \
    --description "Compartimento para os recursos de aplicação do ambiente de produção." \
    --wait-for-state "ACTIVE"

# Database (cmp-database).
oci iam compartment create \
    --compartment-id "$prd_compartment_ocid" \
    --name "cmp-database" \
    --description "Compartimento para os recursos de banco de dados do ambiente de produção." \
    --wait-for-state "ACTIVE"

#
# Ambiente de Homologação (cmp-hml).
#
oci iam compartment create \
    --compartment-id "$tenancy_ocid" \
    --name "cmp-hml" \
    --description "Compartimento para os recursos de homologação (cmp-hml)." \
    --wait-for-state "ACTIVE"

hml_compartment_ocid="$(get_compartmet_ocid "cmp-hml")"

# Network (cmp-network).
oci iam compartment create \
    --compartment-id "$hml_compartment_ocid" \
    --name "cmp-network" \
    --description "Compartimento para os recursos de redes do ambiente de homologação." \
    --wait-for-state "ACTIVE"

# Appl (cmp-appl).
oci iam compartment create \
    --compartment-id "$hml_compartment_ocid" \
    --name "cmp-appl" \
    --description "Compartimento para os recursos de aplicação do ambiente de homologação." \
    --wait-for-state "ACTIVE"

# Database (cmp-database).
oci iam compartment create \
    --compartment-id "$hml_compartment_ocid" \
    --name "cmp-database" \
    --description "Compartimento para os recursos de banco de dados do ambiente de Homologação." \
    --wait-for-state "ACTIVE"

#
# Ambiente de Desenvolvimento (cmp-dev).
#
oci iam compartment create \
    --compartment-id "$tenancy_ocid" \
    --name "cmp-dev" \
    --description "Compartimento para os recursos de desenvolvimento (cmp-dev)." \
    --wait-for-state "ACTIVE"

dev_compartment_ocid="$(get_compartmet_ocid "cmp-dev")"

# Network (cmp-network)
oci iam compartment create \
    --compartment-id "$dev_compartment_ocid" \
    --name "cmp-network" \
    --description "Compartimento para os recursos de redes do ambiente de desenvolvimento." \
    --wait-for-state "ACTIVE"

# Appl (cmp-appl)
oci iam compartment create \
    --compartment-id "$dev_compartment_ocid" \
    --name "cmp-appl" \
    --description "Compartimento para os recursos de aplicação do ambiente de desenvolvimento." \
    --wait-for-state "ACTIVE"

# Database (cmp-database)
oci iam compartment create \
    --compartment-id "$dev_compartment_ocid" \
    --name "cmp-database" \
    --description "Compartimento para os recursos de banco de dados do ambiente de desenvolvimento." \
    --wait-for-state "ACTIVE"

exit 0

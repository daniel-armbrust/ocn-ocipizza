#!/bin/bash
#
# scripts/capitulo-2/quotas.sh
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

# Compute
oci limits quota create \
    --compartment-id "$tenancy_ocid" \
    --name "compute-quotas" \
    --description "Cotas para os serviços Compute Instances e Container Instances." \
    --statements "[
        'zero compute-core quotas in tenancy',
        'set compute-core quota standard-a1-core-count to 8 in tenancy where any {request.region = sa-saopaulo-1, request.region = sa-vinhedo-1}',
        'set compute-core quota standard-e5-core-count to 8 in tenancy where any {request.region = sa-saopaulo-1, request.region = sa-vinhedo-1}']" \
    --wait-for-state "ACTIVE"

# Block Storage
oci limits quota create \
    --compartment-id "$tenancy_ocid" \
    --name "blockstorage-quotas" \
    --description "Cotas para o serviço Block Storage." \
    --statements "[
        'zero block-storage quotas in tenancy',
        'set block-storage quota volume-count to 20 in tenancy where any {request.region = sa-saopaulo-1, request.region = sa-vinhedo-1}',
        'set block-storage quota total-storage-gb to 500 in tenancy where any {request.region = sa-saopaulo-1, request.region = sa-vinhedo-1}']" \
    --wait-for-state "ACTIVE"

# Database
oci limits quota create \
    --compartment-id "$tenancy_ocid" \
    --name "database-quotas" \
    --description "Cotas para o serviço Database." \
    --statements "['zero database quotas in tenancy']" \
    --wait-for-state "ACTIVE"

# File Storage
oci limits quota create \
    --compartment-id "$tenancy_ocid" \
    --name "filestorage-quotas" \
    --description "Cotas para o serviço File Storage." \
    --statements "['zero filesystem quotas in tenancy']" \
    --wait-for-state "ACTIVE"

# Vault 
oci limits quota create \
    --compartment-id "$tenancy_ocid" \
    --name "vault-quotas" \
    --description "Cotas para o serviço Vault." \
    --statements "['zero kms quotas in tenancy']" \
    --wait-for-state "ACTIVE"

# Network
oci limits quota create \
    --compartment-id "$tenancy_ocid" \
    --name "network-quotas" \
    --description "Cotas para o serviço Network." \
    --statements "[
        'zero vcn quotas in tenancy',
        'set vcn quota vcn-count to 6 in tenancy where any {request.region = sa-saopaulo-1, request.region = sa-vinhedo-1}',
        'set vcn quota reserved-public-ip-count to 2 in tenancy where any {request.region = sa-saopaulo-1, request.region = sa-vinhedo-1}']" \
    --wait-for-state "ACTIVE"

# NoSQL
oci limits quota create \
    --compartment-id "$tenancy_ocid" \
    --name "nosql-quotas" \
    --description "Cotas para o serviço NoSQL." \
    --statements "[
        'zero nosql quotas in tenancy',
        'set nosql quota table-size-gb to 100 in tenancy where any {request.region = sa-saopaulo-1, request.region = sa-vinhedo-1}',
        'set nosql quota read-unit-count to 50 in tenancy where any {request.region = sa-saopaulo-1, request.region = sa-vinhedo-1}',
        'set nosql quota write-unit-count to 50 in tenancy where any {request.region = sa-saopaulo-1, request.region = sa-vinhedo-1}']" \
    --wait-for-state "ACTIVE"

exit 0
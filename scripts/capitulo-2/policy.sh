#!/bin/bash
#
# scripts/capitulo-2/policy.sh
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

oci iam policy create \
    --compartment-id "$tenancy_ocid" \
    --name "network-users-policy" \
    --description "Políticas de Acesso para o Grupo network-users." \
    --statements "[
        'Allow group network-users to manage virtual-network-family in compartment cmp-prd:cmp-network',
        'Allow group network-users to manage virtual-network-family in compartment cmp-hml:cmp-network',
        'Allow group network-users to manage virtual-network-family in compartment cmp-dev:cmp-network',
        'Allow group network-users to manage dns in compartment cmp-prd:cmp-network',
        'Allow group network-users to manage dns in compartment cmp-hml:cmp-network',
        'Allow group network-users to manage dns in compartment cmp-dev:cmp-network',
        'Allow group network-users to manage load-balancers in compartment cmp-prd:cmp-network',
        'Allow group network-users to manage load-balancers in compartment cmp-hml:cmp-network',
        'Allow group network-users to manage load-balancers in compartment cmp-dev:cmp-network',
        'Allow group network-users to manage email-family in compartment cmp-prd:cmp-network',
        'Allow group network-users to manage email-family in compartment cmp-hml:cmp-network',
        'Allow group network-users to manage email-family in compartment cmp-dev:cmp-network',
        'Allow group network-users to manage waas-family in compartment cmp-prd:cmp-network',
        'Allow group network-users to manage waas-family in compartment cmp-hml:cmp-network',
        'Allow group network-users to manage waas-family in compartment cmp-dev:cmp-network']" \
    --wait-for-state "ACTIVE"

oci iam policy create \
    --compartment-id "$tenancy_ocid" \
    --name "appl-users-policy" \
    --description "Políticas de Acesso para o Grupo appl-users." \
    --statements "[
        'Allow group appl-users to manage instance-family in compartment cmp-prd:cmp-appl',
        'Allow group appl-users to manage instance-family in compartment cmp-hml:cmp-appl',
        'Allow group appl-users to manage instance-family in compartment cmp-dev:cmp-appl',
        'Allow group appl-users to manage volume-family in compartment cmp-prd:cmp-appl',
        'Allow group appl-users to manage volume-family in compartment cmp-hml:cmp-appl',
        'Allow group appl-users to manage volume-family in compartment cmp-dev:cmp-appl',
        'Allow group appl-users to manage cluster-family in compartment cmp-prd:cmp-appl',
        'Allow group appl-users to manage cluster-family in compartment cmp-hml:cmp-appl',
        'Allow group appl-users to manage cluster-family in compartment cmp-dev:cmp-appl',
        'Allow group appl-users to manage repos in compartment cmp-prd:cmp-appl',
        'Allow group appl-users to manage repos in compartment cmp-hml:cmp-appl',
        'Allow group appl-users to manage repos in compartment cmp-dev:cmp-appl',
        'Allow group appl-users to manage load-balancers in compartment cmp-prd:cmp-network',
        'Allow group appl-users to manage load-balancers in compartment cmp-hml:cmp-network',
        'Allow group appl-users to manage load-balancers in compartment cmp-dev:cmp-network',
        'Allow group appl-users to manage functions-family in compartment cmp-prd:cmp-appl',
        'Allow group appl-users to manage functions-family in compartment cmp-hml:cmp-appl',
        'Allow group appl-users to manage functions-family in compartment cmp-dev:cmp-appl',
        'Allow group appl-users to inspect virtual-network-family in compartment cmp-prd:cmp-network',
        'Allow group appl-users to inspect virtual-network-family in compartment cmp-hml:cmp-network',
        'Allow group appl-users to inspect virtual-network-family in compartment cmp-dev:cmp-network']" \
    --wait-for-state "ACTIVE"

oci iam policy create \
    --compartment-id "$tenancy_ocid" \
    --name "dba-users-policy" \
    --description "Políticas de Acesso para o Grupo dba-users." \
    --statements "[
        'Allow group dba-users to manage nosql-family in compartment cmp-prd:cmp-database',
        'Allow group dba-users to manage nosql-family in compartment cmp-hml:cmp-database',
        'Allow group dba-users to manage nosql-family in compartment cmp-dev:cmp-database']" \
    --wait-for-state "ACTIVE"

exit 0
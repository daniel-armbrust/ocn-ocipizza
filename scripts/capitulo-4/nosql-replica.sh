#!/bin/bash
#
# scripts/capitulo-4/nosql-replica.sh
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

# OCID do compartimento de banco de dados do ambiente de produção (cmp-prd/cmp-database).
cmp_appl_ocid="$(get_compartmet_ocid "$cmp_prd_ocid" "cmp-database")"

# FREEZE SCHEMA da tabela Pizza da região "sa-saopaulo-1".
oci nosql table update \
    --region "sa-saopaulo-1" \
    --table-name-or-id "pizza" \
    --compartment-id "$cmp_appl_ocid" \
    --ddl-statement "ALTER TABLE pizza FREEZE SCHEMA FORCE" \
    --wait-for-state "SUCCEEDED" \
    --force

# Cria uma réplica da tabela Pizza da região "sa-saopaulo-1" para a região "sa-vinhedo-1".
# Essa ação, antes de criar a réplica, irá criar uma cópia idêntica da tabela na região "sa-vinhedo-1".
oci nosql table create-replica \
    --region "sa-saopaulo-1" \
    --replica-region "sa-vinhedo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --table-name-or-id "pizza" \
    --wait-for-state "SUCCEEDED"

# FREEZE SCHEMA da tabela User da região "sa-saopaulo-1".
oci nosql table update \
    --region "sa-saopaulo-1" \
    --table-name-or-id "user" \
    --compartment-id "$cmp_appl_ocid" \
    --ddl-statement "ALTER TABLE user FREEZE SCHEMA FORCE" \
    --wait-for-state "SUCCEEDED" \
    --force

# FREEZE SCHEMA da tabela User.Order da região "sa-saopaulo-1".
oci nosql table update \
    --region "sa-saopaulo-1" \
    --table-name-or-id "user.order" \
    --compartment-id "$cmp_appl_ocid" \
    --ddl-statement "ALTER TABLE user.order FREEZE SCHEMA FORCE" \
    --wait-for-state "SUCCEEDED" \
    --force

# Cria uma réplica da tabela User da região "sa-saopaulo-1" para a região "sa-vinhedo-1".
# Essa ação, antes de criar a réplica, irá criar uma cópia idêntica da tabela na região "sa-vinhedo-1".
oci nosql table create-replica \
    --region "sa-saopaulo-1" \
    --replica-region "sa-vinhedo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --table-name-or-id "user" \
    --wait-for-state "SUCCEEDED"

# Cria uma réplica da tabela User.Order da região "sa-saopaulo-1" para a região "sa-vinhedo-1".
# Essa ação, antes de criar a réplica, irá criar uma cópia idêntica da tabela na região "sa-vinhedo-1".
oci nosql table create-replica \
    --region "sa-saopaulo-1" \
    --replica-region "sa-vinhedo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --table-name-or-id "user.order" \
    --wait-for-state "SUCCEEDED"

# FREEZE SCHEMA da tabela Email_Verification da região "sa-saopaulo-1".
oci nosql table update \
    --region "sa-saopaulo-1" \
    --table-name-or-id "email_verification" \
    --compartment-id "$cmp_appl_ocid" \
    --ddl-statement "ALTER TABLE email_verification FREEZE SCHEMA FORCE" \
    --wait-for-state "SUCCEEDED" \
    --force

# Cria uma réplica da tabela Email_Verification da região "sa-saopaulo-1" para a região "sa-vinhedo-1".
# Essa ação, antes de criar a réplica, irá criar uma cópia idêntica da tabela na região "sa-vinhedo-1".
oci nosql table create-replica \
     --region "sa-saopaulo-1" \
     --replica-region "sa-vinhedo-1" \
     --compartment-id "$cmp_appl_ocid" \
     --table-name-or-id "email_verification" \
     --wait-for-state "SUCCEEDED"

exit 0
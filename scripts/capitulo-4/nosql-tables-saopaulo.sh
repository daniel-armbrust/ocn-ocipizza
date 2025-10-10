#!/bin/bash
#
# scripts/capitulo-4/nosql-tables-saopaulo.sh
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

# OCI do compartimento de aplicação do ambiente de produção (cmp-prd/cmp-appl).
cmp_appl_ocid="$(get_compartmet_ocid "$cmp_prd_ocid" "cmp-appl")"

# Tabela Pizza da região "sa-saopaulo-1".
oci nosql table create \
    --region "sa-saopaulo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --name "pizza" \
    --table-limits "{\"capacityMode\": \"PROVISIONED\", \"maxReadUnits\": 5, \"maxWriteUnits\": 5, \"maxStorageInGBs\": 2}" \
    --wait-for-state "SUCCEEDED" \
    --ddl-statement "
        CREATE TABLE IF NOT EXISTS pizza (
            id INTEGER,
            name STRING,
            description STRING,
            image STRING,
            price NUMBER,
            json_replica JSON,
         PRIMARY KEY(id))"

# Tabela User da região "sa-saopaulo-1".
oci nosql table create \
    --region "sa-saopaulo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --name "user" \
    --table-limits "{\"capacityMode\": \"PROVISIONED\", \"maxReadUnits\": 5, \"maxWriteUnits\": 5, \"maxStorageInGBs\": 2}" \
    --wait-for-state "SUCCEEDED" \
    --ddl-statement "
         CREATE TABLE IF NOT EXISTS user (
            id INTEGER,
            name STRING,
            email STRING,
            password STRING,
            telephone STRING,
            verified BOOLEAN DEFAULT FALSE,
            json_replica JSON,           
         PRIMARY KEY(id))"

# Tabela User.Order da região "sa-saopaulo-1".
oci nosql table create \
    --region "sa-saopaulo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --name "user.order" \
    --wait-for-state "SUCCEEDED" \
    --ddl-statement "
         CREATE TABLE IF NOT EXISTS user.order ( 
            order_id INTEGER,             
            address JSON,
            pizza JSON,  
            total NUMBER,
            order_datetime INTEGER,
            status ENUM(PREPARING,OUT_FOR_DELIVERY,DELIVERED,CANCELED) DEFAULT PREPARING,             
         PRIMARY KEY (order_id))"

# Tabela Email_Verification da região "sa-saopaulo-1".
oci nosql table create \
    --region "sa-saopaulo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --name "email_verification" \
    --table-limits "{\"capacityMode\": \"PROVISIONED\", \"maxReadUnits\": 5, \"maxWriteUnits\": 5, \"maxStorageInGBs\": 2}" \
    --wait-for-state "SUCCEEDED" \
     --ddl-statement "
         CREATE TABLE IF NOT EXISTS email_verification ( 
            email STRING,
            token STRING,                         
            expiration_ts INTEGER,
         PRIMARY KEY (email)) USING TTL 1 DAYS"

exit 0
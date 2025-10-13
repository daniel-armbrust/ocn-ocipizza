#!/bin/bash
#
# scripts/capitulo-4/nosql-data.sh
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

# Pizzas (data/pizza.data).
while IFS= read -r data_line; do

    oci nosql row update \
        --region "sa-saopaulo-1" \
        --compartment-id "$cmp_appl_ocid" \
        --table-name-or-id "pizza" \
        --value "$data_line" \
        --option "IF_ABSENT" \
        --force
    
    # Aguarda 1.2 segundos após a inserção do registro.
    sleep 1.2
    
done < "data/pizza.data"

# Users (data/user.data).
while IFS=";" read -r id name email password telephone verified; do

    # Gera um hash da senha.
    crypt_password="$(echo -n "$password" | openssl dgst -sha256 | awk '{print $2}')"

    sql="
        INSERT INTO user (id, name, email, password, telephone, verified)
            VALUES ($id, '$name', '$email', '$crypt_password', '$telephone', $verified)"

    oci nosql query execute \
        --region "sa-saopaulo-1" \
        --compartment-id "$cmp_appl_ocid" \
        --statement "$sql"

    # Aguarda 1.2 segundos após a inserção do registro.
    sleep 1.2

done < "data/user.data"

# Orders (data/order.data).
while IFS=";" read -r user_id order_id address pizza total order_datetime status; do

    sql="
        INSERT INTO user.order (id, order_id, address, pizza, total, order_datetime, status)
            VALUES ($user_id, $order_id, '$address', '$pizza', $total, $order_datetime, '$status')"
       
    oci nosql query execute \
        --region "sa-saopaulo-1" \
        --compartment-id "$cmp_appl_ocid" \
        --statement "$sql"

    # Aguarda 1.2 segundos após a inserção do registro.
    sleep 1.2
    
done < "data/order.data"

exit 0
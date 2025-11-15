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

function hash_password() {
    # Gera um hash de senha compatível com a implementação Werkzeug.
    # https://werkzeug.palletsprojects.com/en/stable/
    
    local password="$1"

    local iter="${2:-260000}"
    local salt_len="${3:-8}"

python3 - "$password" "$iter" "$salt_len" <<PYTHON
import hashlib, binascii, random, string, sys

password = sys.argv[1].encode('utf-8')
iterations = int(sys.argv[2])
salt_length = int(sys.argv[3])

SALT_CHARS = string.ascii_letters + string.digits
salt = ''.join(random.choice(SALT_CHARS) for _ in range(salt_length))

dk = hashlib.pbkdf2_hmac('sha256', password, salt.encode('utf-8'), iterations)
hash_hex = binascii.hexlify(dk).decode('ascii')

print(f"pbkdf2:sha256:{iterations}\${salt}\${hash_hex}")
PYTHON
}

# OCID do compartimento do ambiente de produção (cmp-prd).
cmp_prd_ocid="$(get_compartmet_ocid "cmp-prd")"

# OCID do compartimento de aplicação do ambiente de produção (cmp-prd/cmp-database).
cmp_appl_ocid="$(get_compartmet_ocid "$cmp_prd_ocid" "cmp-database")"

if [ -z "`which python3`" ]; then
    echo 'Binário python3 não encontrado! É necessário instalá-lo.'
    exit 1
fi

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
    crypt_password="$(hash_password "$password")"
    
    sql="INSERT INTO user (id, name, email, password, telephone, verified)
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

    sql="INSERT INTO user.order (id, order_id, address, pizza, total, order_datetime, status)
           VALUES ($user_id, $order_id, '$address', '$pizza', $total, $order_datetime, '$status')"
       
    oci nosql query execute \
        --region "sa-saopaulo-1" \
        --compartment-id "$cmp_appl_ocid" \
        --statement "$sql"

    # Aguarda 1.2 segundos após a inserção do registro.
    sleep 1.2
    
done < "data/order.data"

exit 0
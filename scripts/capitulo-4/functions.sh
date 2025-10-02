#!/bin/bash
#
# scripts/capitulo-4/functions.sh
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

function get_compartmet_ocid() {
    local name_or_ocid="$1"
    local name="$2"

    if [ -z "$(echo -n "$name_or_ocid" | egrep 'ocid[0-9]{1,1}\.')" ]; then
       
        oci iam compartment list \
            --name "$name_or_ocid" \
            --query "data[].id" | tr -d '[]" \n'

    else        
         
        oci iam compartment list \
            --compartment-id "$name_or_ocid" \
            --name "$name" \
            --query "data[].id" | tr -d '[]" \n'

    fi    
}
#!/bin/bash
#
# scripts/capitulo-4/bucket-file-upload.sh
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

# Cópia dos arquivos do diretório "imgs/" para o Bucket "pizza" da 
# região "sa-saopaulo-1".
oci os object bulk-upload \
    --region "sa-saopaulo-1" \
    --bucket-name "pizza" \
    --src-dir "imgs/" \
    --content-type "image/jpeg" \
    --verify-checksum

# Cópia dos arquivos do diretório "imgs/" para o Bucket "pizza" da 
# região "sa-vinhedo-1".
oci os object bulk-upload \
    --region "sa-vinhedo-1" \
    --bucket-name "pizza" \
    --src-dir "imgs/" \
    --content-type "image/jpeg" \
    --verify-checksum

exit 0
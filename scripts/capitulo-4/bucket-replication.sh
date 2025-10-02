#!/bin/bash
#
# scripts/capitulo-4/bucket-replication.sh
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

# Habilita a replicação dos dados do bucket "pizza" da região "sa-saopaulo-1" 
# para a região "sa-vinhedo-1".
oci os replication create-replication-policy \
    --region "sa-saopaulo-1" \
    --bucket-name "pizza" \
    --destination-bucket "pizza" \
    --destination-region "sa-vinhedo-1" \
    --name "pizza-repl-policy"

exit 0



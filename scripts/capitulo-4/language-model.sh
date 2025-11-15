#!/bin/bash
#
# scripts/capitulo-4/language-model.sh
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

# OCID do compartimento de aplicação do ambiente de produção (cmp-prd/cmp-appl).
cmp_appl_ocid="$(get_compartmet_ocid "$cmp_prd_ocid" "cmp-appl")"

# OCID do Projeto OCI Language na região "sa-saopaulo-1".
saopaulo_project_ocid="$(get_lang_project_ocid "chatbot-project" "$cmp_appl_ocid" "sa-saopaulo-1")"

# OCID do Projeto OCI Language na região "sa-vinhedo-1". 
vinhedo_project_ocid="$(get_lang_project_ocid "chatbot-project" "$cmp_appl_ocid" "sa-vinhedo-1")"

# Object Storage Namespace.
os_namespace="$(oci os ns get --raw-output --query 'data')"

# Cria e treina o modelo para Classificação de Texto na região "sa-saopaulo-1".
oci ai language model create \
    --region "sa-saopaulo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --project-id "$saopaulo_project_ocid" \
    --display-name "model-text-classification" \
    --description "Modelo para Classificação de Texto." \
    --model-details "{
        \"modelType\": \"TEXT_CLASSIFICATION\",
        \"languageCode\": \"en\",
        \"version\": \"V1.0\",
        \"classificationMode\": { 
            \"classificationMode\": \"MULTI_CLASS\" 
        }       
    }" \
    --training-dataset "{
        \"locationDetails\": {
            \"locationType\": \"OBJECT_LIST\",
            \"bucketName\": \"chatbot-data\",
            \"namespaceName\": \"$os_namespace\",
            \"objectNames\": [\"chatbot-train-intents.csv\"]
        },
        \"datasetType\": \"OBJECT_STORAGE\"
    }" \
    --test-strategy "{
        \"testingDataset\": {
            \"locationDetails\": {
                \"locationType\": \"OBJECT_LIST\",
                 \"bucketName\": \"chatbot-data\",
                 \"namespaceName\": \"$os_namespace\",
                 \"objectNames\": [\"chatbot-test-intents.csv\"]
            },
            \"datasetType\": \"OBJECT_STORAGE\"
        },
        \"strategyType\": \"TEST_AND_VALIDATION_DATASET\"
    }" \
    --wait-for-state "ACCEPTED"

# Cria e treina o modelo para Classificação de Texto na região "sa-vinhedo-1".
oci ai language model create \
    --region "sa-vinhedo-1" \
    --compartment-id "$cmp_appl_ocid" \
    --project-id "$vinhedo_project_ocid" \
    --display-name "model-text-classification" \
    --description "Modelo para Classificação de Texto." \
    --model-details "{
        \"modelType\": \"TEXT_CLASSIFICATION\",
        \"languageCode\": \"en\",
        \"version\": \"V1.0\",
        \"classificationMode\": { 
            \"classificationMode\": \"MULTI_CLASS\" 
        }       
    }" \
    --training-dataset "{
        \"locationDetails\": {
            \"locationType\": \"OBJECT_LIST\",
            \"bucketName\": \"chatbot-data\",
            \"namespaceName\": \"$os_namespace\",
            \"objectNames\": [\"chatbot-train-intents.csv\"]
        },
        \"datasetType\": \"OBJECT_STORAGE\"
    }" \
    --test-strategy "{
        \"testingDataset\": {
            \"locationDetails\": {
                \"locationType\": \"OBJECT_LIST\",
                 \"bucketName\": \"chatbot-data\",
                 \"namespaceName\": \"$os_namespace\",
                 \"objectNames\": [\"chatbot-test-intents.csv\"]
            },
            \"datasetType\": \"OBJECT_STORAGE\"
        },
        \"strategyType\": \"TEST_AND_VALIDATION_DATASET\"
    }" \
    --wait-for-state "ACCEPTED"
    
exit 0
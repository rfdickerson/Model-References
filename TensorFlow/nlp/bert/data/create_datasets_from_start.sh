#!/bin/bash

# Copyright (c) 2019 NVIDIA CORPORATION. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

###############################################################################
# Copyright (C) 2021 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
#
# Changes:
# - Removed downloading and preprocessing datasets that are not related to BERT pretrain
# - Modified file structures originally for NVidia container
# - Added downloading WikiExtractor and bookcorpus repositories
###############################################################################


to_download=${1:-"wiki_only"} # By default, we don't download BooksCorpus dataset due to recent issues with the host server

data_dir=$(pwd)
BERT_PREP_WORKING_DIR="${data_dir}"
export BERT_PREP_WORKING_DIR="${BERT_PREP_WORKING_DIR}"

echo "Checkout WikiExtractor repository"
# checkout WikiExtractor scripts
git clone https://github.com/attardi/wikiextractor.git && cd wikiextractor && git checkout 6408a430fc504a38b04d37ce5e7fc740191dee16 && cd ..

# Download Wikipedia dataset and/or Bookscorpus dataset
echo "Download dataset ${to_download}"
if [ "$to_download" = "wiki_books" ] ; then
    # checkout BookCorpus download scripts
    git clone https://github.com/soskek/bookcorpus.git
    python3 ${data_dir}/bertPrep.py --action download --dataset bookscorpus
fi
python3 ${data_dir}/bertPrep.py --action download --dataset wikicorpus_en

echo "Download pretrained weights"
echo "${data_dir}"
python3 ${data_dir}/bertPrep.py --action download --dataset google_pretrained_weights  # Includes vocab

DATASET="wikicorpus_en"

# Properly format the text files
if [ "$to_download" = "wiki_books" ] ; then
    python3 ${data_dir}/bertPrep.py --action text_formatting --dataset bookscorpus
    DATASET="books_wiki_en_corpus"
fi
python3 ${data_dir}/bertPrep.py --action text_formatting --dataset wikicorpus_en

# Shard the text files
python3 ${data_dir}/bertPrep.py --action sharding --dataset ${DATASET}

# Create TFRecord files Phase 1
python3 ${data_dir}/bertPrep.py --action create_tfrecord_files --dataset ${DATASET} --max_seq_length 128 \
 --max_predictions_per_seq 20 --vocab_file ${BERT_PREP_WORKING_DIR}/download/google_pretrained_weights/uncased_L-24_H-1024_A-16/vocab.txt


# Create TFRecord files Phase 2
python3 ${data_dir}/bertPrep.py --action create_tfrecord_files --dataset ${DATASET} --max_seq_length 512 \
 --max_predictions_per_seq 80 --vocab_file ${BERT_PREP_WORKING_DIR}/download/google_pretrained_weights/uncased_L-24_H-1024_A-16/vocab.txt

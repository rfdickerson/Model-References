###############################################################################
# Copyright (C) 2020-2021 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
###############################################################################

import os
from pathlib import Path
import sys
import socket
import subprocess
from TensorFlow.common.habana_model_runner_utils import get_canonical_path

def create_pretraining_data_overfit_r(dataset_path, pretrained_model, seq_length, max_pred_per_seq):
    host_name = socket.gethostname()
    try:
        ds_path = get_canonical_path(dataset_path)
        if not os.path.isdir(ds_path):
            os.makedirs(ds_path, mode=0o777, exist_ok=True)
            run_create_pretraining_path = Path(__file__).parent.joinpath('create_pretraining_data.py')
            input_file_path = Path(__file__).parent.joinpath("sample_text.txt")
            output_file_path = ds_path.joinpath("tf_examples.tfrecord")
            pretrained_model_path = get_canonical_path(pretrained_model)
            vocab_file_path = pretrained_model_path.joinpath("vocab.txt")

            command = (
                f"python3 {str(run_create_pretraining_path)}"
                f" --input_file={str(input_file_path)}"
                f" --output_file={str(output_file_path)}"
                f" --vocab_file={str(vocab_file_path)}"
                f" --do_lower_case=True"
                f" --max_seq_length={seq_length}"
                f" --max_predictions_per_seq={max_pred_per_seq}"
                f" --masked_lm_prob=0.15"
                f" --random_seed=12345"
                f" --dupe_factor=5"
            )
            print(f"{host_name}: {__file__}: create_pretraining_data_overfit_r() command = {command}")
            sys.stdout.flush()
            sys.stderr.flush()
            with subprocess.Popen(command, shell=True, executable='/bin/bash') as proc:
                proc.wait()
    except Exception as exc:
        raise Exception(f"{host_name}: Error in {__file__} create_pretraining_data_overfit_r({dataset_path}, {pretrained_model}, {seq_length}, {max_pred_per_seq})") from exc

if __name__ == "__main__":
    host_name = socket.gethostname()
    print(f"{host_name}: In {sys.argv[0]}")
    print(f"{host_name}: called with arguments: \"{sys.argv[1]} {sys.argv[2]} {sys.argv[3]} {sys.argv[4]}\"")
    dataset_path = sys.argv[1]
    pretrained_model = sys.argv[2]
    seq_length = sys.argv[3]
    max_pred_per_seq = sys.argv[4]
    print(f"{host_name}: MULTI_HLS_IPS = {os.environ.get('MULTI_HLS_IPS')}")
    create_pretraining_data_overfit_r(dataset_path, pretrained_model, seq_length, max_pred_per_seq)

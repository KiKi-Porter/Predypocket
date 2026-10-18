#!/usr/bin/env bash
# Download the pretrained PocketMiner checkpoint used to initialize the frozen
# GVP-GNN encoder for training. Inference uses weights/predypocket_model only.
set -euo pipefail
OUT_DIR=${1:-weights/pocketminer}
BASE=https://raw.githubusercontent.com/Mickdub/gvp/pocket_pred/models
mkdir -p "${OUT_DIR}"
for f in pocketminer.index pocketminer.data-00000-of-00001; do
  curl -fL --retry 3 -o "${OUT_DIR}/${f}" "${BASE}/${f}"
done
echo "PocketMiner checkpoint saved to ${OUT_DIR}/pocketminer"

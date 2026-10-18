# Model weights

`predypocket_model` is the trained PreDyPocket checkpoint used for inference. Pass
the checkpoint prefix, not an individual file:

```text
weights/predypocket_model
```

| File | Size | SHA256 |
|---|---:|---|
| `predypocket_model.index` | 16 KB | `248f622ea27df2673c01ea3bd80668ef62be38591948e1b844d962ab7d4120bf` |
| `predypocket_model.data-00000-of-00001` | 5.2 MB | `69f0c2ae243da354a10526febce3f7017131450abcf5151e8053924bd1476883` |

Training additionally requires the pretrained PocketMiner checkpoint, which
initializes the frozen GVP-GNN encoder. It is not redistributed here; download it with

```bash
bash scripts/download_pocketminer_weights.sh
```

which writes `weights/pocketminer/pocketminer.{index,data-00000-of-00001}`.

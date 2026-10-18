"""Residue-level evaluation of PreDyPocket on the cleaned PM39 benchmark.

Predictions are the ``<case_id>_scores.csv`` files written by
``predypocket_predict.py``. Labels come from ``pm39_residue_labels.csv``
(1 = cryptic-pocket residue, 0 = negative, 2 = not evaluated). Only residues with
``is_eval_residue == yes`` are scored; metrics are pooled over all evaluated
residues of the selected cases. AUROC and AUPRC are computed from continuous
scores with ``tf.keras.metrics.AUC`` (the metric used during training); recall
and specificity use a residue-score threshold (default 0.6).
"""

from __future__ import print_function

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from config import parse_args_with_config


def tf_auc(y, s, curve):
    """AUROC or AUPRC with tf.keras.metrics.AUC, as used during training."""
    import tensorflow as tf
    metric = tf.keras.metrics.AUC(curve=curve)
    metric.update_state(y.astype("float32"), s.astype("float32"))
    return float(metric.result().numpy())


def read_labels(path, cases):
    labels = defaultdict(dict)
    with open(path, "r") as handle:
        for row in csv.DictReader(handle):
            if cases and row["case_id"] not in cases:
                continue
            if row["is_eval_residue"].strip().lower() != "yes":
                continue
            key = (row["chain"], row["residue_number"], row.get("insertion_code", "") or "")
            labels[row["case_id"]][key] = int(row["label"])
    return labels


def read_scores(path):
    scores = {}
    with open(path, "r") as handle:
        for row in csv.DictReader(handle):
            chain, resseq, icode, _ = row["residue_key"].split(":")
            scores[(chain, resseq, "" if icode == "-" else icode)] = float(row["score"])
    return scores


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Evaluate PreDyPocket residue scores on PM39.")
    parser.add_argument("--labels", required=True, help="pm39_residue_labels.csv")
    parser.add_argument("--cases", default=None, help="pm39_cases.csv; restricts evaluation to the listed cases.")
    parser.add_argument("--split", default="all", choices=["all", "val", "test"], help="Case subset to evaluate.")
    parser.add_argument("--predictions-dir", required=True, help="Directory containing <case_id>_scores.csv files.")
    parser.add_argument("--threshold", type=float, default=0.6, help="Residue-score threshold for recall and specificity.")
    parser.add_argument("--out-json", default=None, help="Optional path for the metrics JSON.")
    return parser


def main(argv=None):
    args = parse_args_with_config(build_arg_parser(), argv)
    cases = None
    if args.cases:
        with open(args.cases, "r") as handle:
            cases = {r["case_id"] for r in csv.DictReader(handle) if args.split in ("all", r["split"])}
    labels = read_labels(args.labels, cases)
    pred_dir = Path(args.predictions_dir)
    y_all, s_all, missing, unmatched = [], [], [], 0
    for case_id in sorted(labels):
        path = pred_dir / ("%s_scores.csv" % case_id)
        if not path.exists():
            missing.append(case_id)
            continue
        scores = read_scores(path)
        for key, label in labels[case_id].items():
            if key not in scores:
                unmatched += 1
                continue
            y_all.append(label)
            s_all.append(scores[key])
    if missing:
        raise SystemExit("Missing predictions for %d case(s): %s" % (len(missing), ", ".join(missing)))
    y = np.asarray(y_all, dtype=np.int32)
    s = np.asarray(s_all, dtype=np.float64)
    pred = s >= args.threshold
    tp = int(np.sum(pred & (y == 1)))
    tn = int(np.sum(~pred & (y == 0)))
    metrics = {
        "cases": len(labels),
        "evaluated_residues": int(len(y)),
        "positive_residues": int(y.sum()),
        "unmatched_label_residues": unmatched,
        "AUPRC": tf_auc(y, s, "PR"),
        "AUROC": tf_auc(y, s, "ROC"),
        "recall": tp / max(int(y.sum()), 1),
        "specificity": tn / max(int((y == 0).sum()), 1),
        "threshold": args.threshold,
    }
    print(json.dumps(metrics, indent=2))
    if args.out_json:
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out_json, "w") as handle:
            json.dump(metrics, handle, indent=2)


if __name__ == "__main__":
    main()

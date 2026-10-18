# Toy MD example

A tiny synthetic system for smoke-testing sampling, label preparation, training and
inference. It is not a benchmark and must not be used to evaluate model quality.

```text
examples/dynamic_data_example/
├── TOY/
│   └── TOY_TOY_1.LIG_B_101/
│       ├── aa_traj.pdb             # 12-frame multi-model PDB trajectory (8 Ala residues)
│       └── complex_reference.pdb   # reference complex; ligand LIG, chain B, residue 101
├── split/                          # toy partition files (TOY in train.txt)
└── make_toy_md.py                  # regenerates the two PDB files
```

The commands that use this example are listed in the **Quick start** section of the
top-level `README.md`. Because the toy protein has no homologs, labels are prepared
offline (`enable_rcsb: false` in `configs/toy/prepare.yaml`) and contain no positive
residues; the residues contacting `LIG` are masked (label −1).

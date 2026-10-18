"""YAML parameter files for the PreDyPocket command-line tools.

Every entry point accepts ``--config FILE.yaml``. Keys in the file use the
long option names with underscores (for example ``batch_size: 4``) and become
the defaults of the parser; options given on the command line override them.
"""

from __future__ import print_function

import argparse

import yaml


def parse_args_with_config(parser, argv=None):
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", default=None)
    known, _ = pre.parse_known_args(argv)
    parser.add_argument("--config", default=None, help="YAML parameter file; command-line options override it.")
    if known.config:
        with open(known.config, "r") as handle:
            values = yaml.safe_load(handle) or {}
        dests = {action.dest: action for action in parser._actions}
        unknown = sorted(key for key in values if key.replace("-", "_") not in dests)
        if unknown:
            parser.error("unknown key(s) in %s: %s" % (known.config, ", ".join(unknown)))
        defaults = {}
        for key, value in values.items():
            dest = key.replace("-", "_")
            defaults[dest] = value
            dests[dest].required = False
        parser.set_defaults(**defaults)
    return parser.parse_args(argv)

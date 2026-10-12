"""List, display or export catalog samples without executing hardware operations."""

import argparse
from pathlib import Path

from redfish_lab.use_cases import BY_ID, render_markdown, search_cases

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--search", default="")
parser.add_argument("--case", type=int, choices=range(1, 101), metavar="1..100")
parser.add_argument("--export-docs", type=Path)
parser.add_argument("--export-samples", type=Path)
args = parser.parse_args()
if args.export_docs:
    args.export_docs.parent.mkdir(parents=True, exist_ok=True)
    args.export_docs.write_text(render_markdown())
elif args.export_samples:
    args.export_samples.mkdir(parents=True, exist_ok=True)
    for case in search_cases(args.search):
        (args.export_samples / case.filename).write_text(case.code)
elif args.case:
    print(BY_ID[args.case].code)
else:
    for case in search_cases(args.search):
        print(f"{case.label} [{case.category}; {case.kind}]")

from __future__ import annotations

import argparse
import json

from radier_lab_v24 import LabConfig, run_full_pipeline_demo


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Executa o pipeline do Radier Lab.')
    parser.add_argument('--output-dir', default='output')
    parser.add_argument('--base-name', default='radier_lab_v24')
    parser.add_argument('--columns-csv', default=None)
    parser.add_argument('--measurements-csv', default=None)
    return parser

if __name__ == '__main__':
    args = _build_parser().parse_args()
    result = run_full_pipeline_demo(
        LabConfig(
            output_dir=args.output_dir,
            base_name=args.base_name,
            columns_csv=args.columns_csv,
            measurements_csv=args.measurements_csv,
        )
    )
    print(json.dumps(result, indent=2))

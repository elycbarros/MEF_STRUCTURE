from __future__ import annotations

import argparse
import json

from radier_regression_tests_v2 import run_tests


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Executa os testes de regressão do Radier Lab.')
    parser.add_argument('--output-dir', default='output')
    return parser


if __name__ == '__main__':
    args = _build_parser().parse_args()
    result = run_tests(args.output_dir)
    print(json.dumps(result, indent=2))

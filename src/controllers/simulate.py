from __future__ import annotations

import argparse
from typing import Dict, Optional

from src.models.transaction_db import generate_simulation_batch


def run_simulation(
    total_records: int = 100,
    chaos_ratio: float = 0.15,
    seed: Optional[int] = None,
) -> Dict[str, int]:
    """
    Controller entrypoint used by routes/CLI to trigger data simulation.

    SQL logic stays in src/models/transaction_db.py.
    """
    return generate_simulation_batch(
        total_records=total_records,
        chaos_ratio=chaos_ratio,
        seed=seed,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate happy and chaos transactions into MySQL tables."
    )
    parser.add_argument(
        "--total",
        type=int,
        default=100,
        help="How many transactions to generate (default: 100).",
    )
    parser.add_argument(
        "--chaos-ratio",
        type=float,
        default=0.15,
        help="Fraction of generated transactions that should be anomalous (default: 0.15).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible generated data.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    result = run_simulation(
        total_records=args.total,
        chaos_ratio=args.chaos_ratio,
        seed=args.seed,
    )
    print("Simulation complete:", result)


if __name__ == "__main__":
    main()

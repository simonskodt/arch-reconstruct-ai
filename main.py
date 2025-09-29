import sys
import argparse

from src import run

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ArchReconstructAI: run architectural reconstruction agent"
    )

    return parser.parse_args()

def main() -> None:
    exit_code: int = run.run_agent()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
"""
Main entry point for the ArchReconstructAI application.

This module sets up the command-line interface (CLI) for the ArchReconstructAI tool,
parsing arguments and invoking the appropriate functions to run the architectural
reconstruction agent.
"""
import sys
import argparse

from src import run

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the ArchReconstructAI application.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="ArchReconstructAI: run architectural reconstruction agent"
    )

    return parser.parse_args()

def main() -> None:
    """Main entry point for the ArchReconstructAI application.

    This function orchestrates the execution of the application by parsing
    command-line arguments and invoking the appropriate functions to run
    the architectural reconstruction agent.

    Exits:
        int: The exit code of the application (0 for success).
    """
    exit_code: int = run.run_agent()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

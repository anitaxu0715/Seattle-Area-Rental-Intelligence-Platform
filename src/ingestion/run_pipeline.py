"""Run the full ingestion pipeline: extract -> load -> audit."""

from src.ingestion.extract_public_datasets import load_dataset_config, run_extraction
from src.ingestion.load_to_postgres import run_load
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def main():
    logger.info("=== Seattle Rental Intelligence — Ingestion Pipeline ===")

    config = load_dataset_config()

    logger.info("--- Step 1: Extract from Socrata APIs ---")
    extraction_results = run_extraction()

    logger.info("--- Step 2: Load to PostgreSQL ---")
    run_load(extraction_results, config)

    logger.info("=== Pipeline complete ===")
    for key, result in extraction_results.items():
        logger.info(
            "  %s: %s (%d rows extracted)",
            key, result["status"], result["rows_extracted"]
        )


if __name__ == "__main__":
    main()

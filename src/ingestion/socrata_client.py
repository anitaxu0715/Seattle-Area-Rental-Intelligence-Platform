"""Reusable client for the Socrata Open Data API (SODA)."""

import time
from typing import Any

import requests

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF = 2


class SocrataClient:
    """Fetch records from any Socrata-powered open data portal."""

    def __init__(self, domain: str, app_token: str | None = None):
        self.domain = domain
        self.session = requests.Session()
        if app_token:
            self.session.headers["X-App-Token"] = app_token

    def _build_url(self, dataset_id: str) -> str:
        return f"https://{self.domain}/resource/{dataset_id}.json"

    def get_records(
        self,
        dataset_id: str,
        limit: int = 1000,
        offset: int = 0,
        select: str | None = None,
        where: str | None = None,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch a single page of records from a Socrata dataset."""
        url = self._build_url(dataset_id)
        params: dict[str, Any] = {"$limit": limit, "$offset": offset}
        if select:
            params["$select"] = select
        if where:
            params["$where"] = where
        if order:
            params["$order"] = order

        logger.info("GET %s  limit=%d offset=%d", url, limit, offset)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self.session.get(
                    url, params=params, timeout=DEFAULT_TIMEOUT
                )
                resp.raise_for_status()
                records = resp.json()
                logger.info("Received %d records (attempt %d)", len(records), attempt)
                return records

            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else None
                if status and status == 429 or (status and status >= 500):
                    wait = RETRY_BACKOFF ** attempt
                    logger.warning(
                        "HTTP %s on attempt %d — retrying in %ds",
                        status, attempt, wait,
                    )
                    time.sleep(wait)
                    continue
                logger.error("HTTP error %s (non-retryable): %s", status, exc)
                raise

            except requests.exceptions.ConnectionError as exc:
                wait = RETRY_BACKOFF ** attempt
                logger.warning(
                    "Connection error on attempt %d — retrying in %ds: %s",
                    attempt, wait, exc,
                )
                time.sleep(wait)
                continue

            except requests.exceptions.Timeout:
                wait = RETRY_BACKOFF ** attempt
                logger.warning(
                    "Timeout on attempt %d — retrying in %ds", attempt, wait
                )
                time.sleep(wait)
                continue

        logger.error("All %d attempts failed for %s", MAX_RETRIES, url)
        raise RuntimeError(
            f"Failed to fetch {url} after {MAX_RETRIES} attempts"
        )

    def get_all_records(
        self,
        dataset_id: str,
        max_records: int = 1000,
        page_size: int = 1000,
        select: str | None = None,
        where: str | None = None,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        """Paginate through a dataset up to max_records."""
        all_records: list[dict[str, Any]] = []
        offset = 0

        while len(all_records) < max_records:
            batch_limit = min(page_size, max_records - len(all_records))
            batch = self.get_records(
                dataset_id,
                limit=batch_limit,
                offset=offset,
                select=select,
                where=where,
                order=order,
            )

            if not batch:
                logger.info("Empty page at offset %d — pagination complete", offset)
                break

            all_records.extend(batch)
            offset += len(batch)

            if len(batch) < batch_limit:
                logger.info("Partial page (%d < %d) — pagination complete",
                            len(batch), batch_limit)
                break

        logger.info("Total records fetched: %d", len(all_records))
        return all_records

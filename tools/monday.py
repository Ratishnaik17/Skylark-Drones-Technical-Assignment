import os
import csv
import requests
from typing import Any, Dict, List, Optional

from config import settings
from services.logger import app_logger
from services.cache import cached, cache_service


class MondayClient:
    """Client for interacting with the Monday.com GraphQL API, with local CSV fallbacks."""

    def __init__(self):
        self.url = settings.MONDAY_API_URL
        self.headers = {
            "Authorization": settings.MONDAY_API_TOKEN or "",
            "Content-Type": "application/json",
        }
        self.use_mock_data = False  # Can be toggled at runtime

    # ----------------------------------------------------
    # GraphQL Executor
    # ----------------------------------------------------

    def execute(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a GraphQL query."""

        if not settings.MONDAY_API_TOKEN:
            raise ValueError("MONDAY_API_TOKEN is empty. Cannot execute API request.")

        payload = {
            "query": query,
            "variables": variables or {},
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=15,
            )

            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                raise RuntimeError(
                    f"Monday GraphQL Error: {data['errors']}"
                )

            return data["data"]

        except Exception as e:
            raise RuntimeError(
                f"Monday API request failed: {e}"
            ) from e

    # ----------------------------------------------------
    # Board Information
    # ----------------------------------------------------

    def get_board(self, board_id: int) -> Dict[str, Any]:
        query = """
        query ($boardId: [ID!]!) {
          boards(ids: $boardId) {
            id
            name
          }
        }
        """

        return self.execute(query, {"boardId": board_id})

    # ----------------------------------------------------
    # Helpers
    # ----------------------------------------------------

    @staticmethod
    def _normalize_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Monday item into a flat dictionary.
        """

        record = {
            "id": item["id"],
            "name": item["name"],
        }

        for column in item.get("column_values", []):
            title = column.get("column", {}).get("title")
            if title:
                record[title] = column.get("text")

        return record

    # ----------------------------------------------------
    # Items
    # ----------------------------------------------------

    def get_board_items(
        self,
        board_id: int,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:

        query = """
        query ($boardId: [ID!]!) {
          boards(ids: $boardId) {
            items_page(limit: LIMIT_PLACEHOLDER) {
              items {
                id
                name
                column_values {
                  id
                  text
                  value
                  column {
                    title
                  }
                }
              }
            }
          }
        }
        """

        query = query.replace(
            "LIMIT_PLACEHOLDER",
            str(limit),
        )

        data = self.execute(
            query,
            {"boardId": board_id},
        )

        items = data["boards"][0]["items_page"]["items"]

        return [
            self._normalize_item(item)
            for item in items
        ]

    # ----------------------------------------------------
    # CSV Fallback Loader
    # ----------------------------------------------------

    def _load_local_csv(self, filename: str) -> List[Dict[str, Any]]:
        """
        Loads and parses local CSV files, automatically skipping
        empty lines and finding the header row.
        """
        # Search path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "data", filename)
        
        if not os.path.exists(filepath):
            app_logger.warning(f"Local file {filepath} not found. Returning empty list.")
            return []

        records = []
        try:
            with open(filepath, encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                header = None
                for row in reader:
                    # Skip empty rows or rows that contain only empty spaces
                    if not row or all(cell.strip() == '' for cell in row):
                        continue
                    if header is None:
                        header = [h.strip() for h in row]
                    else:
                        record = {}
                        for idx, col_name in enumerate(header):
                            if idx < len(row):
                                record[col_name] = row[idx].strip()
                            else:
                                record[col_name] = ""
                        records.append(record)
            
            # Add an 'id' and 'name' field if missing
            for idx, r in enumerate(records):
                if 'id' not in r:
                    r['id'] = str(idx)
                if 'name' not in r:
                    # Heuristically set 'name' to the primary key/deal name
                    r['name'] = r.get('Deal Name', r.get('Deal name masked', f"Record {idx}"))
            
            app_logger.info(f"Successfully loaded {len(records)} records from local CSV: {filename}")
            return records
            
        except Exception as e:
            app_logger.error(f"Error reading local CSV {filename}: {e}")
            return []

    # ----------------------------------------------------
    # Convenience Methods with Cache and fallback
    # ----------------------------------------------------

    @cached("deals")
    def get_deals(self) -> List[Dict[str, Any]]:
        if self.use_mock_data or not settings.MONDAY_API_TOKEN:
            app_logger.info("Fetching DEALS from local CSV (Mock/Fallback mode)")
            return self._load_local_csv("deals.csv")

        try:
            app_logger.info("Fetching DEALS from Monday.com API")
            return self.get_board_items(settings.DEALS_BOARD_ID)
        except Exception as e:
            app_logger.warning(f"Monday.com API Deals fetch failed, falling back to CSV: {e}")
            return self._load_local_csv("deals.csv")

    @cached("work_orders")
    def get_work_orders(self) -> List[Dict[str, Any]]:
        if self.use_mock_data or not settings.MONDAY_API_TOKEN:
            app_logger.info("Fetching WORK ORDERS from local CSV (Mock/Fallback mode)")
            return self._load_local_csv("work_orders.csv")

        try:
            app_logger.info("Fetching WORK ORDERS from Monday.com API")
            return self.get_board_items(settings.WORK_ORDERS_BOARD_ID)
        except Exception as e:
            app_logger.warning(f"Monday.com API Work Orders fetch failed, falling back to CSV: {e}")
            return self._load_local_csv("work_orders.csv")

    # ----------------------------------------------------
    # Health Check
    # ----------------------------------------------------

    def health(self) -> Dict[str, Any]:
        if not settings.MONDAY_API_TOKEN:
            return {"status": "Offline / Mock Mode", "detail": "No API token provided"}
            
        query = """
        {
          me {
            id
            name
            email
          }
        }
        """
        try:
            return self.execute(query)
        except Exception as e:
            return {"status": "Disconnected", "error": str(e)}


monday_client = MondayClient()
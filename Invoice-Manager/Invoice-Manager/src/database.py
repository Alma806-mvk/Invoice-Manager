"""
JSON file-based database for clients and invoices.
"""

import json
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path


DATA_DIR = Path("data")
CLIENTS_FILE = DATA_DIR / "clients.json"
INVOICES_FILE = DATA_DIR / "invoices.json"

logger = logging.getLogger(__name__)


def ensure_data_dir():
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(exist_ok=True)


def _get_default_clients() -> dict:
    """Return default clients data structure."""
    return {"clients": [], "next_id": 1}


def _get_default_invoices() -> dict:
    """Return default invoices data structure."""
    return {"invoices": [], "next_id": 1}


def load_clients() -> dict:
    """Load clients from JSON file with error recovery."""
    ensure_data_dir()
    if not CLIENTS_FILE.exists():
        return _get_default_clients()
    try:
        with open(CLIENTS_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.warning("Invalid clients data structure, resetting to defaults")
                return _get_default_clients()
            if "clients" not in data or not isinstance(data.get("clients"), list):
                logger.warning("Missing or invalid clients list, resetting to defaults")
                return _get_default_clients()
            if "next_id" not in data or not isinstance(data.get("next_id"), int):
                logger.warning("Missing or invalid next_id, recalculating")
                max_id = max((c.get("id", 0) for c in data["clients"]), default=0)
                data["next_id"] = max_id + 1
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse clients.json: {e}. Resetting to defaults.")
        return _get_default_clients()
    except Exception as e:
        logger.error(f"Unexpected error loading clients: {e}. Resetting to defaults.")
        return _get_default_clients()


def save_clients(data: dict):
    """Save clients to JSON file."""
    ensure_data_dir()
    with open(CLIENTS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_invoices() -> dict:
    """Load invoices from JSON file with error recovery."""
    ensure_data_dir()
    if not INVOICES_FILE.exists():
        return _get_default_invoices()
    try:
        with open(INVOICES_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.warning("Invalid invoices data structure, resetting to defaults")
                return _get_default_invoices()
            if "invoices" not in data or not isinstance(data.get("invoices"), list):
                logger.warning("Missing or invalid invoices list, resetting to defaults")
                return _get_default_invoices()
            if "next_id" not in data or not isinstance(data.get("next_id"), int):
                logger.warning("Missing or invalid next_id, recalculating")
                max_id = max((inv.get("id", 0) for inv in data["invoices"]), default=0)
                data["next_id"] = max_id + 1
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse invoices.json: {e}. Resetting to defaults.")
        return _get_default_invoices()
    except Exception as e:
        logger.error(f"Unexpected error loading invoices: {e}. Resetting to defaults.")
        return _get_default_invoices()


def save_invoices(data: dict):
    """Save invoices to JSON file."""
    ensure_data_dir()
    with open(INVOICES_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get_client_by_id(client_id: int) -> Optional[dict]:
    """Get a client by ID."""
    data = load_clients()
    for client in data["clients"]:
        if client["id"] == client_id:
            return client
    return None


def get_invoice_by_id(invoice_id: int) -> Optional[dict]:
    """Get an invoice by ID."""
    data = load_invoices()
    for invoice in data["invoices"]:
        if invoice["id"] == invoice_id:
            return invoice
    return None

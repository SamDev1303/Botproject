#!/usr/bin/env python3
"""
Convex MCP Server - Real-time Database for Memory Management
For Clean Up Bros - Bella's persistent memory storage
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from mcp.logging_config import setup_logging

# Setup logging
logger = setup_logging(__name__)

# Load environment
def load_env():
    env_file = Path.home() / ".clawdbot" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))

load_env()

CONVEX_DEPLOY_KEY = os.environ.get('CONVEX_DEPLOY_KEY', '')
CONVEX_TEAM_ID = os.environ.get('CONVEX_TEAM_ID', '')
CONVEX_URL = os.environ.get('CONVEX_URL', '')  # Will be set after project creation

# Create MCP server
mcp = FastMCP("Convex")

@mcp.tool()
def convex_store_memory(entity_type: str, entity_id: str, data: dict) -> str:
    """
    Store entity data in Convex database

    Args:
        entity_type: Type of entity (e.g., 'client', 'invoice', 'task', 'session')
        entity_id: Unique identifier for the entity
        data: Dictionary of data to store

    Example:
        convex_store_memory('client', 'claudia-alz', {
            'name': 'Claudia Alz',
            'email': 'claudia@example.com',
            'status': 'overdue',
            'amount_owed': 320.00
        })
    """
    if not CONVEX_URL:
        logger.error("Convex URL not configured")
        return "Error: Convex URL not configured. Set CONVEX_URL in .env"

    payload = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "data": data,
        "updated_at": datetime.now().isoformat()
    }

    try:
        url = f"{CONVEX_URL}/api/store"
        headers = {
            "Authorization": f"Bearer {CONVEX_DEPLOY_KEY}",
            "Content-Type": "application/json"
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Stored {entity_type}/{entity_id} in Convex")
            return f"✓ Stored {entity_type}: {entity_id}"

    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:200]
        logger.error(f"Failed to store in Convex: {e.code} - {error_msg}")
        return f"Error: {e.code} - {error_msg}"
    except Exception as e:
        logger.error(f"Convex store error: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def convex_get_memory(entity_type: str, entity_id: str) -> str:
    """
    Retrieve entity data from Convex database

    Args:
        entity_type: Type of entity (e.g., 'client', 'invoice')
        entity_id: Unique identifier for the entity

    Example:
        convex_get_memory('client', 'claudia-alz')
    """
    if not CONVEX_URL:
        logger.error("Convex URL not configured")
        return "Error: Convex URL not configured"

    try:
        url = f"{CONVEX_URL}/api/get?entity_type={entity_type}&entity_id={entity_id}"
        headers = {
            "Authorization": f"Bearer {CONVEX_DEPLOY_KEY}"
        }

        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Retrieved {entity_type}/{entity_id} from Convex")
            return json.dumps(result, indent=2)

    except urllib.error.HTTPError as e:
        if e.code == 404:
            logger.info(f"{entity_type}/{entity_id} not found in Convex")
            return f"Not found: {entity_type}/{entity_id}"
        error_msg = e.read().decode()[:200]
        logger.error(f"Failed to get from Convex: {e.code} - {error_msg}")
        return f"Error: {e.code} - {error_msg}"
    except Exception as e:
        logger.error(f"Convex get error: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def convex_search_memories(entity_type: str, filters: dict = None, limit: int = 50) -> str:
    """
    Search for entities in Convex database

    Args:
        entity_type: Type of entity to search for
        filters: Dictionary of filters to apply (e.g., {'status': 'overdue'})
        limit: Maximum number of results to return

    Example:
        convex_search_memories('client', {'status': 'overdue'}, limit=10)
    """
    if not CONVEX_URL:
        logger.error("Convex URL not configured")
        return "Error: Convex URL not configured"

    try:
        query_params = f"entity_type={entity_type}&limit={limit}"
        if filters:
            query_params += f"&filters={json.dumps(filters)}"

        url = f"{CONVEX_URL}/api/search?{query_params}"
        headers = {
            "Authorization": f"Bearer {CONVEX_DEPLOY_KEY}"
        }

        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Searched {entity_type} in Convex, found {len(result.get('results', []))} results")
            return json.dumps(result, indent=2)

    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:200]
        logger.error(f"Failed to search Convex: {e.code} - {error_msg}")
        return f"Error: {e.code} - {error_msg}"
    except Exception as e:
        logger.error(f"Convex search error: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def convex_delete_memory(entity_type: str, entity_id: str) -> str:
    """
    Delete entity data from Convex database

    Args:
        entity_type: Type of entity
        entity_id: Unique identifier for the entity

    Example:
        convex_delete_memory('session', '2026-01-31')
    """
    if not CONVEX_URL:
        logger.error("Convex URL not configured")
        return "Error: Convex URL not configured"

    try:
        url = f"{CONVEX_URL}/api/delete"
        headers = {
            "Authorization": f"Bearer {CONVEX_DEPLOY_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "entity_type": entity_type,
            "entity_id": entity_id
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="DELETE"
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Deleted {entity_type}/{entity_id} from Convex")
            return f"✓ Deleted {entity_type}: {entity_id}"

    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:200]
        logger.error(f"Failed to delete from Convex: {e.code} - {error_msg}")
        return f"Error: {e.code} - {error_msg}"
    except Exception as e:
        logger.error(f"Convex delete error: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def convex_sync_client(client_id: str, client_data: dict) -> str:
    """
    Sync client entity to Convex database

    Args:
        client_id: Client identifier (e.g., 'claudia-alz')
        client_data: Client data dictionary

    Example:
        convex_sync_client('claudia-alz', {
            'name': 'Claudia Alz',
            'amount_owed': 320.00,
            'days_overdue': 45,
            'status': 'overdue'
        })
    """
    return convex_store_memory('client', client_id, client_data)


@mcp.tool()
def convex_sync_invoice(invoice_id: str, invoice_data: dict) -> str:
    """
    Sync invoice entity to Convex database

    Args:
        invoice_id: Invoice identifier
        invoice_data: Invoice data dictionary
    """
    return convex_store_memory('invoice', invoice_id, invoice_data)


@mcp.tool()
def convex_sync_session(date: str, session_data: dict) -> str:
    """
    Sync session summary to Convex database

    Args:
        date: Session date (YYYY-MM-DD)
        session_data: Session summary data
    """
    return convex_store_memory('session', date, session_data)


@mcp.tool()
def convex_get_all_overdue_clients() -> str:
    """
    Get all clients with overdue payments from Convex
    """
    return convex_search_memories('client', {'status': 'overdue'}, limit=100)


if __name__ == "__main__":
    mcp.run()

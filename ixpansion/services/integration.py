"""Integration module connecting cash flow, YouTube ads, and API key management.

This module ties together:
1. Cash flow tracking (fiat, crypto, NFTs)
2. YouTube channel ops and ads
3. Enhanced API key management
4. Dashboard data generation
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .cashflow import (
    CashFlowTracker,
    CashFlowError,
    log_expenditure,
    log_revenue,
    init_cashflow_tracker,
)
from .youtube import (
    YouTubeError,
    YouTubeChannel,
    YouTubeChannelManager,
    AdCampaign,
    ChannelMetrics,
    create_channel,
    get_channel_summary,
)

# API key management
API_KEYS_FILE = "ixpansion/content_output/api_keys.json"


class APIKeyManager:
    """Manages API keys and credentials securely."""

    # First-class key types used across the hub (XAI is a primary provider).
    KEY_TYPES: tuple[str, ...] = (
        "xai",       # Grok
        "openai",
        "google",    # YouTube / Google Ads
        "youtube",
        "anthropic",
        "openrouter",
        "custom",
    )

    def __init__(self, base_dir: str = "ixpansion/content_output") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.keys_file = self.base_dir / "api_keys.json"
        self._keys: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load API keys from disk."""
        if self.keys_file.is_file():
            try:
                with open(self.keys_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._keys = data
            except (json.JSONDecodeError, KeyError, ValueError):
                self._keys = {}

    def _save(self) -> None:
        """Save API keys to disk."""
        with open(self.keys_file, "w", encoding="utf-8") as f:
            json.dump(self._keys, f, indent=2, default=str)

    def add_key(self, name: str, key_type: str, key_value: str, 
                description: str = "", expires_at: Optional[str] = None) -> Dict[str, Any]:
        """Add a new API key."""
        if key_type not in self.KEY_TYPES:
            raise ValueError(
                f"Unknown key_type '{key_type}'. Expected one of {self.KEY_TYPES}"
            )
        key_id = f"{key_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        key_entry = {
            "id": key_id,
            "key_type": key_type,
            "key_value": key_value,  # In production, encrypt this!
            "description": description,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "last_used": None,
            "usage_count": 0,
        }
        self._keys[key_id] = key_entry
        self._save()
        return key_entry

    def add_xai_key(self, key_value: str, name: str = "Grok (XAI)",
                    description: str = "", expires_at: Optional[str] = None) -> Dict[str, Any]:
        """Add an XAI / Grok API key (first-class provider)."""
        return self.add_key(
            name=name,
            key_type="xai",
            key_value=key_value,
            description=description or "XAI Grok API key for agent + IXPANSION runs",
            expires_at=expires_at,
        )

    def count_by_type(self) -> Dict[str, int]:
        """Return counts of managed keys grouped by type."""
        counts: Dict[str, int] = {}
        for entry in self._keys.values():
            t = entry.get("key_type", "custom")
            counts[t] = counts.get(t, 0) + 1
        return counts

    def get_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get an API key by ID (returns masked version)."""
        key_entry = self._keys.get(key_id)
        if key_entry is None:
            return None
        # Return masked version - never expose full key
        return {
            "id": key_entry["id"],
            "key_type": key_entry["key_type"],
            "description": key_entry["description"],
            "created_at": key_entry["created_at"],
            "expires_at": key_entry["expires_at"],
            "last_used": key_entry["last_used"],
            "usage_count": key_entry["usage_count"],
            "key_value_masked": "***MASKED***",
        }

    def update_key_usage(self, key_id: str, used: bool = True) -> Optional[Dict[str, Any]]:
        """Update key usage tracking."""
        key_entry = self._keys.get(key_id)
        if key_entry is None:
            return None
        key_entry["last_used"] = datetime.now().isoformat()
        key_entry["usage_count"] = key_entry.get("usage_count", 0) + 1
        if used:
            key_entry["status"] = "used"
        self._save()
        return key_entry

    def list_keys(self, key_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List API keys, optionally filtered by type."""
        keys = list(self._keys.values())
        if key_type:
            keys = [k for k in keys if k["key_type"] == key_type]
        return keys

    def remove_key(self, key_id: str) -> bool:
        """Remove an API key."""
        if key_id in self._keys:
            del self._keys[key_id]
            self._save()
            return True
        return False


# Integration functions

def init_integration(
    cashflow_base: str = "ixpansion/content_output/cashflow",
    youtube_base: str = "ixpansion/content_output/youtube",
    api_keys_base: str = "ixpansion/content_output",
) -> Dict[str, Any]:
    """Initialize all integration components."""
    return {
        "cashflow": init_cashflow_tracker(cashflow_base),
        "youtube": YouTubeChannelManager(youtube_base),
        "api_keys": APIKeyManager(api_keys_base),
    }


def record_ad_revenue(
    tracker: CashFlowTracker,
    campaign_id: str,
    amount: Decimal,
    description: str = "",
) -> Transaction:
    """Record ad revenue from a YouTube campaign."""
    return tracker.log_transaction(
        tx_type="revenue",
        category="ads",
        amount=amount,
        description=f"Ad revenue - {campaign_id}: {description}",
        asset="usdt",  # Typically stablecoin for ad revenue
    )


def record_ad_expenditure(
    tracker: CashFlowTracker,
    amount: Decimal,
    description: str = "",
    asset: str = "usdt",
) -> Transaction:
    """Record ad expenditure."""
    return tracker.log_transaction(
        tx_type="expenditure",
        category="ads",
        amount=amount,
        description=description or "YouTube ad spend",
        asset=asset,
    )


def get_integration_summary(
    integration: Dict[str, Any],
) -> Dict[str, Any]:
    """Get comprehensive integration summary."""
    cashflow = integration["cashflow"]
    youtube = integration["youtube"]
    api_keys = integration["api_keys"]

    cf_summary = cashflow.get_summary()
    yt_summary = youtube.get_all_campaigns()

    # Calculate ad-related cash flow
    ad_revenue = Decimal("0")
    ad_expenditure = Decimal("0")
    for tx in cashflow.get_transactions(category="ads"):
        if tx.type == "revenue":
            ad_revenue += tx.amount
        elif tx.type == "expenditure":
            ad_expenditure += tx.amount

    api_key_count = len(api_keys.list_keys())

    return {
        "cash_flow": cf_summary,
        "youtube_channels": len(youtube._channels),
        "active_campaigns": len(yt_summary),
        "ad_revenue": str(ad_revenue),
        "ad_expenditure": str(ad_expenditure),
        "net_ad_profit": str(ad_revenue - ad_expenditure),
        "api_keys_managed": api_key_count,
        "total_channels": len(youtube._channels),
    }

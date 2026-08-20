"""Cash flow tracking module supporting fiat, crypto, and NFTs.

This module provides:
- Multi-asset cash flow tracking (fiat, crypto, NFTs)
- Revenue/expenditure logging
- Portfolio valuation
- Cash flow reporting
- Integration with existing ixpansion ecosystem
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class CashFlowError(Exception):
    """Raised when cash flow operations fail."""
    pass


@dataclass
class Transaction:
    """Represents a single cash flow transaction."""
    id: str
    timestamp: datetime
    type: str  # "revenue" or "expenditure"
    category: str  # "fiat", "crypto", "nft", "service", "product"
    amount: Decimal  # positive value
    description: str
    asset: str  # e.g., "USDT", "BTC", "ETH", "NFT-001"
    tx_hash: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Portfolio:
    """Represents a user's asset portfolio."""
    assets: Dict[str, Decimal]  # asset_name -> amount
    nfts: Dict[str, Dict]  # nft_id -> {name, rarity, value}
    last_updated: datetime

    def total_value(self, price_lookup: Dict[str, Decimal]) -> Decimal:
        """Calculate total portfolio value in base currency."""
        total = Decimal("0")
        for asset, amount in self.assets.items():
            if asset in price_lookup:
                total += amount * price_lookup[asset]
        for nft_id, nft in self.nfts.items():
            total += nft.get("value", Decimal("0"))
        return total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assets": {k: str(v) for k, v in self.assets.items()},
            "nfts": self.nfts,
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portfolio":
        assets = {k: Decimal(v) for k, v in data.get("assets", {}).items()}
        nfts = data.get("nfts", {})
        last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        return cls(assets=assets, nfts=nfts, last_updated=last_updated)


class CashFlowTracker:
    """Main cash flow tracker supporting fiat, crypto, and NFTs."""

    def __init__(self, base_dir: str = "ixpansion/content_output/cashflow") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.transactions_file = self.base_dir / "transactions.json"
        self.portfolio_file = self.base_dir / "portfolio.json"
        self.price_lookup_file = self.base_dir / "price_lookup.json"
        self._transactions: List[Transaction] = []
        self._portfolio: Optional[Portfolio] = None
        self._load()

    def _load(self) -> None:
        """Load existing data from disk."""
        if self.transactions_file.is_file():
            try:
                with open(self.transactions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._transactions = [
                    Transaction(
                        id=t["id"],
                        timestamp=datetime.fromisoformat(t["timestamp"]),
                        type=t["type"],
                        category=t["category"],
                        amount=Decimal(t["amount"]),
                        description=t["description"],
                        asset=t["asset"],
                        tx_hash=t.get("tx_hash"),
                        metadata=t.get("metadata", {}),
                    )
                    for t in data
                ]
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                raise CashFlowError(f"Failed to load transactions: {e}")

        if self.portfolio_file.is_file():
            try:
                with open(self.portfolio_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._portfolio = Portfolio.from_dict(data)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                raise CashFlowError(f"Failed to load portfolio: {e}")

        if self.price_lookup_file.is_file():
            try:
                with open(self.price_lookup_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Convert string Decimal values back
                self._price_lookup = {
                    k: Decimal(v) for k, v in data.items()
                }
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                raise CashFlowError(f"Failed to load price lookup: {e}")
        else:
            self._price_lookup = {}

    def _save(self) -> None:
        """Save all data to disk."""
        # Save transactions
        with open(self.transactions_file, "w", encoding="utf-8") as f:
            json.dump(
                [t.to_dict() for t in self._transactions],
                f,
                indent=2,
                default=str,
            )

        # Save portfolio
        if self._portfolio:
            with open(self.portfolio_file, "w", encoding="utf-8") as f:
                json.dump(
                    self._portfolio.to_dict(),
                    f,
                    indent=2,
                    default=str,
                )

        # Save price lookup
        with open(self.price_lookup_file, "w", encoding="utf-8") as f:
            json.dump(
                {k: str(v) for k, v in self._price_lookup.items()},
                f,
                indent=2,
                default=str,
            )

    # Transaction methods

    def log_transaction(
        self,
        tx_type: str,
        category: str,
        amount: Decimal,
        description: str,
        asset: str = "fiat",
        tx_hash: Optional[str] = None,
    ) -> Transaction:
        """Log a new cash flow transaction."""
        if tx_type not in ("revenue", "expenditure"):
            raise CashFlowError(f"Invalid transaction type: {tx_type}")

        tx_id = f"{tx_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(self._transactions)}"
        tx = Transaction(
            id=tx_id,
            timestamp=datetime.now(),
            type=tx_type,
            category=category,
            amount=amount,
            description=description,
            asset=asset,
            tx_hash=tx_hash,
        )
        self._transactions.append(tx)
        self._save()
        return tx

    # Portfolio methods

    def update_portfolio(
        self,
        asset: str,
        amount: Decimal,
        nft_data: Optional[Dict[str, Any]] = None,
    ) -> Portfolio:
        """Update portfolio with new assets or NFTs."""
        if self._portfolio is None:
            self._portfolio = Portfolio(
                assets={},
                nfts={},
                last_updated=datetime.now(),
            )

        if asset in self._portfolio.assets:
            self._portfolio.assets[asset] += amount
        else:
            self._portfolio.assets[asset] = amount

        if nft_data:
            nft_id = nft_data.get("id", f"nft-{len(self._portfolio.nfts)}")
            self._portfolio.nfts[nft_id] = {
                "name": nft_data.get("name", "Unknown NFT"),
                "rarity": nft_data.get("rarity", "common"),
                "value": nft_data.get("value", Decimal("0")),
                "added": datetime.now().isoformat(),
            }

        self._portfolio.last_updated = datetime.now()
        self._save()
        return self._portfolio

    def get_portfolio(self) -> Portfolio:
        """Get current portfolio."""
        if self._portfolio is None:
            self._portfolio = Portfolio(
                assets={},
                nfts={},
                last_updated=datetime.now(),
            )
        return self._portfolio

    # Price lookup methods

    def update_price(self, asset: str, price: Decimal) -> None:
        """Update price for a given asset."""
        self._price_lookup[asset] = price
        self._save()

    def get_price(self, asset: str) -> Optional[Decimal]:
        """Get current price for an asset."""
        return self._price_lookup.get(asset)

    # Reporting methods

    def get_summary(self) -> Dict[str, Any]:
        """Get cash flow summary."""
        revenue = Decimal("0")
        expenditure = Decimal("0")

        for tx in self._transactions:
            if tx.type == "revenue":
                revenue += tx.amount
            elif tx.type == "expenditure":
                expenditure += tx.amount

        net = revenue - expenditure

        # Group by category
        by_category: Dict[str, Decimal] = {}
        for tx in self._transactions:
            cat = tx.category
            by_category[cat] = by_category.get(cat, Decimal("0")) + tx.amount

        # Group by asset
        by_asset: Dict[str, Decimal] = {}
        for tx in self._transactions:
            ast = tx.asset
            by_asset[ast] = by_asset.get(ast, Decimal("0")) + tx.amount

        return {
            "revenue": str(revenue),
            "expenditure": str(expenditure),
            "net": str(net),
            "transaction_count": len(self._transactions),
            "by_category": {k: str(v) for k, v in by_category.items()},
            "by_asset": {k: str(v) for k, v in by_asset.items()},
            "portfolio_value": str(self.get_portfolio().total_value(self._price_lookup)),
        }

    def get_transactions(
        self,
        tx_type: Optional[str] = None,
        category: Optional[str] = None,
        asset: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transaction]:
        """Get filtered transactions."""
        filtered = self._transactions

        if tx_type:
            filtered = [t for t in filtered if t.type == tx_type]

        if category:
            filtered = [t for t in filtered if t.category == category]

        if asset:
            filtered = [t for t in filtered if t.asset == asset]

        if start_date:
            filtered = [t for t in filtered if t.timestamp >= start_date]

        if end_date:
            filtered = [t for t in filtered if t.timestamp <= end_date]

        return filtered


# Convenience functions for common operations

def init_cashflow_tracker(base_dir: str = "ixpansion/content_output/cashflow") -> CashFlowTracker:
    """Initialize the cash flow tracker."""
    return CashFlowTracker(base_dir)


def log_revenue(
    tracker: CashFlowTracker,
    amount: Decimal,
    description: str,
    asset: str = "fiat",
    tx_hash: Optional[str] = None,
) -> Transaction:
    """Log revenue transaction."""
    return tracker.log_transaction(
        tx_type="revenue",
        category=asset,
        amount=amount,
        description=description,
        asset=asset,
        tx_hash=tx_hash,
    )


def log_expenditure(
    tracker: CashFlowTracker,
    amount: Decimal,
    description: str,
    asset: str = "fiat",
    tx_hash: Optional[str] = None,
) -> Transaction:
    """Log expenditure transaction."""
    return tracker.log_transaction(
        tx_type="expenditure",
        category=asset,
        amount=amount,
        description=description,
        asset=asset,
        tx_hash=tx_hash,
    )

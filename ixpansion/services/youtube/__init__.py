"""YouTube channel ops and ads command center integration.

Provides capabilities for:
- YouTube channel management
- Ads campaign creation and monitoring
- Analytics reporting
- Content scheduling
- Audience insights
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


class YouTubeError(Exception):
    """Raised when YouTube operations fail."""
    pass


@dataclass
class AdCampaign:
    """Represents a YouTube ad campaign."""
    id: str
    name: str
    status: str  # "pending", "active", "paused", "ended"
    budget: Decimal
    spend: Decimal
    impressions: int
    clicks: int
    ctr: float  # click-through rate
    cpc: Decimal  # cost per click
    start_date: datetime
    end_date: Optional[datetime]
    target_audience: Dict[str, Any]
    ad_format: str  # "skippable", "non-skippable", "bumper", "overlay"
    created_at: datetime


@dataclass
class ChannelMetrics:
    """YouTube channel metrics."""
    subscribers: int
    views: int
    watch_time: Decimal  # in hours
    videos_published: int
    average_view_duration: Decimal
    engagement_rate: float
    top_performing_videos: List[Dict[str, Any]]
    recent_growth_rate: float  # percentage per period


@dataclass
class YouTubeChannel:
    """Represents a YouTube channel."""
    id: str
    name: str
    handle: str
    description: str
    created_at: datetime
    status: str  # "active", "paused", "terminated"
    custom_url: Optional[str]
    verified: bool
    metrics: ChannelMetrics
    ad_campaigns: List[AdCampaign]


class YouTubeChannelManager:
    """Manager for YouTube channel operations and ads."""

    def __init__(self, base_dir: str = "ixpansion/content_output/youtube") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.channels_file = self.base_dir / "channels.json"
        self.campaigns_file = self.base_dir / "campaigns.json"
        self._channels: Dict[str, YouTubeChannel] = {}
        self._campaigns: Dict[str, AdCampaign] = {}
        self._load()

    def _load(self) -> None:
        """Load existing data from disk."""
        if self.channels_file.is_file():
            try:
                with open(self.channels_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for ch_data in data:
                    # Reconstruct ChannelMetrics
                    metrics_data = ch_data.pop("metrics", {})
                    metrics = ChannelMetrics(
                        subscribers=metrics_data.get("subscribers", 0),
                        views=metrics_data.get("views", 0),
                        watch_time=Decimal(str(metrics_data.get("watch_time", 0))),
                        videos_published=metrics_data.get("videos_published", 0),
                        average_view_duration=Decimal(str(metrics_data.get("average_view_duration", 0))),
                        engagement_rate=metrics_data.get("engagement_rate", 0.0),
                        top_performing_videos=metrics_data.get("top_performing_videos", []),
                        recent_growth_rate=metrics_data.get("recent_growth_rate", 0.0),
                    )
                    ch = YouTubeChannel(
                        id=ch_data["id"],
                        name=ch_data["name"],
                        handle=ch_data["handle"],
                        description=ch_data["description"],
                        created_at=datetime.fromisoformat(ch_data["created_at"]),
                        status=ch_data["status"],
                        custom_url=ch_data.get("custom_url"),
                        verified=ch_data.get("verified", False),
                        metrics=metrics,
                        ad_campaigns=[],  # Will be populated separately
                    )
                    self._channels[ch.id] = ch
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                raise YouTubeError(f"Failed to load channels: {e}")

        if self.campaigns_file.is_file():
            try:
                with open(self.campaigns_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for camp_data in data:
                    camp = AdCampaign(
                        id=camp_data["id"],
                        name=camp_data["name"],
                        status=camp_data["status"],
                        budget=Decimal(str(camp_data["budget"])),
                        spend=Decimal(str(camp_data["spend"])),
                        impressions=camp_data.get("impressions", 0),
                        clicks=camp_data.get("clicks", 0),
                        ctr=float(camp_data.get("ctr", 0)),
                        cpc=Decimal(str(camp_data.get("cpc", "0"))),
                        start_date=datetime.fromisoformat(camp_data["start_date"]),
                        end_date=datetime.fromisoformat(camp_data["end_date"]) if camp_data.get("end_date") else None,
                        target_audience=camp_data.get("target_audience", {}),
                        ad_format=camp_data.get("ad_format", "skippable"),
                        created_at=datetime.fromisoformat(camp_data["created_at"]) if camp_data.get("created_at") else datetime.now(),
                    )
                    self._campaigns[camp.id] = camp
                    # Add campaign to channel
                    if camp.id in self._channels:
                        self._channels[camp.id].ad_campaigns.append(camp)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                raise YouTubeError(f"Failed to load campaigns: {e}")

    def _save(self) -> None:
        """Save all data to disk."""
        # Save channels
        channels_data = []
        for ch in self._channels.values():
            metrics_dict = {
                "subscribers": ch.metrics.subscribers,
                "views": ch.metrics.views,
                "watch_time": float(ch.metrics.watch_time),
                "videos_published": ch.metrics.videos_published,
                "average_view_duration": float(ch.metrics.average_view_duration),
                "engagement_rate": ch.metrics.engagement_rate,
                "top_performing_videos": ch.metrics.top_performing_videos,
                "recent_growth_rate": ch.metrics.recent_growth_rate,
            }
            ch_dict = {
                "id": ch.id,
                "name": ch.name,
                "handle": ch.handle,
                "description": ch.description,
                "created_at": ch.created_at.isoformat(),
                "status": ch.status,
                "custom_url": ch.custom_url,
                "verified": ch.verified,
                "metrics": metrics_dict,
                "ad_campaigns": [c.to_dict() if hasattr(c, 'to_dict') else {
                    "id": c.id, "name": c.name, "status": c.status,
                    "budget": str(c.budget), "spend": str(c.spend),
                    "impressions": c.impressions, "clicks": c.clicks,
                    "ctr": c.ctr, "cpc": str(c.cpc),
                    "start_date": c.start_date.isoformat(),
                    "end_date": c.end_date.isoformat() if c.end_date else None,
                    "target_audience": c.target_audience,
                    "ad_format": c.ad_format,
                    "created_at": c.created_at.isoformat(),
                } for c in ch.ad_campaigns],
            }
            channels_data.append(ch_dict)

        with open(self.channels_file, "w", encoding="utf-8") as f:
            json.dump(channels_data, f, indent=2, default=str)

        # Save campaigns
        campaigns_data = [camp.to_dict() if hasattr(camp, 'to_dict') else {
            "id": camp.id,
            "name": camp.name,
            "status": camp.status,
            "budget": str(camp.budget),
            "spend": str(camp.spend),
            "impressions": camp.impressions,
            "clicks": camp.clicks,
            "ctr": camp.ctr,
            "cpc": str(camp.cpc),
            "start_date": camp.start_date.isoformat(),
            "end_date": camp.end_date.isoformat() if camp.end_date else None,
            "target_audience": camp.target_audience,
            "ad_format": camp.ad_format,
            "created_at": camp.created_at.isoformat(),
        } for camp in self._campaigns.values()]

        with open(self.campaigns_file, "w", encoding="utf-8") as f:
            json.dump(campaigns_data, f, indent=2, default=str)

    # Channel methods

    def create_channel(
        self,
        name: str,
        handle: str,
        description: str,
        custom_url: Optional[str] = None,
    ) -> YouTubeChannel:
        """Create a new YouTube channel."""
        channel_id = f"channel-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        metrics = ChannelMetrics(
            subscribers=0,
            views=0,
            watch_time=Decimal("0"),
            videos_published=0,
            average_view_duration=Decimal("0"),
            engagement_rate=0.0,
            top_performing_videos=[],
            recent_growth_rate=0.0,
        )
        channel = YouTubeChannel(
            id=channel_id,
            name=name,
            handle=handle,
            description=description,
            created_at=datetime.now(),
            status="active",
            custom_url=custom_url,
            verified=False,
            metrics=metrics,
            ad_campaigns=[],
        )
        self._channels[channel_id] = channel
        self._save()
        return channel

    def get_channel(self, channel_id: str) -> Optional[YouTubeChannel]:
        """Get a channel by ID."""
        return self._channels.get(channel_id)

    def update_channel_metrics(
        self,
        channel_id: str,
        **kwargs: Any,
    ) -> Optional[YouTubeChannel]:
        """Update channel metrics."""
        channel = self.get_channel(channel_id)
        if channel is None:
            return None
        for key, value in kwargs.items():
            if hasattr(channel.metrics, key):
                setattr(channel.metrics, key, value)
        self._save()
        return channel

    # Ad campaign methods

    def create_ad_campaign(
        self,
        channel_id: str,
        name: str,
        budget: Decimal,
        start_date: datetime,
        end_date: datetime,
        target_audience: Dict[str, Any],
        ad_format: str = "skippable",
    ) -> Optional[AdCampaign]:
        """Create a new ad campaign for a channel."""
        channel = self.get_channel(channel_id)
        if channel is None:
            return None

        campaign_id = f"camp-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        campaign = AdCampaign(
            id=campaign_id,
            name=name,
            status="pending",
            budget=budget,
            spend=Decimal("0"),
            impressions=0,
            clicks=0,
            ctr=0.0,
            cpc=Decimal("0"),
            start_date=start_date,
            end_date=end_date,
            target_audience=target_audience,
            ad_format=ad_format,
            created_at=datetime.now(),
        )

        self._campaigns[campaign.id] = campaign
        channel.ad_campaigns.append(campaign)
        self._save()
        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[AdCampaign]:
        """Get a campaign by ID."""
        return self._campaigns.get(campaign_id)

    def update_campaign_status(
        self,
        campaign_id: str,
        status: str,
    ) -> Optional[AdCampaign]:
        """Update campaign status."""
        campaign = self.get_campaign(campaign_id)
        if campaign is None:
            return None
        campaign.status = status
        self._save()
        return campaign

    def update_campaign_metrics(
        self,
        campaign_id: str,
        impressions: Optional[int] = None,
        clicks: Optional[int] = None,
        spend: Optional[Decimal] = None,
    ) -> Optional[AdCampaign]:
        """Update campaign performance metrics."""
        campaign = self.get_campaign(campaign_id)
        if campaign is None:
            return None

        if impressions is not None:
            campaign.impressions = impressions
        if clicks is not None:
            campaign.clicks = clicks
        if spend is not None:
            campaign.spend = spend

        # Calculate derived metrics
        if campaign.impressions > 0:
            campaign.ctr = round(campaign.clicks / campaign.impressions, 4)
        if campaign.clicks > 0 and campaign.spend > Decimal("0"):
            campaign.cpc = campaign.spend / campaign.clicks

        self._save()
        return campaign

    # Reporting methods

    def get_channel_summary(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get summary for a channel."""
        channel = self.get_channel(channel_id)
        if channel is None:
            return None

        total_spend = sum(c.spend for c in channel.ad_campaigns)
        total_impressions = sum(c.impressions for c in channel.ad_campaigns)
        total_clicks = sum(c.clicks for c in channel.ad_campaigns)
        overall_ctr = round(total_clicks / total_impressions, 4) if total_impressions > 0 else 0.0

        return {
            "channel_name": channel.name,
            "subscribers": channel.metrics.subscribers,
            "views": channel.metrics.views,
            "watch_time_hours": float(channel.metrics.watch_time),
            "videos_published": channel.metrics.videos_published,
            "engagement_rate": channel.metrics.engagement_rate,
            "campaigns": len(channel.ad_campaigns),
            "total_ad_spend": str(total_spend),
            "overall_ctr": overall_ctr,
            "status": channel.status,
        }

    def get_all_campaigns(self) -> List[AdCampaign]:
        """Get all campaigns across all channels."""
        all_campaigns = []
        for channel in self._channels.values():
            all_campaigns.extend(channel.ad_campaigns)
        return all_campaigns

    def get_recent_campaigns(
        self,
        days: int = 30,
    ) -> List[AdCampaign]:
        """Get campaigns created or updated in the last N days."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        for channel in self._channels.values():
            for campaign in channel.ad_campaigns:
                if campaign.created_at >= cutoff:
                    recent.append(campaign)
        return recent

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "budget": str(self.budget),
            "spend": str(self.spend),
            "impressions": self.impressions,
            "clicks": self.clicks,
            "ctr": self.ctr,
            "cpc": str(self.cpc),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "target_audience": self.target_audience,
            "ad_format": self.ad_format,
            "created_at": self.created_at.isoformat(),
        }


# Module-level exports for backward compatibility
create_channel_instance = YouTubeChannelManager

# Export the manager class so integration can instantiate it
YouTubeChannelManager = YouTubeChannelManager
create_channel = YouTubeChannelManager.create_channel
get_channel_summary = lambda self, ch_id: self.get_channel_summary(ch_id) if hasattr(self, 'get_channel_summary') else None
get_all_campaigns = lambda self: self.get_all_campaigns() if hasattr(self, 'get_all_campaigns') else []

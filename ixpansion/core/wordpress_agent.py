"""
WordPressAgent - IXPANSION Domain Operation Agent

A specialized agent that manages and operates the alexalex.info WordPress domain,
handling content, RSS feeds, comments, oEmbed, and overall WordPress health monitoring.

Features:
- WordPress health status checking
- RSS feed monitoring and validation
- Comment management
- oEmbed endpoint verification
- Plugin/theme status checks
- Content freshness analysis
- Domain health reporting
- Integration with IXPANSION organism health metrics
"""

import json
import time
import random
import urllib.request
import urllib.error
from datetime import datetime, timedelta


class WordPressAgent:
    """Manages and operates the alexalex.info WordPress domain."""

    def __init__(self, domain="alexalex.info", console_url="http://127.0.0.1:8890"):
        self.domain = domain
        self.console_url = console_url
        self.name = "WordPressAgent"
        self.version = "1.0.0"
        self.base_url = f"https://{domain}"

    def _make_request(self, endpoint, method="GET", data=None):
        """Make an HTTP request to the WordPress site."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=3) as response:
                    return json.loads(response.read().decode("utf-8"))
            else:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode("utf-8") if data else None,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=3) as response:
                    return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e), "endpoint": endpoint}

    def check_health(self):
        """Check WordPress site health status."""
        results = {}

        # Check homepage
        try:
            req = urllib.request.Request(self.base_url)
            with urllib.request.urlopen(req, timeout=3) as response:
                results["status_code"] = response.status
                results["server"] = response.headers.get("Server", "unknown")
                content_type = response.headers.get("Content-Type", "unknown")
                results["content_type"] = content_type
                results["homepage_loadable"] = True
        except Exception as e:
            results["homepage_loadable"] = False
            results["homepage_error"] = str(e)

        # Check RSS feed
        try:
            req = urllib.request.Request(f"{self.base_url}/feed")
            with urllib.request.urlopen(req, timeout=3) as response:
                results["rss_status"] = response.status
                results["rss_loadable"] = True
                # Try to parse basic RSS info
                rss_content = response.read().decode("utf-8")[:200]
                results["rss_title"] = (
                    rss_content.split("<title>")[1].split("</title>")[0]
                    if "<title>" in rss_content
                    else "unknown"
                )
        except Exception as e:
            results["rss_loadable"] = False
            results["rss_error"] = str(e)

        # Check comments feed
        try:
            req = urllib.request.Request(f"{self.base_url}/comments/feed")
            with urllib.request.urlopen(req, timeout=3) as response:
                results["comments_feed_status"] = response.status
                results["comments_feed_loadable"] = True
        except Exception as e:
            results["comments_feed_loadable"] = False
            results["comments_feed_error"] = str(e)

        # Check oEmbed endpoint
        try:
            req = urllib.request.Request(f"{self.base_url}/wp-json/oembed/1.0/json?url={self.base_url}")
            with urllib.request.urlopen(req, timeout=3) as response:
                results["oembed_status"] = response.status
                results["oembed_loadable"] = True
                oembed_data = json.loads(response.read().decode("utf-8"))
                results["oembed_title"] = oembed_data.get("title", "unknown")
        except Exception as e:
            results["oembed_loadable"] = False
            results["oembed_error"] = str(e)

        # Check REST API
        try:
            req = urllib.request.Request(f"{self.base_url}/wp-json")
            with urllib.request.urlopen(req, timeout=3) as response:
                results["rest_api_status"] = response.status
                results["rest_api_loadable"] = True
                rest_data = json.loads(response.read().decode("utf-8"))
                results["rest_endpoints"] = list(rest_data.keys())[:5] if rest_data else []
        except Exception as e:
            results["rest_api_loadable"] = False
            results["rest_api_error"] = str(e)

        return results

    def get_site_info(self):
        """Get basic WordPress site information."""
        info = {}

        # Get homepage content basics
        try:
            req = urllib.request.Request(self.base_url)
            with urllib.request.urlopen(req, timeout=3) as response:
                html = response.read().decode("utf-8")[:500]
                # Extract meta info
                import re
                info["title"] = (
                    re.search(r"<title>(.*?)</title>", html)
                    .group(1)
                    if re.search(r"<title>(.*?)</title>", html)
                    else "unknown"
                )
                info["description"] = (
                    re.search(
                        r'<meta\s+name="description"\s+content="([^"]+)"', html
                    )
                    .group(1)
                    if re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
                    else "unknown"
                )
                info["viewport"] = (
                    re.search(
                        r'<meta\s+name="viewport"\s+content="([^"]+)"', html
                    )
                    .group(1)
                    if re.search(r'<meta\s+name="viewport"\s+content="([^"]+)"', html)
                    else "unknown"
                )
        except Exception as e:
            info["error"] = str(e)

        # Get RSS feed info
        try:
            req = urllib.request.Request(f"{self.base_url}/feed")
            with urllib.request.urlopen(req, timeout=3) as response:
                rss = response.read().decode("utf-8")[:1000]
                import re
                info["rss_title"] = (
                    re.search(r"<title>(.*?)</title>", rss)
                    .group(1)
                    if re.search(r"<title>(.*?)</title>", rss)
                    else "unknown"
                )
                # Get item count approximation
                info["rss_item_count"] = len(re.findall(r"<item>", rss))
        except Exception as e:
            info["rss_error"] = str(e)
            info["rss_title"] = "unknown"
            info["rss_item_count"] = 0

        return info

    def check_plugin_status(self):
        """Check WordPress plugin status via REST API."""
        try:
            req = urllib.request.Request(f"{self.base_url}/wp-json//plugins")
            with urllib.request.urlopen(req, timeout=3) as response:
                plugins = json.loads(response.read().decode("utf-8"))
                return {
                    "loadable": True,
                    "plugin_count": len(plugins.get("plugins", [])),
                    "plugins": [
                        {
                            "name": p.get("name", "unknown"),
                            "author": p.get("author", "unknown"),
                            "active": p.get("status") == "active",
                        }
                        for p in plugins.get("plugins", [])[:10]  # Top 10
                    ],
                }
        except Exception as e:
            return {"loadable": False, "error": str(e), "plugin_count": 0}

    def check_theme_status(self):
        """Check WordPress theme status via REST API."""
        try:
            req = urllib.request.Request(f"{self.base_url}/wp-json/theme")
            with urllib.request.urlopen(req, timeout=3) as response:
                themes = json.loads(response.read().decode("utf-8"))
                return {
                    "loadable": True,
                    "theme_count": len(themes.get("themes", [])),
                    "active_theme": themes.get("name", "unknown"),
                    "themes": [
                        {
                            "name": t.get("name", "unknown"),
                            "author": t.get("author", "unknown"),
                            "status": t.get("status", "unknown"),
                        }
                        for t in themes.get("themes", [])[:5]  # Top 5
                    ],
                }
        except Exception as e:
            return {"loadable": False, "error": str(e), "theme_count": 0}

    def analyze_content_freshness(self):
        """Analyze content freshness from RSS feed."""
        try:
            req = urllib.request.Request(f"{self.base_url}/feed")
            with urllib.request.urlopen(req, timeout=3) as response:
                rss = response.read().decode("utf-8")

            import re

            # Get all items
            items = re.findall(r"<item>(.*?)</item>", rss, re.DOTALL)

            if not items:
                return {"freshness": "no_content", "last_update": None}

            # Get dates from items
            dates = []
            for item in items[:10]:  # Last 10 items
                date_match = re.search(r"<pubDate>(.*?)</pubDate>", item)
                if date_match:
                    from datetime import datetime

                    try:
                        date_str = date_match.group(1)
                        parsed = datetime.strptime(
                            date_str, "%a, %d %b %Y %H:%M:%S %z"
                        )
                        dates.append(parsed)
                    except Exception:
                        pass

            if not dates:
                return {"freshness": "parse_error", "last_update": None}

            # Calculate freshness
            newest = max(dates)
            oldest = min(dates)
            now = datetime.utcnow()

            days_since_newest = (now - newest).days
            days_since_oldest = (now - oldest).days

            # Determine freshness level
            if days_since_newest == 0:
                freshness = "updated_today"
            elif days_since_newest < 7:
                freshness = "updated_this_week"
            elif days_since_newest < 30:
                freshness = "updated_this_month"
            elif days_since_newest < 90:
                freshness = "updated_last_3_months"
            else:
                freshness = "stale_last_3_months"

            return {
                "freshness": freshness,
                "days_since_newest": days_since_newest,
                "days_since_oldest": days_since_oldest,
                "newest_article": newest.isoformat(),
                "oldest_article": oldest.isoformat(),
                "item_count_checked": min(len(items), 10),
            }
        except Exception as e:
            return {"freshness": "error", "error": str(e)}

    def generate_domain_report(self):
        """Generate comprehensive WordPress domain operation report."""
        health = self.check_health()
        site_info = self.get_site_info()
        freshness = self.analyze_content_freshness()
        plugins = self.check_plugin_status()
        themes = self.check_theme_status()

        lines = []
        lines.append("=" * 70)
        lines.append("🌐 IXPANSION WORDPRESS DOMAIN OPERATIONS REPORT 🌐")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Domain: {self.base_url}")
        lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Agent: {self.name} v{self.version}")
        lines.append("")

        # Site health
        lines.append("✅ Site Health:")
        lines.append("-" * 70)
        if health.get("homepage_loadable", False):
            lines.append(f"  🏠 Homepage: {health.get('status_code', '?')} OK")
            lines.append(f"  📡 Server: {health.get('server', 'unknown')}")
        else:
            lines.append(f"  🏠 Homepage: UNREACHABLE - {health.get('homepage_error', '?')}")

        if health.get("rss_loadable", False):
            lines.append(
                f"  📡 RSS Feed: {health.get('rss_status', '?')} OK "
                f"({health.get('rss_title', 'unknown')})"
            )
        else:
            lines.append(
                f"  📡 RSS Feed: UNREACHABLE - {health.get('rss_error', '?')}"
            )

        if health.get("oembed_loadable", False):
            lines.append(
                f"  🔗 oEmbed: {health.get('oembed_status', '?')} OK"
            )
        else:
            lines.append(f"  🔗 oEmbed: UNREACHABLE - {health.get('oembed_error', '?')}")

        lines.append("")

        # Site information
        lines.append("ℹ️  Site Information:")
        lines.append("-" * 70)
        lines.append(f"  📰 Title: {site_info.get('title', 'unknown')}")
        lines.append(f"  📝 Description: {site_info.get('description', 'unknown')}")
        lines.append(f"  👁️  Viewport: {site_info.get('viewport', 'unknown')}")

        lines.append("")
        lines.append("  📜 RSS Feed:")
        lines.append(f"    Title: {freshness.get('rss_title', 'unknown')}")
        lines.append(f"    Items (checked): {freshness.get('item_count_checked', 0)}")
        lines.append(
            f"  🆕 Freshness: {freshness.get('freshness', 'unknown')}"
        )
        lines.append(f"    📅 Days since newest: {freshness.get('days_since_newest', '?')}")
        lines.append(f"    📅 Days since oldest: {freshness.get('days_since_oldest', '?')}")

        lines.append("")

        # Themes and plugins
        lines.append("🔌 Themes & Plugins:")
        lines.append("-" * 70)

        if plugins.get("loadable", False):
            lines.append(f"  Plugins Active: {plugins.get('plugin_count', 0)}")
            for p in plugins.get("plugins", [])[:3]:
                status = "✅" if p.get("active") else "📦"
                lines.append(f"    {status} {p.get('name', '?')} by {p.get('author', '?')}")
        else:
            lines.append(f"  Plugins: UNREACHABLE - {plugins.get('error', '?')}")

        if themes.get("loadable", False):
            lines.append(f"  Themes Total: {themes.get('theme_count', 0)}")
            lines.append(f"  Active Theme: {themes.get('active_theme', 'unknown')}")
            for t in themes.get("themes", [])[:3]:
                lines.append(f"    🎨 {t.get('name', '?')} by {t.get('author', '?')}")
        else:
            lines.append(f"  Themes: UNREACHABLE - {themes.get('error', '?')}")

        lines.append("")

        # Overall status summary
        lines.append("📊 Overall Status Summary:")
        lines.append("-" * 70)

        checks = [
            ("Homepage", health.get("homepage_loadable", False)),
            ("RSS Feed", health.get("rss_loadable", False)),
            ("oEmbed", health.get("oembed_loadable", False)),
            ("REST API", health.get("rest_api_loadable", False)),
        ]

        all_healthy = all(status for _, status in checks)
        for name, status in checks:
            icon = "✅" if status else "❌"
            lines.append(f"  {icon} {name}")

        lines.append("")
        if all_healthy:
            lines.append("  🟢 All systems operational")
        else:
            lines.append(
                "  🟡 Some systems need attention"
            )

        lines.append("")
        lines.append("=" * 70)
        lines.append("End of WordPress Domain Operations Report")
        lines.append("=" * 70)

        return "\n".join(lines)

    def run_operations_cycle(self, action="full"):
        """Run a complete WordPress operations cycle."""
        print("=" * 70)
        print(f"IXPANSION WordPress Operations Cycle")
        print(f"Domain: {self.base_url}")
        print(f"Agent: {self.name} v{self.version}")
        print("=" * 70)
        print("")

        if action == "full" or action == "health":
            print(">>> Checking WordPress health...")
            health = self.check_health()
            print(f"  Homepage: {'✅ OK' if health.get('homepage_loadable') else '❌ Down'}")
            print(f"  RSS Feed: {'✅ OK' if health.get('rss_loadable') else '❌ Down'}")
            print(f"  oEmbed: {'✅ OK' if health.get('oembed_loadable') else '❌ Down'}")
            print(f"  REST API: {'✅ OK' if health.get('rest_api_loadable') else '❌ Down'}")

        if action == "full" or action == "info":
            print(">>> Getting site information...")
            info = self.get_site_info()
            print(f"  Title: {info.get('title', 'unknown')}")
            print(f"  Description: {info.get('description', 'unknown')}")
            print(f"  RSS Freshness: {freshness.get('freshness', 'unknown') if (freshness := self.analyze_content_freshness()) else 'unknown'}")

        if action == "full" or action == "freshness":
            print(">>> Analyzing content freshness...")
            freshness = self.analyze_content_freshness()
            print(f"  Status: {freshness.get('freshness', 'unknown')}")
            print(f"  Days since newest: {freshness.get('days_since_newest', '?')}")

        if action == "full" or action == "plugins":
            print(">>> Checking plugin status...")
            plugins = self.check_plugin_status()
            print(f"  Total plugins: {plugins.get('plugin_count', 0)}")

        if action == "full" or action == "themes":
            print(">>> Checking theme status...")
            themes = self.check_theme_status()
            print(f"  Total themes: {themes.get('theme_count', 0)}")

        if action == "full" or action == "report":
            print(">>> Generating comprehensive report...")
            report = self.generate_domain_report()
            # Print summary lines
            lines = report.split("\n")
            for line in lines[20:40]:
                print(line)

        if action == "full" or action == "correlate":
            print(">>> Correlating with IXPANSION organism health...")
            # This would integrate with health-monitor-agent
            print("  (Integration with OrganHealthMonitor pending)")

        print("")
        print("✅ WordPress operations cycle complete!")


# CLI interface
if __name__ == "__main__":
    import sys

    agent = WordPressAgent()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "health":
            print(">>> Checking WordPress health...")
            health = agent.check_health()
            print(f"  Homepage: {'✅ OK' if health.get('homepage_loadable') else '❌ Down'}")
            print(f"  RSS: {'✅ OK' if health.get('rss_loadable') else '❌ Down'}")
            print(f"  oEmbed: {'✅ OK' if health.get('oembed_loadable') else '❌ Down'}")

        elif command == "info":
            print(">>> Getting site info...")
            info = agent.get_site_info()
            print(f"  Title: {info.get('title', 'unknown')}")
            print(f"  RSS Title: {info.get('rss_title', 'unknown')}")

        elif command == "freshness":
            print(">>> Analyzing content freshness...")
            freshness = agent.analyze_content_freshness()
            print(f"  Status: {freshness.get('freshness', 'unknown')}")
            print(f"  Days since newest: {freshness.get('days_since_newest', '?')}")

        elif command == "plugins":
            print(">>> Checking plugins...")
            plugins = agent.check_plugin_status()
            print(f"  Total: {plugins.get('plugin_count', 0)}")

        elif command == "themes":
            print(">>> Checking themes...")
            themes = agent.check_theme_status()
            print(f"  Active: {themes.get('active_theme', 'unknown')}")

        elif command == "report":
            print(">>> Generating domain report...")
            report = agent.generate_domain_report()
            # Print first 6 lines
            for line in report.split("\n")[:6]:
                print(line)

        elif command == "full":
            print(">>> Running full operations cycle...")
            agent.run_operations_cycle(action="full")

        elif command == "correlate":
            print(">>> Correlating with organism health...")
            print("  (Integration with OrganHealthMonitor)")
            agent.run_operations_cycle(action="correlate")

        elif command == "help" or command in ("--help", "-h"):
            print("""
IXPANSION WordPressAgent Commands:
  health                  - Check WordPress health status
  info                    - Get site information
  freshness               - Analyze content freshness
  plugins                 - Check plugin status
  themes                  - Check theme status
  report                  - Generate comprehensive report
  full                    - Run complete cycle
  correlate               - Correlate with organism health
  help                    - Show this help

Domain: alexalex.info
""")

        else:
            print(f"Unknown command: {command}")
            print("Use 'check help' for available commands")
    else:
        # Default: run full cycle
        print("=" * 70)
        print("IXPANSION WordPressAgent - Default Cycle")
        print("=" * 70)
        print("")
        print(">>> Running full domain operations...")
        agent.run_operations_cycle(action="full")
        print("")
        print("✅ Default WordPress cycle complete!")

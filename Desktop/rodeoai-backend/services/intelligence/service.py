"""
Intelligence Service
Orchestrates deep user analysis across all extraction components.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .extraction import (
    UserIntelligence,
    UserEngagement,
    SocialGraph,
    EngagementScraper,
    PoliticalAnalyzer,
    BrandAffinityAnalyzer,
    HiddenDataExtractor
)

logger = logging.getLogger(__name__)


class IntelligenceService:
    """
    Comprehensive intelligence gathering service.
    Combines scraping with analysis to build detailed user profiles.
    """

    def __init__(self):
        self.engagement_scraper = EngagementScraper()
        self.political_analyzer = PoliticalAnalyzer()
        self.brand_analyzer = BrandAffinityAnalyzer()
        self.hidden_extractor = HiddenDataExtractor()

    async def analyze_user(
        self,
        platform: str,
        username: str,
        depth: str = "standard"  # light, standard, deep
    ) -> UserIntelligence:
        """
        Perform comprehensive analysis on a user.

        Args:
            platform: Social platform
            username: Target username
            depth: Analysis depth (light=fast, deep=thorough)

        Returns:
            UserIntelligence object with all gathered data
        """
        logger.info(f"Starting {depth} analysis of {platform}/{username}")

        intel = UserIntelligence(username=username, platform=platform)

        # Get base profile and posts
        profile_data, posts = await self._get_base_data(platform, username, depth)

        if profile_data:
            intel.display_name = profile_data.get("display_name", "")
            intel.bio = profile_data.get("bio", "")
            intel.location = profile_data.get("location", "")
            intel.website = profile_data.get("website", "")

        # Get engagement data (followers/following)
        if depth in ["standard", "deep"]:
            intel.engagement = await self.engagement_scraper.get_user_engagement(
                platform, username, depth
            )

        # Extract hashtags and mentions from posts
        intel.hashtags_used = self._extract_hashtags(posts)
        intel.mentions_frequent = self._extract_mentions(posts)

        # Political analysis
        following = intel.engagement.following if intel.engagement else []
        political = self.political_analyzer.analyze_political_leaning(
            posts, following, intel.bio
        )
        intel.political_leaning = political["leaning"]
        intel.political_confidence = political["confidence"]
        intel.political_topics = political["topics"]

        # Sentiment analysis
        sentiment = self.political_analyzer.analyze_sentiment(posts)
        intel.sentiment_overall = sentiment["sentiment"]

        # Brand affinity
        brand_data = self.brand_analyzer.analyze_brand_affinity(posts, following)
        intel.brand_affinities = brand_data["brand_affinities"]
        intel.brand_categories = list(brand_data["top_categories"].keys())

        # Hidden data extraction
        demographics = self.hidden_extractor.extract_demographics(
            intel.bio, posts, intel.display_name
        )
        intel.likely_age_range = demographics["likely_age_range"]
        intel.likely_gender = demographics["likely_gender"]
        intel.likely_occupation = demographics["likely_occupation"]
        intel.interests = demographics["interests"]

        # Personality traits
        intel.personality_traits = self.hidden_extractor.extract_personality_traits(posts)

        # Posting patterns
        intel.posting_frequency = self._analyze_posting_frequency(posts)
        intel.active_hours = self._analyze_active_hours(posts)
        intel.content_types = self._analyze_content_types(posts)

        # Topics of interest
        intel.topics_of_interest = self._extract_topics(posts, intel.hashtags_used)

        logger.info(f"Completed analysis of {platform}/{username}")

        return intel

    async def _get_base_data(
        self,
        platform: str,
        username: str,
        depth: str
    ) -> tuple:
        """Get profile and posts data."""
        from services.scrapers import (
            TwitterScraper, InstagramScraper, RedditScraper, YouTubeScraper
        )

        scrapers = {
            "twitter": TwitterScraper,
            "instagram": InstagramScraper,
            "reddit": RedditScraper,
            "youtube": YouTubeScraper
        }

        post_limits = {"light": 50, "standard": 200, "deep": 500}
        limit = post_limits.get(depth, 200)

        scraper_class = scrapers.get(platform)
        if not scraper_class:
            return None, []

        scraper = scraper_class()
        profile_data = None
        posts = []

        try:
            # Get profile
            profile = await scraper.scrape_profile(username)
            if profile:
                profile_data = profile.to_dict()

            # Get posts
            scraped_posts = await scraper.scrape_posts(username, limit)
            posts = [p.to_dict() for p in scraped_posts]

        except Exception as e:
            logger.error(f"Error getting base data: {e}")
        finally:
            await scraper.close()

        return profile_data, posts

    def _extract_hashtags(self, posts: List[Dict]) -> List[str]:
        """Extract most used hashtags."""
        import re
        from collections import Counter

        hashtags = Counter()
        for post in posts:
            content = post.get("content", "")
            found = re.findall(r"#(\w+)", content)
            hashtags.update(found)

        return [tag for tag, _ in hashtags.most_common(50)]

    def _extract_mentions(self, posts: List[Dict]) -> List[str]:
        """Extract most mentioned users."""
        import re
        from collections import Counter

        mentions = Counter()
        for post in posts:
            content = post.get("content", "")
            found = re.findall(r"@(\w+)", content)
            mentions.update(found)

        return [mention for mention, _ in mentions.most_common(30)]

    def _analyze_posting_frequency(self, posts: List[Dict]) -> str:
        """Analyze posting frequency."""
        if len(posts) < 5:
            return "low"

        # Check timestamps
        timestamps = []
        for post in posts:
            ts = post.get("timestamp")
            if ts:
                try:
                    if isinstance(ts, str):
                        timestamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
                    else:
                        timestamps.append(ts)
                except:
                    pass

        if len(timestamps) < 2:
            return "unknown"

        timestamps.sort()
        total_days = (timestamps[-1] - timestamps[0]).days or 1
        posts_per_day = len(timestamps) / total_days

        if posts_per_day >= 5:
            return "very_high"
        elif posts_per_day >= 2:
            return "high"
        elif posts_per_day >= 0.5:
            return "medium"
        else:
            return "low"

    def _analyze_active_hours(self, posts: List[Dict]) -> List[int]:
        """Analyze most active posting hours."""
        from collections import Counter

        hours = Counter()
        for post in posts:
            ts = post.get("timestamp")
            if ts:
                try:
                    if isinstance(ts, str):
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    else:
                        dt = ts
                    hours[dt.hour] += 1
                except:
                    pass

        # Return top 5 most active hours
        return [hour for hour, _ in hours.most_common(5)]

    def _analyze_content_types(self, posts: List[Dict]) -> Dict[str, int]:
        """Analyze types of content posted."""
        types = {"text": 0, "image": 0, "video": 0, "link": 0}

        for post in posts:
            media = post.get("media_urls", [])
            content = post.get("content", "")

            if media:
                # Check if video or image
                for url in media:
                    if any(ext in url.lower() for ext in [".mp4", ".mov", "video"]):
                        types["video"] += 1
                    else:
                        types["image"] += 1
            elif "http" in content:
                types["link"] += 1
            else:
                types["text"] += 1

        return types

    def _extract_topics(
        self,
        posts: List[Dict],
        hashtags: List[str]
    ) -> List[str]:
        """Extract main topics of interest."""
        # Topic keywords
        topic_keywords = {
            "politics": ["politics", "election", "vote", "government", "congress", "democrat", "republican"],
            "technology": ["tech", "ai", "crypto", "software", "startup", "coding", "programming"],
            "sports": ["game", "team", "season", "playoffs", "championship", "score"],
            "entertainment": ["movie", "show", "series", "netflix", "watch", "concert"],
            "business": ["market", "stock", "invest", "business", "economy", "money"],
            "health": ["health", "fitness", "workout", "diet", "mental", "wellness"],
            "news": ["breaking", "news", "report", "update", "happening"],
            "lifestyle": ["life", "happy", "blessed", "grateful", "love", "family"]
        }

        from collections import Counter
        topic_scores = Counter()

        all_text = " ".join(p.get("content", "") for p in posts).lower()
        all_text += " " + " ".join(hashtags).lower()

        for topic, keywords in topic_keywords.items():
            score = sum(all_text.count(kw) for kw in keywords)
            if score > 0:
                topic_scores[topic] = score

        return [topic for topic, _ in topic_scores.most_common(5)]

    async def build_social_graph(
        self,
        platform: str,
        username: str,
        depth: int = 1  # How many levels deep to go
    ) -> SocialGraph:
        """
        Build a social graph for a user.

        Args:
            platform: Social platform
            username: Target username
            depth: Network depth (1 = direct connections, 2 = friends of friends)
        """
        graph = SocialGraph(center_user=username, platform=platform)

        # Get direct followers/following
        followers = await self.engagement_scraper.scrape_followers(platform, username, 1000)
        following = await self.engagement_scraper.scrape_following(platform, username, 1000)

        graph.followers = set(followers)
        graph.following = set(following)
        graph.mutuals = graph.followers & graph.following

        # Extended network (depth 2)
        if depth >= 2:
            # Sample mutual connections to explore
            sample_mutuals = list(graph.mutuals)[:20]

            for mutual in sample_mutuals:
                try:
                    mutual_following = await self.engagement_scraper.scrape_following(
                        platform, mutual, 100
                    )
                    graph.extended_network[mutual] = set(mutual_following)
                    await asyncio.sleep(1)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error getting extended network for {mutual}: {e}")

        return graph

    async def compare_users(
        self,
        platform: str,
        usernames: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple users and find commonalities/differences.
        """
        profiles = []

        for username in usernames[:10]:  # Limit to 10
            intel = await self.analyze_user(platform, username, "light")
            profiles.append(intel)

        # Find common interests
        all_interests = [set(p.interests) for p in profiles]
        common_interests = set.intersection(*all_interests) if all_interests else set()

        # Find common brands
        all_brands = [set(p.brand_affinities.keys()) for p in profiles]
        common_brands = set.intersection(*all_brands) if all_brands else set()

        # Political distribution
        political_dist = {}
        for p in profiles:
            leaning = p.political_leaning
            political_dist[leaning] = political_dist.get(leaning, 0) + 1

        return {
            "users_analyzed": len(profiles),
            "common_interests": list(common_interests),
            "common_brands": list(common_brands),
            "political_distribution": political_dist,
            "profiles": [p.to_dict() for p in profiles]
        }

    async def find_influencers_in_network(
        self,
        platform: str,
        username: str,
        min_followers: int = 10000
    ) -> List[Dict]:
        """
        Find influencers in a user's network.
        """
        # Get who they follow
        following = await self.engagement_scraper.scrape_following(platform, username, 500)

        influencers = []

        # Check follower counts of people they follow
        from services.scrapers import TwitterScraper, InstagramScraper

        scrapers = {
            "twitter": TwitterScraper,
            "instagram": InstagramScraper
        }

        scraper_class = scrapers.get(platform)
        if not scraper_class:
            return []

        # Sample to avoid rate limits
        sample = following[:50]

        for account in sample:
            scraper = scraper_class()
            try:
                profile = await scraper.scrape_profile(account)
                if profile and profile.followers >= min_followers:
                    influencers.append({
                        "username": account,
                        "followers": profile.followers,
                        "verified": profile.verified
                    })
            except:
                pass
            finally:
                await scraper.close()
                await asyncio.sleep(0.5)

        # Sort by followers
        influencers.sort(key=lambda x: x["followers"], reverse=True)

        return influencers


# Global service instance
_service: Optional[IntelligenceService] = None


def get_intelligence_service() -> IntelligenceService:
    """Get or create the global intelligence service."""
    global _service
    if _service is None:
        _service = IntelligenceService()
    return _service

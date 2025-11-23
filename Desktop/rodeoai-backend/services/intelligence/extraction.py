"""
Deep Intelligence Extraction
Extract engagement data, social graphs, brand affiliations, and behavioral insights.
"""

import asyncio
import re
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from dataclasses import dataclass, field
from collections import Counter
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserEngagement:
    """Detailed engagement data for a user."""
    username: str
    platform: str

    # Followers/Following
    followers: List[str] = field(default_factory=list)
    following: List[str] = field(default_factory=list)
    follower_count: int = 0
    following_count: int = 0

    # Engagement patterns
    liked_posts: List[Dict] = field(default_factory=list)
    commented_posts: List[Dict] = field(default_factory=list)
    shared_posts: List[Dict] = field(default_factory=list)

    # Brands & accounts interacted with
    brands_followed: List[str] = field(default_factory=list)
    brands_engaged: List[str] = field(default_factory=list)
    influencers_followed: List[str] = field(default_factory=list)

    # Media engagement
    media_accounts_followed: List[str] = field(default_factory=list)
    politicians_followed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "platform": self.platform,
            "followers": self.followers[:100],  # Limit for response size
            "following": self.following[:100],
            "follower_count": self.follower_count,
            "following_count": self.following_count,
            "liked_posts_count": len(self.liked_posts),
            "brands_followed": self.brands_followed,
            "brands_engaged": self.brands_engaged,
            "influencers_followed": self.influencers_followed,
            "media_accounts_followed": self.media_accounts_followed,
            "politicians_followed": self.politicians_followed
        }


@dataclass
class SocialGraph:
    """Social relationship graph."""
    center_user: str
    platform: str

    # Direct connections
    followers: Set[str] = field(default_factory=set)
    following: Set[str] = field(default_factory=set)

    # Mutual connections
    mutuals: Set[str] = field(default_factory=set)

    # Extended network (followers of followers)
    extended_network: Dict[str, Set[str]] = field(default_factory=dict)

    # Clusters (groups of interconnected users)
    clusters: List[Set[str]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "center_user": self.center_user,
            "platform": self.platform,
            "follower_count": len(self.followers),
            "following_count": len(self.following),
            "mutual_count": len(self.mutuals),
            "followers": list(self.followers)[:500],
            "following": list(self.following)[:500],
            "mutuals": list(self.mutuals),
            "extended_network_size": sum(len(v) for v in self.extended_network.values()),
            "cluster_count": len(self.clusters)
        }


@dataclass
class UserIntelligence:
    """Comprehensive intelligence profile for a user."""
    username: str
    platform: str

    # Basic profile
    display_name: str = ""
    bio: str = ""
    location: str = ""
    website: str = ""
    join_date: str = ""

    # Engagement metrics
    engagement: Optional[UserEngagement] = None
    social_graph: Optional[SocialGraph] = None

    # Content analysis
    topics_of_interest: List[str] = field(default_factory=list)
    hashtags_used: List[str] = field(default_factory=list)
    mentions_frequent: List[str] = field(default_factory=list)

    # Brand affinity
    brand_affinities: Dict[str, float] = field(default_factory=dict)  # brand -> score
    brand_categories: List[str] = field(default_factory=list)

    # Political & sentiment
    political_leaning: str = ""  # left, center-left, center, center-right, right
    political_confidence: float = 0.0
    sentiment_overall: str = ""  # positive, neutral, negative
    political_topics: List[str] = field(default_factory=list)

    # Behavioral patterns
    posting_frequency: str = ""  # high, medium, low
    active_hours: List[int] = field(default_factory=list)
    content_types: Dict[str, int] = field(default_factory=dict)  # text, image, video, link

    # Hidden insights
    likely_age_range: str = ""
    likely_gender: str = ""
    likely_occupation: str = ""
    interests: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "platform": self.platform,
            "display_name": self.display_name,
            "bio": self.bio,
            "location": self.location,
            "website": self.website,
            "topics_of_interest": self.topics_of_interest,
            "hashtags_used": self.hashtags_used[:50],
            "brand_affinities": dict(sorted(self.brand_affinities.items(), key=lambda x: -x[1])[:20]),
            "brand_categories": self.brand_categories,
            "political_leaning": self.political_leaning,
            "political_confidence": self.political_confidence,
            "political_topics": self.political_topics,
            "sentiment_overall": self.sentiment_overall,
            "posting_frequency": self.posting_frequency,
            "active_hours": self.active_hours,
            "content_types": self.content_types,
            "likely_age_range": self.likely_age_range,
            "likely_gender": self.likely_gender,
            "likely_occupation": self.likely_occupation,
            "interests": self.interests,
            "personality_traits": self.personality_traits,
            "engagement": self.engagement.to_dict() if self.engagement else None,
            "social_graph": self.social_graph.to_dict() if self.social_graph else None
        }


class EngagementScraper:
    """
    Scrapes engagement data - followers, following, likes, interactions.
    """

    # Known brand accounts (expandable)
    KNOWN_BRANDS = {
        # Tech
        "nike", "adidas", "apple", "google", "amazon", "microsoft", "meta", "tesla",
        "coca-cola", "pepsi", "mcdonalds", "starbucks", "walmart", "target",
        "netflix", "disney", "spotify", "uber", "airbnb", "samsung", "sony",
        "bmw", "mercedes", "toyota", "ford", "chevrolet", "honda",
        "gucci", "louisvuitton", "chanel", "prada", "supreme", "yeezy",
        "nfl", "nba", "mlb", "nhl", "espn", "foxsports", "bleacherreport",

        # Western Wear - Boots
        "lucchese", "tecovas", "ariat", "justinboots", "tonylamaboots", "andersonbean",
        "oldgringoboots", "corralboots", "danhpost", "laredo", "durango", "twistex",
        "cavenders", "bootbarn", "sheplers",

        # Western Wear - Hats
        "resistol", "stetson", "americanhatco", "prohats", "atwood", "greeley",
        "rodeoking", "bullhide", "charliehorse", "baileywestern", "serratelli",

        # Western Wear - Apparel
        "wrangler", "hooey", "panhandleslim", "cinch", "roper", "rockymountainclothing",
        "scully", "drysdales", "westportbigandtall", "millerranch", "ranchwear",

        # Western Wear - Premium/Lifestyle
        "txstandard", "texasstandard", "doubledranchwear", "manready", "imogeneandwillie",
        "ryonabrands", "barkingirons",

        # Rodeo/Western Organizations & Events
        "prca", "prorodeo", "pbr", "pbrockstar", "nfrodeo", "wranglernfr",
        "rncfr", "tfrrodeo", "houstonstockshow", "sanantoniostockshow", "fortworth",
        "cheyennefrontierdays", "calgarystampede", "pendletonroundup",

        # Western Lifestyle Brands
        "yellowstone", "yelllowstonetv", "1883", "1923", "taylorsheridon",
        "yeti", "traeger", "kodiak", "carhartt", "filson",

        # Tack & Equipment
        "martinsaddlery", "billcooksaddlery", "circley", "weaver", "professional",
        "classicropes", "cactusropes", "topropes", "rattler", "lonestarropes"
    }

    # Western-specific accounts to track
    KNOWN_WESTERN_INFLUENCERS = {
        "taborropin", "speedwilliams", "claywsmith", "trevorbrazilebrand",
        "tyemurray", "tyharris", "shylohuff", "ryantardibueno", "dallonkasel",
        "sagejohnson", "wright_broncs", "jbmauney", "lockwood", "kobyradley"
    }

    # Known media outlets
    KNOWN_MEDIA = {
        "cnn", "foxnews", "msnbc", "nytimes", "washingtonpost", "wsj",
        "bbc", "reuters", "ap", "npr", "abc", "cbs", "nbc",
        "breitbart", "huffpost", "dailywire", "theguardian", "politico",
        "vice", "vox", "thehill", "newsmax", "oann"
    }

    # Known politicians/political figures (US-centric, expandable)
    KNOWN_POLITICIANS = {
        "joebiden", "potus", "kamalaharris", "vp",
        "donaldtrump", "realdonaldtrump",
        "elonmusk", "berniesanders", "aoc", "tedcruz", "marcorubio",
        "rondesantis", "gavinnewsom", "elizabethwarren", "jdvance",
        "speakerjohnson", "senatemajldr", "slowell", "mattgaetz"
    }

    # Political keywords for classification
    LEFT_INDICATORS = [
        "progressive", "liberal", "democrat", "blm", "blacklivesmatter",
        "prochoice", "climatejustice", "medicare4all", "defundthepolice",
        "votebluematter", "resist", "impeach", "acab", "abolishice",
        "lgbtq", "pride", "trans rights", "gun control", "green new deal",
        "bernie", "aoc", "warren", "biden", "harris"
    ]

    RIGHT_INDICATORS = [
        "conservative", "republican", "maga", "trump", "prolife",
        "2a", "secondamendment", "buildthewall", "backtheblue",
        "alllivesmatter", "bluelivesmatter", "patriot", "freedom",
        "letsgobrandon", "fjb", "draintheswamp", "stopthesteal",
        "wwg1wga", "qanon", "america first", "desantis", "cruz"
    ]

    def __init__(self):
        self.platform_scrapers = {}

    async def scrape_followers(
        self,
        platform: str,
        username: str,
        limit: int = 1000
    ) -> List[str]:
        """Scrape follower list for a user."""
        if platform == "reddit":
            # Reddit doesn't have traditional followers visible
            return []
        elif platform == "twitter":
            return await self._scrape_twitter_followers(username, limit)
        elif platform == "instagram":
            return await self._scrape_instagram_followers(username, limit)
        return []

    async def scrape_following(
        self,
        platform: str,
        username: str,
        limit: int = 1000
    ) -> List[str]:
        """Scrape following list for a user."""
        if platform == "twitter":
            return await self._scrape_twitter_following(username, limit)
        elif platform == "instagram":
            return await self._scrape_instagram_following(username, limit)
        return []

    async def _scrape_twitter_followers(self, username: str, limit: int) -> List[str]:
        """Scrape Twitter followers using Playwright."""
        from services.playwright_scraper import PlaywrightScraper

        scraper = PlaywrightScraper()
        followers = []

        try:
            page = await scraper._new_page()
            url = f"https://x.com/{username}/followers"

            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Scroll and collect followers
            collected = set()
            scroll_attempts = min(limit // 20 + 1, 50)

            for _ in range(scroll_attempts):
                # Extract visible usernames
                usernames = await page.evaluate("""
                    () => {
                        const users = [];
                        const cells = document.querySelectorAll('[data-testid="UserCell"]');
                        cells.forEach(cell => {
                            const link = cell.querySelector('a[href^="/"]');
                            if (link) {
                                const href = link.getAttribute('href');
                                if (href && href.startsWith('/') && !href.includes('/')) {
                                    users.push(href.replace('/', ''));
                                }
                            }
                        });
                        return users;
                    }
                """)

                for u in usernames:
                    if u and u not in collected:
                        collected.add(u)
                        followers.append(u)

                if len(followers) >= limit:
                    break

                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1)

            await page.close()

        except Exception as e:
            logger.error(f"Error scraping Twitter followers: {e}")
        finally:
            await scraper.close()

        return followers[:limit]

    async def _scrape_twitter_following(self, username: str, limit: int) -> List[str]:
        """Scrape Twitter following list."""
        from services.playwright_scraper import PlaywrightScraper

        scraper = PlaywrightScraper()
        following = []

        try:
            page = await scraper._new_page()
            url = f"https://x.com/{username}/following"

            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            collected = set()
            scroll_attempts = min(limit // 20 + 1, 50)

            for _ in range(scroll_attempts):
                usernames = await page.evaluate("""
                    () => {
                        const users = [];
                        const cells = document.querySelectorAll('[data-testid="UserCell"]');
                        cells.forEach(cell => {
                            const link = cell.querySelector('a[href^="/"]');
                            if (link) {
                                const href = link.getAttribute('href');
                                if (href && href.startsWith('/') && !href.includes('/')) {
                                    users.push(href.replace('/', ''));
                                }
                            }
                        });
                        return users;
                    }
                """)

                for u in usernames:
                    if u and u not in collected:
                        collected.add(u)
                        following.append(u)

                if len(following) >= limit:
                    break

                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1)

            await page.close()

        except Exception as e:
            logger.error(f"Error scraping Twitter following: {e}")
        finally:
            await scraper.close()

        return following[:limit]

    async def _scrape_instagram_followers(self, username: str, limit: int) -> List[str]:
        """
        Scrape Instagram followers.
        Note: Instagram requires login for follower lists.
        """
        logger.warning("Instagram follower scraping requires authentication")
        return []

    async def _scrape_instagram_following(self, username: str, limit: int) -> List[str]:
        """Scrape Instagram following list."""
        logger.warning("Instagram following scraping requires authentication")
        return []

    def categorize_accounts(
        self,
        accounts: List[str]
    ) -> Dict[str, List[str]]:
        """Categorize accounts into brands, media, politicians, etc."""
        categorized = {
            "brands": [],
            "media": [],
            "politicians": [],
            "influencers": [],
            "other": []
        }

        for account in accounts:
            account_lower = account.lower().replace("_", "").replace(".", "")

            if any(brand in account_lower for brand in self.KNOWN_BRANDS):
                categorized["brands"].append(account)
            elif any(media in account_lower for media in self.KNOWN_MEDIA):
                categorized["media"].append(account)
            elif any(pol in account_lower for pol in self.KNOWN_POLITICIANS):
                categorized["politicians"].append(account)
            else:
                categorized["other"].append(account)

        return categorized

    async def get_user_engagement(
        self,
        platform: str,
        username: str,
        depth: str = "standard"  # light, standard, deep
    ) -> UserEngagement:
        """Get comprehensive engagement data for a user."""
        engagement = UserEngagement(username=username, platform=platform)

        # Get followers/following
        follower_limit = {"light": 100, "standard": 500, "deep": 2000}.get(depth, 500)

        followers = await self.scrape_followers(platform, username, follower_limit)
        following = await self.scrape_following(platform, username, follower_limit)

        engagement.followers = followers
        engagement.following = following
        engagement.follower_count = len(followers)
        engagement.following_count = len(following)

        # Categorize following
        categories = self.categorize_accounts(following)
        engagement.brands_followed = categories["brands"]
        engagement.media_accounts_followed = categories["media"]
        engagement.politicians_followed = categories["politicians"]
        engagement.influencers_followed = categories["influencers"]

        return engagement


class PoliticalAnalyzer:
    """
    Analyzes political leaning and sentiment from user content.
    """

    LEFT_KEYWORDS = EngagementScraper.LEFT_INDICATORS
    RIGHT_KEYWORDS = EngagementScraper.RIGHT_INDICATORS

    # Weighted media sources
    LEFT_MEDIA = {"msnbc": 2, "cnn": 1, "nytimes": 1, "washingtonpost": 1, "huffpost": 2, "vox": 2, "vice": 1}
    RIGHT_MEDIA = {"foxnews": 2, "breitbart": 3, "dailywire": 2, "newsmax": 2, "oann": 3}
    CENTER_MEDIA = {"reuters": 0, "ap": 0, "bbc": 0, "npr": 0.5}

    def analyze_political_leaning(
        self,
        posts: List[Dict],
        following: List[str] = None,
        bio: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze political leaning from posts, following list, and bio.

        Returns dict with:
        - leaning: left, center-left, center, center-right, right
        - confidence: 0-1
        - indicators: list of detected indicators
        - topics: political topics discussed
        """
        left_score = 0
        right_score = 0
        indicators = []
        topics = set()

        # Analyze posts
        all_text = bio.lower() + " "
        for post in posts:
            content = post.get("content", "").lower()
            all_text += content + " "

        # Check for keywords
        for keyword in self.LEFT_KEYWORDS:
            count = all_text.count(keyword.lower())
            if count > 0:
                left_score += count
                indicators.append(f"left:{keyword}")
                topics.add(keyword)

        for keyword in self.RIGHT_KEYWORDS:
            count = all_text.count(keyword.lower())
            if count > 0:
                right_score += count
                indicators.append(f"right:{keyword}")
                topics.add(keyword)

        # Analyze following (if available)
        if following:
            for account in following:
                account_lower = account.lower()

                # Check media
                for media, weight in self.LEFT_MEDIA.items():
                    if media in account_lower:
                        left_score += weight
                        indicators.append(f"follows:{media}")

                for media, weight in self.RIGHT_MEDIA.items():
                    if media in account_lower:
                        right_score += weight
                        indicators.append(f"follows:{media}")

                # Check politicians
                left_pols = ["aoc", "berniesanders", "elizabethwarren", "joebiden", "kamalaharris"]
                right_pols = ["realdonaldtrump", "tedcruz", "rondesantis", "elonmusk", "mattgaetz"]

                for pol in left_pols:
                    if pol in account_lower:
                        left_score += 2
                        indicators.append(f"follows:{pol}")

                for pol in right_pols:
                    if pol in account_lower:
                        right_score += 2
                        indicators.append(f"follows:{pol}")

        # Calculate leaning
        total = left_score + right_score
        if total == 0:
            return {
                "leaning": "unknown",
                "confidence": 0,
                "indicators": [],
                "topics": [],
                "left_score": 0,
                "right_score": 0
            }

        # Normalize scores
        left_ratio = left_score / total
        right_ratio = right_score / total

        # Determine leaning
        if left_ratio > 0.7:
            leaning = "left"
        elif left_ratio > 0.55:
            leaning = "center-left"
        elif right_ratio > 0.7:
            leaning = "right"
        elif right_ratio > 0.55:
            leaning = "center-right"
        else:
            leaning = "center"

        # Confidence based on total signals
        confidence = min(total / 20, 1.0)

        return {
            "leaning": leaning,
            "confidence": round(confidence, 2),
            "indicators": indicators[:30],
            "topics": list(topics)[:20],
            "left_score": left_score,
            "right_score": right_score
        }

    def analyze_sentiment(self, posts: List[Dict]) -> Dict[str, Any]:
        """
        Analyze overall sentiment from posts.
        """
        positive_words = [
            "love", "great", "amazing", "awesome", "excellent", "happy",
            "wonderful", "fantastic", "beautiful", "best", "good", "thank",
            "excited", "blessed", "grateful", "incredible"
        ]

        negative_words = [
            "hate", "terrible", "awful", "bad", "worst", "angry", "sad",
            "disappointed", "disgusted", "horrible", "sucks", "stupid",
            "pathetic", "trash", "garbage", "disaster", "failure"
        ]

        positive_count = 0
        negative_count = 0

        for post in posts:
            content = post.get("content", "").lower()
            for word in positive_words:
                positive_count += content.count(word)
            for word in negative_words:
                negative_count += content.count(word)

        total = positive_count + negative_count
        if total == 0:
            sentiment = "neutral"
            score = 0.5
        else:
            score = positive_count / total
            if score > 0.6:
                sentiment = "positive"
            elif score < 0.4:
                sentiment = "negative"
            else:
                sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive_signals": positive_count,
            "negative_signals": negative_count
        }


class BrandAffinityAnalyzer:
    """
    Analyzes brand affinities and interests from user activity.
    """

    # Brand categories
    BRAND_CATEGORIES = {
        "tech": ["apple", "google", "microsoft", "samsung", "sony", "meta", "amazon"],
        "fashion": ["nike", "adidas", "gucci", "louisvuitton", "chanel", "prada", "supreme"],
        "automotive": ["tesla", "bmw", "mercedes", "toyota", "ford", "porsche"],
        "food_beverage": ["starbucks", "mcdonalds", "cocacola", "pepsi", "chipotle"],
        "entertainment": ["netflix", "disney", "spotify", "hbo", "hulu"],
        "sports": ["nfl", "nba", "mlb", "nhl", "espn", "ufc"],
        "finance": ["robinhood", "coinbase", "venmo", "cashapp", "paypal"],
        "travel": ["airbnb", "uber", "lyft", "delta", "united", "marriott"],

        # Western Wear Categories
        "western_boots": [
            "lucchese", "tecovas", "ariat", "justinboots", "tonylamaboots",
            "andersonbean", "oldgringoboots", "corralboots", "danhpost",
            "laredo", "durango", "twistex", "cavenders", "bootbarn", "sheplers"
        ],
        "western_hats": [
            "resistol", "stetson", "americanhatco", "prohats", "atwood",
            "greeley", "rodeoking", "bullhide", "charliehorse", "baileywestern", "serratelli"
        ],
        "western_apparel": [
            "wrangler", "hooey", "panhandleslim", "cinch", "roper",
            "rockymountainclothing", "scully", "drysdales", "millerranch", "ranchwear"
        ],
        "western_premium": [
            "txstandard", "texasstandard", "doubledranchwear", "manready",
            "imogeneandwillie", "ryonabrands", "barkingirons"
        ],
        "rodeo_events": [
            "prca", "prorodeo", "pbr", "pbrockstar", "nfrodeo", "wranglernfr",
            "rncfr", "houstonstockshow", "sanantoniostockshow", "fortworth",
            "cheyennefrontierdays", "calgarystampede", "pendletonroundup"
        ],
        "western_lifestyle": [
            "yellowstone", "yellowstonetv", "1883", "1923",
            "yeti", "traeger", "kodiak", "carhartt", "filson"
        ],
        "rodeo_equipment": [
            "martinsaddlery", "billcooksaddlery", "circley", "weaver",
            "classicropes", "cactusropes", "topropes", "rattler", "lonestarropes"
        ]
    }

    # Western influencers/athletes to track
    WESTERN_INFLUENCERS = {
        # Team Ropers
        "taborropin", "speedwilliams", "claywsmith", "trevorbrazilebrand",
        "kalubwray", "wesleyduby", "colemilligan", "tyleranderson",

        # Bull Riders
        "jbmauney", "lockwood", "dallonkasel", "josetovito",
        "bushwacker", "sagejohnson", "kobyradley",

        # Bronc Riders
        "wright_broncs", "russmetal", "zekethe", "jadecoutts",

        # Barrel Racers
        "hailiekinsel", "brittanypozzi", "ivypconrado",
        "tianyehager", "shalielarsson",

        # Legends/Personalities
        "tyemurray", "tyharris", "trevorbrazile", "rickysonnygreen"
    }

    def analyze_brand_affinity(
        self,
        posts: List[Dict],
        following: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze brand affinities from posts and following.
        """
        brand_mentions = Counter()
        brand_engagement = Counter()

        # Flatten all brands
        all_brands = set()
        for brands in self.BRAND_CATEGORIES.values():
            all_brands.update(brands)

        # Analyze posts
        for post in posts:
            content = post.get("content", "").lower()
            for brand in all_brands:
                if brand in content:
                    brand_mentions[brand] += 1

        # Analyze following
        if following:
            for account in following:
                account_lower = account.lower().replace("_", "")
                for brand in all_brands:
                    if brand in account_lower:
                        brand_engagement[brand] += 3  # Higher weight for following

        # Combine scores
        combined = Counter()
        for brand, count in brand_mentions.items():
            combined[brand] += count
        for brand, count in brand_engagement.items():
            combined[brand] += count

        # Get top brands
        top_brands = dict(combined.most_common(20))

        # Identify categories
        category_scores = Counter()
        for category, brands in self.BRAND_CATEGORIES.items():
            for brand in brands:
                if brand in combined:
                    category_scores[category] += combined[brand]

        return {
            "brand_affinities": top_brands,
            "top_categories": dict(category_scores.most_common(5)),
            "total_brand_signals": sum(combined.values())
        }


class HiddenDataExtractor:
    """
    Extracts hidden/inferred data points from user profiles and content.
    """

    # Age indicators
    AGE_PATTERNS = {
        "13-17": ["high school", "homework", "prom", "freshman", "sophomore"],
        "18-24": ["college", "university", "dorm", "grad school", "student loan"],
        "25-34": ["career", "promotion", "wedding", "first house", "startup"],
        "35-44": ["kids", "mortgage", "minivan", "school district", "401k"],
        "45-54": ["empty nest", "retirement planning", "grandkids", "downsizing"],
        "55+": ["retired", "grandchildren", "medicare", "social security"]
    }

    # Occupation indicators
    OCCUPATION_PATTERNS = {
        "tech": ["developer", "engineer", "coding", "software", "startup", "tech", "programming"],
        "healthcare": ["nurse", "doctor", "hospital", "medical", "healthcare", "patient"],
        "education": ["teacher", "professor", "student", "classroom", "education"],
        "finance": ["trading", "investing", "finance", "banker", "wall street", "stocks"],
        "creative": ["design", "artist", "photographer", "creative", "portfolio"],
        "sales": ["sales", "marketing", "b2b", "quota", "client", "account"],
        "service": ["restaurant", "retail", "customer service", "hospitality"]
    }

    # Interest indicators
    INTEREST_PATTERNS = {
        "fitness": ["gym", "workout", "fitness", "running", "lifting", "gains"],
        "gaming": ["gaming", "gamer", "esports", "twitch", "xbox", "playstation"],
        "travel": ["travel", "vacation", "adventure", "wanderlust", "passport"],
        "food": ["foodie", "cooking", "recipe", "chef", "restaurant", "brunch"],
        "music": ["concert", "music", "spotify", "playlist", "band", "festival"],
        "sports": ["sports", "game day", "fantasy", "season", "playoffs"],
        "crypto": ["crypto", "bitcoin", "nft", "web3", "blockchain", "hodl"],
        "parenting": ["mom", "dad", "parent", "kids", "family", "children"]
    }

    def extract_demographics(
        self,
        bio: str,
        posts: List[Dict],
        display_name: str = ""
    ) -> Dict[str, Any]:
        """
        Extract demographic inferences from content.
        """
        all_text = f"{bio} {display_name} ".lower()
        for post in posts:
            all_text += post.get("content", "").lower() + " "

        # Age inference
        age_scores = {}
        for age_range, keywords in self.AGE_PATTERNS.items():
            score = sum(all_text.count(kw) for kw in keywords)
            if score > 0:
                age_scores[age_range] = score

        likely_age = max(age_scores, key=age_scores.get) if age_scores else "unknown"

        # Gender inference (from name/pronouns)
        gender = "unknown"
        male_indicators = ["he/him", "father", "dad", "husband", "mr.", "king"]
        female_indicators = ["she/her", "mother", "mom", "wife", "mrs.", "queen"]

        male_score = sum(all_text.count(ind) for ind in male_indicators)
        female_score = sum(all_text.count(ind) for ind in female_indicators)

        if male_score > female_score:
            gender = "likely_male"
        elif female_score > male_score:
            gender = "likely_female"

        # Occupation inference
        occupation_scores = {}
        for occupation, keywords in self.OCCUPATION_PATTERNS.items():
            score = sum(all_text.count(kw) for kw in keywords)
            if score > 0:
                occupation_scores[occupation] = score

        likely_occupation = max(occupation_scores, key=occupation_scores.get) if occupation_scores else "unknown"

        # Interest inference
        interests = []
        for interest, keywords in self.INTEREST_PATTERNS.items():
            score = sum(all_text.count(kw) for kw in keywords)
            if score >= 2:
                interests.append(interest)

        return {
            "likely_age_range": likely_age,
            "age_confidence": age_scores,
            "likely_gender": gender,
            "likely_occupation": likely_occupation,
            "occupation_scores": occupation_scores,
            "interests": interests
        }

    def extract_personality_traits(self, posts: List[Dict]) -> List[str]:
        """
        Infer personality traits from posting behavior.
        """
        traits = []

        if len(posts) == 0:
            return traits

        # Calculate metrics
        total_posts = len(posts)
        total_chars = sum(len(p.get("content", "")) for p in posts)
        avg_length = total_chars / total_posts if total_posts > 0 else 0

        # Analyze content
        all_text = " ".join(p.get("content", "") for p in posts).lower()

        # Verbose/concise
        if avg_length > 200:
            traits.append("verbose")
        elif avg_length < 50:
            traits.append("concise")

        # Question asker
        if all_text.count("?") > total_posts * 0.3:
            traits.append("inquisitive")

        # Emotional expression
        if all_text.count("!") > total_posts * 0.5:
            traits.append("expressive")

        # Self-focused vs others-focused
        i_count = all_text.count(" i ") + all_text.count(" my ") + all_text.count(" me ")
        we_count = all_text.count(" we ") + all_text.count(" our ") + all_text.count(" us ")

        if i_count > we_count * 2:
            traits.append("individualistic")
        elif we_count > i_count:
            traits.append("community-oriented")

        # Technical vs casual
        tech_words = ["data", "analysis", "research", "study", "evidence", "statistic"]
        if sum(all_text.count(w) for w in tech_words) > total_posts * 0.2:
            traits.append("analytical")

        # Humor
        humor_indicators = ["lol", "lmao", "haha", "😂", "🤣", "😭"]
        if sum(all_text.count(h) for h in humor_indicators) > total_posts * 0.2:
            traits.append("humorous")

        return traits

    def extract_location_hints(self, bio: str, posts: List[Dict]) -> Dict[str, Any]:
        """
        Extract location hints from content.
        """
        all_text = bio.lower() + " "
        for post in posts:
            all_text += post.get("content", "").lower() + " "

        # Common location patterns
        location_hints = []

        # Time zone hints
        if any(x in all_text for x in ["pst", "pacific", "la", "san francisco", "seattle"]):
            location_hints.append("US West Coast")
        if any(x in all_text for x in ["est", "eastern", "nyc", "new york", "boston"]):
            location_hints.append("US East Coast")
        if any(x in all_text for x in ["cst", "central", "chicago", "texas", "austin"]):
            location_hints.append("US Central")
        if any(x in all_text for x in ["gmt", "london", "uk", "british"]):
            location_hints.append("UK")

        # Weather/season references can hint at hemisphere
        # Sports team references can hint at city

        return {
            "location_hints": location_hints,
            "detected_cities": [],  # Could be expanded
            "timezone_guess": location_hints[0] if location_hints else "unknown"
        }


class SponsoredContentDetector:
    """
    Detects sponsored/paid content and brand partnerships.
    """

    # FTC disclosure keywords
    DISCLOSURE_PATTERNS = [
        r"#ad\b", r"#sponsored", r"#paid", r"#partner",
        r"#brandpartner", r"#brandambassador", r"#ambassador",
        r"#gifted", r"#promo", r"#collab\b", r"#collaboration",
        r"paid partnership", r"sponsored by", r"in partnership with",
        r"thanks to .* for", r"partnered with", r"working with",
        r"#rodeoambassador", r"#teamwrangler", r"#teamariat",
        r"#teamcavenders", r"#teambootbarn", r"#teamstetson",
        r"#teamresistol", r"#teamlucchese", r"#teamtecovas"
    ]

    # Western brand partnership indicators
    WESTERN_PARTNERSHIP_TAGS = {
        "wrangler": ["#wrangler", "#wranglernfr", "#teamwrangler", "#wranglercowboy"],
        "ariat": ["#ariat", "#ariatinternational", "#teamariat", "#ariatcountry"],
        "resistol": ["#resistol", "#resistolhats", "#teamresistol"],
        "stetson": ["#stetson", "#stetsonhat", "#teamstetson"],
        "cavenders": ["#cavenders", "#teamcavenders"],
        "bootbarn": ["#bootbarn", "#teambootbarn"],
        "lucchese": ["#lucchese", "#teamlucchese"],
        "tecovas": ["#tecovas", "#teamtecovas"],
        "cinch": ["#cinch", "#cinchcowboy", "#teamcinch"],
        "hooey": ["#hooey", "#teamhooey", "#hooeyco"],
        "pbr": ["#pbr", "#pbrambassador", "#teampbr"],
        "prca": ["#prca", "#prorodeo", "#prcaambassador"]
    }

    def detect_sponsored_content(self, posts: List[Dict]) -> Dict[str, Any]:
        """
        Analyze posts for sponsored content indicators.
        """
        sponsored_posts = []
        brand_partnerships = Counter()
        disclosure_types = Counter()

        for post in posts:
            content = post.get("content", "").lower()
            post_id = post.get("id", "unknown")
            is_sponsored = False
            detected_brands = []
            detected_disclosures = []

            # Check disclosure patterns
            for pattern in self.DISCLOSURE_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    is_sponsored = True
                    detected_disclosures.append(pattern.replace(r"\b", "").replace("#", ""))

            # Check brand-specific partnership tags
            for brand, tags in self.WESTERN_PARTNERSHIP_TAGS.items():
                for tag in tags:
                    if tag in content:
                        detected_brands.append(brand)
                        brand_partnerships[brand] += 1
                        if "team" in tag:
                            is_sponsored = True

            if is_sponsored:
                sponsored_posts.append({
                    "post_id": post_id,
                    "content_preview": content[:150],
                    "brands_detected": list(set(detected_brands)),
                    "disclosures": list(set(detected_disclosures))
                })

            for disclosure in detected_disclosures:
                disclosure_types[disclosure] += 1

        # Calculate sponsorship rate
        sponsorship_rate = len(sponsored_posts) / max(len(posts), 1) * 100

        # Identify likely brand ambassadors
        likely_ambassadors = []
        for brand, count in brand_partnerships.items():
            if count >= 3:  # Multiple posts with same brand
                likely_ambassadors.append({
                    "brand": brand,
                    "post_count": count,
                    "confidence": "high" if count >= 5 else "medium"
                })

        return {
            "total_posts_analyzed": len(posts),
            "sponsored_posts_count": len(sponsored_posts),
            "sponsorship_rate": round(sponsorship_rate, 1),
            "sponsored_posts": sponsored_posts[:20],  # Limit response
            "brand_partnerships": dict(brand_partnerships.most_common(10)),
            "disclosure_types": dict(disclosure_types),
            "likely_brand_ambassadors": likely_ambassadors,
            "is_likely_influencer": len(likely_ambassadors) > 0 or sponsorship_rate > 10
        }

    def analyze_partnership_value(
        self,
        posts: List[Dict],
        follower_count: int
    ) -> Dict[str, Any]:
        """
        Estimate partnership value based on engagement and sponsorship patterns.
        """
        sponsored = self.detect_sponsored_content(posts)

        # Calculate average engagement on sponsored posts
        total_engagement = 0
        for post in posts:
            likes = post.get("likes", 0) or 0
            comments = post.get("comments", 0) or 0
            total_engagement += likes + comments

        avg_engagement = total_engagement / max(len(posts), 1)
        engagement_rate = (avg_engagement / max(follower_count, 1)) * 100

        # Estimate CPM (cost per mille) based on niche
        # Western/rodeo niche commands premium rates
        base_cpm = 15  # $15 base CPM for western niche
        if engagement_rate >= 5:
            cpm_multiplier = 2.0
        elif engagement_rate >= 3:
            cpm_multiplier = 1.5
        elif engagement_rate >= 1:
            cpm_multiplier = 1.0
        else:
            cpm_multiplier = 0.7

        estimated_cpm = base_cpm * cpm_multiplier

        # Estimate post value
        estimated_post_value = (follower_count / 1000) * estimated_cpm

        return {
            "follower_count": follower_count,
            "avg_engagement": round(avg_engagement, 1),
            "engagement_rate": round(engagement_rate, 2),
            "sponsorship_rate": sponsored["sponsorship_rate"],
            "brand_partnerships": sponsored["brand_partnerships"],
            "estimated_cpm": round(estimated_cpm, 2),
            "estimated_post_value": round(estimated_post_value, 2),
            "partnership_tier": self._get_partnership_tier(follower_count, engagement_rate)
        }

    def _get_partnership_tier(self, followers: int, engagement_rate: float) -> str:
        if followers >= 500000 and engagement_rate >= 2:
            return "premium_ambassador"
        elif followers >= 100000 and engagement_rate >= 3:
            return "brand_ambassador"
        elif followers >= 25000 and engagement_rate >= 4:
            return "sponsored_athlete"
        elif followers >= 10000 and engagement_rate >= 5:
            return "micro_influencer"
        else:
            return "affiliate"


class AudiencePersonaBuilder:
    """
    Builds audience personas from follower analysis.
    """

    PERSONA_TEMPLATES = {
        "ranch_hand": {
            "description": "Working cowboy/cowgirl, practical focus",
            "indicators": ["ranch", "cattle", "horse", "work", "dawn", "chores"],
            "brands": ["ariat", "wrangler", "carhartt", "yeti"],
            "age_range": "25-45",
            "income_bracket": "middle"
        },
        "rodeo_competitor": {
            "description": "Active rodeo athlete or enthusiast",
            "indicators": ["rodeo", "roping", "barrel", "bronc", "bull", "compete", "prca", "pbr"],
            "brands": ["classicropes", "cactusropes", "resistol", "cinch"],
            "age_range": "18-35",
            "income_bracket": "varies"
        },
        "western_fashion": {
            "description": "Style-focused western aesthetic",
            "indicators": ["outfit", "style", "fashion", "boots", "hat", "look"],
            "brands": ["lucchese", "tecovas", "txstandard", "doubledranch"],
            "age_range": "22-40",
            "income_bracket": "upper-middle"
        },
        "country_lifestyle": {
            "description": "Rural/country living enthusiast",
            "indicators": ["country", "rural", "farm", "land", "truck", "hunting", "fishing"],
            "brands": ["yeti", "traeger", "carhartt", "filson", "kodiak"],
            "age_range": "30-55",
            "income_bracket": "middle"
        },
        "yellowstone_fan": {
            "description": "Western media/entertainment fan",
            "indicators": ["yellowstone", "1883", "dutton", "rip", "beth", "sheridan"],
            "brands": ["yellowstone", "wrangler", "stetson"],
            "age_range": "35-60",
            "income_bracket": "middle"
        },
        "weekend_cowboy": {
            "description": "Urban professional with western interests",
            "indicators": ["weekend", "concert", "nashville", "country music", "festival"],
            "brands": ["bootbarn", "cavenders", "tecovas"],
            "age_range": "25-45",
            "income_bracket": "upper-middle"
        }
    }

    def build_persona(self, posts: List[Dict], following: List[str], bio: str = "") -> Dict[str, Any]:
        """
        Build an audience persona based on content and behavior.
        """
        persona_scores = Counter()

        all_text = bio.lower() + " "
        for post in posts:
            all_text += post.get("content", "").lower() + " "

        following_lower = {f.lower() for f in following}

        for persona_name, persona_data in self.PERSONA_TEMPLATES.items():
            score = 0

            # Check indicators in content
            for indicator in persona_data["indicators"]:
                count = all_text.count(indicator)
                score += min(count, 5)  # Cap at 5 per indicator

            # Check brands followed
            for brand in persona_data["brands"]:
                if brand in following_lower:
                    score += 3

            persona_scores[persona_name] = score

        # Get primary and secondary personas
        ranked = persona_scores.most_common()
        primary_persona = ranked[0][0] if ranked and ranked[0][1] > 0 else "general_western"
        secondary_persona = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0 else None

        primary_data = self.PERSONA_TEMPLATES.get(primary_persona, {})

        return {
            "primary_persona": primary_persona,
            "primary_description": primary_data.get("description", "General western enthusiast"),
            "secondary_persona": secondary_persona,
            "persona_scores": dict(persona_scores),
            "likely_age_range": primary_data.get("age_range", "unknown"),
            "income_bracket": primary_data.get("income_bracket", "unknown"),
            "recommended_brands": primary_data.get("brands", []),
            "content_indicators": self._extract_top_indicators(all_text)
        }

    def _extract_top_indicators(self, text: str) -> List[str]:
        """Extract most frequent western-related keywords."""
        western_keywords = [
            "rodeo", "cowboy", "western", "ranch", "horse", "boots", "hat",
            "roping", "barrel", "bull", "bronc", "country", "rural",
            "yellowstone", "wrangler", "stetson", "ariat", "nfr", "pbr"
        ]

        found = Counter()
        for kw in western_keywords:
            count = text.count(kw)
            if count > 0:
                found[kw] = count

        return [kw for kw, _ in found.most_common(10)]

    def segment_audience(self, user_profiles: List[Dict]) -> Dict[str, Any]:
        """
        Segment a list of users into persona groups.
        """
        segments = {name: [] for name in self.PERSONA_TEMPLATES.keys()}
        segments["general_western"] = []

        for profile in user_profiles:
            posts = profile.get("posts", [])
            following = profile.get("following", [])
            bio = profile.get("bio", "")
            username = profile.get("username", "unknown")

            persona = self.build_persona(posts, following, bio)
            primary = persona["primary_persona"]

            if primary in segments:
                segments[primary].append(username)
            else:
                segments["general_western"].append(username)

        # Calculate percentages
        total = len(user_profiles)
        distribution = {}
        for segment, users in segments.items():
            distribution[segment] = {
                "count": len(users),
                "percentage": round(len(users) / max(total, 1) * 100, 1),
                "sample_users": users[:10]
            }

        return {
            "total_users": total,
            "segments": distribution,
            "largest_segment": max(segments.keys(), key=lambda k: len(segments[k])) if segments else None
        }

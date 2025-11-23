"""
Comprehensive Western Data Extraction Models
Data point specifications for all scraping targets.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class StockStatus(Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    LOW_STOCK = "low_stock"
    PREORDER = "preorder"
    DISCONTINUED = "discontinued"


class ReviewSentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class FitRating(Enum):
    RUNS_SMALL = "runs_small"
    TRUE_TO_SIZE = "true_to_size"
    RUNS_LARGE = "runs_large"


class PostType(Enum):
    PHOTO = "photo"
    VIDEO = "video"
    CAROUSEL = "carousel"
    REEL = "reel"
    STORY = "story"
    TEXT = "text"
    LINK = "link"


class HorseSex(Enum):
    GELDING = "gelding"
    MARE = "mare"
    STALLION = "stallion"
    COLT = "colt"
    FILLY = "filly"


class ListingCondition(Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


# ============================================================================
# E-COMMERCE DATA MODELS
# ============================================================================

@dataclass
class EcommerceProduct:
    """Complete e-commerce product data extraction."""
    # Core identifiers
    sku: str = ""
    product_name: str = ""
    brand_name: str = ""
    category: str = ""  # boots, jeans, hats, etc.
    subcategory: str = ""

    # Pricing
    current_price: float = 0.0
    original_price: float = 0.0
    discount_percentage: float = 0.0
    sale_start_date: Optional[datetime] = None
    sale_end_date: Optional[datetime] = None
    currency: str = "USD"

    # Inventory
    stock_status: StockStatus = StockStatus.IN_STOCK
    quantity_available: int = 0
    available_sizes: List[str] = field(default_factory=list)
    available_colors: List[str] = field(default_factory=list)

    # Reviews & Ratings
    rating: float = 0.0  # 1-5 stars
    review_count: int = 0
    rating_breakdown: Dict[int, int] = field(default_factory=dict)  # {5: 100, 4: 50, ...}

    # Questions
    question_count: int = 0

    # Media
    product_image_urls: List[str] = field(default_factory=list)
    video_url: str = ""

    # Recommendations
    related_products: List[str] = field(default_factory=list)  # SKUs
    frequently_bought_together: List[str] = field(default_factory=list)

    # Ranking
    sales_rank: int = 0
    popularity_rank: int = 0
    category_rank: int = 0

    # Shipping
    shipping_available: bool = True
    free_shipping: bool = False
    shipping_estimate: str = ""

    # Metadata
    product_url: str = ""
    source: str = ""
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "sku": self.sku,
            "product_name": self.product_name,
            "brand_name": self.brand_name,
            "category": self.category,
            "subcategory": self.subcategory,
            "current_price": self.current_price,
            "original_price": self.original_price,
            "discount_percentage": self.discount_percentage,
            "sale_start_date": self.sale_start_date.isoformat() if self.sale_start_date else None,
            "sale_end_date": self.sale_end_date.isoformat() if self.sale_end_date else None,
            "currency": self.currency,
            "stock_status": self.stock_status.value,
            "quantity_available": self.quantity_available,
            "available_sizes": self.available_sizes,
            "available_colors": self.available_colors,
            "rating": self.rating,
            "review_count": self.review_count,
            "rating_breakdown": self.rating_breakdown,
            "question_count": self.question_count,
            "product_image_urls": self.product_image_urls[:10],
            "video_url": self.video_url,
            "related_products": self.related_products[:10],
            "frequently_bought_together": self.frequently_bought_together[:5],
            "sales_rank": self.sales_rank,
            "popularity_rank": self.popularity_rank,
            "category_rank": self.category_rank,
            "shipping_available": self.shipping_available,
            "free_shipping": self.free_shipping,
            "shipping_estimate": self.shipping_estimate,
            "product_url": self.product_url,
            "source": self.source,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class AmazonProduct(EcommerceProduct):
    """Amazon-specific product data."""
    asin: str = ""
    best_sellers_rank_overall: int = 0
    best_sellers_rank_category: Dict[str, int] = field(default_factory=dict)
    seller_count: int = 0
    prime_eligible: bool = False
    subscribe_save_discount: float = 0.0
    coupon_available: bool = False
    coupon_value: str = ""
    deal_badge: str = ""  # Lightning Deal, Deal of the Day, etc.
    verified_purchase_reviews: int = 0
    non_verified_reviews: int = 0
    review_helpfulness_votes: int = 0
    product_dimensions: str = ""
    product_weight: str = ""
    date_first_available: Optional[datetime] = None
    manufacturer: str = ""

    def to_dict(self) -> Dict:
        base = super().to_dict()
        base.update({
            "asin": self.asin,
            "best_sellers_rank_overall": self.best_sellers_rank_overall,
            "best_sellers_rank_category": self.best_sellers_rank_category,
            "seller_count": self.seller_count,
            "prime_eligible": self.prime_eligible,
            "subscribe_save_discount": self.subscribe_save_discount,
            "coupon_available": self.coupon_available,
            "coupon_value": self.coupon_value,
            "deal_badge": self.deal_badge,
            "verified_purchase_reviews": self.verified_purchase_reviews,
            "non_verified_reviews": self.non_verified_reviews,
            "review_helpfulness_votes": self.review_helpfulness_votes,
            "product_dimensions": self.product_dimensions,
            "product_weight": self.product_weight,
            "date_first_available": self.date_first_available.isoformat() if self.date_first_available else None,
            "manufacturer": self.manufacturer
        })
        return base


@dataclass
class ProductReview:
    """Product review data extraction."""
    product_sku: str = ""
    product_name: str = ""

    # Review content
    review_date: Optional[datetime] = None
    star_rating: float = 0.0
    review_title: str = ""
    review_text: str = ""

    # Reviewer info
    reviewer_name: str = ""
    reviewer_username: str = ""
    reviewer_location: str = ""
    verified_purchase: bool = False

    # Engagement
    helpful_votes: int = 0

    # Product specifics
    size_purchased: str = ""
    color_purchased: str = ""
    fit_rating: Optional[FitRating] = None
    quality_rating: int = 0  # 1-5
    value_rating: int = 0  # 1-5

    # Sentiment analysis
    sentiment: ReviewSentiment = ReviewSentiment.NEUTRAL
    pros_mentioned: List[str] = field(default_factory=list)
    cons_mentioned: List[str] = field(default_factory=list)

    # Media
    has_photo: bool = False
    has_video: bool = False
    media_urls: List[str] = field(default_factory=list)

    # Metadata
    review_url: str = ""
    source: str = ""
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "product_sku": self.product_sku,
            "product_name": self.product_name,
            "review_date": self.review_date.isoformat() if self.review_date else None,
            "star_rating": self.star_rating,
            "review_title": self.review_title,
            "review_text": self.review_text[:2000],
            "reviewer_name": self.reviewer_name,
            "reviewer_username": self.reviewer_username,
            "reviewer_location": self.reviewer_location,
            "verified_purchase": self.verified_purchase,
            "helpful_votes": self.helpful_votes,
            "size_purchased": self.size_purchased,
            "color_purchased": self.color_purchased,
            "fit_rating": self.fit_rating.value if self.fit_rating else None,
            "quality_rating": self.quality_rating,
            "value_rating": self.value_rating,
            "sentiment": self.sentiment.value,
            "pros_mentioned": self.pros_mentioned,
            "cons_mentioned": self.cons_mentioned,
            "has_photo": self.has_photo,
            "has_video": self.has_video,
            "media_urls": self.media_urls[:5],
            "review_url": self.review_url,
            "source": self.source,
            "scraped_at": self.scraped_at.isoformat()
        }


# ============================================================================
# SOCIAL MEDIA - INSTAGRAM
# ============================================================================

@dataclass
class InstagramAccount:
    """Instagram account profile data."""
    username: str = ""
    display_name: str = ""

    # Metrics
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0

    # Profile info
    bio_text: str = ""
    website_link: str = ""
    verification_status: bool = False
    account_category: str = ""  # public figure, brand, etc.
    profile_picture_url: str = ""

    # Engagement metrics
    engagement_rate: float = 0.0
    average_likes: float = 0.0
    average_comments: float = 0.0

    # Content frequency
    posts_per_week: float = 0.0
    story_frequency: float = 0.0
    reel_count: int = 0
    photo_count: int = 0

    # Brand analysis
    sponsored_post_count: int = 0
    brand_mentions: List[str] = field(default_factory=list)
    top_hashtags: List[str] = field(default_factory=list)
    location_tags_frequency: Dict[str, int] = field(default_factory=dict)
    tagged_accounts_frequency: Dict[str, int] = field(default_factory=dict)

    # Metadata
    profile_url: str = ""
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "display_name": self.display_name,
            "follower_count": self.follower_count,
            "following_count": self.following_count,
            "post_count": self.post_count,
            "bio_text": self.bio_text,
            "website_link": self.website_link,
            "verification_status": self.verification_status,
            "account_category": self.account_category,
            "profile_picture_url": self.profile_picture_url,
            "engagement_rate": self.engagement_rate,
            "average_likes": self.average_likes,
            "average_comments": self.average_comments,
            "posts_per_week": self.posts_per_week,
            "story_frequency": self.story_frequency,
            "reel_count": self.reel_count,
            "photo_count": self.photo_count,
            "sponsored_post_count": self.sponsored_post_count,
            "brand_mentions": self.brand_mentions[:20],
            "top_hashtags": self.top_hashtags[:20],
            "location_tags_frequency": dict(list(self.location_tags_frequency.items())[:10]),
            "tagged_accounts_frequency": dict(list(self.tagged_accounts_frequency.items())[:10]),
            "profile_url": self.profile_url,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class InstagramPost:
    """Instagram post/content data."""
    post_url: str = ""
    post_id: str = ""

    # Content
    post_date: Optional[datetime] = None
    caption_text: str = ""
    hashtags: List[str] = field(default_factory=list)

    # Engagement
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    save_count: int = 0

    # Comments analysis
    comment_sentiment: ReviewSentiment = ReviewSentiment.NEUTRAL
    top_comments: List[Dict] = field(default_factory=list)

    # Location & Tags
    location_tagged: str = ""
    accounts_tagged: List[str] = field(default_factory=list)
    product_tags: List[str] = field(default_factory=list)

    # Media
    post_type: PostType = PostType.PHOTO
    video_view_count: int = 0
    media_urls: List[str] = field(default_factory=list)

    # Author
    author_username: str = ""

    # Metadata
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "post_url": self.post_url,
            "post_id": self.post_id,
            "post_date": self.post_date.isoformat() if self.post_date else None,
            "caption_text": self.caption_text[:2000],
            "hashtags": self.hashtags,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "share_count": self.share_count,
            "save_count": self.save_count,
            "comment_sentiment": self.comment_sentiment.value,
            "top_comments": self.top_comments[:10],
            "location_tagged": self.location_tagged,
            "accounts_tagged": self.accounts_tagged,
            "product_tags": self.product_tags,
            "post_type": self.post_type.value,
            "video_view_count": self.video_view_count,
            "media_urls": self.media_urls[:10],
            "author_username": self.author_username,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class InstagramHashtag:
    """Instagram hashtag data."""
    hashtag_name: str = ""
    total_post_count: int = 0

    # Related
    related_hashtags: List[str] = field(default_factory=list)

    # Content
    top_posts: List[Dict] = field(default_factory=list)
    recent_posts: List[Dict] = field(default_factory=list)

    # Engagement
    average_engagement_rate: float = 0.0

    # Geographic
    geographic_distribution: Dict[str, int] = field(default_factory=dict)

    # Trending
    trending_score: float = 0.0
    posts_last_hour: int = 0
    posts_last_day: int = 0

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "hashtag_name": self.hashtag_name,
            "total_post_count": self.total_post_count,
            "related_hashtags": self.related_hashtags[:20],
            "top_posts": self.top_posts[:10],
            "recent_posts": self.recent_posts[:10],
            "average_engagement_rate": self.average_engagement_rate,
            "geographic_distribution": dict(list(self.geographic_distribution.items())[:10]),
            "trending_score": self.trending_score,
            "posts_last_hour": self.posts_last_hour,
            "posts_last_day": self.posts_last_day,
            "scraped_at": self.scraped_at.isoformat()
        }


# ============================================================================
# SOCIAL MEDIA - FACEBOOK
# ============================================================================

@dataclass
class FacebookGroup:
    """Facebook group data."""
    group_name: str = ""
    group_url: str = ""
    group_id: str = ""

    # Size
    member_count: int = 0
    active_member_percentage: float = 0.0

    # Activity
    posts_per_day: float = 0.0
    comments_per_post_avg: float = 0.0

    # Leadership
    admin_names: List[str] = field(default_factory=list)
    moderator_names: List[str] = field(default_factory=list)

    # Settings
    group_rules: str = ""
    group_description: str = ""
    is_private: bool = False

    # Top contributors
    most_active_posters: List[Dict] = field(default_factory=list)

    # Content analysis
    common_topics: List[str] = field(default_factory=list)
    buy_sell_post_frequency: float = 0.0
    price_ranges: Dict[str, float] = field(default_factory=dict)  # {"min": 0, "max": 0, "avg": 0}

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "group_name": self.group_name,
            "group_url": self.group_url,
            "group_id": self.group_id,
            "member_count": self.member_count,
            "active_member_percentage": self.active_member_percentage,
            "posts_per_day": self.posts_per_day,
            "comments_per_post_avg": self.comments_per_post_avg,
            "admin_names": self.admin_names,
            "moderator_names": self.moderator_names,
            "group_rules": self.group_rules[:1000],
            "group_description": self.group_description[:1000],
            "is_private": self.is_private,
            "most_active_posters": self.most_active_posters[:10],
            "common_topics": self.common_topics[:20],
            "buy_sell_post_frequency": self.buy_sell_post_frequency,
            "price_ranges": self.price_ranges,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class FacebookPost:
    """Facebook post data."""
    post_id: str = ""
    post_url: str = ""

    # Content
    post_text: str = ""
    post_date: Optional[datetime] = None
    post_type: PostType = PostType.TEXT
    link_url: str = ""

    # Reactions
    reaction_count: int = 0
    reactions_by_type: Dict[str, int] = field(default_factory=dict)  # {"like": 10, "love": 5, ...}

    # Engagement
    comment_count: int = 0
    share_count: int = 0

    # Comments
    comments: List[Dict] = field(default_factory=list)
    comment_sentiment: ReviewSentiment = ReviewSentiment.NEUTRAL

    # Author
    author_name: str = ""
    author_id: str = ""

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "post_id": self.post_id,
            "post_url": self.post_url,
            "post_text": self.post_text[:2000],
            "post_date": self.post_date.isoformat() if self.post_date else None,
            "post_type": self.post_type.value,
            "link_url": self.link_url,
            "reaction_count": self.reaction_count,
            "reactions_by_type": self.reactions_by_type,
            "comment_count": self.comment_count,
            "share_count": self.share_count,
            "comments": self.comments[:20],
            "comment_sentiment": self.comment_sentiment.value,
            "author_name": self.author_name,
            "author_id": self.author_id,
            "scraped_at": self.scraped_at.isoformat()
        }


# ============================================================================
# SOCIAL MEDIA - YOUTUBE
# ============================================================================

@dataclass
class YouTubeChannel:
    """YouTube channel data."""
    channel_name: str = ""
    channel_id: str = ""
    channel_url: str = ""

    # Metrics
    subscriber_count: int = 0
    total_video_count: int = 0
    total_view_count: int = 0

    # Profile
    channel_description: str = ""
    channel_created_date: Optional[datetime] = None
    verification_status: bool = False

    # Activity
    upload_frequency: float = 0.0  # videos per week

    # Engagement averages
    avg_views_per_video: float = 0.0
    avg_likes_per_video: float = 0.0
    avg_comments_per_video: float = 0.0

    # Monetization
    has_merchandise_shelf: bool = False
    sponsor_count: int = 0

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "channel_name": self.channel_name,
            "channel_id": self.channel_id,
            "channel_url": self.channel_url,
            "subscriber_count": self.subscriber_count,
            "total_video_count": self.total_video_count,
            "total_view_count": self.total_view_count,
            "channel_description": self.channel_description[:1000],
            "channel_created_date": self.channel_created_date.isoformat() if self.channel_created_date else None,
            "verification_status": self.verification_status,
            "upload_frequency": self.upload_frequency,
            "avg_views_per_video": self.avg_views_per_video,
            "avg_likes_per_video": self.avg_likes_per_video,
            "avg_comments_per_video": self.avg_comments_per_video,
            "has_merchandise_shelf": self.has_merchandise_shelf,
            "sponsor_count": self.sponsor_count,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class YouTubeVideo:
    """YouTube video data."""
    video_id: str = ""
    video_url: str = ""

    # Content
    video_title: str = ""
    upload_date: Optional[datetime] = None
    video_description: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = ""

    # Metrics
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0

    # Technical
    video_length_seconds: int = 0
    thumbnail_url: str = ""

    # Engagement
    engagement_rate: float = 0.0

    # Comments
    comments: List[Dict] = field(default_factory=list)
    comment_sentiment: ReviewSentiment = ReviewSentiment.NEUTRAL
    top_comments: List[Dict] = field(default_factory=list)
    pinned_comment: str = ""

    # Links & sponsors
    links_in_description: List[str] = field(default_factory=list)
    sponsor_mentions: List[str] = field(default_factory=list)
    product_mentions: List[str] = field(default_factory=list)

    # Channel
    channel_name: str = ""
    channel_id: str = ""

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "video_id": self.video_id,
            "video_url": self.video_url,
            "video_title": self.video_title,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "video_description": self.video_description[:2000],
            "tags": self.tags[:30],
            "category": self.category,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "dislike_count": self.dislike_count,
            "comment_count": self.comment_count,
            "video_length_seconds": self.video_length_seconds,
            "thumbnail_url": self.thumbnail_url,
            "engagement_rate": self.engagement_rate,
            "comments": self.comments[:20],
            "comment_sentiment": self.comment_sentiment.value,
            "top_comments": self.top_comments[:10],
            "pinned_comment": self.pinned_comment[:500],
            "links_in_description": self.links_in_description[:20],
            "sponsor_mentions": self.sponsor_mentions,
            "product_mentions": self.product_mentions,
            "channel_name": self.channel_name,
            "channel_id": self.channel_id,
            "scraped_at": self.scraped_at.isoformat()
        }


# ============================================================================
# SOCIAL MEDIA - TIKTOK
# ============================================================================

@dataclass
class TikTokAccount:
    """TikTok account data."""
    username: str = ""
    display_name: str = ""

    # Metrics
    follower_count: int = 0
    following_count: int = 0
    total_likes_received: int = 0
    video_count: int = 0

    # Profile
    bio_text: str = ""
    profile_picture_url: str = ""
    verification_status: bool = False

    # Engagement averages
    avg_views_per_video: float = 0.0
    avg_likes_per_video: float = 0.0
    avg_comments_per_video: float = 0.0
    avg_shares_per_video: float = 0.0

    # Activity
    posting_frequency: float = 0.0  # videos per week

    profile_url: str = ""
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "display_name": self.display_name,
            "follower_count": self.follower_count,
            "following_count": self.following_count,
            "total_likes_received": self.total_likes_received,
            "video_count": self.video_count,
            "bio_text": self.bio_text,
            "profile_picture_url": self.profile_picture_url,
            "verification_status": self.verification_status,
            "avg_views_per_video": self.avg_views_per_video,
            "avg_likes_per_video": self.avg_likes_per_video,
            "avg_comments_per_video": self.avg_comments_per_video,
            "avg_shares_per_video": self.avg_shares_per_video,
            "posting_frequency": self.posting_frequency,
            "profile_url": self.profile_url,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class TikTokVideo:
    """TikTok video data."""
    video_url: str = ""
    video_id: str = ""

    # Content
    post_date: Optional[datetime] = None
    caption: str = ""
    hashtags: List[str] = field(default_factory=list)
    sound_name: str = ""
    sound_author: str = ""

    # Metrics
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    save_count: int = 0

    # Technical
    video_length_seconds: int = 0

    # Features
    is_duet: bool = False
    is_stitch: bool = False
    original_video_url: str = ""

    # Author
    author_username: str = ""

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "video_url": self.video_url,
            "video_id": self.video_id,
            "post_date": self.post_date.isoformat() if self.post_date else None,
            "caption": self.caption[:1000],
            "hashtags": self.hashtags,
            "sound_name": self.sound_name,
            "sound_author": self.sound_author,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "share_count": self.share_count,
            "save_count": self.save_count,
            "video_length_seconds": self.video_length_seconds,
            "is_duet": self.is_duet,
            "is_stitch": self.is_stitch,
            "original_video_url": self.original_video_url,
            "author_username": self.author_username,
            "scraped_at": self.scraped_at.isoformat()
        }


# ============================================================================
# COMPETITION DATA - NCHA/NRCHA
# ============================================================================

@dataclass
class CompetitionResult:
    """NCHA/NRCHA competition result data."""
    # Event info
    event_name: str = ""
    event_date: Optional[datetime] = None
    event_location: str = ""
    event_venue: str = ""

    # Participant info
    rider_name: str = ""
    horse_name: str = ""
    horse_age: int = 0
    owner_name: str = ""
    trainer_name: str = ""

    # Scoring
    score: float = 0.0
    place: int = 0
    prize_money: float = 0.0

    # Judge details
    judge_names: List[str] = field(default_factory=list)
    judge_scores: List[float] = field(default_factory=list)

    # Run info
    draw_position: int = 0
    set_number: int = 0
    go_round: int = 1

    # Class info
    class_division: str = ""
    entry_fee: float = 0.0
    total_entries: int = 0

    # Other
    weather_conditions: str = ""
    cattle_contractor: str = ""

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "event_name": self.event_name,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "event_location": self.event_location,
            "event_venue": self.event_venue,
            "rider_name": self.rider_name,
            "horse_name": self.horse_name,
            "horse_age": self.horse_age,
            "owner_name": self.owner_name,
            "trainer_name": self.trainer_name,
            "score": self.score,
            "place": self.place,
            "prize_money": self.prize_money,
            "judge_names": self.judge_names,
            "judge_scores": self.judge_scores,
            "draw_position": self.draw_position,
            "set_number": self.set_number,
            "go_round": self.go_round,
            "class_division": self.class_division,
            "entry_fee": self.entry_fee,
            "total_entries": self.total_entries,
            "weather_conditions": self.weather_conditions,
            "cattle_contractor": self.cattle_contractor,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class CompetitionEntry:
    """NCHA/NRCHA entry list data."""
    # Event info
    event_name: str = ""
    entry_deadline: Optional[datetime] = None

    # Counts
    total_entry_count: int = 0
    entries_by_class: Dict[str, int] = field(default_factory=dict)

    # Entry details
    horse_name: str = ""
    rider_name: str = ""
    owner_name: str = ""
    trainer_name: str = ""
    entry_number: int = 0
    draw_position: int = 0
    set_assignment: int = 0
    ride_datetime: Optional[datetime] = None

    # Horse info
    horse_sire: str = ""
    horse_dam: str = ""
    horse_age: int = 0

    # Earnings
    horse_previous_earnings: float = 0.0
    rider_current_year_earnings: float = 0.0

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "event_name": self.event_name,
            "entry_deadline": self.entry_deadline.isoformat() if self.entry_deadline else None,
            "total_entry_count": self.total_entry_count,
            "entries_by_class": self.entries_by_class,
            "horse_name": self.horse_name,
            "rider_name": self.rider_name,
            "owner_name": self.owner_name,
            "trainer_name": self.trainer_name,
            "entry_number": self.entry_number,
            "draw_position": self.draw_position,
            "set_assignment": self.set_assignment,
            "ride_datetime": self.ride_datetime.isoformat() if self.ride_datetime else None,
            "horse_sire": self.horse_sire,
            "horse_dam": self.horse_dam,
            "horse_age": self.horse_age,
            "horse_previous_earnings": self.horse_previous_earnings,
            "rider_current_year_earnings": self.rider_current_year_earnings,
            "scraped_at": self.scraped_at.isoformat()
        }


# ============================================================================
# HORSE DATA
# ============================================================================

@dataclass
class HorseSaleResult:
    """Horse sale result data."""
    # Sale info
    sale_name: str = ""
    sale_date: Optional[datetime] = None
    lot_number: int = 0

    # Horse info
    horse_name: str = ""
    horse_age: int = 0
    horse_sex: HorseSex = HorseSex.GELDING
    horse_color: str = ""

    # Pedigree
    sire_name: str = ""
    dam_name: str = ""

    # Sale details
    consignor_name: str = ""
    buyer_name: str = ""
    sale_price: float = 0.0
    reserve_met: bool = True
    passed: bool = False

    # Bidding
    bidder_count: int = 0
    opening_bid: float = 0.0
    bid_increments: List[float] = field(default_factory=list)

    # Media
    has_video: bool = False
    video_url: str = ""

    # Performance
    performance_record: str = ""
    lifetime_earnings: float = 0.0

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "sale_name": self.sale_name,
            "sale_date": self.sale_date.isoformat() if self.sale_date else None,
            "lot_number": self.lot_number,
            "horse_name": self.horse_name,
            "horse_age": self.horse_age,
            "horse_sex": self.horse_sex.value,
            "horse_color": self.horse_color,
            "sire_name": self.sire_name,
            "dam_name": self.dam_name,
            "consignor_name": self.consignor_name,
            "buyer_name": self.buyer_name,
            "sale_price": self.sale_price,
            "reserve_met": self.reserve_met,
            "passed": self.passed,
            "bidder_count": self.bidder_count,
            "opening_bid": self.opening_bid,
            "bid_increments": self.bid_increments,
            "has_video": self.has_video,
            "video_url": self.video_url,
            "performance_record": self.performance_record,
            "lifetime_earnings": self.lifetime_earnings,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class HorsePedigree:
    """Horse pedigree data."""
    # Horse info
    horse_name: str = ""
    registration_number: str = ""
    date_of_birth: Optional[datetime] = None
    color: str = ""
    sex: HorseSex = HorseSex.GELDING

    # Immediate parents
    sire_name: str = ""
    dam_name: str = ""

    # Extended pedigree (5+ generations)
    sire_of_sire: str = ""
    dam_of_sire: str = ""
    sire_of_dam: str = ""
    dam_of_dam: str = ""
    full_pedigree: Dict[str, str] = field(default_factory=dict)  # Generational tree

    # Offspring
    offspring_count: int = 0
    offspring_names: List[str] = field(default_factory=list)
    offspring_earnings: float = 0.0

    # Performance
    lifetime_earnings: float = 0.0
    performance_records: List[Dict] = field(default_factory=list)
    show_records: List[Dict] = field(default_factory=list)

    # Status
    registration_status: str = ""
    breeding_status: str = ""  # alive/deceased

    # History
    owner_history: List[Dict] = field(default_factory=list)

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "horse_name": self.horse_name,
            "registration_number": self.registration_number,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "color": self.color,
            "sex": self.sex.value,
            "sire_name": self.sire_name,
            "dam_name": self.dam_name,
            "sire_of_sire": self.sire_of_sire,
            "dam_of_sire": self.dam_of_sire,
            "sire_of_dam": self.sire_of_dam,
            "dam_of_dam": self.dam_of_dam,
            "full_pedigree": self.full_pedigree,
            "offspring_count": self.offspring_count,
            "offspring_names": self.offspring_names[:50],
            "offspring_earnings": self.offspring_earnings,
            "lifetime_earnings": self.lifetime_earnings,
            "performance_records": self.performance_records[:20],
            "show_records": self.show_records[:20],
            "registration_status": self.registration_status,
            "breeding_status": self.breeding_status,
            "owner_history": self.owner_history[:10],
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class StallionDirectory:
    """Stallion directory entry data."""
    # Horse info
    stallion_name: str = ""
    registration_number: str = ""
    color: str = ""
    height: str = ""
    foaling_date: Optional[datetime] = None

    # Pedigree
    sire_name: str = ""
    dam_name: str = ""

    # Breeding info
    stud_fee: float = 0.0
    breeding_terms: str = ""  # live cover/AI
    shipped_semen: bool = False
    breeding_seasons: List[str] = field(default_factory=list)
    mare_care_fees: float = 0.0
    breeding_contract_terms: str = ""

    # Location
    standing_location: str = ""
    city: str = ""
    state: str = ""

    # Contact
    owner_name: str = ""
    farm_name: str = ""
    contact_info: str = ""

    # Performance
    lifetime_earnings: float = 0.0
    offspring_earnings: float = 0.0
    major_wins: List[str] = field(default_factory=list)

    # Notes
    temperament_notes: str = ""

    # Media
    video_url: str = ""
    photo_urls: List[str] = field(default_factory=list)

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "stallion_name": self.stallion_name,
            "registration_number": self.registration_number,
            "color": self.color,
            "height": self.height,
            "foaling_date": self.foaling_date.isoformat() if self.foaling_date else None,
            "sire_name": self.sire_name,
            "dam_name": self.dam_name,
            "stud_fee": self.stud_fee,
            "breeding_terms": self.breeding_terms,
            "shipped_semen": self.shipped_semen,
            "breeding_seasons": self.breeding_seasons,
            "mare_care_fees": self.mare_care_fees,
            "breeding_contract_terms": self.breeding_contract_terms[:500],
            "standing_location": self.standing_location,
            "city": self.city,
            "state": self.state,
            "owner_name": self.owner_name,
            "farm_name": self.farm_name,
            "contact_info": self.contact_info,
            "lifetime_earnings": self.lifetime_earnings,
            "offspring_earnings": self.offspring_earnings,
            "major_wins": self.major_wins[:10],
            "temperament_notes": self.temperament_notes[:500],
            "video_url": self.video_url,
            "photo_urls": self.photo_urls[:10],
            "scraped_at": self.scraped_at.isoformat()
        }


# ============================================================================
# CONTENT DATA - NEWS, PODCASTS, FORUMS
# ============================================================================

@dataclass
class WesternNewsArticle:
    """Western news article data."""
    article_url: str = ""

    # Source
    publication_name: str = ""

    # Content
    article_title: str = ""
    publish_date: Optional[datetime] = None
    author_name: str = ""
    article_text: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)

    # Engagement
    social_shares: int = 0
    comment_count: int = 0

    # Media
    images: List[str] = field(default_factory=list)
    embedded_videos: List[str] = field(default_factory=list)
    related_articles: List[str] = field(default_factory=list)

    # Entities mentioned
    mentioned_people: List[str] = field(default_factory=list)
    mentioned_brands: List[str] = field(default_factory=list)
    mentioned_events: List[str] = field(default_factory=list)

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "article_url": self.article_url,
            "publication_name": self.publication_name,
            "article_title": self.article_title,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "author_name": self.author_name,
            "article_text": self.article_text[:5000],
            "category": self.category,
            "tags": self.tags[:20],
            "social_shares": self.social_shares,
            "comment_count": self.comment_count,
            "images": self.images[:10],
            "embedded_videos": self.embedded_videos[:5],
            "related_articles": self.related_articles[:10],
            "mentioned_people": self.mentioned_people[:20],
            "mentioned_brands": self.mentioned_brands[:20],
            "mentioned_events": self.mentioned_events[:10],
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class PodcastEpisode:
    """Podcast episode data."""
    # Podcast info
    podcast_name: str = ""
    episode_number: int = 0
    episode_title: str = ""

    # Content
    publish_date: Optional[datetime] = None
    duration_seconds: int = 0
    description: str = ""
    transcript: str = ""

    # Guests
    guest_names: List[str] = field(default_factory=list)
    host_names: List[str] = field(default_factory=list)

    # Engagement
    listen_count: int = 0
    rating: float = 0.0
    rating_count: int = 0

    # Content analysis
    sponsor_mentions: List[str] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)

    # Charts
    apple_podcasts_rank: int = 0

    episode_url: str = ""
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "podcast_name": self.podcast_name,
            "episode_number": self.episode_number,
            "episode_title": self.episode_title,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "duration_seconds": self.duration_seconds,
            "description": self.description[:2000],
            "transcript": self.transcript[:10000],
            "guest_names": self.guest_names,
            "host_names": self.host_names,
            "listen_count": self.listen_count,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "sponsor_mentions": self.sponsor_mentions,
            "topics_discussed": self.topics_discussed[:20],
            "apple_podcasts_rank": self.apple_podcasts_rank,
            "episode_url": self.episode_url,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class ForumPost:
    """Forum/community post data."""
    # Forum info
    forum_name: str = ""

    # Thread info
    thread_title: str = ""
    thread_url: str = ""
    thread_status: str = ""  # active/locked/pinned
    thread_tags: List[str] = field(default_factory=list)

    # Post content
    post_datetime: Optional[datetime] = None
    post_text: str = ""

    # Author info
    poster_username: str = ""
    poster_join_date: Optional[datetime] = None
    poster_post_count: int = 0

    # Engagement
    reply_count: int = 0
    view_count: int = 0
    like_count: int = 0

    # Quoted posts
    quoted_posts: List[str] = field(default_factory=list)

    # Media
    embedded_images: List[str] = field(default_factory=list)
    embedded_videos: List[str] = field(default_factory=list)

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "forum_name": self.forum_name,
            "thread_title": self.thread_title,
            "thread_url": self.thread_url,
            "thread_status": self.thread_status,
            "thread_tags": self.thread_tags[:10],
            "post_datetime": self.post_datetime.isoformat() if self.post_datetime else None,
            "post_text": self.post_text[:5000],
            "poster_username": self.poster_username,
            "poster_join_date": self.poster_join_date.isoformat() if self.poster_join_date else None,
            "poster_post_count": self.poster_post_count,
            "reply_count": self.reply_count,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "quoted_posts": self.quoted_posts[:5],
            "embedded_images": self.embedded_images[:10],
            "embedded_videos": self.embedded_videos[:5],
            "scraped_at": self.scraped_at.isoformat()
        }


# ============================================================================
# EVENT & MARKETPLACE DATA
# ============================================================================

@dataclass
class EventCalendar:
    """Event calendar entry data."""
    # Event info
    event_name: str = ""
    event_dates: List[datetime] = field(default_factory=list)
    event_location: str = ""
    venue_name: str = ""
    city: str = ""
    state: str = ""

    # Event type
    event_type: str = ""  # cutting, reining, all-around
    sanctioning_org: str = ""

    # Registration
    entry_deadline: Optional[datetime] = None
    entry_fees: Dict[str, float] = field(default_factory=dict)  # by class

    # Prize money
    total_prize_money: float = 0.0
    prize_money_by_class: Dict[str, float] = field(default_factory=dict)
    added_money: float = 0.0

    # Staff
    judge_names: List[str] = field(default_factory=list)
    event_producer: str = ""
    event_contact: str = ""

    # Additional info
    venue_website: str = ""
    entry_count: int = 0
    past_year_attendance: int = 0
    sponsor_names: List[str] = field(default_factory=list)

    event_url: str = ""
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "event_name": self.event_name,
            "event_dates": [d.isoformat() for d in self.event_dates] if self.event_dates else [],
            "event_location": self.event_location,
            "venue_name": self.venue_name,
            "city": self.city,
            "state": self.state,
            "event_type": self.event_type,
            "sanctioning_org": self.sanctioning_org,
            "entry_deadline": self.entry_deadline.isoformat() if self.entry_deadline else None,
            "entry_fees": self.entry_fees,
            "total_prize_money": self.total_prize_money,
            "prize_money_by_class": self.prize_money_by_class,
            "added_money": self.added_money,
            "judge_names": self.judge_names,
            "event_producer": self.event_producer,
            "event_contact": self.event_contact,
            "venue_website": self.venue_website,
            "entry_count": self.entry_count,
            "past_year_attendance": self.past_year_attendance,
            "sponsor_names": self.sponsor_names[:20],
            "event_url": self.event_url,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class MarketplaceListing:
    """Resale marketplace listing (eBay, Poshmark, Mercari)."""
    # Listing info
    listing_title: str = ""
    listing_url: str = ""
    listing_id: str = ""

    # Pricing
    current_price: float = 0.0
    original_retail_price: float = 0.0

    # Item details
    condition: ListingCondition = ListingCondition.NEW
    brand: str = ""
    size: str = ""
    color: str = ""
    description: str = ""

    # Engagement
    view_count: int = 0
    watcher_count: int = 0
    bid_count: int = 0

    # Dates
    listing_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Seller
    seller_username: str = ""
    seller_rating: float = 0.0
    seller_location: str = ""

    # Shipping
    shipping_cost: float = 0.0
    return_policy: str = ""

    # Media
    photo_count: int = 0
    photo_urls: List[str] = field(default_factory=list)

    # Sale status
    is_sold: bool = False
    sold_date: Optional[datetime] = None
    final_sale_price: float = 0.0

    source: str = ""  # ebay, poshmark, mercari
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "listing_title": self.listing_title,
            "listing_url": self.listing_url,
            "listing_id": self.listing_id,
            "current_price": self.current_price,
            "original_retail_price": self.original_retail_price,
            "condition": self.condition.value,
            "brand": self.brand,
            "size": self.size,
            "color": self.color,
            "description": self.description[:2000],
            "view_count": self.view_count,
            "watcher_count": self.watcher_count,
            "bid_count": self.bid_count,
            "listing_date": self.listing_date.isoformat() if self.listing_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "seller_username": self.seller_username,
            "seller_rating": self.seller_rating,
            "seller_location": self.seller_location,
            "shipping_cost": self.shipping_cost,
            "return_policy": self.return_policy,
            "photo_count": self.photo_count,
            "photo_urls": self.photo_urls[:10],
            "is_sold": self.is_sold,
            "sold_date": self.sold_date.isoformat() if self.sold_date else None,
            "final_sale_price": self.final_sale_price,
            "source": self.source,
            "scraped_at": self.scraped_at.isoformat()
        }


# ============================================================================
# GEOGRAPHIC & TIME-SERIES DATA
# ============================================================================

@dataclass
class GeographicData:
    """Geographic/regional data point."""
    # Location
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = "USA"
    latitude: float = 0.0
    longitude: float = 0.0

    # Context
    location_type: str = ""  # store, venue, buyer, seller

    # Regional data
    regional_price_variation: float = 0.0  # vs national average
    state_association_memberships: List[str] = field(default_factory=list)

    # Source
    source_type: str = ""
    source_id: str = ""

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_type": self.location_type,
            "regional_price_variation": self.regional_price_variation,
            "state_association_memberships": self.state_association_memberships,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class TimeSeriesData:
    """Time-series tracking data point."""
    # Entity being tracked
    entity_type: str = ""  # product, account, hashtag
    entity_id: str = ""
    entity_name: str = ""

    # Timestamp
    recorded_at: datetime = field(default_factory=datetime.utcnow)

    # Price tracking
    price_snapshot: float = 0.0

    # Stock tracking
    stock_status: StockStatus = StockStatus.IN_STOCK
    quantity_available: int = 0

    # Sales tracking
    sales_velocity: float = 0.0  # units per day

    # Engagement tracking
    follower_count: int = 0
    engagement_rate: float = 0.0

    # Review tracking
    review_count: int = 0
    average_rating: float = 0.0
    review_velocity: float = 0.0  # reviews per day

    # Seasonal/trend flags
    is_trending: bool = False
    seasonal_adjustment: float = 0.0

    # Year-over-year
    yoy_growth: float = 0.0

    # Product lifecycle
    is_new_launch: bool = False
    is_discontinued: bool = False
    launch_date: Optional[datetime] = None
    discontinuation_date: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "recorded_at": self.recorded_at.isoformat(),
            "price_snapshot": self.price_snapshot,
            "stock_status": self.stock_status.value,
            "quantity_available": self.quantity_available,
            "sales_velocity": self.sales_velocity,
            "follower_count": self.follower_count,
            "engagement_rate": self.engagement_rate,
            "review_count": self.review_count,
            "average_rating": self.average_rating,
            "review_velocity": self.review_velocity,
            "is_trending": self.is_trending,
            "seasonal_adjustment": self.seasonal_adjustment,
            "yoy_growth": self.yoy_growth,
            "is_new_launch": self.is_new_launch,
            "is_discontinued": self.is_discontinued,
            "launch_date": self.launch_date.isoformat() if self.launch_date else None,
            "discontinuation_date": self.discontinuation_date.isoformat() if self.discontinuation_date else None
        }


# ============================================================================
# MODEL REGISTRY
# ============================================================================

MODEL_REGISTRY = {
    # E-Commerce
    "ecommerce_product": EcommerceProduct,
    "amazon_product": AmazonProduct,
    "product_review": ProductReview,

    # Instagram
    "instagram_account": InstagramAccount,
    "instagram_post": InstagramPost,
    "instagram_hashtag": InstagramHashtag,

    # Facebook
    "facebook_group": FacebookGroup,
    "facebook_post": FacebookPost,

    # YouTube
    "youtube_channel": YouTubeChannel,
    "youtube_video": YouTubeVideo,

    # TikTok
    "tiktok_account": TikTokAccount,
    "tiktok_video": TikTokVideo,

    # Competition
    "competition_result": CompetitionResult,
    "competition_entry": CompetitionEntry,

    # Horse Data
    "horse_sale_result": HorseSaleResult,
    "horse_pedigree": HorsePedigree,
    "stallion_directory": StallionDirectory,

    # Content
    "western_news_article": WesternNewsArticle,
    "podcast_episode": PodcastEpisode,
    "forum_post": ForumPost,

    # Events & Marketplace
    "event_calendar": EventCalendar,
    "marketplace_listing": MarketplaceListing,

    # Tracking
    "geographic_data": GeographicData,
    "time_series_data": TimeSeriesData
}


def get_model_fields(model_name: str) -> List[str]:
    """Get list of fields for a model."""
    model_class = MODEL_REGISTRY.get(model_name)
    if model_class:
        return list(model_class.__dataclass_fields__.keys())
    return []


def get_all_models() -> Dict[str, List[str]]:
    """Get all models and their fields."""
    return {name: get_model_fields(name) for name in MODEL_REGISTRY.keys()}


def get_model_summary() -> Dict[str, int]:
    """Get summary of all models and field counts."""
    return {name: len(get_model_fields(name)) for name in MODEL_REGISTRY.keys()}

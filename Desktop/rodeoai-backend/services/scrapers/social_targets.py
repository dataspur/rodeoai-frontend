"""
Western/Cutting Horse Social Media Scraping Targets
Comprehensive list of accounts, hashtags, and groups to monitor.
"""

# Instagram Accounts - Cutting Horse Industry
INSTAGRAM_CUTTING_ACCOUNTS = {
    # Official Organizations
    "organizations": [
        "nchacutting",
        "nrcha_reined_cow_horse",
        "aqha",
        "pccha_cutting",
        "wrcha_cutting"
    ],

    # Top Trainers
    "trainers": [
        "lloydcox_cuttinghorses",
        "beau_galyean",
        "wesleyparamore",
        "grant_setnicka",
        "todd_bergen",
        "matt_gaines_cutting",
        "austin_shepard",
        "adan_banuelos",
        "morgan_cromer",
        "clint_allen_cutting",
        "geoffrey_sheehan",
        "tatum_rice",
        "james_payne_cutting"
    ],

    # Ranches & Breeding Programs
    "ranches": [
        "6666ranch",
        "fourcornerranch",
        "cattellacranch",
        "bitterwater_ranch",
        "rafter_w_ranch",
        "shiningsparranch",
        "wrightscuttinghorses",
        "oakcreekranch",
        "bellranch",
        "silverstatecutting"
    ],

    # Stallion Promotions
    "stallions": [
        "metallicat",
        "dual_rey",
        "reyzin_the_cash",
        "smooth_talkin_style",
        "kit_kat_sugar",
        "hottish",
        "once_in_a_blu_boon"
    ],

    # Industry Media
    "media": [
        "cuttinghorsecentral",
        "quarterhorsenews",
        "westernhorseman",
        "chronicleofthehorse"
    ]
}

# Instagram Hashtags - Cutting Horses
INSTAGRAM_CUTTING_HASHTAGS = [
    # Primary hashtags
    "#ncha",
    "#cuttinghorse",
    "#cuttinghorses",
    "#cuttinghorsetraining",
    "#nchafuturity",
    "#futurity",

    # Events
    "#nchafuturity",
    "#superstakes",
    "#westernnationals",
    "#summerspectacular",

    # Training/Lifestyle
    "#cuttinghorsetraining",
    "#cowhorsetraining",
    "#ranchhorse",
    "#workingcowhorse",

    # Related disciplines
    "#nrcha",
    "#reinedcowhorse",
    "#cowhorse",

    # Breeding
    "#cuttinghorsesire",
    "#quarterhorse",
    "#aqha",

    # Lifestyle
    "#cowboylife",
    "#ranchlife",
    "#westernlifestyle"
]

# Facebook Groups - Cutting Horses
FACEBOOK_CUTTING_GROUPS = [
    {
        "name": "Cutting Horses For Sale",
        "url": "https://www.facebook.com/groups/cuttinghorsesforsale",
        "type": "marketplace"
    },
    {
        "name": "NCHA Horses For Sale",
        "url": "https://www.facebook.com/groups/nchahorsesforsale",
        "type": "marketplace"
    },
    {
        "name": "Performance Horses For Sale",
        "url": "https://www.facebook.com/groups/performancehorsesforsale",
        "type": "marketplace"
    },
    {
        "name": "Cutting Horse Talk",
        "url": "https://www.facebook.com/groups/cuttinghorsetalk",
        "type": "discussion"
    },
    {
        "name": "Cutting Horse Owners",
        "url": "https://www.facebook.com/groups/cuttinghorseowners",
        "type": "discussion"
    },
    {
        "name": "NCHA Cutting",
        "url": "https://www.facebook.com/groups/nchacutting",
        "type": "official"
    },
    {
        "name": "Cutting Horse Breeders",
        "url": "https://www.facebook.com/groups/cuttinghorsebreeders",
        "type": "breeding"
    },
    {
        "name": "Ranch Horse Versatility",
        "url": "https://www.facebook.com/groups/ranchhorseversatility",
        "type": "discussion"
    }
]

# Facebook Pages - Official
FACEBOOK_CUTTING_PAGES = [
    "NCHACutting",
    "NRCHAOfficial",
    "AQHAOfficial",
    "QuarterHorseNews",
    "WesternHorseman"
]

# YouTube Channels - Cutting Horse Content
YOUTUBE_CUTTING_CHANNELS = [
    {
        "name": "NCHA Futurity",
        "channel_id": "nchafuturity",
        "type": "official"
    },
    {
        "name": "Cutting Horse Training Online",
        "channel_id": "cuttinghorsetrainingonline",
        "type": "educational"
    },
    {
        "name": "Quarter Horse News",
        "channel_id": "quarterhorsenews",
        "type": "media"
    },
    {
        "name": "Western Horseman",
        "channel_id": "westernhorseman",
        "type": "media"
    },
    {
        "name": "Lloyd Cox Cutting Horses",
        "channel_id": "lloydcoxcuttinghorses",
        "type": "trainer"
    }
]

# Twitter/X Accounts - Cutting Horse
TWITTER_CUTTING_ACCOUNTS = [
    "NCHACutting",
    "NRCHA",
    "AQHA",
    "QuarterHorseNews",
    "WesternHorseman"
]

# Western News/Media Sources
WESTERN_NEWS_SOURCES = [
    {
        "name": "Quarter Horse News",
        "url": "https://www.quarterhorsenews.com",
        "rss": "https://www.quarterhorsenews.com/feed",
        "categories": ["cutting", "reining", "breeding", "sales"]
    },
    {
        "name": "Western Horseman",
        "url": "https://www.westernhorseman.com",
        "rss": "https://www.westernhorseman.com/feed",
        "categories": ["lifestyle", "training", "ranching"]
    },
    {
        "name": "Equine Chronicle",
        "url": "https://www.equinechronicle.com",
        "rss": "https://www.equinechronicle.com/feed",
        "categories": ["shows", "breeding", "industry"]
    },
    {
        "name": "The Team Roping Journal",
        "url": "https://www.teamropingjournal.com",
        "rss": "https://www.teamropingjournal.com/feed",
        "categories": ["roping", "rodeo"]
    },
    {
        "name": "Barrel Horse News",
        "url": "https://www.barrelhorsenews.com",
        "rss": "https://www.barrelhorsenews.com/feed",
        "categories": ["barrel_racing"]
    }
]

# Rodeo Event Venues to Monitor
RODEO_VENUES = [
    {
        "name": "Will Rogers Coliseum",
        "location": "Fort Worth, TX",
        "url": "https://www.willrogerscoliseum.com",
        "events": ["NCHA Futurity", "NCHA Super Stakes"]
    },
    {
        "name": "South Point Arena",
        "location": "Las Vegas, NV",
        "url": "https://www.southpointarena.com",
        "events": ["NCHA Western Nationals", "Various NCHA events"]
    },
    {
        "name": "National Western Complex",
        "location": "Denver, CO",
        "url": "https://www.nationalwestern.com",
        "events": ["National Western Stock Show"]
    },
    {
        "name": "Reno Livestock Events Center",
        "location": "Reno, NV",
        "url": "https://www.renolivestockeventscenter.com",
        "events": ["NRCHA Snaffle Bit Futurity"]
    },
    {
        "name": "State Fair Park",
        "location": "Oklahoma City, OK",
        "url": "https://www.okstatefair.com",
        "events": ["Various NCHA events"]
    }
]

# Forum/Community Sites
CUTTING_FORUMS = [
    {
        "name": "Cutting Horse Talk Forum",
        "url": "https://www.cuttinghorsetalk.com",
        "type": "forum"
    },
    {
        "name": "Chronicle Forums - Cutting",
        "url": "https://www.chronicleofthehorse.com/forum/forum/cutting",
        "type": "forum"
    }
]

# Reddit Communities
REDDIT_WESTERN_SUBREDDITS = [
    "r/horses",
    "r/cowboys",
    "r/equestrian",
    "r/rodeo",
    "r/ranching"
]

# Breeding/Stallion Directories
STALLION_DIRECTORIES = [
    {
        "name": "NCHA Stallion Directory",
        "url": "https://www.nchacutting.com/stallions"
    },
    {
        "name": "Quarter Horse Directory",
        "url": "https://www.quarterhorsedirectory.com"
    },
    {
        "name": "Performance Horse Registry",
        "url": "https://www.performancehorseregistry.com"
    }
]

# Top Cutting Horse Sires to Track
TOP_CUTTING_SIRES = [
    {"name": "Metallic Cat", "hashtags": ["#metalliccat", "#metallicat"]},
    {"name": "Dual Rey", "hashtags": ["#dualrey"]},
    {"name": "High Brow Cat", "hashtags": ["#highbrowcat"]},
    {"name": "Smooth Talkin Style", "hashtags": ["#smoothtalkinstyle"]},
    {"name": "Hottish", "hashtags": ["#hottish"]},
    {"name": "Kit Kat Sugar", "hashtags": ["#kitkatsugar"]},
    {"name": "Once In A Blu Boon", "hashtags": ["#onceinabluboon"]},
    {"name": "Spots Hot", "hashtags": ["#spotshot"]},
    {"name": "Stevie Rey Von", "hashtags": ["#steviereyvin"]},
    {"name": "Reyzin The Cash", "hashtags": ["#reyzinthecash"]}
]

# Comprehensive list of all Instagram accounts to scrape
def get_all_instagram_accounts() -> list:
    """Get flattened list of all Instagram accounts."""
    accounts = []
    for category, accts in INSTAGRAM_CUTTING_ACCOUNTS.items():
        accounts.extend(accts)
    return accounts


# Get all hashtags including sire-specific ones
def get_all_hashtags() -> list:
    """Get all hashtags including sire hashtags."""
    tags = INSTAGRAM_CUTTING_HASHTAGS.copy()
    for sire in TOP_CUTTING_SIRES:
        tags.extend(sire["hashtags"])
    return list(set(tags))


# Scraping targets summary
SCRAPING_TARGETS_SUMMARY = {
    "instagram_accounts": len(get_all_instagram_accounts()),
    "instagram_hashtags": len(get_all_hashtags()),
    "facebook_groups": len(FACEBOOK_CUTTING_GROUPS),
    "facebook_pages": len(FACEBOOK_CUTTING_PAGES),
    "youtube_channels": len(YOUTUBE_CUTTING_CHANNELS),
    "twitter_accounts": len(TWITTER_CUTTING_ACCOUNTS),
    "news_sources": len(WESTERN_NEWS_SOURCES),
    "rodeo_venues": len(RODEO_VENUES),
    "forums": len(CUTTING_FORUMS),
    "subreddits": len(REDDIT_WESTERN_SUBREDDITS),
    "stallion_directories": len(STALLION_DIRECTORIES),
    "tracked_sires": len(TOP_CUTTING_SIRES)
}

"""
Comprehensive Western Data Scraping Targets
Full catalog of all western industry data sources.
"""

# ============================================================================
# RETAIL CHAINS
# ============================================================================

RETAIL_CHAINS = {
    # Major Western Retailers
    "boot_barn": {
        "name": "Boot Barn",
        "url": "https://www.bootbarn.com",
        "stores": 300,
        "market": "national",
        "categories": ["boots", "hats", "apparel", "tack", "workwear"]
    },
    "sheplers": {
        "name": "Sheplers",
        "url": "https://www.sheplers.com",
        "market": "national",
        "categories": ["boots", "hats", "apparel", "accessories"]
    },
    "cavenders": {
        "name": "Cavender's",
        "url": "https://www.cavenders.com",
        "market": "regional_texas",
        "categories": ["boots", "hats", "apparel", "tack"]
    },

    # Farm/Ranch Supply Crossover
    "tractor_supply": {
        "name": "Tractor Supply Co",
        "url": "https://www.tractorsupply.com",
        "stores": 2000,
        "market": "national",
        "categories": ["workwear", "boots", "tack", "feed", "equipment"]
    },
    "rural_king": {
        "name": "Rural King",
        "url": "https://www.ruralking.com",
        "market": "midwest",
        "categories": ["workwear", "boots", "tack", "feed"]
    },
    "big_r": {
        "name": "Big R Stores",
        "url": "https://www.bigranchstores.com",
        "market": "western_states",
        "categories": ["workwear", "boots", "tack", "ranch_supply"]
    },
    "murdochs": {
        "name": "Murdoch's Ranch & Home",
        "url": "https://www.murdochs.com",
        "market": "mountain_west",
        "categories": ["workwear", "boots", "tack", "ranch_supply"]
    },
    "cal_ranch": {
        "name": "Cal Ranch Stores",
        "url": "https://www.calranch.com",
        "market": "utah_idaho",
        "categories": ["workwear", "boots", "tack", "feed"]
    },
    "smith_edwards": {
        "name": "Smith & Edwards",
        "url": "https://www.smithandedwards.com",
        "market": "utah",
        "categories": ["surplus", "workwear", "tack"]
    },
    "fort_western": {
        "name": "Fort Western Stores",
        "url": "https://www.fortwestern.com",
        "market": "regional",
        "categories": ["boots", "apparel", "tack"]
    }
}

# ============================================================================
# APPAREL BRANDS - DIRECT TO CONSUMER
# ============================================================================

APPAREL_BRANDS = {
    # Major Denim/Workwear
    "wrangler": {"name": "Wrangler", "url": "https://www.wrangler.com", "category": "denim"},
    "lee": {"name": "Lee", "url": "https://www.lee.com", "category": "denim"},
    "levis_western": {"name": "Levi's", "url": "https://www.levi.com", "category": "denim"},
    "cinch": {"name": "Cinch", "url": "https://www.cinchjeans.com", "category": "denim"},

    # Women's Western
    "cruel_girl": {"name": "Cruel Girl", "url": "https://www.cruelgirl.com", "category": "womens"},
    "rock_roll_cowgirl": {"name": "Rock & Roll Cowgirl", "url": "https://www.rockandrollcowgirl.com", "category": "womens"},
    "cowgirl_tuff": {"name": "Cowgirl Tuff", "url": "https://www.cowgirltuff.com", "category": "womens"},

    # Western Shirts/Apparel
    "panhandle_slim": {"name": "Panhandle Slim", "url": "https://www.panhandleslim.com", "category": "shirts"},
    "roper": {"name": "Roper", "url": "https://www.roperapparel.com", "category": "shirts"},
    "tin_haul": {"name": "Tin Haul", "url": "https://www.tinhaul.com", "category": "casual"},

    # Modern Western
    "kimes_ranch": {"name": "Kimes Ranch", "url": "https://www.kimesranch.com", "category": "modern"},
    "hooey": {"name": "Hooey", "url": "https://www.hooey.com", "category": "casual"}
}

# ============================================================================
# BOOT MANUFACTURERS
# ============================================================================

BOOT_BRANDS = {
    # Premium
    "lucchese": {"name": "Lucchese", "url": "https://www.lucchese.com", "tier": "premium", "price_range": "400-3000"},
    "old_gringo": {"name": "Old Gringo", "url": "https://www.oldgringoboots.com", "tier": "premium", "price_range": "400-1500"},
    "anderson_bean": {"name": "Anderson Bean", "url": "https://www.andersonbean.com", "tier": "premium", "price_range": "350-800"},

    # Upper Mid
    "tecovas": {"name": "Tecovas", "url": "https://www.tecovas.com", "tier": "upper_mid", "price_range": "200-400"},
    "ariat": {"name": "Ariat", "url": "https://www.ariat.com", "tier": "upper_mid", "price_range": "150-400"},
    "corral": {"name": "Corral Boots", "url": "https://www.corralboots.com", "tier": "upper_mid", "price_range": "200-500"},

    # Traditional
    "justin": {"name": "Justin Boots", "url": "https://www.justinboots.com", "tier": "traditional", "price_range": "150-400"},
    "tony_lama": {"name": "Tony Lama", "url": "https://www.tonylama.com", "tier": "traditional", "price_range": "150-500"},
    "dan_post": {"name": "Dan Post", "url": "https://www.danpostboots.com", "tier": "traditional", "price_range": "150-350"},
    "double_h": {"name": "Double H Boots", "url": "https://www.doublehboots.com", "tier": "traditional", "price_range": "150-300"},

    # Value
    "laredo": {"name": "Laredo", "url": "https://www.laredoboots.com", "tier": "value", "price_range": "80-200"},
    "durango": {"name": "Durango", "url": "https://www.durangoboots.com", "tier": "value", "price_range": "80-200"},
    "twisted_x": {"name": "Twisted X", "url": "https://www.twistedx.com", "tier": "value", "price_range": "100-200"}
}

# ============================================================================
# HAT BRANDS
# ============================================================================

HAT_BRANDS = {
    # Premium Custom
    "american_hat": {"name": "American Hat Company", "url": "https://www.americanhatco.com", "tier": "premium"},
    "greeley": {"name": "Greeley Hat Works", "url": "https://www.greeleyhatworks.com", "tier": "premium"},

    # Premium Ready
    "resistol": {"name": "Resistol", "url": "https://www.resistol.com", "tier": "premium_ready"},
    "stetson": {"name": "Stetson", "url": "https://www.stetson.com", "tier": "premium_ready"},
    "atwood": {"name": "Atwood Hats", "url": "https://www.atwoodhats.com", "tier": "premium_ready"},

    # Mid-Range
    "charlie_horse": {"name": "Charlie 1 Horse", "url": "https://www.charlie1horse.com", "tier": "mid"},
    "bullhide": {"name": "Bullhide Hats", "url": "https://www.bullhidehats.com", "tier": "mid"},
    "twister": {"name": "Twister", "url": "https://www.twisterhats.com", "tier": "value"},
    "bailey": {"name": "Bailey Western", "url": "https://www.baileywestern.com", "tier": "mid"}
}

# ============================================================================
# SADDLE MANUFACTURERS
# ============================================================================

SADDLE_BRANDS = {
    # Cutting/Reining Specialists
    "martin": {"name": "Martin Saddlery", "url": "https://www.martinsaddlery.com", "specialty": "cutting"},
    "billy_cook": {"name": "Billy Cook Saddles", "url": "https://www.billycooksaddlery.com", "specialty": "all_around"},
    "circle_y": {"name": "Circle Y", "url": "https://www.circley.com", "specialty": "trail_show"},
    "cactus": {"name": "Cactus Saddlery", "url": "https://www.cactussaddlery.com", "specialty": "roping"},
    "bobs_custom": {"name": "Bob's Custom Saddles", "url": "https://www.bobscustomsaddles.com", "specialty": "reining"},

    # General Western
    "tucker": {"name": "Tucker Saddles", "url": "https://www.tuckersaddles.com", "specialty": "trail"},
    "dale_chavez": {"name": "Dale Chavez", "url": "https://www.dalechavez.com", "specialty": "bits_equipment"},
    "teskeys": {"name": "Teskey's", "url": "https://www.teskeys.com", "specialty": "tack_retailer"},
    "colorado_saddlery": {"name": "Colorado Saddlery", "url": "https://www.coloradosaddlery.com", "specialty": "ranch"},
    "simco": {"name": "Simco", "url": "https://www.simco.com", "specialty": "value"}
}

# ============================================================================
# TACK & EQUIPMENT RETAILERS
# ============================================================================

TACK_RETAILERS = {
    "state_line_tack": {"name": "State Line Tack", "url": "https://www.statelinetack.com", "market": "national"},
    "riding_warehouse": {"name": "Riding Warehouse", "url": "https://www.ridingwarehouse.com", "market": "national"},
    "horse_saddle_shop": {"name": "Horse Saddle Shop", "url": "https://www.horsesaddleshop.com", "market": "national"},
    "schneiders": {"name": "Schneiders Saddlery", "url": "https://www.sstack.com", "market": "national"},
    "valley_vet": {"name": "Valley Vet Supply", "url": "https://www.valleyvet.com", "market": "national"},
    "dover": {"name": "Dover Saddlery", "url": "https://www.doversaddlery.com", "market": "national"},
    "smartpak": {"name": "SmartPak", "url": "https://www.smartpakequine.com", "market": "national"},
    "chicks": {"name": "Chicks Saddlery", "url": "https://www.chickssaddlery.com", "market": "national"},
    "jeffers": {"name": "Jeffers Pet", "url": "https://www.jefferspet.com", "market": "national"},
    "horse_com": {"name": "Horse.com", "url": "https://www.horse.com", "market": "national"}
}

# ============================================================================
# PERFORMANCE EQUIPMENT BRANDS
# ============================================================================

EQUIPMENT_BRANDS = {
    # Protection/Boots
    "classic_equine": {"name": "Classic Equine", "url": "https://www.classicequine.com", "category": "boots_protection"},
    "professionals_choice": {"name": "Professional's Choice", "url": "https://www.professionalschoice.com", "category": "boots_protection"},
    "cashel": {"name": "Cashel Company", "url": "https://www.cashelcompany.com", "category": "protection"},

    # Tack/Leather
    "weaver": {"name": "Weaver Leather", "url": "https://www.weaverleather.com", "category": "tack"},
    "reinsman": {"name": "Reinsman", "url": "https://www.reinsman.com", "category": "bits_tack"},

    # Ropes
    "classic_ropes": {"name": "Classic Ropes", "url": "https://www.classicropes.com", "category": "ropes"},
    "cactus_ropes": {"name": "Cactus Ropes", "url": "https://www.cactusropes.com", "category": "ropes"},
    "rattler_ropes": {"name": "Rattler Ropes", "url": "https://www.rattlerropes.com", "category": "ropes"},

    # General
    "tough_1": {"name": "Tough-1", "url": "https://www.tough1.com", "category": "general"},
    "mustang": {"name": "Mustang Manufacturing", "url": "https://www.mustangmfg.com", "category": "general"}
}

# ============================================================================
# MARKETPLACE PLATFORMS
# ============================================================================

MARKETPLACES = {
    "amazon": {
        "name": "Amazon",
        "url": "https://www.amazon.com",
        "western_categories": [
            "/s?k=western+boots",
            "/s?k=cowboy+hats",
            "/s?k=western+shirts",
            "/s?k=horse+saddles",
            "/s?k=horse+tack",
            "/s?k=western+home+decor"
        ],
        "data_points": ["price", "reviews", "sales_rank", "qa"]
    },
    "ebay": {
        "name": "eBay",
        "url": "https://www.ebay.com",
        "western_categories": [
            "/sch/i.html?_nkw=used+western+saddle",
            "/sch/i.html?_nkw=vintage+western+wear",
            "/sch/i.html?_nkw=cowboy+boots+used"
        ],
        "data_points": ["sold_prices", "active_listings", "demand"]
    },
    "etsy": {
        "name": "Etsy",
        "url": "https://www.etsy.com",
        "search_terms": ["western", "cowboy", "ranch", "rodeo", "cowgirl"],
        "data_points": ["handmade_trends", "custom_pricing", "emerging_styles"]
    },
    "poshmark": {
        "name": "Poshmark",
        "url": "https://www.poshmark.com",
        "categories": ["western-boots", "western-wear"],
        "data_points": ["resale_value", "brand_demand"]
    },
    "mercari": {
        "name": "Mercari",
        "url": "https://www.mercari.com",
        "search_terms": ["western boots", "cowboy hat", "rodeo"],
        "data_points": ["resale_pricing", "popularity"]
    },
    "grailed": {
        "name": "Grailed",
        "url": "https://www.grailed.com",
        "search_terms": ["western", "cowboy"],
        "data_points": ["mens_western_fashion", "premium_resale"]
    },
    "depop": {
        "name": "Depop",
        "url": "https://www.depop.com",
        "search_terms": ["western", "cowgirl", "rodeo"],
        "data_points": ["gen_z_trends", "vintage_western"]
    }
}

# ============================================================================
# LIFESTYLE BRANDS (CROSSOVER MARKET)
# ============================================================================

LIFESTYLE_BRANDS = {
    # Outdoor/Ranch Crossover
    "yeti": {"name": "YETI", "url": "https://www.yeti.com", "crossover": "outdoor_ranch"},
    "carhartt": {"name": "Carhartt", "url": "https://www.carhartt.com", "crossover": "workwear"},
    "filson": {"name": "Filson", "url": "https://www.filson.com", "crossover": "heritage_outdoor"},
    "pendleton": {"name": "Pendleton", "url": "https://www.pendleton-usa.com", "crossover": "western_heritage"},
    "orvis": {"name": "Orvis", "url": "https://www.orvis.com", "crossover": "outdoor"},
    "sitka": {"name": "Sitka Gear", "url": "https://www.sitkagear.com", "crossover": "hunting_ranch"},

    # Modern Western
    "howler_brothers": {"name": "Howler Brothers", "url": "https://www.howlerbros.com", "crossover": "casual_western"},
    "texas_standard": {"name": "Texas Standard", "url": "https://www.texasstandard.com", "crossover": "premium_western"}
}

# ============================================================================
# FEED & NUTRITION
# ============================================================================

FEED_BRANDS = {
    "purina": {"name": "Purina", "url": "https://www.purina.com", "category": "major"},
    "triple_crown": {"name": "Triple Crown", "url": "https://www.triplecrownfeed.com", "category": "premium"},
    "nutrena": {"name": "Nutrena", "url": "https://www.nutrena.com", "category": "major"},
    "tribute": {"name": "Tribute Equine", "url": "https://www.tributeequinenutrition.com", "category": "premium"}
}

# ============================================================================
# VETERINARY/HEALTH PRODUCTS
# ============================================================================

VET_PRODUCTS = {
    "absorbine": {"name": "Absorbine", "url": "https://www.absorbine.com", "category": "liniments"},
    "farnam": {"name": "Farnam", "url": "https://www.farnam.com", "category": "health"},
    "vetericyn": {"name": "Vetericyn", "url": "https://www.vetericyn.com", "category": "wound_care"},
    "draw_it_out": {"name": "Draw It Out", "url": "https://www.drawitout.com", "category": "poultice"},
    "sore_no_more": {"name": "Sore No-More", "url": "https://www.sorenomore.com", "category": "pain_relief"}
}

# ============================================================================
# WESTERN HOME & DECOR
# ============================================================================

HOME_DECOR = {
    "lone_star_decor": {"name": "Lone Star Western Decor", "url": "https://www.lonestarwesterndecor.com"},
    "black_forest": {"name": "Black Forest Decor", "url": "https://www.blackforestdecor.com"},
    "king_ranch_saddle": {"name": "King Ranch Saddle Shop", "url": "https://www.krsaddleshop.com"},
    "goodes": {"name": "Goode's Outdoor Western", "url": "https://www.goodesoutdoorwesternstore.com"}
}

# ============================================================================
# TRUCK/AUTO ACCESSORIES (RANCH MARKET)
# ============================================================================

TRUCK_ACCESSORIES = {
    "weathertech": {"name": "WeatherTech", "url": "https://www.weathertech.com"},
    "husky_liners": {"name": "Husky Liners", "url": "https://www.huskyliners.com"},
    "ranch_hand": {"name": "Ranch Hand", "url": "https://www.ranchhand.com"},
    "dee_zee": {"name": "Dee Zee", "url": "https://www.deezee.com"}
}

# ============================================================================
# COMPETITION ORGANIZATIONS
# ============================================================================

COMPETITION_ORGS = {
    "ncha": {
        "name": "National Cutting Horse Association",
        "url": "https://www.nchacutting.com",
        "data": ["results", "standings", "events", "entries", "futurity"]
    },
    "nrcha": {
        "name": "National Reined Cow Horse Association",
        "url": "https://www.nrcha.com",
        "data": ["results", "standings", "events", "snaffle_bit_futurity"]
    },
    "nrha": {
        "name": "National Reining Horse Association",
        "url": "https://www.nrha.com",
        "data": ["results", "standings", "events", "futurity"]
    },
    "aqha": {
        "name": "American Quarter Horse Association",
        "url": "https://www.aqha.com",
        "data": ["shows", "results", "registration", "standings"]
    },
    "apha": {
        "name": "American Paint Horse Association",
        "url": "https://www.apha.com",
        "data": ["shows", "results"]
    }
}

# ============================================================================
# HORSE SALES VENUES
# ============================================================================

HORSE_SALES = {
    "heritage_place": {
        "name": "Heritage Place",
        "url": "https://www.heritageplace.com",
        "location": "Oklahoma City, OK",
        "sales_per_year": 6
    },
    "wagonhound": {
        "name": "Wagonhound Ranch",
        "url": "https://www.wagonhoundranch.com",
        "location": "Douglas, WY",
        "sales_per_year": 1
    },
    "rocking_p": {
        "name": "Rocking P Ranch",
        "url": "https://www.rockingpranch.com",
        "sales_per_year": 2
    },
    "billings_livestock": {
        "name": "Billings Livestock",
        "url": "https://www.billingslivestock.com",
        "location": "Billings, MT"
    },
    "superior_livestock": {
        "name": "Superior Livestock",
        "url": "https://www.superiorldc.com",
        "type": "video_auction"
    }
}

# ============================================================================
# PEDIGREE & STALLION DATABASES
# ============================================================================

PEDIGREE_SOURCES = {
    "allbreedpedigree": {"name": "All Breed Pedigree", "url": "https://www.allbreedpedigree.com"},
    "aqha_records": {"name": "AQHA Records", "url": "https://www.aqha.com"},
    "equibase": {"name": "Equibase", "url": "https://www.equibase.com"},
    "equi_stat": {"name": "Equi-Stat", "url": "https://www.equi-stat.com"}
}

STALLION_DIRECTORIES = {
    "stallion_search": {"name": "Stallion Search", "url": "https://www.stallionsearch.com"},
    "qhn_register": {"name": "QHN Stallion Register", "url": "https://www.quarterhorsenews.com/stallions"},
    "cowboy_times": {"name": "Cowboy Times", "url": "https://www.cowboytimes.com"}
}

# ============================================================================
# NEWS & MEDIA SOURCES
# ============================================================================

NEWS_SOURCES = {
    # Horse Industry
    "quarter_horse_news": {"name": "Quarter Horse News", "url": "https://www.quarterhorsenews.com", "rss": True},
    "western_horseman": {"name": "Western Horseman", "url": "https://www.westernhorseman.com", "rss": True},
    "equine_chronicle": {"name": "Equine Chronicle", "url": "https://www.equinechronicle.com", "rss": True},
    "horse_rider": {"name": "Horse & Rider", "url": "https://www.horseandrider.com", "rss": True},
    "americas_horse": {"name": "America's Horse Daily", "url": "https://www.americashorsedaily.com", "rss": True},

    # Western Lifestyle
    "cowgirl_magazine": {"name": "Cowgirl Magazine", "url": "https://www.cowgirlmagazine.com", "rss": True},
    "american_cowboy": {"name": "American Cowboy", "url": "https://www.americancowboy.com", "rss": True},
    "ranch_reata": {"name": "Ranch & Reata", "url": "https://www.ranchandreata.com", "rss": True},

    # Rodeo
    "team_roping_journal": {"name": "Team Roping Journal", "url": "https://www.teamropingjournal.com", "rss": True},
    "barrel_horse_news": {"name": "Barrel Horse News", "url": "https://www.barrelhorsenews.com", "rss": True},

    # Trade
    "western_lifestyle_retailer": {"name": "Western Lifestyle Retailer", "url": "https://www.wlrmag.com", "trade": True}
}

# ============================================================================
# SOCIAL MEDIA TARGETS - EXPANDED
# ============================================================================

INSTAGRAM_TARGETS = {
    "accounts": {
        # Organizations
        "organizations": [
            "nchacutting", "nrcha_reined_cow_horse", "aqha", "nrhausa", "prorodeo",
            "pbr", "wranglernfr", "houstonstockshow"
        ],

        # Major Influencers (500K+)
        "mega_influencers": [
            "westernlifestyle", "southernlivingmag", "rfdtv", "cowgirlmagazine"
        ],

        # Trainers (Top 100)
        "trainers": [
            "lloydcox_cuttinghorses", "beau_galyean", "wesleyparamore",
            "grant_setnicka", "todd_bergen", "matt_gaines_cutting",
            "austin_shepard", "adan_banuelos", "morgan_cromer"
        ],

        # Ranches
        "ranches": [
            "6666ranch", "fourcornerranch", "cattellacranch", "bitterwater_ranch",
            "shiningsparranch", "bellranch", "kingranch"
        ],

        # Brands
        "brands": [
            "ariat", "wrangler", "resistol", "stetson", "luccheseboots",
            "tecovas", "bootbarn", "cavenders", "cinchcowboy", "hooeyco"
        ]
    },

    "hashtags": {
        "high_volume": [
            "#westernfashion", "#cowboyboots", "#westernstyle", "#cowgirlstyle",
            "#ranchlife", "#westernlifestyle", "#rodeolife"
        ],
        "cutting_specific": [
            "#cuttinghorse", "#ncha", "#cuttinghorses", "#cuttinghorsetraining",
            "#nchafuturity", "#futurity", "#cowhorse"
        ],
        "breeding": [
            "#quarterhorse", "#aqha", "#cuttinghorsesire", "#quarterhorsesire"
        ],
        "lifestyle": [
            "#cowboyhat", "#westernboots", "#countrylife", "#farmlife"
        ]
    }
}

TIKTOK_TARGETS = {
    "search_terms": [
        "western fashion", "cowboy boots", "ranch life", "cutting horse",
        "rodeo life", "cowgirl style", "western outfit"
    ],
    "hashtags": [
        "#westernfashion", "#cowboyboots", "#ranchlife", "#cuttinghorse",
        "#cowgirlstyle", "#rodeo", "#westernstyle"
    ]
}

YOUTUBE_TARGETS = {
    "channels": [
        {"name": "NCHA Official", "id": "nchafuturity", "type": "organization"},
        {"name": "Cutting Horse Training Online", "id": "cuttinghorsetraining", "type": "education"},
        {"name": "Quarter Horse News", "id": "quarterhorsenews", "type": "media"},
        {"name": "Western Horseman", "id": "westernhorseman", "type": "media"},
        {"name": "Team Roping Journal", "id": "teamropingjournal", "type": "media"},
        {"name": "Horse & Rider", "id": "horseandrider", "type": "media"}
    ],
    "search_terms": [
        "cutting horse training", "western riding", "horse training", "rodeo"
    ]
}

FACEBOOK_TARGETS = {
    "groups": [
        {"name": "Cutting Horses For Sale", "members": "50K+", "type": "marketplace"},
        {"name": "NCHA Cutting Horses", "members": "40K+", "type": "discussion"},
        {"name": "Performance Horses For Sale", "members": "35K+", "type": "marketplace"},
        {"name": "Western Horse Tack For Sale", "members": "30K+", "type": "marketplace"},
        {"name": "Cowgirl Style", "members": "25K+", "type": "lifestyle"},
        {"name": "Ranch Life", "members": "20K+", "type": "lifestyle"},
        {"name": "Western Boots Buy Sell Trade", "members": "15K+", "type": "marketplace"},
        {"name": "Cowboy Gear Marketplace", "members": "10K+", "type": "marketplace"}
    ],
    "pages": [
        "NCHACutting", "NRCHAOfficial", "AQHAOfficial", "WranglerOfficial",
        "AriatInternational", "BootBarn", "Cavenders"
    ]
}

REDDIT_TARGETS = [
    "r/horses", "r/equestrian", "r/cowboys", "r/ranching", "r/rodeo",
    "r/westernriding", "r/cowboy"
]

# ============================================================================
# FORUMS & COMMUNITIES
# ============================================================================

FORUMS = {
    "cutting_horse_talk": {"name": "Cutting Horse Talk", "url": "https://www.cuttinghorsetalk.com"},
    "chronicle_forums": {"name": "Chronicle of the Horse Forums", "url": "https://www.chronofhorse.com/forum"},
    "horse_forum": {"name": "The Horse Forum", "url": "https://www.thehorseforum.com"},
    "barrel_racing_world": {"name": "Barrel Racing World Forum", "url": "https://www.barrelracingworld.com/forum"}
}

# ============================================================================
# EVENTS & VENUES
# ============================================================================

MAJOR_VENUES = {
    "will_rogers": {
        "name": "Will Rogers Memorial Center",
        "location": "Fort Worth, TX",
        "events": ["NCHA Futurity", "NCHA Super Stakes", "Stock Show"]
    },
    "south_point": {
        "name": "South Point Arena",
        "location": "Las Vegas, NV",
        "events": ["NCHA Western Nationals", "Various NCHA"]
    },
    "lazy_e": {
        "name": "Lazy E Arena",
        "location": "Guthrie, OK",
        "events": ["Timed Event Championship", "Various rodeos"]
    },
    "national_western": {
        "name": "National Western Complex",
        "location": "Denver, CO",
        "events": ["National Western Stock Show"]
    },
    "houston_livestock": {
        "name": "NRG Center",
        "location": "Houston, TX",
        "events": ["Houston Livestock Show & Rodeo"]
    },
    "reno_events": {
        "name": "Reno Livestock Events Center",
        "location": "Reno, NV",
        "events": ["NRCHA Snaffle Bit Futurity"]
    }
}

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

def get_target_summary():
    """Get summary of all scraping targets."""
    return {
        "retail_chains": len(RETAIL_CHAINS),
        "apparel_brands": len(APPAREL_BRANDS),
        "boot_brands": len(BOOT_BRANDS),
        "hat_brands": len(HAT_BRANDS),
        "saddle_brands": len(SADDLE_BRANDS),
        "tack_retailers": len(TACK_RETAILERS),
        "equipment_brands": len(EQUIPMENT_BRANDS),
        "marketplaces": len(MARKETPLACES),
        "lifestyle_brands": len(LIFESTYLE_BRANDS),
        "feed_brands": len(FEED_BRANDS),
        "vet_products": len(VET_PRODUCTS),
        "competition_orgs": len(COMPETITION_ORGS),
        "horse_sales": len(HORSE_SALES),
        "news_sources": len(NEWS_SOURCES),
        "forums": len(FORUMS),
        "venues": len(MAJOR_VENUES),
        "instagram_accounts": sum(len(v) for v in INSTAGRAM_TARGETS["accounts"].values()),
        "instagram_hashtags": sum(len(v) for v in INSTAGRAM_TARGETS["hashtags"].values()),
        "facebook_groups": len(FACEBOOK_TARGETS["groups"]),
        "youtube_channels": len(YOUTUBE_TARGETS["channels"]),
        "reddit_subs": len(REDDIT_TARGETS)
    }

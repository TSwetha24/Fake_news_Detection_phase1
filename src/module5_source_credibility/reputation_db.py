from typing import Dict, Any

# Domain Reputation Database (Taxonomy aligned with NewsGuard, Media Bias/Fact Check MBFC, and PageRank credibility metrics)
DOMAIN_REPUTATION_DATABASE: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------
    # TIER 1: Highly Authoritative / Wire Agencies / Reference (Score 0.90 - 1.00)
    # -------------------------------------------------------------
    "reuters.com": {
        "name": "Reuters News Agency",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.98,
        "factuality": "VERY HIGH",
        "bias": "LEAST BIASED",
        "description": "Global wire news service adhering to rigorous Thomson Reuters Trust Principles."
    },
    "apnews.com": {
        "name": "Associated Press (AP)",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.98,
        "factuality": "VERY HIGH",
        "bias": "LEAST BIASED",
        "description": "Non-profit international news agency with strict editorial standards."
    },
    "en.wikipedia.org": {
        "name": "Wikipedia Knowledge Base",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.92,
        "factuality": "HIGH",
        "bias": "NEUTRAL REFERENCE",
        "description": "Peer-moderated online encyclopedia with cited citations and edit history tracking."
    },
    "bbc.com": {
        "name": "BBC News",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.95,
        "factuality": "HIGH",
        "bias": "CENTER",
        "description": "UK public service broadcaster with global investigative fact-checking desks."
    },
    "bbc.co.uk": {
        "name": "BBC News UK",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.95,
        "factuality": "HIGH",
        "bias": "CENTER",
        "description": "British Broadcasting Corporation official news portal."
    },
    "ptinews.com": {
        "name": "Press Trust of India (PTI)",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.94,
        "factuality": "HIGH",
        "bias": "LEAST BIASED",
        "description": "Premier news agency of India transmitting verified factual reports."
    },
    "aninews.in": {
        "name": "Asian News International (ANI)",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.90,
        "factuality": "HIGH",
        "bias": "CENTER",
        "description": "Major multimedia news agency operating in South Asia."
    },
    "nature.com": {
        "name": "Nature Scientific Journal",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.99,
        "factuality": "VERY HIGH",
        "bias": "SCIENTIFIC PEER REVIEW",
        "description": "Premier international scientific journal."
    },
    "who.int": {
        "name": "World Health Organization",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.99,
        "factuality": "VERY HIGH",
        "bias": "OFFICIAL GLOBAL HEALTH",
        "description": "United Nations specialized health agency."
    },
    "nasa.gov": {
        "name": "NASA Official Portal",
        "tier": "Tier 1: Highly Authoritative",
        "credibility_score": 0.99,
        "factuality": "VERY HIGH",
        "bias": "OFFICIAL SCIENTIFIC",
        "description": "Official aerospace and civil space exploration federal agency."
    },

    # -------------------------------------------------------------
    # TIER 2: Mainstream National & International Press (Score 0.75 - 0.89)
    # -------------------------------------------------------------
    "thehindu.com": {
        "name": "The Hindu",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.88,
        "factuality": "HIGH",
        "bias": "LEFT-CENTER",
        "description": "Prestigious Indian English-language national daily with strong regional coverage."
    },
    "timesofindia.indiatimes.com": {
        "name": "The Times of India",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.84,
        "factuality": "MOSTLY FACTUAL",
        "bias": "CENTER",
        "description": "Largest circulating Indian English daily with widespread nationwide reporting bureaus."
    },
    "indianexpress.com": {
        "name": "The Indian Express",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.87,
        "factuality": "HIGH",
        "bias": "CENTER",
        "description": "Indian news daily noted for investigative journalism and transparency."
    },
    "ndtv.com": {
        "name": "NDTV",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.85,
        "factuality": "HIGH",
        "bias": "CENTER",
        "description": "Major Indian television network and news website."
    },
    "indiatoday.in": {
        "name": "India Today",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.83,
        "factuality": "MOSTLY FACTUAL",
        "bias": "CENTER",
        "description": "Leading Indian news weekly and digital broadcasting platform."
    },
    "hindustantimes.com": {
        "name": "Hindustan Times",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.84,
        "factuality": "MOSTLY FACTUAL",
        "bias": "CENTER",
        "description": "Prominent national daily published from New Delhi."
    },
    "deccanherald.com": {
        "name": "Deccan Herald",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.85,
        "factuality": "HIGH",
        "bias": "CENTER",
        "description": "Respected English daily published in Karnataka and Southern India."
    },
    "news18.com": {
        "name": "News18 / CNN-News18",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.81,
        "factuality": "MOSTLY FACTUAL",
        "bias": "CENTER-RIGHT",
        "description": "National English and regional language television news portal."
    },
    "theprint.in": {
        "name": "ThePrint",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.82,
        "factuality": "HIGH",
        "bias": "CENTER",
        "description": "Digital news platform focusing on politics and policy."
    },
    "thequint.com": {
        "name": "The Quint",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.82,
        "factuality": "HIGH",
        "bias": "LEFT-CENTER",
        "description": "Digital publication with an IFCN-signatory fact-checking unit (WebQoof)."
    },
    "nytimes.com": {
        "name": "The New York Times",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.88,
        "factuality": "HIGH",
        "bias": "LEFT-CENTER",
        "description": "Leading American daily with comprehensive international coverage."
    },
    "theguardian.com": {
        "name": "The Guardian",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.86,
        "factuality": "HIGH",
        "bias": "LEFT-CENTER",
        "description": "UK daily newspaper known for independent trust governance."
    },
    "webmd.com": {
        "name": "WebMD Health",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.85,
        "factuality": "HIGH",
        "bias": "HEALTH SPECIALIZED",
        "description": "Medical information portal written and reviewed by healthcare professionals."
    },

    # -------------------------------------------------------------
    # TIER 3: Regional / Local / Independent Press (Score 0.65 - 0.74)
    # -------------------------------------------------------------
    "nagalandpost.com": {
        "name": "Nagaland Post",
        "tier": "Tier 3: Regional / Independent",
        "credibility_score": 0.72,
        "factuality": "REGIONAL REPORTING",
        "bias": "LOCAL PRESS",
        "description": "English daily newspaper published from Dimapur, Nagaland focusing on regional state news."
    },
    "udayavani.com": {
        "name": "Udayavani",
        "tier": "Tier 3: Regional / Independent",
        "credibility_score": 0.70,
        "factuality": "REGIONAL REPORTING",
        "bias": "LOCAL PRESS",
        "description": "Kannada language regional daily newspaper published from Manipal, Karnataka."
    },
    "livemint.com": {
        "name": "Livemint",
        "tier": "Tier 2: Mainstream Credible",
        "credibility_score": 0.82,
        "factuality": "GENERAL REPORTING",
        "bias": "BUSINESS / FINANCIAL",
        "description": "Indian financial and business news daily published by HT Media."
    },
    "pinkvilla.com": {
        "name": "Pinkvilla",
        "tier": "Tier 3: Mixed / Entertainment",
        "credibility_score": 0.62,
        "factuality": "MIXED",
        "bias": "ENTERTAINMENT / CELEBRITY",
        "description": "Celebrity gossip, lifestyle, and film industry portal with unverified rumors."
    },
    "bollywoodhungama.com": {
        "name": "Bollywood Hungama",
        "tier": "Tier 3: Mixed / Entertainment",
        "credibility_score": 0.65,
        "factuality": "MIXED",
        "bias": "ENTERTAINMENT",
        "description": "Film industry box-office and promotional news site."
    },
    "cinemaexpress.com": {
        "name": "Cinema Express",
        "tier": "Tier 3: Mixed / Entertainment",
        "credibility_score": 0.70,
        "factuality": "MOSTLY FACTUAL",
        "bias": "CINEMA NEWS",
        "description": "South Indian entertainment and film critique portal."
    },
    "dailymail.co.uk": {
        "name": "Daily Mail",
        "tier": "Tier 3: Mixed / Tabloid",
        "credibility_score": 0.55,
        "factuality": "MIXED",
        "bias": "RIGHT",
        "description": "UK tabloid known for sensationalism and sensationalized headlines."
    },

    # -------------------------------------------------------------
    # TIER 4: Satirical / Unverified / User-Generated (Score 0.05 - 0.49)
    # -------------------------------------------------------------
    "theonion.com": {
        "name": "The Onion",
        "tier": "Tier 4: Satire / Parody",
        "credibility_score": 0.10,
        "factuality": "SATIRE / FICTION",
        "bias": "SATIRICAL",
        "description": "Parody newspaper producing purely satirical and fictional news."
    },
    "babylonbee.com": {
        "name": "The Babylon Bee",
        "tier": "Tier 4: Satire / Parody",
        "credibility_score": 0.10,
        "factuality": "SATIRE / FICTION",
        "bias": "SATIRICAL",
        "description": "Satirical news website publishing fictional comedic articles."
    },
    "reddit.com": {
        "name": "Reddit User Forum",
        "tier": "Tier 4: User-Generated",
        "credibility_score": 0.40,
        "factuality": "UNVERIFIED",
        "bias": "COMMUNITY SUBMITTED",
        "description": "Social media forum where content is generated by anonymous users."
    }
}

# Default profile for unrecognized domains
DEFAULT_REPUTATION_PROFILE = {
    "name": "General Digital Media Outlet",
    "tier": "Tier 2: Mainstream Credible",
    "credibility_score": 0.75,
    "factuality": "GENERAL REPORTING",
    "bias": "UNSPECIFIED",
    "description": "Standard digital web outlet evaluated under general journalistic heuristics."
}

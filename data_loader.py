import os
import pandas as pd
import numpy as np
import config

def generate_sample_fakeddit_data(filepath=config.FAKEDDIT_PATH, num_samples=100):
    """
    Generates a realistic benchmark sample dataset adhering to the official Fakeddit schema.
    Used for rapid local testing and training when full 100GB Fakeddit media dump is not locally present.
    """
    print(f"Generating realistic Fakeddit benchmark dataset at {filepath}...")
    
    np.random.seed(42)
    
    claims = [
        # Real News (True)
        ("NASA's James Webb Space Telescope discovers water vapor on distant rocky exoplanet", "nasa.gov", "Real"),
        ("Global renewable energy capacity grew by a record 50% in 2023, report finds", "reuters.com", "Real"),
        ("Scientists identify new species of deep-sea octopus in Pacific trench", "nationalgeographic.com", "Real"),
        ("FDA approves new targeted gene therapy for rare pediatric blood disorder", "apnews.com", "Real"),
        ("European Central Bank lowers interest rates by 25 basis points amid cooling inflation", "bloomberg.com", "Real"),
        ("World Health Organization declares eradication of wild poliovirus in region", "who.int", "Real"),
        ("MIT researchers develop high-efficiency solar cells using perovskite technology", "techcrunch.com", "Real"),
        ("International Space Station crew completes successful 7-hour spacewalk for solar array upgrade", "nasa.gov", "Real"),
        ("New archaeological findings confirm ancient trade routes across the Mediterranean", "bbc.com", "Real"),
        ("Oceanographers track massive deep-sea current migration in the Southern Ocean", "nature.com", "Real"),
        
        # Fake News (False / Misleading / Manipulated)
        ("Secret government lab admit creating weather control laser that caused recent hurricanes", "conspiracyworld.xyz", "Fake"),
        ("Drinking warm lemon water cures stage 4 cancer in 3 days, viral video claims", "healthfactslive.net", "Fake"),
        ("Tech billionaire buys entire country of Greenland to create private cryptocurrency state", "buzznews24.co", "Fake"),
        ("5G towers confirmed to cause instant battery drain and memory loss in humans", "truthleak.org", "Fake"),
        ("Leaked documents show moon landing was filmed in underground desert studio in 1969", "realtruthdaily.info", "Fake"),
        ("Scientists uncover 10,000 year old giant skeleton wearing modern wrist watch in cave", "ancientmysteries.xyz", "Fake"),
        ("Ancient pyramid discovered under Antarctic ice sheet proves extraterrestrial civilization built it", "alienufoinquiry.net", "Fake"),
        ("BREAKING: Major bank accidentally deposits $1 billion into every citizen account", "fakeviralnews.net", "Fake"),
        ("New law makes it illegal to own more than one cat in major metropolitan city", "clickbaittimes.co", "Fake"),
        ("Eating banana peels before sleep grants lucid dreaming abilities, study claims", "viralhacks.org", "Fake"),
        
        # Unverified / Satirical / Satire Claims
        ("Study suggests coffee drinkers live longer, but researchers aren't sure why", "healthdigest.com", "Unverified"),
        ("Local man claims his pet parrot can predict stock market crashes with 90% accuracy", "satirepost.com", "Unverified"),
        ("Unconfirmed reports suggest tech giant preparing secret launch of holographic smartphone", "rumortech.io", "Unverified"),
        ("Experts debate whether AI models will achieve human-level consciousness by 2030", "futurism.com", "Unverified"),
        ("Mysterious radio signal from deep space repeats every 16 days, origin unknown", "spaceinsider.com", "Unverified"),
        ("Leaked prototype images claim to show unannounced next-gen gaming console", "gamemag.org", "Unverified"),
        ("Unverified social media post claims popular fast food chain changing secret recipe", "foodinsider.net", "Unverified"),
        ("Astronomers detect fast radio burst from nearby galaxy cluster with unusual cadence", "astronomynow.com", "Unverified"),
        ("Bizarre sea creature washes ashore on Pacific coastline; marine biologists investigate", "oceanlife.org", "Unverified"),
        ("Anonymous insider claims major movie studio secretly filming reboot of classic franchise", "cinemarumors.com", "Unverified")
    ]
    
    data = []
    label_map = {"Real": 0, "Fake": 1, "Unverified": 2}
    
    for i in range(num_samples):
        title, domain, label_str = claims[i % len(claims)]
        label_id = label_map[label_str]
        
        row = {
            "author": f"user_{i+1000}",
            "clean_title": title,
            "created_utc": 1600000000 + i * 3600,
            "domain": domain,
            "hasImage": True if i % 2 == 0 else False,
            "id": f"fakeddit_{i:05d}",
            "image_url": f"https://picsum.photos/400/300?random={i}",
            "num_comments": np.random.randint(5, 500),
            "score": np.random.randint(10, 2000),
            "upvote_ratio": round(np.random.uniform(0.5, 0.99), 2),
            "2_way_label": 0 if label_str == "Real" else 1,
            "3_way_label": label_id,
            "6_way_label": label_id,
            "label_name": label_str
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Dataset generated successfully with {len(df)} rows.")
    return df

def load_fakeddit_dataset(filepath=config.FAKEDDIT_PATH):
    """
    Loads Fakeddit dataset from local file or generates sample if not present.
    Returns cleaned DataFrame with standardized target column 'label_name' ('Real', 'Fake', 'Unverified').
    """
    if not os.path.exists(filepath):
        print(f"File {filepath} not found. Generating sample Fakeddit benchmark data.")
        return generate_sample_fakeddit_data(filepath)
    
    print(f"Loading Fakeddit dataset from {filepath}...")
    if filepath.endswith('.tsv'):
        df = pd.read_csv(filepath, sep='\t')
    else:
        df = pd.read_csv(filepath)
        
    # Map 3_way_label or label_name to Real, Fake, Unverified
    if 'label_name' not in df.columns:
        if '3_way_label' in df.columns:
            map_dict = {0: "Real", 1: "Fake", 2: "Unverified"}
            df['label_name'] = df['3_way_label'].map(map_dict)
        elif '2_way_label' in df.columns:
            map_dict = {0: "Real", 1: "Fake"}
            df['label_name'] = df['2_way_label'].map(map_dict)
        else:
            df['label_name'] = "Unverified"
            
    # Ensure title column is named clean_title
    if 'clean_title' not in df.columns and 'title' in df.columns:
        df['clean_title'] = df['title']
        
    df['clean_title'] = df['clean_title'].fillna('')
    return df

if __name__ == "__main__":
    df = load_fakeddit_dataset()
    print("Dataset shape:", df.shape)
    print(df[['clean_title', 'domain', 'label_name']].head())

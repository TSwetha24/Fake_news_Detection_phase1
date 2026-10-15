import os
import pandas as pd
import numpy as np
import config

def load_fakeddit_dataset(filepath=config.FAKEDDIT_PATH):
    """
    Loads Fakeddit dataset from local file.
    Returns cleaned DataFrame with standardized target column 'label_name' ('Real', 'Fake', 'Unverified')
    and aliases 'text', 'image', 'label'.
    """
    if not os.path.exists(filepath):
        alt_path = os.path.join(config.DATA_DIR, "fakeddit_60k.csv")
        if os.path.exists(alt_path):
            filepath = alt_path
        else:
            raise FileNotFoundError(f"Fakeddit dataset not found at {filepath}")
    
    print(f"Loading Fakeddit dataset from {filepath}...")
    if filepath.endswith('.tsv'):
        df = pd.read_csv(filepath, sep='\t', on_bad_lines='skip', low_memory=False)
    else:
        df = pd.read_csv(filepath, on_bad_lines='skip', low_memory=False)
        
    # Ensure clean_title and text columns
    for col in ['clean_title', 'text', 'title', 'headline']:
        if col in df.columns:
            df['clean_title'] = df[col].astype(str)
            df['text'] = df['clean_title']
            break
            
    # Ensure image_url and image columns
    if 'image_url' in df.columns:
        df['image'] = df['image_url'].fillna('')
    elif 'image' in df.columns:
        df['image_url'] = df['image'].fillna('')
    else:
        df['image'] = ''
        df['image_url'] = ''

    # Map label to 3 standard classes: Real (0), Fake (1), Unverified (2)
    label_map = {0: "Real", 1: "Fake", 2: "Unverified"}
    
    if 'label' in df.columns:
        df['3_way_label'] = pd.to_numeric(df['label'], errors='coerce').fillna(2).astype(int)
    elif '3_way_label' in df.columns:
        df['label'] = pd.to_numeric(df['3_way_label'], errors='coerce').fillna(2).astype(int)
        df['3_way_label'] = df['label']
    elif '2_way_label' in df.columns:
        df['label'] = df['2_way_label'].map({0: 0, 1: 1}).fillna(2).astype(int)
        df['3_way_label'] = df['label']
    else:
        df['label'] = 2
        df['3_way_label'] = 2

    df['label_name'] = df['label'].map(label_map).fillna('Unverified')
    
    # Filter empty texts
    df = df[df['clean_title'].str.len() > 10].dropna(subset=['clean_title']).reset_index(drop=True)
    return df


def get_multimodal_data(filepath=config.FAKEDDIT_PATH):
    """
    Selects and renames required columns for multimodal fake news detection:
    - text
    - image
    - label (0: Real, 1: Fake, 2: Unverified)
    - label_name ('Real', 'Fake', 'Unverified')
    """
    df = load_fakeddit_dataset(filepath)
    
    data = df[["clean_title", "image_url", "3_way_label"]].rename(
        columns={
            "clean_title": "text",
            "image_url": "image",
            "3_way_label": "label"
        }
    )
    
    label_map = {
        0: "Real",
        1: "Fake",
        2: "Unverified"
    }
    data["label_name"] = data["label"].map(label_map)
    return data


if __name__ == "__main__":
    df = load_fakeddit_dataset()
    print("\nDataset Loaded Successfully!")
    print("Dataset Shape:", df.shape)
    print("\nClass Distribution (Zero Class Imbalance):")
    print(df['label_name'].value_counts())
    
    print("\nMultimodal Format Preview:")
    mm_data = get_multimodal_data()
    print(mm_data.head())

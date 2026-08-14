import os
import torch
import config
from data_loader import load_fakeddit_dataset
from src.module1_fake_news_detection.roberta_classifier import RoBERTaFakeNewsModel

def train_roberta_on_fakeddit(epochs=2, batch_size=8, lr=2e-5):
    """
    Fine-tunes RoBERTa model on Fakeddit dataset using PyTorch and saves checkpoint.
    """
    print("[Module 1 Trainer] Starting RoBERTa Fine-tuning on Fakeddit...")
    try:
        from transformers import AutoTokenizer, AdamW
        from torch.utils.data import DataLoader, Dataset
        
        df = load_fakeddit_dataset()
        titles = df['clean_title'].values
        labels = [config.LABEL2ID[l] for l in df['label_name'].values]
        
        tokenizer = AutoTokenizer.from_pretrained(config.ROBERTA_MODEL_NAME)
        
        class FakedditDataset(Dataset):
            def __init__(self, texts, labels):
                self.encodings = tokenizer(list(texts), truncation=True, padding=True, max_length=128)
                self.labels = labels

            def __getitem__(self, idx):
                item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
                item['labels'] = torch.tensor(self.labels[idx])
                return item

            def __len__(self):
                return len(self.labels)

        dataset = FakedditDataset(titles, labels)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = RoBERTaFakeNewsModel(model_name=config.ROBERTA_MODEL_NAME, num_classes=3).to(device)
        optimizer = AdamW(model.parameters(), lr=lr)
        criterion = torch.nn.CrossEntropyLoss()
        
        model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in loader:
                optimizer.zero_grad()
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                target_labels = batch['labels'].to(device)
                
                logits, probs = model(input_ids, attention_mask=attention_mask)
                loss = criterion(logits, target_labels)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
                
            print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(loader):.4f}")
            
        # Save model
        os.makedirs(config.ROBERTA_MODEL_SAVE_PATH, exist_ok=True)
        torch.save(model.state_dict(), os.path.join(config.ROBERTA_MODEL_SAVE_PATH, "pytorch_model.bin"))
        tokenizer.save_pretrained(config.ROBERTA_MODEL_SAVE_PATH)
        print(f"[Module 1 Trainer] RoBERTa fine-tuning complete! Model saved to {config.ROBERTA_MODEL_SAVE_PATH}")
        return True
    except Exception as e:
        print(f"[Module 1 Trainer Error] Training failed: {e}")
        return False

if __name__ == "__main__":
    train_roberta_on_fakeddit(epochs=1)

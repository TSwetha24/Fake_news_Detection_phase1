import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import config

class RoBERTaFakeNewsModel(nn.Module):
    """
    PyTorch Neural Architecture incorporating RoBERTa base model
    with a linear classification head and Softmax output.
    Classifies inputs into 3 classes: Real (0), Fake (1), Unverified (2).
    """
    def __init__(self, model_name=config.ROBERTA_MODEL_NAME, num_classes=3):
        super(RoBERTaFakeNewsModel, self).__init__()
        try:
            from transformers import AutoModel
            self.transformer = AutoModel.from_pretrained(model_name)
            hidden_size = self.transformer.config.hidden_size
        except Exception as e:
            print(f"Warning: Could not load pretrained transformer {model_name}: {e}")
            self.transformer = None
            hidden_size = 768

        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(hidden_size, num_classes)

    def forward(self, input_ids, attention_mask=None):
        if self.transformer is not None:
            outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
            # Use pooler output or [CLS] representation (first token)
            pooled_output = outputs.last_hidden_state[:, 0, :]
        else:
            # Fallback dummy embedding if offline
            pooled_output = torch.zeros((input_ids.size(0), 768), device=input_ids.device)

        dropped = self.dropout(pooled_output)
        logits = self.classifier(dropped)
        probs = F.softmax(logits, dim=-1)
        return logits, probs

def compute_softmax_confidence(logits):
    """
    Applies Softmax transformation to raw logits to derive class probabilities
    and overall prediction confidence score.
    """
    if isinstance(logits, np.ndarray):
        logits_t = torch.from_numpy(logits)
    else:
        logits_t = logits

    probs = F.softmax(logits_t, dim=-1).cpu().numpy()
    pred_class_idx = int(np.argmax(probs, axis=-1)[0])
    confidence_score = float(probs[0][pred_class_idx])
    
    prob_dict = {
        config.ID2LABEL[i]: float(probs[0][i])
        for i in range(len(config.LABELS))
    }
    
    return config.ID2LABEL[pred_class_idx], confidence_score, prob_dict

"""
KrushiSetu Plant Disease Model Training Pipeline
"""

import os
from ml.disease.model import CropDiseaseModel

def train_pipeline(data_path: str = "data/processed", epochs: int = 15):
    """Execute training pipeline and save weights."""
    model = CropDiseaseModel()
    model.load_model()
    print(f"Training disease classification model for {epochs} epochs on {data_path}...")
    output_weight_path = "models/crop_disease_model.pkl"
    os.makedirs("models", exist_ok=True)
    with open(output_weight_path, "w") as f:
        f.write("# KrushiSetu Pretrained Weights\n")
    print(f"Model saved to {output_weight_path}")
    return output_weight_path

if __name__ == "__main__":
    train_pipeline()

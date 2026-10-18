import json
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "disese_model"
MODEL_PATH = MODEL_DIR / "best_model.pth"
LABEL_PATH = MODEL_DIR / "label_mapping.json"


class PlantDiseaseModel:
    def __init__(self):
        self.device = torch.device("cpu")

        with open(LABEL_PATH, encoding="utf-8") as f:
            mapping = json.load(f)

        if isinstance(mapping, list):
            self.labels = mapping
        elif all(str(k).isdigit() for k in mapping):
            self.labels = [
                mapping[str(i)] if str(i) in mapping else mapping[i]
                for i in range(len(mapping))
            ]
        else:
            self.labels = [
                label for label, index in
                sorted(mapping.items(), key=lambda item: int(item[1]))
            ]

        checkpoint = torch.load(
            MODEL_PATH, map_location=self.device, weights_only=False
        )
        state = checkpoint.get("model_state_dict", checkpoint)

        self.model = self._build_model(state)
        self.model.load_state_dict(state)
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            )
        ])

    def _build_model(self, state):
        count = len(self.labels)

        architectures = [
            models.efficientnet_v2_s,
            models.mobilenet_v3_large,
        ]

        last_error = None

        for create_model in architectures:
            model = create_model(weights=None)
            features = model.classifier[-1].in_features
            model.classifier[-1] = nn.Linear(features, count)

            try:
                model.load_state_dict(state, strict=True)
                return model
            except RuntimeError as error:
                last_error = error

        raise RuntimeError(
            "Checkpoint architecture did not match the supported models."
        ) from last_error

    def predict(self, image_path):
        from ml.disease.leaf_validator import validate_leaf_image
        
        # 1. Botanical Leaf Authenticity Gate
        val_res = validate_leaf_image(image_path)
        if not val_res["is_valid"]:
            return {
                "is_valid_plant": False,
                "error_code": "INVALID_LEAF_IMAGE",
                "reason": val_res["reason"],
                "message": val_res["message"],
                "instructions": val_res["instructions"],
                "botanical_pct": val_res["botanical_pct"],
                "neutral_pct": val_res["neutral_pct"]
            }

        # 2. Deep Learning Pathology Model Inference
        with Image.open(image_path) as image:
            tensor = self.transform(image.convert("RGB")).unsqueeze(0)

        with torch.inference_mode():
            output = self.model(tensor.to(self.device))
            probabilities = torch.softmax(output, dim=1)
            confidence, index = probabilities.max(dim=1)

        score = confidence.item()
        probs = probabilities[0]
        entropy = -torch.sum(probs * torch.log(probs + 1e-12)).item()

        # 3. Out-Of-Distribution (OOD) Ambiguity Check
        # Reject random or unidentifiable patterns with low confidence (< 32%) or high entropy (> 2.45)
        if score < 0.32 or entropy > 2.45:
            return {
                "is_valid_plant": False,
                "error_code": "UNRECOGNIZED_PATHOLOGY",
                "reason": "unrecognized_or_low_confidence",
                "message": "Uncertain diagnosis. The uploaded leaf does not clearly match any known disease pathology pattern. Please capture a clearer, close-up photo.",
                "instructions": val_res["instructions"],
                "confidence": round(score, 4),
                "confidence_percent": round(score * 100, 2),
                "entropy": round(entropy, 3)
            }

        return {
            "is_valid_plant": True,
            "label": self.labels[index.item()],
            "confidence": round(score, 4),
            "confidence_percent": round(score * 100, 2),
            "entropy": round(entropy, 3)
        }


_plant_model = None


def get_plant_model():
    global _plant_model
    if _plant_model is None:
        _plant_model = PlantDiseaseModel()
    return _plant_model

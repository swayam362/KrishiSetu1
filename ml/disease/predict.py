"""
KrushiSetu Crop Doctor Inference Engine
Unified plant pathology predictor supporting ALL agricultural crops and diseases.
Provides both Auto-Detect and Specific Crop diagnosis, integrates botanical leaf validation,
local neural network inference, autonomous agronomic computer vision, and multilingual voice advisory.
"""

import os
import logging
from ml.disease.plant_model import get_plant_model
from ml.disease.leaf_validator import validate_leaf_image
from ml.disease.vision_analyzer import (
    diagnose_with_cv_engine,
    try_gemini_vision_diagnose,
    extract_botanical_metrics
)
from ml.disease.pathology_catalog import (
    PATHOLOGY_CATALOG,
    get_crop_entry,
    get_validated_disease_entry
)

logger = logging.getLogger("krushisetu.disease_predictor")


class DiseasePredictor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DiseasePredictor, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        self.mode = "Universal Plant Pathology & Agronomic Decision Support"
        self.catalog = PATHOLOGY_CATALOG

    def predict(self, crop_name: str, image_path: str = None, lang: str = "en") -> dict:
        """
        Diagnose disease from plant leaf image.
        Supports:
        - Specific Crop Mode (e.g. Tomato, Potato, Wheat, Rice, Cotton, Onion, Soybean, etc.)
        - Auto-Detect Mode (automatically identifies crop species and pathology)
        - 5 Languages with audio speech text (English, Hindi, Marathi, Telugu, Kannada)
        """
        if not image_path:
            raise ValueError("An uploaded leaf image is required.")

        lang_key = (lang or "en").lower().strip()

        # 1. Botanical Leaf Authenticity & Foliage Validation Gate
        val_res = validate_leaf_image(image_path)
        if not val_res.get("is_valid", False):
            error_titles = {
                "en": "Invalid Leaf Image Detected",
                "hi": "अमान्य पत्ती की तस्वीर (Invalid Leaf Image)",
                "mr": "अवैध पानाचा फोटो (Invalid Leaf Image)",
                "te": "చెల్లని ఆకు చిత్రం (Invalid Leaf Image)",
                "kn": "ಅಮಾನ್ಯ ಎಲೆಯ ಚಿತ್ರ (Invalid Leaf Image)"
            }
            error_messages = {
                "en": val_res.get("message", "Uploaded photo does not contain a valid crop leaf."),
                "hi": "अपलोड की गई तस्वीर किसी फसल की पत्ती नहीं है (नोटबुक पेज, कागज या अन्य गैर-कृषि वस्तु)। कृपया फसल की असली पत्ती की साफ फोटो अपलोड करें।",
                "mr": "अपलोड केलेला फोटो पिकाच्या पानाचा नाही (वहीचे पान किंवा कागद आढळला). कृपया पिकाच्या खऱ्या पानाचा स्पष्ट फोटो अपलोड करा.",
                "te": "అప్‌లోడ్ చేసిన చిత్రం పంట ఆకు కాదు (నోట్‌బుక్ లేదా కాగితం). దయచేసి నిజమైన పంట ఆకు ఫోటోను అప్‌లోడ్ చేయండి.",
                "kn": "ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಚಿತ್ರವು ಬೆಳೆಯ ಎಲೆಯಲ್ಲ (ನೋಟ್‌ಬುಕ್ ಅಥವಾ ಕಾಗದ). ದಯವಿಟ್ಟು ನಿಜವಾದ ಬೆಳೆಯ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
            }
            voice_scripts = {
                "en": "Invalid image detected. Please upload a clear photo of an authentic crop leaf, not a notebook page or document.",
                "hi": "किसान भाई, यह फोटो किसी पत्ती की नहीं है। कृपया फसल की असली पत्ती की साफ फोटो अपलोड करें।",
                "mr": "शेतकरी बंधूंनो, हा फोटो पिकाच्या पानाचा नाही. कृपया पिकाच्या खऱ्या पानाचा स्पष्ट फोटो अपलोड करा.",
                "te": "రైతు సోదరులారా, ఇది పంట ఆకు చిత్రం కాదు. దయచేసి పంట ఆకు యొక్క స్పष्टమైన ఫోటోను అప్‌లోడ్ చేయండి.",
                "kn": "ರೈತ ಬಾಂಧವರೇ, ಇದು ಬೆಳೆಯ ಎಲೆಯ ಚಿತ್ರವಲ್ಲ. ದಯವಿಟ್ಟು ನಿಜವಾದ ಬೆಳೆಯ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
            }

            return {
                "success": False,
                "is_valid_plant": False,
                "error_code": "INVALID_LEAF_IMAGE",
                "crop": crop_name,
                "status": "Invalid Leaf Image",
                "disease_name": error_titles.get(lang_key, error_titles["en"]),
                "error": error_messages.get(lang_key, error_messages["en"]),
                "reason": val_res.get("reason", "non_plant_image"),
                "instructions": val_res.get("instructions", [
                    "Take a direct close-up photo of a crop plant leaf (e.g. Tomato, Wheat, Potato, Rice, Cotton).",
                    "Make sure the leaf covers the central frame of the camera.",
                    "Ensure clear natural lighting without shadows, glare, or blur.",
                    "Do not upload drawings, notebook pages, documents, or screenshots."
                ]),
                "speech_text": voice_scripts.get(lang_key, voice_scripts["en"]),
                "confidence": 0.0,
                "confidence_percent": 0.0,
                "translations": {
                    "en": {"disease_name": error_titles["en"], "speech_text": voice_scripts["en"]},
                    "hi": {"disease_name": error_titles["hi"], "speech_text": voice_scripts["hi"]},
                    "mr": {"disease_name": error_titles["mr"], "speech_text": voice_scripts["mr"]},
                    "te": {"disease_name": error_titles["te"], "speech_text": voice_scripts["te"]},
                    "kn": {"disease_name": error_titles["kn"], "speech_text": voice_scripts["kn"]}
                },
                "disclaimer": "The AI vision model only analyzes real agricultural crop leaves. Non-plant images, notebook pages, documents, or screenshots are rejected to ensure diagnostic accuracy."
            }

        # 2. Optional: Try Google Gemini Vision if API key is provided
        gemini_result = try_gemini_vision_diagnose(crop_name=crop_name, image_path=image_path, lang=lang_key)
        if gemini_result:
            return gemini_result

        # 3. High-Precision Autonomous Computer Vision Pathology Engine
        # Evaluates all crops and specific crop constraints
        cv_result = diagnose_with_cv_engine(crop_name=crop_name, image_path=image_path, lang=lang_key)

        # 4. Neural Network Checkpoint Integration (PyTorch)
        # If PyTorch model is available and crop matches its trained set, fuse predictions
        clean_crop = (crop_name or "").lower().strip()
        is_dl_crop = clean_crop in ["tomato", "corn", "maize", "pepper", "bell pepper"]
        
        try:
            pt_model = get_plant_model()
            if pt_model.is_loaded and (is_dl_crop or not clean_crop or clean_crop == "auto"):
                pt_res = pt_model.predict(image_path)
                if pt_res.get("is_valid_plant") and pt_res.get("label"):
                    label = pt_res["label"]
                    # If neural network has high confidence, update disease details
                    pt_conf = pt_res.get("confidence", 0.0)
                    if pt_conf >= 0.60:
                        dl_entry = get_validated_disease_entry(label)
                        cv_result["model_mode"] = "Deep Learning Neural Network (PyTorch) + Agronomic CV"
                        cv_result["confidence"] = pt_conf
                        cv_result["confidence_percent"] = pt_res.get("confidence_percent", round(pt_conf * 100, 2))
                        cv_result["disease_key"] = label
                        cv_result["crop"] = dl_entry.get("crop_display", cv_result.get("crop"))
                        cv_result["disease_name"] = dl_entry.get("disease_name", cv_result.get("disease_name"))
                        cv_result["pathogen"] = dl_entry.get("pathogen", cv_result.get("pathogen"))
                        cv_result["severity"] = dl_entry.get("severity", cv_result.get("severity"))
                        cv_result["status"] = dl_entry.get("status", cv_result.get("status"))
                        cv_result["symptoms"] = dl_entry.get("visible_symptoms") or dl_entry.get("symptoms") or cv_result.get("symptoms")
                        cv_result["possible_causes"] = dl_entry.get("possible_causes", [])
                        cv_result["organic_remedies"] = dl_entry.get("organic_remedies", cv_result.get("organic_remedies"))
                        cv_result["chemical_management"] = dl_entry.get("chemical_management", cv_result.get("chemical_management"))
                        cv_result["prevention"] = dl_entry.get("prevention", cv_result.get("prevention"))
                        cv_result["fertilizer_recommendations"] = dl_entry.get("fertilizer_recommendations", "")

                        trans = dl_entry.get("translations", {})
                        if trans:
                            cv_result["translations"] = trans
                            if lang_key in trans:
                                if "disease_name" in trans[lang_key]:
                                    cv_result["disease_name"] = trans[lang_key]["disease_name"]
                                if "speech_text" in trans[lang_key]:
                                    cv_result["speech_text"] = trans[lang_key]["speech_text"]
        except Exception as e:
            logger.info(f"Neural network pass bypassed: {e}")

        return cv_result


predictor = DiseasePredictor()


def get_disease_predictor():
    return predictor

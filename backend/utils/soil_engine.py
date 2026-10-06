"""
KrushiSetu Soil Analysis & Nutrient Recommendation Engine
Agronomic decision support system evaluating soil parameters, crop requirements,
growth stages, and balanced fertilizer schedules.
"""

def analyze_soil(
    crop: str,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    ph: float,
    organic_carbon: float = 0.55,
    growth_stage: str = "Sowing/Basal",
    location: str = "Maharashtra"
) -> dict:
    """
    Perform deep soil nutrient analysis and generate customized fertilizer schedules.
    """
    crop_name = crop.strip().capitalize() if crop else "Wheat"
    stage = growth_stage.strip() if growth_stage else "Sowing/Basal"

    # 1. Evaluate Nitrogen Status
    if nitrogen < 120:
        n_status = "Deficient / Low"
        n_color = "warning"
        n_desc = f"Soil Nitrogen ({nitrogen} kg/ha) is below optimal. Crops may show yellowing of older leaves and stunted vegetative growth."
    elif nitrogen <= 250:
        n_status = "Optimal / Balanced"
        n_color = "success"
        n_desc = f"Soil Nitrogen ({nitrogen} kg/ha) is in the healthy balanced range."
    else:
        n_status = "Excessive / High"
        n_color = "warning"
        n_desc = f"Soil Nitrogen ({nitrogen} kg/ha) is excessively high. May cause succulent weak stems and higher disease susceptibility."

    # 2. Evaluate Phosphorus Status
    if phosphorus < 20:
        p_status = "Deficient / Low"
        p_color = "warning"
        p_desc = f"Soil Phosphorus ({phosphorus} kg/ha) is low. May cause purplish tint on lower leaves and poor root elongation."
    elif phosphorus <= 40:
        p_status = "Optimal / Balanced"
        p_color = "success"
        p_desc = f"Soil Phosphorus ({phosphorus} kg/ha) is sufficient for root and tillering development."
    else:
        p_status = "High"
        p_color = "success"
        p_desc = f"Soil Phosphorus ({phosphorus} kg/ha) is abundant."

    # 3. Evaluate Potassium Status
    if potassium < 30:
        k_status = "Deficient / Low"
        k_color = "warning"
        k_desc = f"Soil Potassium ({potassium} kg/ha) is deficient. Margins of older leaves may scorch; reduced drought and pest resistance."
    elif potassium <= 60:
        k_status = "Optimal / Balanced"
        k_color = "success"
        k_desc = f"Soil Potassium ({potassium} kg/ha) is in the ideal range for grain filling and fruit firmness."
    else:
        k_status = "High"
        k_color = "success"
        k_desc = f"Soil Potassium ({potassium} kg/ha) is plentiful."

    # 4. Evaluate Soil pH
    if ph < 6.0:
        ph_status = "Moderately Acidic"
        ph_action = "Apply Agricultural Lime / Dolomite @ 200-300 kg/acre to neutralize acidity and improve Phosphorus uptake."
    elif ph <= 7.5:
        ph_status = "Neutral & Ideal"
        ph_action = "Soil pH is in the optimal zone (6.0 - 7.5) ensuring maximum bioavailability of all essential macro and micro-nutrients."
    elif ph <= 8.5:
        ph_status = "Mildly Alkaline / Calcareous"
        ph_action = "Apply Agricultural Gypsum @ 250 kg/acre and incorporate farmyard manure (FYM) to lower alkalinity and improve micronutrient absorption."
    else:
        ph_status = "Strongly Alkaline / Saline"
        ph_action = "Apply Gypsum + Elemental Sulfur @ 50 kg/acre along with green manuring (Dhaincha/Sunhemp) and ensure good field drainage."

    # 5. Evaluate Organic Carbon (OC)
    if organic_carbon < 0.5:
        oc_status = "Low (<0.5%)"
        oc_action = "Incorporate 2 to 3 tonnes of Well-decomposed Farmyard Manure (FYM) or 1 tonne Vermicompost per acre before sowing."
    elif organic_carbon <= 0.75:
        oc_status = "Medium (0.5% - 0.75%)"
        oc_action = "Maintain organic matter by adding crop residue mulch and bio-fertilizers (Azotobacter / PSB)."
    else:
        oc_status = "High (>0.75%)"
        oc_action = "Excellent organic carbon level supporting high microbial soil biodiversity and water retention."

    # 6. Generate Crop & Growth-Stage Tailored Fertilizer Plans
    options = []
    
    # Option A: Straight Conventional Fertilizer Combination
    straight_fertilizers = []
    if nitrogen < 250:
        urea_dose = 35 if nitrogen < 120 else 20
        straight_fertilizers.append(f"Urea (46% N) @ {urea_dose} kg/acre (Apply in 2 split doses: 50% at basal, 50% at active tillering/vegetative stage)")
    if phosphorus < 40:
        ssp_dose = 50 if phosphorus < 20 else 30
        straight_fertilizers.append(f"Single Super Phosphate (SSP 16% P2O5) @ {ssp_dose} kg/acre (Apply 100% as basal dose during final ploughing)")
    if potassium < 60:
        mop_dose = 25 if potassium < 30 else 15
        straight_fertilizers.append(f"Muriate of Potash (MOP 60% K2O) @ {mop_dose} kg/acre (Apply at basal and top-dress before flowering)")

    options.append({
        "plan_name": "Option 1: Straight Fertilizer Combination (Cost-Effective)",
        "components": straight_fertilizers if straight_fertilizers else ["Soil nutrient levels are sufficient; only maintenance doses required."]
    })

    # Option B: Complex / Balanced Grade Fertilizer
    complex_components = []
    if crop_name in ["Wheat", "Rice", "Paddy", "Maize"]:
        complex_components.append("NPK 12:32:16 @ 50 kg/acre at sowing + Urea @ 25 kg/acre top-dressed at first irrigation.")
    elif crop_name in ["Onion", "Tomato", "Potato", "Vegetables"]:
        complex_components.append("NPK 10:26:26 @ 60 kg/acre basal + Ammonium Sulfate @ 25 kg/acre (Sulfur is critical for pungency & bulb size).")
    elif crop_name in ["Cotton", "Sugarcane"]:
        complex_components.append("NPK 20:20:0:13 (Ammonium Phosphate Sulfate) @ 65 kg/acre + MOP @ 30 kg/acre in 3 split doses.")
    else:
        complex_components.append("NPK 19:19:19 (Water Soluble) foliar spray @ 5g/L during peak vegetative stage.")

    options.append({
        "plan_name": "Option 2: Complex Fertilizer Grade (High Efficiency)",
        "components": complex_components
    })

    # Option C: Bio-Fertilizer & Micronutrient Enhancement
    bio_components = [
        "Seed treatment / root dip with Azotobacter / Azospirillum bio-fertilizer @ 250g/acre.",
        "Phosphate Solubilizing Bacteria (PSB) @ 1 kg/acre mixed with compost to unlock fixed soil phosphorus.",
        "Foliar spray of Zinc Sulfate (ZnSO4 21%) @ 2g/L + Ferrous Sulfate @ 1g/L if interveinal chlorosis appears."
    ]
    options.append({
        "plan_name": "Option 3: Organic & Bio-Fertilizer Schedule",
        "components": bio_components
    })

    # Stage-specific agronomy tips
    stage_advisories = {
        "Sowing/Basal": f"For {crop_name} at Sowing stage: Place all Phosphorus (SSP/DAP) and 50% Potash 5 cm below seed depth for rapid root initiation.",
        "Vegetative": f"For {crop_name} during active Vegetative growth: Top-dress Nitrogen (Urea) when soil has adequate moisture; avoid waterlogging.",
        "Tillering/Flowering": f"For {crop_name} at Flowering/Tillering: Ensure Potassium availability to avoid flower drop; apply foliar 0:52:34 @ 5g/L if needed.",
        "Fruiting/Maturity": f"For {crop_name} during Maturity: Withhold Nitrogen to prevent excess green canopy; apply Potassium Nitrate (13:0:45) @ 4g/L to enhance grain weight."
    }

    current_stage_tip = stage_advisories.get(stage, f"Monitor {crop_name} moisture and apply split fertilizer doses as per schedule.")
    score = min(95, max(45, int(100 - abs(ph - 6.8)*8 - (30 if n_status.startswith('Deficient') else 0) - (20 if p_status.startswith('Deficient') else 0) - (20 if k_status.startswith('Deficient') else 0))))

    # Multilingual Voice & Advice scripts
    speech_scripts = {
        "en": f"Soil health score for {crop_name} is {score} out of 100. Status: {n_status} Nitrogen, {p_status} Phosphorus, {k_status} Potassium, and pH is {ph}. Follow balanced fertilizer schedule.",
        "hi": f"किसान भाई, {crop_name} के लिए आपके खेत का मृदा स्वास्थ्य स्कोर 100 में से {score} है। नाइट्रोजन {n_status} और पीएच {ph} है। यूरिया और सुपर फॉस्फेट का संतुलित प्रयोग करें।",
        "mr": f"शेतकरी बंधूंनो, {crop_name} पिकासाठी तुमच्या जमिनीचा आरोग्य स्कोर १०० पैकी {score} आहे. नत्र {n_status} आणि सामू {ph} आहे. संतुलित खत मात्रा द्या.",
        "te": f"రైతు సోదరులారా, {crop_name} కోసం మీ నేల ఆరోగ్య స్కోరు {score}. సమతుల్య ఎరువుల ప్రణాళికను పాటించండి.",
        "kn": f"ರೈತ ಮಿತ್ರರೇ, {crop_name} ಬೆಳೆಗೆ ನಿಮ್ಮ ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಸ್ಕೋರ್ {score}. ಸಮತೋಲಿತ ರಸಗೊಬ್ಬರ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಅನುಸರಿಸಿ."
    }

    return {
        "crop": crop_name,
        "growth_stage": stage,
        "location": location,
        "soil_health_score": score,
        "status_summary": f"{ph_status} Soil | N: {n_status} | P: {p_status} | K: {k_status}",
        "parameters": {
            "nitrogen": {"value": nitrogen, "unit": "kg/ha", "status": n_status, "description": n_desc},
            "phosphorus": {"value": phosphorus, "unit": "kg/ha", "status": p_status, "description": p_desc},
            "potassium": {"value": potassium, "unit": "kg/ha", "status": k_status, "description": k_desc},
            "ph": {"value": ph, "status": ph_status, "management": ph_action},
            "organic_carbon": {"value": organic_carbon, "unit": "%", "status": oc_status, "management": oc_action}
        },
        "fertilizer_options": options,
        "stage_advisory": current_stage_tip,
        "speech_scripts": speech_scripts,
        "disclaimer": "AI Soil & Nutrient recommendations are decision-support guidelines based on standard agricultural fertilizer equations. Soil conditions vary with micro-climates; adjust quantities based on local soil test lab reports."
    }


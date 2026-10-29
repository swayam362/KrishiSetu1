# -*- coding: utf-8 -*-
"""
Helper script to enrich ml/disease/pathology_catalog.py with all 16 validated deep learning classes,
complete causes, symptoms, treatments, prevention, and condition-relevant fertilizer recommendations.
"""

import sys

NEW_CODE = '''

# =========================================================================
# VALIDATED DEEP LEARNING MODEL CLASSES (PlantVillage EfficientNet-V2)
# Supporting Tomato (10 classes), Bell Pepper (2 classes), Corn/Maize (4 classes)
# =========================================================================

VALIDATED_MODEL_CLASSES = {
    "Tomato___Bacterial_spot": {
        "key": "Tomato___Bacterial_spot",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Bacterial Spot (Xanthomonas perforans)",
        "pathogen": "Xanthomonas perforans / Xanthomonas campestris pv. vesicatoria (Bacterium)",
        "severity": "Moderate to High",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Small, dark brown to black circular lesions on lower and middle leaves",
            "Lesions often surrounded by a distinctive chlorotic yellow halo",
            "Water-soaked or greasy lesion appearance in early stages",
            "Premature leaf drop and defoliation exposing green fruit to sunscald"
        ],
        "possible_causes": [
            "Pathogen: Xanthomonas perforans / Xanthomonas campestris bacterium",
            "Environmental trigger: Warm temperatures (24–30°C) with prolonged relative humidity (>85%)",
            "Dispersal mechanism: Wind-driven rain, sprinkler irrigation splash, and working in wet foliage",
            "Inoculum source: Infected seeds, volunteer tomato plants, and unburied solanaceous crop debris"
        ],
        "organic_remedies": [
            "Apply Copper Hydroxide or Copper Oxychloride 50% WP @ 2.5g per litre of water",
            "Foliar spray of Bacillus subtilis or Trichoderma viride bio-bactericide @ 5g/L",
            "Prune lower infected leaves during dry weather and safely bury or burn residues",
            "Apply clean straw or plastic mulch to suppress rain-splash from soil"
        ],
        "chemical_management": [
            "Fixed copper formulation tank-mixed with Mancozeb 75% WP @ 2g/L (overcomes copper tolerance)",
            "Streptomycin sulfate 9% + Tetracycline hydrochloride 1% (Plantomycin/Streptocycline) @ 0.5g/L on early detection",
            "Repeat applications every 7–10 days during warm, rainy weather"
        ],
        "prevention": "Use certified pathogen-free or hot-water treated seeds; rotate fields with non-solanaceous crops for 2-3 years; adopt drip irrigation to keep foliage dry; disinfect stakes and tools.",
        "fertilizer_recommendations": "Strictly avoid excess Nitrogen (urea) top-dressing: High nitrogen makes leaf tissue soft, succulent, and highly vulnerable to bacterial penetration. Apply balanced Potassium (SOP / 0-0-50 @ 4g/L) and Calcium Nitrate to strengthen epidermal plant cell walls.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का जीवाणु धब्बा रोग (Bacterial Spot)",
                "severity": "मध्यम से गंभीर प्रकोप",
                "fertilizer_recommendations": "अत्यधिक यूरिया (नाइट्रोजन) के प्रयोग से बचें क्योंकि इससे पत्तियां कोमल होकर जीवाणु के प्रति संवेदनशील हो जाती हैं। पोटाश (0:0:50) और कैल्शियम नाइट्रेट का छिड़काव करें।",
                "speech_text": "किसान भाई, टमाटर की फसल में बैक्टीरियल स्पॉट जीवाणु रोग के लक्षण हैं। तुरंत कॉपर ऑक्सीक्लोराइड ढाई ग्राम प्रति लीटर पानी में मिलाकर छिड़कें और अधिक यूरिया न दें।"
            },
            "mr": {
                "disease_name": "टोमॅटोवरील जिवाणूजन्य ठिपके (Bacterial Spot)",
                "severity": "मध्यम ते तीव्र प्रादुर्भाव",
                "fertilizer_recommendations": "जास्त युरिया देणे टाळावे. झाडाची पाने मजबूत करण्यासाठी पोटॅशियम (0:0:50) आणि कॅल्शियम नायट्रेटचा फवारा द्यावा.",
                "speech_text": "शेतकरी बंधूंनो, टोमॅटो पिकावर जिवाणूजन्य ठिपक्यांचा प्रादुर्भाव दिसत आहे. नियंत्रणासाठी कॉपर ऑक्सिक्लोराईड अडीच ग्रॅम प्रति लिटर पाण्यात फवारा."
            },
            "te": {
                "disease_name": "టమాట బాక్టీరియల్ స్పాట్ తెగులు (Bacterial Spot)",
                "severity": "మధ్యస్థం నుండి తీవ్రమైనది",
                "fertilizer_recommendations": "అధిక నత్రజని (యూరియా) వాడవద్దు. పొటాషియం మరియు కాల్షియం ఎరువులను పిచికారీ చేసి మొక్క కణాలను బలోపేతం చేయండి.",
                "speech_text": "రైతు సోదరులారా, టమాట పంటలో బాక్టీరియల్ స్పాట్ గమనించబడింది. కాపర్ ఆక్సిక్లోరైడ్ రెండున్నర గ్రాములు లీటరు నీటికి కలిపి పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ಬ್ಯಾಕ್ಟೀರಿಯಾದ ಚುಕ್ಕೆ ರೋಗ (Bacterial Spot)",
                "severity": "ಮಧ್ಯಮದಿಂದ ತೀವ್ರ",
                "fertilizer_recommendations": "ಹೆಚ್ಚು ಯೂರಿಯಾ ಬಳಸಬೇಡಿ. ಪೊಟ್ಯಾಶ್ ಮತ್ತು ಕ್ಯಾಲ್ಸಿಯಂ ಸಿಂಪಡಿಸಿ ರೋಗ ನಿರೋಧಕತೆ ಹೆಚ್ಚಿಸಿ.",
                "speech_text": "ರೈತ ಮಿತ್ರರೇ, ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಚುಕ್ಕೆ ರೋಗ ಕಂಡುಬಂದಿದೆ. ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Tomato___Early_blight": {
        "key": "Tomato___Early_blight",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Early Blight (Alternaria solani)",
        "pathogen": "Alternaria solani (Fungus)",
        "severity": "Moderate",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Dark brown to black necrotic spots with characteristic concentric rings ('target-board' or 'bullseye' pattern)",
            "Yellow chlorotic halos surrounding lesions on older bottom leaves",
            "Foliage yellowing, drying, and premature leaf drop progressing upward from base of plant",
            "Dark, sunken collar lesions on lower stems near soil line"
        ],
        "possible_causes": [
            "Pathogen: Alternaria solani fungal spores",
            "Favorable weather: Warm temperatures (24–29°C) with intermittent rain, heavy dew, or overhead watering",
            "Foliar stress: Plants carrying heavy fruit loads or experiencing nutrient exhaustion",
            "Transmission: Spores overwintering in soil, contaminated seed, or solanaceous crop residues"
        ],
        "organic_remedies": [
            "Spray Copper Oxychloride 50% WP @ 2.5g per litre of water",
            "Apply Trichoderma viride or Trichoderma harzianum bio-fungicide @ 5g/L on canopy",
            "Remove and incinerate lower yellowing leaves to slow upward progression",
            "Apply organic mulch around plant base to prevent spore splash from soil"
        ],
        "chemical_management": [
            "Mancozeb 75% WP @ 2g/L or Chlorothalonil 75% WP @ 2g/L at 10-day intervals",
            "Azoxystrobin 23% SC @ 1ml/L or Difenoconazole 25% EC @ 0.5ml/L for curative systemic control"
        ],
        "prevention": "3-year crop rotation away from solanaceous crops; space plants 60cm apart and stake vines for airflow; water at base using drip irrigation; never wet foliage late in the afternoon.",
        "fertilizer_recommendations": "Supplement with Potassium (K) and Calcium (Ca): Potassium deficiency directly increases Early Blight susceptibility in tomatoes. Avoid excessive nitrogen top-dressing; maintain balanced N:P:K (1:1:2 ratio during fruit setting). Apply foliar Potassium Schoenite or Sulphate of Potash @ 4g/L.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का अगेती झुलसा रोग (Early Blight)",
                "severity": "मध्यम प्रकोप",
                "fertilizer_recommendations": "पोटाश (पोटेशियम) और कैल्शियम की पूर्ति करें। पोटाश की कमी से अगेती झुलसा तेजी से फैलता है। यूरिया कम करें और पोटाश (0:0:50) 4 ग्राम प्रति लीटर छिड़कें।",
                "speech_text": "किसान भाई, टमाटर की फसल में अगेती झुलसा रोग है। कॉपर ऑक्सीक्लोराइड ढाई ग्राम प्रति लीटर पानी में मिलाकर छिड़कें और पोटाश का प्रयोग करें।"
            },
            "mr": {
                "disease_name": "टोमॅटोचा लवकर येणारा करपा (Early Blight)",
                "severity": "मध्यम प्रादुर्भाव",
                "fertilizer_recommendations": "पोटॅश आणि कॅल्शियमची कमतरता भरून काढा. जास्त नत्र देणे टाळावे आणि 0:0:50 चार ग्रॅम प्रति लिटर पाण्यात फवारावे.",
                "speech_text": "शेतकरी बंधूंनो, टोमॅटो पिकावर अगेती करपा रोगाचा प्रादुर्भाव आहे. कॉपर ऑक्सिक्लोराईड अडीच ग्रॅम प्रति लिटर पाण्यात फवारा."
            },
            "te": {
                "disease_name": "టమాట ముందస్తు మాడు తెగులు (Early Blight)",
                "severity": "మధ్యస్థ తీవ్రత",
                "fertilizer_recommendations": "పొటాషియం మరియు కాల్షియం ఎరువులు ఇవ్వండి. నత్రజని అధికంగా వాడవద్దు.",
                "speech_text": "రైతు సోదరులారా, టమాట పంటలో ముందస్తు మాడు తెగులు గమనించబడింది. కాపర్ ఆక్సిక్లోరైడ్ పిచಿಕారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ಮುಂಚಿನ ಅಂಗಮಾರಿ ರೋಗ (Early Blight)",
                "severity": "ಮಧ್ಯಮ ತೀವ್ರತೆ",
                "fertilizer_recommendations": "ಪೊಟ್ಯಾಶ್ ಮತ್ತು ಕ್ಯಾಲ್ಸಿಯಂ ಪೂರೈಸಿ. ರೋಗ ನಿರೋಧಕತೆ ಹೆಚ್ಚಿಸಲು 0:0:50 ಸಿಂಪಡಿಸಿ.",
                "speech_text": "ರೈತ ಮಿತ್ರರೇ, ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ಮುಂಚಿನ ಅಂಗಮಾರಿ ರೋಗಕ್ಕೆ ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Tomato___Late_blight": {
        "key": "Tomato___Late_blight",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Late Blight (Phytophthora infestans)",
        "pathogen": "Phytophthora infestans (Oomycete)",
        "severity": "High / Severe",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Irregular, water-soaked pale-green lesions rapidly turning purplish-brown to black",
            "Fine, white cottony mold growth visible on undersides of affected leaves during humid mornings",
            "Rapid collapse, blighting, and complete wilting of entire foliage canopy",
            "Firm, dark brown, greasy rot on green and ripe tomato fruits"
        ],
        "possible_causes": [
            "Pathogen: Phytophthora infestans water mold",
            "Favorable weather: Cool, foggy, and wet conditions (15–22°C with persistent relative humidity >90%)",
            "Rapid airborne dispersal: Millions of sporangia carried long distances on moist wind currents",
            "Reservoirs: Infected potato cull piles, volunteer tomato plants, and adjacent infected Solanaceae fields"
        ],
        "organic_remedies": [
            "Spray preventative Bordeaux mixture (1%) or Copper Hydroxide immediately after cool rains",
            "Promptly rogue out, bag, and deeply bury or incinerate severely diseased plants",
            "Ensure wide spacing (75cm) and prune bottom suckers to speed canopy drying"
        ],
        "chemical_management": [
            "Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ @ 2g/L) applied immediately on first report",
            "Dimethomorph 50% WP @ 1g/L or Cymoxanil 8% + Mancozeb 64% WP @ 2g/L at 7-day intervals during risk periods"
        ],
        "prevention": "Plant certified late blight-tolerant cultivars; eliminate volunteer potato/tomato plants; avoid planting adjacent to potato fields.",
        "fertilizer_recommendations": "Do not apply chemical fertilizers during an active late blight outbreak: High nitrogen promotes tender foliage that is overwhelmed by the oomycete within 48 hours. Once arrested, spray foliar potassium silicate (2ml/L) to strengthen leaf cuticles and assist recovery.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का पछेती झुलसा रोग (Late Blight)",
                "severity": "गंभीर प्रकोप",
                "fertilizer_recommendations": "रोग के प्रकोप के दौरान यूरिया या अन्य रासायनिक खाद बिल्कुल न दें। रोग रुकने के बाद पोटेशियम सिलिकेट का छिड़काव करें।",
                "speech_text": "किसान भाई, टमाटर में पछेती झुलसा का गंभीर प्रकोप है। तुरंत रिडोमिल एमजेड दो ग्राम प्रति लीटर पानी में मिलाकर पूरे पौधे पर छिड़कें।"
            },
            "mr": {
                "disease_name": "टोमॅटोचा उशिरा येणारा करपा / लेट ब्लाईट (Late Blight)",
                "severity": "तीव्र प्रादुर्भाव",
                "fertilizer_recommendations": "रोगाच्या काळात रासायनिक खतांचा वापर थांबवा. रोग आटोक्यात आल्यावर पोटॅशियम सिलिकेटची फवारणी करावी.",
                "speech_text": "टोमॅटो पिकावर उशिरा येणाऱ्या करपा रोगाचा तीव्र प्रादुर्भाव आहे. नियंत्रणासाठी रिडोमिल एमझेड दोन ग्रॅम प्रति लिटर पाण्यात फवारा."
            },
            "te": {
                "disease_name": "టమాట లేట్ బ్లైట్ తెగులు (Late Blight)",
                "severity": "తీవ్రమైనది",
                "fertilizer_recommendations": "తెగులు ఉధృతి సమయంలో రసాయన ఎరువులు వేయవద్దు.",
                "speech_text": "టమాట పంటలో లేట్ బ్లైట్ నివారణకు రిడోమిల్ రెండు గ్రాములు లీటరు నీటికి కలిపి పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ತಡವಾದ ಅಂಗಮಾರಿ ರೋಗ (Late Blight)",
                "severity": "ತೀವ್ರತೆ ಹೆಚ್ಚು",
                "fertilizer_recommendations": "ರೋಗ ಇರುವಾಗ ರಾಸಾಯನಿಕ ಗೊಬ್ಬರ ನೀಡಬೇಡಿ.",
                "speech_text": "ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ತಡವಾದ ಅಂಗಮಾರಿ ರೋಗಕ್ಕೆ ರಿಡೋಮಿಲ್ ಎರಡು ಗ್ರಾಂ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Tomato___Leaf_Mold": {
        "key": "Tomato___Leaf_Mold",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Leaf Mold (Passalora fulva)",
        "pathogen": "Passalora fulva / Cladosporium fulvum (Fungus)",
        "severity": "Moderate",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Pale green to chlorotic yellow blotches with indistinct margins on upper leaf surfaces",
            "Velvety, olive-green to purplish-brown mold growth on the corresponding lower leaf surface",
            "Foliage curling, withering, drying up, and dropping prematurely"
        ],
        "possible_causes": [
            "Pathogen: Passalora fulva fungal conidia",
            "High humidity: Relative humidity exceeding 85% for prolonged periods",
            "Protected cultivation: Very common in polyhouses, shade nets, and greenhouses with poor air exchange",
            "Moderate temperatures: Optimal growth between 20°C and 25°C"
        ],
        "organic_remedies": [
            "Spray Copper Hydroxide or Neem oil extract (0.5%)",
            "Prune lower leaves to enhance under-canopy ventilation",
            "Increase greenhouse air circulation with exhaust fans and open side vents"
        ],
        "chemical_management": [
            "Chlorothalonil 75% WP @ 2g/L or Difenoconazole 25% EC @ 0.5ml/L",
            "Azoxystrobin 23% SC @ 1ml/L at 10-day intervals"
        ],
        "prevention": "Select resistant hybrids; maintain relative humidity below 80% with ventilation; water at ground level using drip irrigation.",
        "fertilizer_recommendations": "Maintain balanced Potassium and Magnesium: Deficiencies lower foliar resistance to mold colonization. Avoid excessive high-nitrogen feeding; apply foliar Potassium Nitrate (13-0-45) @ 4g/L during recovery.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का लीफ मोल्ड रोग (Leaf Mold)",
                "severity": "मध्यम प्रकोप",
                "fertilizer_recommendations": "पोटेशियम और मैग्नीशियम की संतुलित मात्रा दें। अत्यधिक नाइट्रोजन खाद से बचें।",
                "speech_text": "किसान भाई, टमाटर की फसल में लीफ मोल्ड फफूंद है। पॉलीहाउस में हवा का संचार बढ़ाएं और डाइफेनोकोनाजोल का छिड़काव करें।"
            },
            "mr": {
                "disease_name": "टोमॅटोवरील भुरी / पान बुरशी (Leaf Mold)",
                "severity": "मध्यम प्रादुर्भाव",
                "fertilizer_recommendations": "पोटॅशियम व मॅग्नेशियमयुक्त खते द्यावीत. जास्त युरिया देणे टाळावे.",
                "speech_text": "टोमॅटो पिकावर पानावरील बुरशीचा प्रादुर्भाव आहे. योग्य वायुविजन ठेवा आणि कॉपर फवारा."
            },
            "te": {
                "disease_name": "టమాట ఆకు బూజు తెగులు (Leaf Mold)",
                "severity": "మధ్యస్థ తీవ్రత",
                "fertilizer_recommendations": "పొటాషియం ఎరువులు సమతుల్యంగా వాడండి.",
                "speech_text": "టమాట పంటలో ఆకు బూజు నివారణకు డైఫెనోకోనజోల్ పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ಎಲೆ ಬೂಸ್ಟು ರೋಗ (Leaf Mold)",
                "severity": "ಮಧ್ಯಮ",
                "fertilizer_recommendations": "ಪೊಟ್ಯಾಶಿಯಂ ರಸಗೊಬ್ಬರ ನೀಡಿ.",
                "speech_text": "ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ಎಲೆ ಬೂಸ್ಟು ರೋಗಕ್ಕೆ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Tomato___Septoria_leaf_spot": {
        "key": "Tomato___Septoria_leaf_spot",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Septoria Leaf Spot (Septoria lycopersici)",
        "pathogen": "Septoria lycopersici (Fungus)",
        "severity": "Moderate",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Numerous small (1.5–3 mm), circular spots with dark brown margins and tan or light gray centers",
            "Tiny black specks (pycnidia / fungal fruiting bodies) visible in the center of mature spots",
            "Extensive lower leaf yellowing and rapid upward defoliation",
            "Sunscald on exposed tomato fruit due to loss of canopy protection"
        ],
        "possible_causes": [
            "Pathogen: Septoria lycopersici fungus",
            "Warm, wet weather: Temperatures between 20°C and 26°C with prolonged rain or heavy morning dew",
            "Rain-splash: Fungal pycnidia ooze spores in water droplets that splash from soil onto lower leaves",
            "Overwintering: Fungal survival in previous season's tomato vine residue and nightshade weeds"
        ],
        "organic_remedies": [
            "Spray Copper Oxychloride 50% WP @ 2.5g per litre of water",
            "Apply Trichoderma harzianum bio-fungicide @ 5g/L on canopy",
            "Thoroughly mulch ground with clean dry straw to block soil-splash",
            "Prune and dispose of lower infected leaves as soon as first spots appear"
        ],
        "chemical_management": [
            "Chlorothalonil 75% WP @ 2g/L or Mancozeb 75% WP @ 2g/L every 7–10 days in wet spells",
            "Pyraclostrobin 20% WG or Difenoconazole 25% EC for systemic protection"
        ],
        "prevention": "Rotate fields for at least 2–3 years with non-solanaceous crops; stake and trellis indeterminate tomatoes for excellent air movement; eradicate nightshade weeds.",
        "fertilizer_recommendations": "Apply balanced N-P-K (12-6-18 or 10-10-10): Potassium and Boron deficiencies worsen Septoria spotting. Avoid quick-release urea; supply well-composted organic manure to support root nutrient absorption.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का सेप्टोरिया पत्ती धब्बा रोग (Septoria Leaf Spot)",
                "severity": "मध्यम प्रकोप",
                "fertilizer_recommendations": "पोटाश और बोरॉन की कमी को पूरा करें। कच्ची खाद या अत्यधिक यूरिया न दें, संतुलित खाद डालें।",
                "speech_text": "किसान भाई, टमाटर की निचली पत्तियों पर सेप्टोरिया धब्बा रोग है। मैन्कोजेब दो ग्राम प्रति लीटर पानी में मिलाकर छिड़कें।"
            },
            "mr": {
                "disease_name": "टोमॅटोचा सेप्टोरिया पानांवरील ठिपके (Septoria Leaf Spot)",
                "severity": "मध्यम प्रादुर्भाव",
                "fertilizer_recommendations": "पोटॅश आणि बोरॉनची मात्रा योग्य ठेवा. संतुलित सेंद्रिय खतांचा वापर करा.",
                "speech_text": "टोमॅटो पिकावर सेप्टोरिया पानांवरील ठिपके दिसत आहेत. मॅन्कोझेब दोन ग्रॅम प्रति लिटर पाण्यात फवारा."
            },
            "te": {
                "disease_name": "టమాట సెప్టోరియా ఆకు మచ్చ తెగులు (Septoria Leaf Spot)",
                "severity": "మధ్యస్థం",
                "fertilizer_recommendations": "సమతుల్య ఎరువులు వాడండి. పొటాషియం లోపం రాకుండా చూసుకోండి.",
                "speech_text": "టమాట పంటలో సెప్టోరియా ఆకు మచ్చల నివారణకు మాంకోజెబ్ పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ಸೆಪ್ಟೋರಿಯಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ (Septoria Leaf Spot)",
                "severity": "ಮಧ್ಯಮ",
                "fertilizer_recommendations": "ಸಮತೋಲಿತ ರಸಗೊಬ್ಬರ ಮತ್ತು ಬೋರಾನ್ ನೀಡಿ.",
                "speech_text": "ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ಸೆಪ್ಟೋರಿಯಾ ಚುಕ್ಕೆ ರೋಗಕ್ಕೆ ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "key": "Tomato___Spider_mites Two-spotted_spider_mite",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Two-Spotted Spider Mites (Tetranychus urticae)",
        "pathogen": "Tetranychus urticae (Acarid / Mite Pest)",
        "severity": "Moderate to High",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Fine yellow or white stippling (pinpoint speckled dots) on upper leaf surfaces",
            "Foliage turns bronze, yellow, and crispy dry with upward curling margins",
            "Delicate silky webbing visible on undersides of leaves, growing tips, and fruit clusters",
            "Stunted growth and severely reduced fruit development under heavy infestation"
        ],
        "possible_causes": [
            "Pest: Two-Spotted Spider Mite (Tetranychus urticae)",
            "Dry, hot climate: Temperatures exceeding 30°C with low relative humidity accelerate reproduction",
            "Drought stress: Water-stressed plants have higher sugar concentrations favorable to mites",
            "Beneficial disruption: Indiscriminate use of broad-spectrum synthetic pyrethroids killing predatory mites"
        ],
        "organic_remedies": [
            "Spray Cold-Pressed Neem Oil (3000 ppm @ 3–5ml/L) with potassium soap on leaf undersides",
            "Release natural predatory mites (Phytoseiulus persimilis or Neoseiulus californicus)",
            "Wash foliage thoroughly with high-pressure water spray to dislodge webbing and mites"
        ],
        "chemical_management": [
            "Spiromesifen 22.9% SC @ 1ml/L or Propargite 57% EC @ 2ml/L",
            "Abamectin 1.9% EC @ 0.5ml/L or Fenazaquin 10% EC @ 2ml/L; spray thoroughly covering undersides"
        ],
        "prevention": "Maintain adequate soil moisture; do not let crops experience drought stress; wet farm roads to suppress dust.",
        "fertilizer_recommendations": "Strictly avoid excess Nitrogen fertilizers: High nitrogen concentrations in sap drastically increase spider mite fecundity and egg-laying speed. Apply Potassium Silicate and Potassium Sulfate to thicken leaf cuticle and deter mite stylet feeding.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का लाल मकड़ी कीट प्रकोप (Two-Spotted Spider Mites)",
                "severity": "मध्यम से तीव्र प्रकोप",
                "fertilizer_recommendations": "नाइट्रोजन (यूरिया) का उपयोग बिल्कुल कम करें। अधिक यूरिया से मकड़ियों की संख्या तेजी से बढ़ती है। पोटाश और सिलिकॉन का छिड़काव करें।",
                "speech_text": "किसान भाई, टमाटर की पत्तियों पर लाल मकड़ी कीट का प्रकोप है। पत्तों के नीचे नीम का तेल या स्पाइरोमेसिफेन का छिड़काव करें।"
            },
            "mr": {
                "disease_name": "टोमॅटोवरील लाल कोळी कीड (Two-Spotted Spider Mites)",
                "severity": "मध्यम ते तीव्र प्रादुर्भाव",
                "fertilizer_recommendations": "युरियाचा वापर कमी करा. जास्त नत्रामुळे लाल कोळीची वाढ वेगाने होते. पोटॅशियम सिलिकेट फवारा.",
                "speech_text": "टोमॅटो पिकावर लाल कोळीचा प्रादुर्भाव आहे. पानांच्या खाली निमार्क किंवा स्पायरोमेसिफेन फवारा."
            },
            "te": {
                "disease_name": "టమాట ఎర్ర నల్లి పురుగు (Two-Spotted Spider Mites)",
                "severity": "తీవ్రమైనది",
                "fertilizer_recommendations": "నత్రజని ఎరువులు అధికంగా వేయవద్దు. పొటాష్ సిలికేట్ వాడండి.",
                "speech_text": "టమాట పంటలో ఎర్ర నల్లి పురుగు నివారణకు వేప నూనె లేదా అబామెక్టిన్ పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ಕೆಂಪು ಜೇಡ ನುಸಿ (Two-Spotted Spider Mites)",
                "severity": "ಮಧ್ಯಮದಿಂದ ತೀವ್ರ",
                "fertilizer_recommendations": "ಹೆಚ್ಚು ಯೂರಿಯಾ ನೀಡಬೇಡಿ. ಸಿಲಿಕಾನ್ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಸಿಂಪಡಿಸಿ.",
                "speech_text": "ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ಕೆಂಪು ಜೇಡ ನುಸಿ ನಿವಾರಣೆಗೆ ಅಬಾಮೆಕ್ಟಿನ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Tomato___Target_Spot": {
        "key": "Tomato___Target_Spot",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Target Spot (Corynespora cassiicola)",
        "pathogen": "Corynespora cassiicola (Fungus)",
        "severity": "Moderate",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Small pinpoint brown lesions that expand into circular brown spots with faint concentric rings",
            "Spots surrounded by a bright yellow halo and dark margins",
            "Lesions coalesce to form extensive foliar blights leading to premature leaf shedding",
            "Circular, dark sunken lesions on green and ripening tomato fruits"
        ],
        "possible_causes": [
            "Pathogen: Corynespora cassiicola fungus",
            "Warm, humid conditions: Temperatures of 20–28°C and continuous high humidity (>85%)",
            "Extended free moisture: Dew or rain remaining on foliage for more than 8–10 hours",
            "Inoculum carryover: Fungus survives on old crop debris, papaya, cotton, and solanaceous weeds"
        ],
        "organic_remedies": [
            "Foliar application of Copper Oxychloride 50% WP @ 2.5g/L",
            "Bio-control spray using Trichoderma viride or Pseudomonas fluorescens @ 5g/L",
            "Prune lower canopy leaves to increase under-row airflow"
        ],
        "chemical_management": [
            "Azoxystrobin 23% SC @ 1ml/L or Pyraclostrobin 20% WG @ 1g/L",
            "Difenoconazole 25% EC @ 0.5ml/L or Fluxapyroxad + Pyraclostrobin @ 1ml/L"
        ],
        "prevention": "Avoid overhead irrigation; use drip lines positioned under mulch; ensure wide plant spacing; plow under crop residues immediately after final harvest.",
        "fertilizer_recommendations": "Apply balanced Calcium and Potassium: Calcium Nitrate (15.5-0-0 + 19% Ca) @ 3g/L fortifies cell wall rigidity against fungal penetration. Avoid heavy nitrogen top-dressing during fruit development to prevent excessive soft vegetative growth.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का टारगेट स्पॉट रोग (Target Spot)",
                "severity": "मध्यम प्रकोप",
                "fertilizer_recommendations": "कैल्शियम नाइट्रेट और पोटाश का छिड़काव करें। फल बनते समय अधिक यूरिया न दें।",
                "speech_text": "किसान भाई, टमाटर की फसल में टारगेट स्पॉट रोग के लक्षण हैं। एज़ोक्सीस्ट्रोबिन या डाइफेनोकोनाजोल का छिड़काव करें।"
            },
            "mr": {
                "disease_name": "टोमॅटोचा टार्गेट स्पॉट ठिपके रोग (Target Spot)",
                "severity": "मध्यम प्रादुर्भाव",
                "fertilizer_recommendations": "कॅल्शियम नायट्रेट आणि पोटॅश द्यावे. जास्त नत्र देणे टाळावे.",
                "speech_text": "टोमॅटो पिकावर टार्गेट स्पॉटचा प्रादुर्भाव आहे. अझॉक्सीस्ट्रोबिनची फवारणी करा."
            },
            "te": {
                "disease_name": "టమాట టార్గెట్ స్పాట్ తెగులు (Target Spot)",
                "severity": "మధ్యస్థ తీవ్రత",
                "fertilizer_recommendations": "కాల్షియం మరియు పొటాషియం ఎరువులు పిచికారీ చేయండి.",
                "speech_text": "టమాట పంటలో టార్గెట్ స్పాట్ నివారణకు అజోక్సిస్ట్రోబిన్ పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ಟಾರ್ಗೆಟ್ ಸ್ಪಾಟ್ ರೋಗ (Target Spot)",
                "severity": "ಮಧ್ಯಮ",
                "fertilizer_recommendations": "ಕ್ಯಾಲ್ಸಿಯಂ ನೈಟ್ರೇಟ್ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಸಿಂಪಡಿಸಿ.",
                "speech_text": "ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ಟಾರ್ಗೆಟ್ ಸ್ಪಾಟ್ ರೋಗಕ್ಕೆ ಅಜಾಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "key": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "pathogen": "Tomato Yellow Leaf Curl Begomovirus (Whitefly-transmitted)",
        "severity": "High / Severe",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Pronounced upward curling and cupping of leaflet margins",
            "Severe leaf size reduction and interveinal yellowing (chlorosis)",
            "Bushy, stunted plant architecture with shortened internodes",
            "Heavy flower drop and near-total failure to set marketable fruit"
        ],
        "possible_causes": [
            "Vector: Silverleaf Whitefly (Bemisia tabaci) transmitting the geminivirus within 15–30 minutes of feeding",
            "Warm, dry climate: Encourages rapid whitefly population explosions and migration",
            "Host reservoirs: Weed hosts (Datura stramonium, Solanum nigrum) harboring virus near fields"
        ],
        "organic_remedies": [
            "Install yellow sticky traps (15–20 per acre) across field at canopy height to capture whiteflies",
            "Spray Neem Oil (10,000 ppm @ 2ml/L) or Pongamia oil to deter whitefly oviposition",
            "Rogue out and destroy infected plants immediately upon early symptom appearance"
        ],
        "chemical_management": [
            "Acetamiprid 20% SP @ 0.4g/L or Thiamethoxam 25% WG @ 0.3g/L to control vector",
            "Diafenthiuron 50% WP @ 1.2g/L or Spiromesifen 22.9% SC @ 1ml/L for nymph control"
        ],
        "prevention": "Plant TYLCV-resistant tomato hybrids; enclose seedling nurseries in 40–50 mesh insect-proof nets; maintain weed-free buffer zone.",
        "fertilizer_recommendations": "Apply micronutrient foliar spray (Zinc 0.5% + Boron 0.2% + Ferrous Sulfate 0.5% + Seaweed extract @ 2ml/L) to sustain remaining metabolic vigor. Do not apply heavy urea top-dressing as stressed plants cannot metabolize excess nitrogen.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का पीला पत्ती मरोड़िया रोग (Yellow Leaf Curl Virus)",
                "severity": "अत्यधिक गंभीर प्रकोप",
                "fertilizer_recommendations": "सूक्ष्म पोषक तत्व (जिंक + बोरॉन + फेरस सल्फेट) और समुद्री शैवाल (सीवीड) अर्क का छिड़काव करें। यूरिया अधिक न दें।",
                "speech_text": "किसान भाई, टमाटर में पीला पत्ती मरोड़िया वायरस है। सफेद मक्खी की रोकथाम हेतु पीले चिपचिपे कार्ड लगाएं और थायामेथोक्सम का छिड़काव करें।"
            },
            "mr": {
                "disease_name": "टोमॅटोचा पिवळा पर्णगुच्छ / चुरडा-मुरडा (Yellow Leaf Curl Virus)",
                "severity": "अति तीव्र प्रादुर्भाव",
                "fertilizer_recommendations": "सूक्ष्म अन्नद्रव्ये (झिंक + बोरॉन) आणि सीवीड अर्काची फवारणी करा. झाडांना ताण देऊ नका.",
                "speech_text": "टोमॅटोवर चुरडा मुरडा रोगाचा प्रादुर्भाव आहे. पांढऱ्या माशीच्या नियंत्रणासाठी पिवळे चिकट सापळे लावा आणि थायामेथॉक्सम फवारा."
            },
            "te": {
                "disease_name": "టమాట ఆకు ముడత తెగులు (Yellow Leaf Curl Virus)",
                "severity": "చాలా తీవ్రమైనది",
                "fertilizer_recommendations": "సూక్ష్మ పోషకాలు (జింక్, బోరాన్) పిచికారీ చేయండి.",
                "speech_text": "టమాట పంటలో ఆకు ముడత వైరస్ నివారణకు తెల్లదోమను అరికట్టండి. పసుపు రంగు జిగురు అట్టలు పెట్టండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ಹಳದಿ ಎಲೆ ಸುರುಳಿ ವೈರಸ್ (Yellow Leaf Curl Virus)",
                "severity": "ಅತಿ ತೀವ್ರ",
                "fertilizer_recommendations": "ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳನ್ನು ಸಿಂಪಡಿಸಿ.",
                "speech_text": "ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ಎಲೆ ಮುದುರು ರೋಗಕ್ಕೆ ಬಿಳಿ ನೊಣ ನಿಯಂತ್ರಣಕ್ಕಾಗಿ ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳನ್ನು ಅಳವಡಿಸಿ."
            }
        }
    },

    "Tomato___Tomato_mosaic_virus": {
        "key": "Tomato___Tomato_mosaic_virus",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Tomato Mosaic Virus (ToMV)",
        "pathogen": "Tomato Mosaic Tobamovirus (Mechanically transmitted)",
        "severity": "Moderate to High",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Mottling of leaves with alternating light green and dark green patches ('mosaic' pattern)",
            "Leaf distortion, blistering, crinkling, and 'shoestring' narrowing of leaflet blades",
            "Plant stunting, poor flower formation, and reduced fruit set",
            "Internal brown browning/necrosis in green fruit walls"
        ],
        "possible_causes": [
            "Transmission: Extremely contagious mechanical transmission via hands, tools, stakes, and plant-to-plant contact",
            "Seed transmission: Virus carried on the outer seed coat of uncertified tomato seeds",
            "Tobacco products: Field workers using cigarettes, bidis, or chewing tobacco carrying the virus",
            "Soil persistence: Stable virus surviving in root debris in soil for multiple seasons"
        ],
        "organic_remedies": [
            "Rogue out and incinerate infected plants immediately (do not compost)",
            "Wash hands and dip pruning shears in 20% skim milk solution between plants to neutralize virus",
            "Treat trellising stakes and tools with 10% trisodium phosphate (TSP) or household bleach solution"
        ],
        "chemical_management": [
            "No curative chemical viricide exists; management is strictly preventative and sanitary"
        ],
        "prevention": "Plant certified virus-free seed treated with trisodium phosphate; select resistant cultivars; strictly ban smoking and handling of tobacco products in or near plots.",
        "fertilizer_recommendations": "Apply balanced organic nutrition (vermicompost + humic acid + seaweed extract) to sustain growth. Avoid heavy chemical inorganic fertilizer spikes which stress damaged root vascular systems.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का मोज़ेक वायरस रोग (Tomato Mosaic Virus)",
                "severity": "मध्यम से गंभीर",
                "fertilizer_recommendations": "जैविक खाद, केंचुआ खाद और ह्यूमिक एसिड का प्रयोग करें। रासायनिक खाद की तेज खुराक न दें।",
                "speech_text": "किसान भाई, टमाटर की पत्तियों पर मोजेक वायरस के धब्बे हैं। रोगी पौधों को उखाड़कर नष्ट करें और हाथ दूध के घोल से धोएं।"
            },
            "mr": {
                "disease_name": "टोमॅटो मोजॅक व्हायरस (Tomato Mosaic Virus)",
                "severity": "तीव्र प्रादुर्भाव",
                "fertilizer_recommendations": "गांडूळ खत आणि ह्युमिक ऍसिड द्यावे. रासायनिक खतांचा अतिवापर टाळावा.",
                "speech_text": "टोमॅटो पिकावर मोजॅक विषाणूचा प्रादुर्भाव आहे. बाधित रोपे त्वरित उपटून नष्ट करा."
            },
            "te": {
                "disease_name": "టమాట మొజాయిక్ వైరస్ (Tomato Mosaic Virus)",
                "severity": "తీవ్రమైనది",
                "fertilizer_recommendations": "సేంద్రీయ ఎరువులు వాడండి.",
                "speech_text": "టమాట పంటలో మొజాయిక్ వైరస్ సోకిన మొక్కలను పీకి నాశనం చేయండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ಮೊಸಾಯಿಕ್ ವೈರಸ್ (Tomato Mosaic Virus)",
                "severity": "ತೀವ್ರ",
                "fertilizer_recommendations": "ಎರೆಹುಳು ಗೊಬ್ಬರ ಮತ್ತು ಸಾವಯವ ಪೋಷಕಾಂಶ ನೀಡಿ.",
                "speech_text": "ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ಮೊಸಾಯಿಕ್ ರೋಗಕ್ಕೆ ಸೋಂಕಿತ ಗಿಡಗಳನ್ನು ಕಿತ್ತು ನಾಶಮಾಡಿ."
            }
        }
    },

    "Tomato___healthy": {
        "key": "Tomato___healthy",
        "crop_display": "Tomato",
        "scientific_crop": "Solanum lycopersicum",
        "disease_name": "Healthy Tomato Foliage (No Disease Detected)",
        "pathogen": "None (Pathogen-Free)",
        "severity": "None detected",
        "status": "Healthy leaf predicted",
        "visible_symptoms": [
            "Vibrant uniform green coloration across entire leaf blade",
            "Intact leaf margins with smooth, vigorous epidermal tissue",
            "Absence of chlorotic yellowing, necrotic lesions, pustules, or viral curling",
            "Active photosynthetic transpiration with sturdy petiole attachment"
        ],
        "possible_causes": [
            "Optimal agronomic management, fertile soil conditions, and timely preventative care",
            "Certified disease-free seeds and balanced drip irrigation management",
            "Absence of pest vectors and active fungal inocula in the field"
        ],
        "organic_remedies": [
            "Continue routine preventative biological drenching with Trichoderma viride and Pseudomonas fluorescens @ 5g/L",
            "Apply organic neem cake (200 kg/acre) to sustain root health and suppress soil pathogens"
        ],
        "chemical_management": [
            "No chemical intervention needed; protect beneficial pollinators and predatory fauna"
        ],
        "prevention": "Maintain consistent drip irrigation schedule to avoid soil moisture fluctuations; scout fields every 5–7 days.",
        "fertilizer_recommendations": "Vegetative stage: Apply balanced water-soluble N-P-K (19:19:19) @ 5g/L via fertigation every 7 days. Flowering & fruiting stage: Transition to Potassium-rich fertilizer (13:0:45 or 0:0:50 @ 4g/L) plus Calcium Nitrate (15.5-0-0 + 19% Ca) and Boron (20% @ 1g/L) to maximize fruit sizing and prevent blossom end rot.",
        "translations": {
            "hi": {
                "disease_name": "स्वस्थ टमाटर की पत्ती (कोई रोग नहीं)",
                "severity": "पूर्णतः स्वस्थ",
                "fertilizer_recommendations": "वानस्पतिक अवस्था में 19:19:19 (5 ग्राम/लीटर) और फूल-फल आते समय पोटेशियम (13:0:45) व कैल्शियम नाइट्रेट दें ताकि फल चमकदार और बड़े बनें।",
                "speech_text": "किसान भाई, आपके टमाटर का पौधा पूरी तरह स्वस्थ है। इसमें किसी रोग के लक्षण नहीं हैं। नियमित खाद-पानी देते रहें।"
            },
            "mr": {
                "disease_name": "निरोगी टोमॅटो पान (कोणताही रोग नाही)",
                "severity": "पूर्णपणे निरोगी",
                "fertilizer_recommendations": "वाढीच्या अवस्थेत 19:19:19 आणि फळधारणेच्या वेळी 13:0:45 व कॅल्शियम बोरॉनची फवारणी करा.",
                "speech_text": "शेतकरी बंधूंनो, तुमचे टोमॅटोचे पीक पूर्णपणे निरोगी आहे. कोणतीही रासायनिक फवारणी करण्याची गरज नाही."
            },
            "te": {
                "disease_name": "ఆరోగ్యకరమైన టమాట ఆకు (ఎటువంటి తెగులు లేదు)",
                "severity": "ఆరోగ్యకరం",
                "fertilizer_recommendations": "19:19:19 మరియు పూత సమయంలో పొటాషియం ఎరువులు అందించండి.",
                "speech_text": "రైతు సోదరులారా, మీ టమాట పంట చాలా ఆరోగ్యంగా ఉంది. ఎటువంటి తెగుళ్లు లేవు."
            },
            "kn": {
                "disease_name": "ಆರೋಗ್ಯಕರ ಟೊಮೆಟೊ ಎಲೆ (ಯಾವುದೇ ರೋಗವಿಲ್ಲ)",
                "severity": "ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರ",
                "fertilizer_recommendations": "19:19:19 ಮತ್ತು ಹೂವು ಬಿಡುವಾಗ ಪೊಟ್ಯಾಶ್ ಗೊಬ್ಬರ ನೀಡಿ.",
                "speech_text": "ರೈತ ಮಿತ್ರರೇ, ನಿಮ್ಮ ಟೊಮೆಟೊ ಬೆಳೆ ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರವಾಗಿದೆ."
            }
        }
    },

    "Pepper,_bell___Bacterial_spot": {
        "key": "Pepper,_bell___Bacterial_spot",
        "crop_display": "Bell Pepper / Chilli",
        "scientific_crop": "Capsicum annuum",
        "disease_name": "Bacterial Spot (Xanthomonas euvesicatoria)",
        "pathogen": "Xanthomonas euvesicatoria / Xanthomonas perforans (Bacterium)",
        "severity": "Moderate to High",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Small (1–3 mm), irregular, water-soaked dark brown to purplish-black spots on leaves",
            "Spots may develop a pale chlorotic yellow halo; centers may drop out forming 'shot-holes'",
            "Extensive lower leaf yellowing and rapid premature leaf drop",
            "Small, raised, wart-like circular brown scabs on bell pepper fruit"
        ],
        "possible_causes": [
            "Pathogen: Xanthomonas euvesicatoria bacterial cells",
            "Climate: Warm temperatures (24–30°C) with persistent high relative humidity (>85%)",
            "Transmission: Splashing rain, overhead sprinkler irrigation, and equipment handling wet foliage",
            "Source: Contaminated pepper seed lots, infected transplants, and solanaceous crop debris"
        ],
        "organic_remedies": [
            "Foliar spray of Copper Hydroxide (2g/L) or Copper Oxychloride 50% WP (2.5g/L)",
            "Bio-control application of Bacillus subtilis or Trichoderma viride @ 5g/L",
            "Prune lower infected foliage during dry sunny hours; do not work in wet fields"
        ],
        "chemical_management": [
            "Copper Oxychloride 50% WP (2.5g/L) tank-mixed with Streptocycline (0.5g/L) at 7–10 day intervals",
            "Mancozeb 75% WP @ 2g/L mixed with copper to overcome copper-tolerant bacterial strains"
        ],
        "prevention": "Use certified disease-free or hot-water treated seeds; practice 2–3 year crop rotation; adopt drip irrigation to prevent water splash.",
        "fertilizer_recommendations": "Avoid excess Nitrogen (urea): Lush, soft nitrogen-rich vegetative tissue accelerates bacterial entry through leaf stomata. Supply Calcium Nitrate (3g/L) and Potassium Sulfate (SOP @ 4g/L) to strengthen plant cell wall barriers.",
        "translations": {
            "hi": {
                "disease_name": "शिमला मिर्च / मिर्च का जीवाणु धब्बा रोग (Bacterial Spot)",
                "severity": "मध्यम से गंभीर",
                "fertilizer_recommendations": "अत्यधिक यूरिया न दें। कैल्शियम नाइट्रेट और पोटेशियम सल्फेट का छिड़काव करके पत्तियों को मजबूत बनाएं।",
                "speech_text": "किसान भाई, शिमला मिर्च में जीवाणु धब्बा रोग है। कॉपर ऑक्सीक्लोराइड के साथ स्ट्रेप्टोसाइक्लिन का छिड़काव करें।"
            },
            "mr": {
                "disease_name": "शिमला मिरचीवरील जिवाणूजन्य ठिपके (Bacterial Spot)",
                "severity": "मध्यम ते तीव्र",
                "fertilizer_recommendations": "युरियाचा अतिवापर टाळा. कॅल्शियम नायट्रेट आणि पोटॅशियम सल्फेटची फवारणी करा.",
                "speech_text": "शिमला मिरची पिकावर जिवाणूजन्य ठिपक्यांचा प्रादुर्भाव आहे. कॉपर ऑक्सिक्लोराईड सोबत स्ट्रेप्टोसायक्लीन फवारा."
            },
            "te": {
                "disease_name": "క్యాప్సికమ్ బాక్టీరియల్ స్పాట్ (Bacterial Spot)",
                "severity": "తీవ్రమైనది",
                "fertilizer_recommendations": "నత్రజని తగ్గించి, కాల్షియం మరియు పొటాషియం ఎరువులు వాడండి.",
                "speech_text": "క్యాప్సికమ్ పంటలో బాక్టీరియల్ స్పాట్ నివారణకు కాపర్ ఆక్సిక్లోరైడ్ మరియు స్ట్రెప్టోసైక్లిన్ పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಚುಕ್ಕೆ ರೋಗ (Bacterial Spot)",
                "severity": "ಮಧ್ಯಮದಿಂದ ತೀವ್ರ",
                "fertilizer_recommendations": "ಯೂರಿಯಾ ಕಡಿಮೆ ಮಾಡಿ, ಕ್ಯಾಲ್ಸಿಯಂ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಸಿಂಪಡಿಸಿ.",
                "speech_text": "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ ಬೆಳೆಯಲ್ಲಿ ಬ್ಯಾಕ್ಟೀರಿಯಾ ರೋಗಕ್ಕೆ ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Pepper,_bell___healthy": {
        "key": "Pepper,_bell___healthy",
        "crop_display": "Bell Pepper / Chilli",
        "scientific_crop": "Capsicum annuum",
        "disease_name": "Healthy Bell Pepper / Chilli Foliage",
        "pathogen": "None (Pathogen-Free)",
        "severity": "None detected",
        "status": "Healthy leaf predicted",
        "visible_symptoms": [
            "Glossy, uniform deep green leaves with crisp margins",
            "Vigorous terminal buds and branching without distortion or mosaic mottling",
            "Clean leaf blade free of water-soaked lesions, necrotic specks, or thrips curling"
        ],
        "possible_causes": [
            "Sound cultural practices, balanced nutrient management, and clean nursery stock",
            "Well-drained soil with adequate organic matter and preventative biopesticide usage"
        ],
        "organic_remedies": [
            "Apply preventative Neem oil spray (1500 ppm @ 3ml/L) every 12–14 days to deter sap-feeding thrips",
            "Soil drenching with bio-fertilizers (Azospirillum and Phosphate Solubilizing Bacteria)"
        ],
        "chemical_management": [
            "No chemical sprays required"
        ],
        "prevention": "Monitor leaf undersides weekly for early thrips activity; maintain uniform drip irrigation.",
        "fertilizer_recommendations": "Vegetative growth: Apply water-soluble N-P-K (19:19:19) @ 4g/L weekly through drip. Flowering & fruiting stage: Transition to Calcium Nitrate (15.5-0-0 + 19% Ca) @ 3g/L and Potassium Schoenite / SOP (0:0:50) @ 4g/L to maximize fruit wall thickness, shine, and yield.",
        "translations": {
            "hi": {
                "disease_name": "स्वस्थ शिमला मिर्च / मिर्च की पत्ती (कोई रोग नहीं)",
                "severity": "पूर्णतः स्वस्थ",
                "fertilizer_recommendations": "शाखाएं बनते समय 19:19:19 और फल लगते समय कैल्शियम नाइट्रेट और पोटाश (0:0:50) दें ताकि फल चमकदार और भारी हों।",
                "speech_text": "किसान भाई, आपकी मिर्च/शिमला मिर्च की फसल एकदम स्वस्थ है। कोई रोग नहीं है।"
            },
            "mr": {
                "disease_name": "निरोगी शिमला मिरची पान (कोणताही रोग नाही)",
                "severity": "पूर्णपणे निरोगी",
                "fertilizer_recommendations": "वाढीसाठी 19:19:19 आणि फळधारणेच्या काळात कॅल्शियम नायट्रेट व पोटॅश (0:0:50) द्यावे.",
                "speech_text": "तुमची शिमला मिरची पूर्णपणे निरोगी आहे. व्यवस्थित पाणी आणि खत व्यवस्थापन ठेवा."
            },
            "te": {
                "disease_name": "ఆరోగ్యకరమైన క్యాప్సికమ్ ఆకు (ఎటువంటి తెగులు లేదు)",
                "severity": "ఆరోగ్యకరం",
                "fertilizer_recommendations": "19:19:19 మరియు కాయ దశలో కాల్షియం, పొటాషియం ఎరువులు ఇవ్వండి.",
                "speech_text": "మీ క్యాప్సికమ్ పంట సంపూర్ణ ఆరోగ్యంగా ఉంది."
            },
            "kn": {
                "disease_name": "ಆರೋಗ್ಯಕರ ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ ಎಲೆ",
                "severity": "ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರ",
                "fertilizer_recommendations": "19:19:19 ಮತ್ತು ಕಾಯಿ ಕಟ್ಟುವಾಗ ಕ್ಯಾಲ್ಸಿಯಂ ನೈಟ್ರೇಟ್ ನೀಡಿ.",
                "speech_text": "ನಿಮ್ಮ ಮೆಣಸಿನಕಾಯಿ ಬೆಳೆ ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರವಾಗಿದೆ."
            }
        }
    },

    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "key": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
        "crop_display": "Corn / Maize",
        "scientific_crop": "Zea mays",
        "disease_name": "Gray Leaf Spot (Cercospora zeae-maydis)",
        "pathogen": "Cercospora zeae-maydis (Fungus)",
        "severity": "Moderate to High",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Narrow, distinctly rectangular lesions running strictly parallel between leaf veins",
            "Lesions begin as small tan spots with yellow halos, expanding into grayish-brown rectangular blocks (1–6 cm long)",
            "In severe cases, lesions coalesce, causing complete blighting and drying of entire maize leaves",
            "Premature lodging and stalk rot due to cannibalization of stalk carbohydrates"
        ],
        "possible_causes": [
            "Pathogen: Cercospora zeae-maydis fungal spores",
            "Weather: Warm (25–32°C), overcast weather with high relative humidity (>90%) and long morning dews (>11 hours)",
            "Conservation tillage: Spores overwintering in unburied corn residue left on the soil surface",
            "Monoculture: Continuous maize cropping without rotational breaks"
        ],
        "organic_remedies": [
            "Soil incorporation of Trichoderma harzianum @ 2.5 kg/acre during land preparation",
            "Spray copper-based bio-fungicide during early vegetative stage",
            "Deep moldboard plowing after harvest to bury corn stubble beneath the soil surface"
        ],
        "chemical_management": [
            "Azoxystrobin 18.2% + Difenoconazole 11.4% SC (Amistar Top @ 1ml/L water)",
            "Pyraclostrobin 20% WG @ 1g/L or Propiconazole 25% EC @ 1ml/L applied from VT (tassel) to R1 (silk) stage"
        ],
        "prevention": "Plant corn hybrids with proven Gray Leaf Spot resistance; rotate with non-host crops (soybean, legumes) for at least one full season; avoid excessive planting density.",
        "fertilizer_recommendations": "Ensure adequate Potassium (MOP / SOP @ 30–40 kg/ha): Potassium deficiency severely increases corn susceptibility to Gray Leaf Spot. Avoid unbalanced, excessive urea top-dressing without proportional potassium.",
        "translations": {
            "hi": {
                "disease_name": "मक्का का ग्रे लीफ स्पॉट रोग (Gray Leaf Spot)",
                "severity": "मध्यम से गंभीर",
                "fertilizer_recommendations": "पोटाश (एमओपी) की पर्याप्त मात्रा दें। पोटाश की कमी से ग्रे लीफ स्पॉट बहुत तेजी से फैलता है। केवल यूरिया न दें।",
                "speech_text": "किसान भाई, मक्के की पत्तियों पर नसों के समानांतर आयताकार भूरे धब्बे हैं जो ग्रे लीफ स्पॉट रोग है। एमिस्टार टॉप एक मिली प्रति लीटर छिड़कें।"
            },
            "mr": {
                "disease_name": "मक्यावरील करपा / ग्रे लीफ स्पॉट (Gray Leaf Spot)",
                "severity": "मध्यम ते तीव्र",
                "fertilizer_recommendations": "मुरिएट ऑफ पोटॅश (एमओपी) योग्य प्रमाणात द्या. एकट्या युरियाचा अतिवापर टाळावा.",
                "speech_text": "मका पिकावर ग्रे लीफ स्पॉट करपा रोगाचा प्रादुर्भाव आहे. अझॉक्सीस्ट्रोबिन + डायफेनोकोनाझोलची फवारणी करा."
            },
            "te": {
                "disease_name": "మొక్కజొన్న గ్రే లీఫ్ స్పాట్ తెగులు (Gray Leaf Spot)",
                "severity": "తీవ్రమైనది",
                "fertilizer_recommendations": "పొటాషియం ఎరువులు తగినంతగా వేయండి.",
                "speech_text": "మొక్కజొన్నలో గ్రే లీఫ్ స్పాట్ నివారణకు ప్రొపికోనజోల్ పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಮೆಕ್ಕೆಜೋಳ ಬೂದು ಎಲೆ ಚುಕ್ಕೆ ರೋಗ (Gray Leaf Spot)",
                "severity": "ಮಧ್ಯಮದಿಂದ ತೀವ್ರ",
                "fertilizer_recommendations": "ಪೊಟ್ಯಾಶ್ ಗೊಬ್ಬರವನ್ನು ಸಮರ್ಪಕವಾಗಿ ನೀಡಿ.",
                "speech_text": "ಮೆಕ್ಕೆಜೋಳದಲ್ಲಿ ಬೂದು ಎಲೆ ಚುಕ್ಕೆ ರೋಗಕ್ಕೆ ಪ್ರೊಪಿಕೋನಾಜೋಲ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Corn_(maize)___Common_rust_": {
        "key": "Corn_(maize)___Common_rust_",
        "crop_display": "Corn / Maize",
        "scientific_crop": "Zea mays",
        "disease_name": "Common Rust (Puccinia sorghi)",
        "pathogen": "Puccinia sorghi (Fungus)",
        "severity": "Moderate",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Small, powdery cinnamon-brown to golden-brown pustules scattered across both upper and lower leaf surfaces",
            "Pustules erupt through the leaf epidermis, shedding powdery rusty-brown urediniospores",
            "Surrounding leaf tissue turns chlorotic yellow; severe pustule clusters lead to leaf scorch and early drying"
        ],
        "possible_causes": [
            "Pathogen: Puccinia sorghi fungal urediniospores",
            "Climate: Moderate temperatures (16–25°C), high relative humidity (>95%), and cool night dews",
            "Wind currents: Airborne spores carried over hundreds of kilometers on atmospheric wind patterns",
            "Alternate host: Wood sorrel (Oxalis species) weeds acting as sexual alternate hosts"
        ],
        "organic_remedies": [
            "Foliar spray of Wettable Sulfur 80% WDG @ 3g per litre of water",
            "Application of bio-fungicide Bacillus amyloliquefaciens @ 5g/L",
            "Eradicate Oxalis weeds from around field boundaries"
        ],
        "chemical_management": [
            "Mancozeb 75% WP @ 2.5g/L or Tebuconazole 25.9% EC @ 1ml/L",
            "Azoxystrobin 23% SC @ 1ml/L applied when rust pustules first appear on leaves above the ear leaf"
        ],
        "prevention": "Select maize hybrids carrying dominant Rp rust resistance genes; plant early in season; avoid late planting near mature corn fields.",
        "fertilizer_recommendations": "Maintain balanced Nitrogen and Potassium: Heavy nitrogen paired with low potassium promotes rapid Common Rust spore colonization. Apply Muriate of Potash (MOP) @ 25 kg/acre during knee-high side-dressing to fortify foliar tissues.",
        "translations": {
            "hi": {
                "disease_name": "मक्का का सामान्य रतुआ / गेरुआ रोग (Common Rust)",
                "severity": "मध्यम प्रकोप",
                "fertilizer_recommendations": "नाइट्रोजन और पोटाश का संतुलन रखें। पोटाश (एमओपी) 25 किग्रा प्रति एकड़ टॉप ड्रेसिंग में दें।",
                "speech_text": "किसान भाई, मक्के की पत्तियों पर भूरे-लाल रंग के रतुआ फफोले हैं। घुलनशील गंधक तीन ग्राम या मैन्कोजेब ढाई ग्राम प्रति लीटर पानी में मिलाकर छिड़कें।"
            },
            "mr": {
                "disease_name": "मक्यावरील तांबेरा रोग (Common Rust)",
                "severity": "मध्यम प्रादुर्भाव",
                "fertilizer_recommendations": "पोटॅश आणि नत्राचा समतोल ठेवा. पिकाला तांबेरा प्रतिकार वाढवण्यासाठी पोटॅश द्या.",
                "speech_text": "मका पिकावर तांबेरा रोगाचे ठिपके दिसत आहेत. मॅन्कोझेब किंवा पाण्यात विरघळणारे गंधक तीन ग्रॅम प्रति लिटर पाण्यात फवारा."
            },
            "te": {
                "disease_name": "మొక్కజొన్న కుంకుమ తెగులు (Common Rust)",
                "severity": "మధ్యస్థం",
                "fertilizer_recommendations": "పొటాష్ ఎరువులు తప్పనిసరిగా వేయండి.",
                "speech_text": "మొక్కజొన్న పంటలో కుంకుమ తెగులు నివారణకు మాంకోజెబ్ లేదా టెబుకొనజోల్ పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಮೆಕ್ಕೆಜೋಳ ತುಕ್ಕು ರೋಗ (Common Rust)",
                "severity": "ಮಧ್ಯಮ",
                "fertilizer_recommendations": "ಪೊಟ್ಯಾಶ್ ರಸಗೊಬ್ಬರವನ್ನು ಸಮತೋಲನದಲ್ಲಿ ನೀಡಿ.",
                "speech_text": "ಮೆಕ್ಕೆಜೋಳದಲ್ಲಿ ತುಕ್ಕು ರೋಗಕ್ಕೆ ಗಂಧಕ ಅಥವಾ ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Corn_(maize)___Northern_Leaf_Blight": {
        "key": "Corn_(maize)___Northern_Leaf_Blight",
        "crop_display": "Corn / Maize",
        "scientific_crop": "Zea mays",
        "disease_name": "Northern Leaf Blight (Exserohilum turcicum)",
        "pathogen": "Exserohilum turcicum / Helminthosporium turcicum (Fungus)",
        "severity": "Moderate to High",
        "status": "Possible disease detected",
        "visible_symptoms": [
            "Long, elliptical, cigar-shaped grayish-green to tan lesions (2.5 to 15 cm long)",
            "Lesions start on lower leaves and rapidly progress upward toward the ear leaf",
            "During damp weather, dark olive-gray fungal fuzz (spores) appears in the center of lesions",
            "Extensive blighting of upper canopy leads to substantial kernel filling losses"
        ],
        "possible_causes": [
            "Pathogen: Exserohilum turcicum fungal conidia",
            "Weather: Moderate temperatures (18–27°C) accompanied by heavy rains and dew periods >6 hours",
            "Overwintering: Fungal survival on unburied corn stubble and sorghum residues",
            "Susceptible genetics: Growing corn hybrids lacking Ht resistance genes"
        ],
        "organic_remedies": [
            "Foliar spray of Copper Hydroxide or bio-fungicide Trichoderma viride @ 5g/L",
            "Deep plowing of field after harvest to bury crop residue below 15 cm depth",
            "Remove severely infected lower leaves in smaller kitchen/demonstration plots"
        ],
        "chemical_management": [
            "Mancozeb 75% WP @ 2.5g/L or Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/L",
            "Metiram 55% + Pyraclostrobin 5% WG @ 2g/L applied at early tassel emergence"
        ],
        "prevention": "Cultivate maize hybrids possessing single-gene (Ht1, Ht2) or multigenic resistance; implement 2-year crop rotation; ensure 60cm row spacing.",
        "fertilizer_recommendations": "Avoid excessive Nitrogen top-dressing without adequate Potassium: Soft, nitrogen-rich corn leaves with low potassium develop significantly larger Northern Leaf Blight lesions. Apply balanced basal N-P-K (120:60:40 kg/ha) with full potash applied at sowing.",
        "translations": {
            "hi": {
                "disease_name": "मक्का का उत्तरी पत्ती झुलसा रोग (Northern Leaf Blight)",
                "severity": "मध्यम से गंभीर",
                "fertilizer_recommendations": "बिना पोटाश के अधिक यूरिया न दें। बुवाई के समय पोटाश की पूरी खुराक (40 किग्रा/हेक्टेयर) देना जरूरी है।",
                "speech_text": "किसान भाई, मक्के की पत्तियों पर नाव के आकार के लंबे भूरे धब्बे हैं जो टर्सिकम झुलसा रोग है। मैन्कोजेब ढाई ग्राम प्रति लीटर पानी में मिलाकर तुरंत छिड़कें।"
            },
            "mr": {
                "disease_name": "मक्याचा मोठा करपा (Northern Leaf Blight)",
                "severity": "मध्यम ते तीव्र",
                "fertilizer_recommendations": "पोटॅशयुक्त खतांचा संतुलित वापर करा. नत्राचा अतिरेक टाळावा.",
                "speech_text": "मका पिकावर लांबट करपा रोगाचा प्रादुर्भाव आहे. नियंत्रणासाठी मॅन्कोझेब अडीच ग्रॅम प्रति लिटर पाण्यात फवारा."
            },
            "te": {
                "disease_name": "మొక్కజొన్న నార్తర్న్ లీఫ్ బ్లైట్ తెగులు (Northern Leaf Blight)",
                "severity": "తీవ్రమైనది",
                "fertilizer_recommendations": "సమతుల్య నత్రజని మరియు పొటాషియం ఎరువులు వాడండి.",
                "speech_text": "మొక్కజొన్న పంటలో నార్తర్న్ లీఫ్ బ్లైట్ నివారణకు అజోక్సిస్ట్రోబిన్ + డైఫెనోకోనజోల్ పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಮೆಕ್ಕೆಜೋಳ ಉತ್ತರದ ಎಲೆ ಅಂಗಮಾರಿ ರೋಗ (Northern Leaf Blight)",
                "severity": "ಮಧ್ಯಮದಿಂದ ತೀವ್ರ",
                "fertilizer_recommendations": "ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಗೊಬ್ಬರ ನೀಡಿ.",
                "speech_text": "ಮೆಕ್ಕೆಜೋಳದಲ್ಲಿ ಉತ್ತರದ ಎಲೆ ಅಂಗಮಾರಿ ರೋಗಕ್ಕೆ ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    },

    "Corn_(maize)___healthy": {
        "key": "Corn_(maize)___healthy",
        "crop_display": "Corn / Maize",
        "scientific_crop": "Zea mays",
        "disease_name": "Healthy Corn / Maize Foliage",
        "pathogen": "None (Pathogen-Free)",
        "severity": "None detected",
        "status": "Healthy leaf predicted",
        "visible_symptoms": [
            "Broad, sturdy dark green leaf blades with clear parallel venation",
            "Clean, intact foliage free of cigar lesions, rust pustules, or rectangular leaf spots",
            "Vigorous stalk development with thick rind and healthy nodal root anchoring"
        ],
        "possible_causes": [
            "High-quality hybrid seed, clean field preparation, and optimal weed and moisture management",
            "Balanced basal and split fertilizer application ensuring no nutritional deficiency"
        ],
        "organic_remedies": [
            "Continue bio-fertilizer seed inoculation (Azotobacter and PSB)",
            "Apply organic FYM (farm yard manure) @ 4 tons/acre to build soil water holding capacity"
        ],
        "chemical_management": [
            "No chemical intervention needed"
        ],
        "prevention": "Scout field every 10–12 days from knee-high to silking; keep rows free of weeds competing for nitrogen.",
        "fertilizer_recommendations": "Split Nitrogen Schedule: 1/3rd at sowing (basal), 1/3rd at knee-high stage (V6, 30-35 days), and 1/3rd at tasseling/silking (50-55 days). Zinc application: Apply Zinc Sulfate (25 kg/ha basal): Corn is especially susceptible to zinc chlorosis ('white bud').",
        "translations": {
            "hi": {
                "disease_name": "स्वस्थ मक्का की पत्ती (कोई रोग नहीं)",
                "severity": "पूर्णतः स्वस्थ",
                "fertilizer_recommendations": "यूरिया को 3 भागों में बांटकर दें (बुवाई, घुटने की ऊंचाई और भुट्टा बनने पर)। जिंक सल्फेट 25 किग्रा प्रति हेक्टेयर अवश्य दें।",
                "speech_text": "किसान भाई, आपकी मक्का की फसल पूरी तरह स्वस्थ है। खेत में नमी और खरपतवार नियंत्रण बनाए रखें।"
            },
            "mr": {
                "disease_name": "निरोगी मका पान (कोणताही रोग नाही)",
                "severity": "पूर्णपणे निरोगी",
                "fertilizer_recommendations": "युरिया तीन हप्त्यांत विभागून द्या (पेरणी, गुडघाभर उंची व कणसे भरताना). झिंक सल्फेट नक्की वापरा.",
                "speech_text": "तुमची मका पीक पूर्णपणे निरोगी आणि सशक्त आहे. वेळेवर पाणी व खत द्या."
            },
            "te": {
                "disease_name": "ఆరోగ్యకరమైన మొక్కజొన్న ఆకు (ఎటువంటి తెగులు లేదు)",
                "severity": "ఆరోగ್ಯకరం",
                "fertilizer_recommendations": "యూరియాను విడతల వారీగా అందించండి మరియు జింక్ సల్ఫేట్ వాడండి.",
                "speech_text": "మీ మొక్కజొన్న పంట సంపూర్ణ ఆరోగ్యంగా ఉంది."
            },
            "kn": {
                "disease_name": "ಆರೋಗ್ಯಕರ ಮೆಕ್ಕೆಜೋಳ ಎಲೆ",
                "severity": "ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರ",
                "fertilizer_recommendations": "ಯೂರಿಯಾವನ್ನು ಮೂರು ಕಂತುಗಳಲ್ಲಿ ನೀಡಿ ಮತ್ತು ಸತು (ಜಿಂಕ್) ಸಲ್ಫೇಟ್ ಬಳಸಿ.",
                "speech_text": "ನಿಮ್ಮ ಮೆಕ್ಕೆಜೋಳ ಬೆಳೆ ಸಂಪೂರ್ಣ ಆರೋಗ್ಯಕರವಾಗಿದೆ."
            }
        }
    }
}


def get_validated_disease_entry(label_or_key: str) -> dict:
    """
    Retrieve rich pathology information for any of the 16 validated deep learning model classes.
    Supports exact keys ('Tomato___Early_blight'), fuzzy matching, and fallback.
    """
    if not label_or_key:
        return VALIDATED_MODEL_CLASSES["Tomato___Early_blight"]

    cleaned = str(label_or_key).strip()

    # Exact key match
    if cleaned in VALIDATED_MODEL_CLASSES:
        return VALIDATED_MODEL_CLASSES[cleaned]

    # Normalized match (ignoring case, spaces, underscores)
    norm = cleaned.lower().replace(" ", "").replace("_", "").replace(",", "").replace("(", "").replace(")", "")
    for k, v in VALIDATED_MODEL_CLASSES.items():
        k_norm = k.lower().replace(" ", "").replace("_", "").replace(",", "").replace("(", "").replace(")", "")
        if norm == k_norm or norm in k_norm or k_norm in norm:
            return v

    # Fallback default
    return VALIDATED_MODEL_CLASSES["Tomato___Early_blight"]


def get_supported_crops_info() -> list:
    """Returns validated information on all plant species and diseases supported by the trained model."""
    return [
        {
            "crop": "Tomato",
            "scientific_name": "Solanum lycopersicum",
            "classes_count": 10,
            "conditions": [
                "Bacterial Spot", "Early Blight", "Late Blight", "Leaf Mold",
                "Septoria Leaf Spot", "Two-Spotted Spider Mites", "Target Spot",
                "Tomato Yellow Leaf Curl Virus", "Tomato Mosaic Virus", "Healthy Foliage"
            ]
        },
        {
            "crop": "Bell Pepper / Chilli",
            "scientific_name": "Capsicum annuum",
            "classes_count": 2,
            "conditions": [
                "Bacterial Spot", "Healthy Foliage"
            ]
        },
        {
            "crop": "Corn / Maize",
            "scientific_name": "Zea mays",
            "classes_count": 4,
            "conditions": [
                "Gray Leaf Spot (Cercospora)", "Common Rust",
                "Northern Leaf Blight", "Healthy Foliage"
            ]
        }
    ]
'''

def main():
    catalog_path = "ml/disease/pathology_catalog.py"
    with open(catalog_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "VALIDATED_MODEL_CLASSES" in content:
        print("VALIDATED_MODEL_CLASSES already present in pathology_catalog.py")
        return

    # Append to end of file
    updated_content = content + NEW_CODE
    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("Successfully appended VALIDATED_MODEL_CLASSES and helper functions to pathology_catalog.py!")

if __name__ == "__main__":
    main()

from ml.disease.plant_model import get_plant_model
"""
KrushiSetu Crop Doctor Inference Engine
Singleton predictor that loads pathology weights once and executes fast inference.
"""

import os
import random

# Agronomy Pathology Knowledge Base with Multilingual Translations
PATHOLOGY_KNOWLEDGE_BASE = {
    "tomato": {
        "disease_name": "Early Blight (Alternaria solani)",
        "confidence": 0.94,
        "severity": "Moderate",
        "symptoms": [
            "Concentric dark brown rings on lower leaves",
            "Yellow halo surrounding necrotic leaf spots",
            "Foliage drying and premature leaf drop"
        ],
        "organic_remedies": [
            "Spray Copper Oxychloride 50% WP @ 2.5g per litre of water.",
            "Apply Trichoderma viride bio-fungicide @ 5g/L on foliage.",
            "Prune infected bottom leaves and dispose of them far from the field.",
            "Avoid overhead sprinkler irrigation to keep foliage dry."
        ],
        "chemical_management": [
            "Mancozeb 75% WP @ 2g/L or Azoxystrobin 23% SC @ 1ml/L water at 10-day intervals."
        ],
        "prevention": "Rotate crops with non-solanaceous crops for 2-3 years; ensure well-drained soil and optimal plant spacing.",
        "translations": {
            "hi": {
                "disease_name": "टमाटर का अगेती झुलसा रोग (Early Blight)",
                "severity": "मध्यम प्रकोप",
                "symptoms": [
                    "निचली पत्तियों पर गहरे भूरे रंग के संकेंद्रित छल्ले (टारगेट स्पॉट)",
                    "धब्बों के चारों ओर पीला घेरा बनना",
                    "पत्तियों का सूखना और समय से पहले गिरना"
                ],
                "organic_remedies": [
                    "कॉपर ऑक्सीक्लोराइड 50% WP @ 2.5 ग्राम प्रति लीटर पानी में मिलाकर छिड़काव करें।",
                    "ट्राइकोडर्मा विरिडी जैव-कवकनाशी @ 5 ग्राम/लीटर का छिड़काव करें।",
                    "संक्रमित निचली पत्तियों को काटकर खेत से दूर नष्ट कर दें।",
                    "ऊपर से फव्वारा सिंचाई से बचें ताकि पत्तियां सूखी रहें।"
                ],
                "chemical_management": [
                    "मैंकोजेब 75% WP @ 2 ग्राम/लीटर या एजोक्सीस्ट्रोबिन 23% SC @ 1 मिली/लीटर का 10 दिन के अंतराल पर छिड़काव करें।"
                ],
                "prevention": "टमाटर के बाद 2-3 साल तक बैंगन/आलू न लगाएं; खेत में जल निकासी का उत्तम प्रबंध रखें।",
                "speech_text": "किसान भाई, आपके टमाटर की फसल में अगेती झुलसा रोग के लक्षण हैं। तुरंत कॉपर ऑक्सीक्लोराइड ढाई ग्राम प्रति लीटर पानी में मिलाकर छिड़काव करें। अधिक प्रकोप होने पर मैंकोजेब दो ग्राम प्रति लीटर का इस्तेमाल करें।"
            },
            "mr": {
                "disease_name": "टोमॅटोचा करपा / लवकर येणारा करपा (Early Blight)",
                "severity": "मध्यम प्रादुर्भाव",
                "symptoms": [
                    "खालच्या पानांवर गडद तपकिरी रंगाची वर्तुळाकार चकतीसारखी ठिपके",
                    "ठिपक्यांभोवती पिवळसर वलय तयार होणे",
                    "पाने सुकणे आणि अकाली गळणे"
                ],
                "organic_remedies": [
                    "कॉपर ऑक्सिक्लोराईड 50% WP @ 2.5 ग्रॅम प्रति लिटर पाण्यात मिसळून फवारणी करा.",
                    "ट्रायकोडर्मा व्हिरीडी जैविक बुरशीनाशक @ 5 ग्रॅम/लिटर फवारा.",
                    "बाधित खालची पाने छाटून शेताबाहेर नष्ट करा.",
                    "पानांवर पाणी साचू नये म्हणून ठिबक सिंचनाचा वापर करा."
                ],
                "chemical_management": [
                    "मॅन्कोझेब 75% WP @ 2 ग्रॅम/लिटर किंवा ॲझोक्सिस्ट्रॉबिन 23% SC @ 1 मिली/लिटर पाण्यात 10 दिवसांच्या अंतराने फवारा."
                ],
                "prevention": "दरवर्षी पीक फेरपालट करा; शेतात चांगला निचरा ठेवा आणि योग्य अंतर ठेवा.",
                "speech_text": "शेतकरी बंधूंनो, टोमॅटो पिकावर लवकर येणाऱ्या करपा रोगाचा प्रादुर्भाव दिसत आहे. तातडीने कॉपर ऑक्सिक्लोराईड अडीच ग्रॅम प्रति लिटर पाण्यात मिसळून फवारा. जास्त प्रादुर्भाव असल्यास मॅन्कोझेब दोन ग्रॅम प्रति लिटर वापरा."
            },
            "te": {
                "disease_name": "టమాట ముందస్తు మాడు తెగులు (Early Blight)",
                "severity": "మధ్యస్థ తీవ్రత",
                "symptoms": [
                    "క్రింది ఆకులపై ముదురు గోధుమ రంగు వలయాల మచ్చలు",
                    "మచ్చల చుట్టూ పసుపు రంగు వలయం ఏర్పడటం",
                    "ఆకులు ఎండి రాలిపోవడం"
                ],
                "organic_remedies": [
                    "కాపర్ ఆక్సిక్లోరైడ్ 50% WP @ 2.5 గ్రాములు లీటరు నీటికి కలిపి పిచికారీ చేయండి.",
                    "ట్రైకోడెర్మా విరిడే @ 5 గ్రాములు లీటరు నీటికి పిచికారీ చేయండి.",
                    "వ్యాధి సోకిన క్రింది ఆకులను తుంచి నాశనం చేయండి."
                ],
                "chemical_management": [
                    "మాంకోజెబ్ 75% WP @ 2 గ్రా/లీ లేదా అజోక్సిస్ట్రోబిన్ @ 1 మి.లీ/లీ 10 రోజుల వ్యవధిలో పిచికారీ చేయండి."
                ],
                "prevention": "పంట మార్పిడి పాటించండి మరియు మురుగునీరు నిల్వ ఉండకుండా చూడండి.",
                "speech_text": "రైతు సోదరులారా, టమాట పంటలో ముందస్తు మాడు తెగులు గమనించబడింది. కాపర్ ఆక్సిక్లోరైడ్ రెండున్నర గ్రాములు లీటరు నీటికి కలిపి పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಟೊಮೆಟೊ ಮುಂಚಿನ ಅಂಗಮಾರಿ ರೋಗ (Early Blight)",
                "severity": "ಮಧ್ಯಮ ತೀವ್ರತೆ",
                "symptoms": [
                    "ಕೆಳಗಿನ ಎಲೆಗಳ ಮೇಲೆ ಕಂದು ಬಣ್ಣದ ವೃತ್ತಾಕಾರದ ಚುಕ್ಕೆಗಳು",
                    "ಚುಕ್ಕೆಗಳ ಸುತ್ತ ಹಳದಿ ಬಣ್ಣದ ಹೊದಿಕೆ",
                    "ಎಲೆಗಳು ಒಣಗಿ ಉದುರುವುದು"
                ],
                "organic_remedies": [
                    "ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ 50% WP @ 2.5 ಗ್ರಾಂ ಪ್ರತಿ ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ.",
                    "ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡಿ @ 5 ಗ್ರಾಂ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ.",
                    "ರೋಗಪೀಡಿತ ಎಲೆಗಳನ್ನು ಕತ್ತರಿಸಿ ನಾಶಪಡಿಸಿ."
                ],
                "chemical_management": [
                    "ಮ್ಯಾಂಕೋಜೆಬ್ 75% WP @ 2 ಗ್ರಾಂ/ಲೀಟರ್ ಅಥವಾ ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ @ 1 ಮಿ.ಲೀ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ."
                ],
                "prevention": "ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಹೊಲದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
                "speech_text": "ರೈತ ಮಿತ್ರರೇ, ಟೊಮೆಟೊ ಬೆಳೆಯಲ್ಲಿ ಮುಂಚಿನ ಅಂಗಮಾರಿ ರೋಗ ಕಂಡುಬಂದಿದೆ. ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ ಎರಡೂವರೆ ಗ್ರಾಂ ಪ್ರತಿ ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ."
            }
        }
    },
    "wheat": {
        "disease_name": "Brown Leaf Rust (Puccinia triticina)",
        "confidence": 0.91,
        "severity": "Moderate",
        "symptoms": [
            "Small, circular to oval orange-brown pustules on leaf blades",
            "Powdery rust spores rubbing off on fingers",
            "Premature drying of flag leaves leading to shriveled grains"
        ],
        "organic_remedies": [
            "Spray sour buttermilk / fermented whey (Lassi) diluted 1:10 with water as a bio-fungicide.",
            "Apply Neem seed kernel extract (NSKE 5%) or Azadirachtin 1500 ppm @ 3ml/L.",
            "Incorporate bio-agent Pseudomonas fluorescens @ 5g/L."
        ],
        "chemical_management": [
            "Propiconazole 25% EC (Tilt) @ 1ml/L or Tebuconazole 25.9% EC @ 1ml/L at first appearance."
        ],
        "prevention": "Sow rust-resistant wheat cultivars (e.g., HD-2967, DBW-187); avoid excess nitrogen fertilization during early tillering.",
        "translations": {
            "hi": {
                "disease_name": "गेहूं का भूरा रतुआ / गेरुआ रोग (Brown Rust)",
                "severity": "मध्यम प्रकोप",
                "symptoms": [
                    "पत्तियों पर छोटे नारंगी-भूरे रंग के दानेदार फफोले",
                    "हाथ लगाने पर उंगलियों पर भूरा चूर्ण लगना",
                    "ध्वज पत्ती का जल्दी सूखना जिससे दाने पतले हो जाते हैं"
                ],
                "organic_remedies": [
                    "खट्टी छाछ/मट्ठा (1:10 अनुपात में पानी के साथ) का छिड़काव करें।",
                    "नीम तेल (एनएसकेई 5%) या एज़ाडिरैक्टिन @ 3 मिली/लीटर का छिड़काव करें।",
                    "स्यूडोमोनास फ्लोरेसेंस @ 5 ग्राम/लीटर का प्रयोग करें।"
                ],
                "chemical_management": [
                    "प्रोपिकोनाजोल 25% EC (टिल्ट) @ 1 मिली/लीटर या टेबुकोनाजोल @ 1 मिली/लीटर का छिड़काव करें।"
                ],
                "prevention": "रोगरोधी किस्में (HD-2967, DBW-187) लगाएं; यूरिया की अत्यधिक खुराक से बचें।",
                "speech_text": "किसान भाई, गेहूं में भूरा रतुआ रोग दिखा है। शुरुआती अवस्था में खट्टी छाछ या प्रोपिकोनाजोल टिल्ट एक मिली प्रति लीटर पानी में मिलाकर फव्वारा करें।"
            },
            "mr": {
                "disease_name": "गव्हाचा तांबेरा रोग (Brown Rust)",
                "severity": "मध्यम प्रादुर्भाव",
                "symptoms": [
                    "पानांवर लहान नारंगी-तांबूस रंगाचे फोड येणे",
                    "बोटाने घासल्यास तांबूस भुकटी हाताला लागणे",
                    "पाने सुकल्यामुळे दाणे बारीक व हलके भरणे"
                ],
                "organic_remedies": [
                    "आंबट ताक (1:10 प्रमाणात पाण्यात मिसळून) फवारा.",
                    "कडुलिंब अर्क (NSKE 5%) किंवा निंबोळी तेल @ 3 मिली/लिटर फवारा.",
                    "स्यूडोमोनास फ्लुरोसेन्स @ 5 ग्रॅम/लिटर वापरा."
                ],
                "chemical_management": [
                    "प्रोपिकोनाझोल 25% EC (टिल्ट) @ 1 मिली/लिटर किंवा टेबुकोनाझोल @ 1 मिली/लिटर फवारा."
                ],
                "prevention": "तांबेरा प्रतिकारक वाणांची लागवड करा; फुटवे फुटताना अतिरिक्त नत्र खते देणे टाळा.",
                "speech_text": "शेतकरी मित्रांनो, गव्हावर तांबेरा रोगाची लक्षणे आढळली आहेत. नियंत्रणासाठी प्रोपिकोनाझोल टिल्ट एक मिली प्रति लिटर पाण्यात फवारा."
            },
            "te": {
                "disease_name": "గోధుమ రస్ట్ / తుప్పు తెగులు (Brown Rust)",
                "severity": "మధ్యస్థ తీవ్రత",
                "symptoms": [
                    "ఆకులపై నారింజ-గోధుమ రంగు చిన్న పొక్కులు",
                    "చేతితో తాకినప్పుడు పొడి రాలడం"
                ],
                "organic_remedies": [
                    "పుల్లటి మజ్జిగ ద్రావణం (1:10) పిచికారీ చేయండి.",
                    "వేప నూనె 3 మి.లీ/లీటర్ పిచికారీ చేయండి."
                ],
                "chemical_management": [
                    "ప్రొపికోనాజోల్ 25% EC @ 1 మి.లీ/లీటర్ నీటికి కలిపి పిచికారీ చేయండి."
                ],
                "prevention": "నిరోధక రకాలను ఎంచుకోండి.",
                "speech_text": "గోధుమ పంటలో తుప్పు తెగులు నివారణకు ప్రొపికోనాజోల్ 1 మి.లీ లీటరు నీటికి కలిపి పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಗೋಧಿ ತುಕ್ಕು ರೋಗ (Brown Rust)",
                "severity": "ಮಧ್ಯಮ ತೀವ್ರತೆ",
                "symptoms": [
                    "ಎಲೆಗಳ ಮೇಲೆ ಕಿತ್ತಳೆ-ಕಂದು ಬಣ್ಣದ ಚುಕ್ಕೆಗಳು",
                    "ಕೈಯಿಂದ ಮುಟ್ಟಿದರೆ ಪುಡಿ ಅಂಟಿಕೊಳ್ಳುವುದು"
                ],
                "organic_remedies": [
                    "ಹುಳಿ ಮಜ್ಜಿಗೆ ಸಿಂಪಡಿಸಿ.",
                    "ಬೇವಿನ ಎಣ್ಣೆ 3 ಮಿ.ಲೀ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ."
                ],
                "chemical_management": [
                    "ಪ್ರೊಪಿಕೊನಾಜೋಲ್ 25% EC @ 1 ಮಿ.ಲೀ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ."
                ],
                "prevention": "ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬಳಸಿ.",
                "speech_text": "ಗೋಧಿ ಬೆಳೆಯಲ್ಲಿ ತುಕ್ಕು ರೋಗ ತಡೆಗಟ್ಟಲು ಪ್ರೊಪಿಕೊನಾಜೋಲ್ ಒಂದು ಮಿಲಿ ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ."
            }
        }
    },
    "onion": {
        "disease_name": "Purple Blotch (Alternaria porri)",
        "confidence": 0.93,
        "severity": "Moderate to Severe",
        "symptoms": [
            "Small water-soaked lesions turning purple with dark concentric rings",
            "Girdling of leaves leading to leaf collapse from the tip down",
            "Reduced bulb development and premature lodging"
        ],
        "organic_remedies": [
            "Foliar spray of Panchagavya (3%) mixed with neem oil (5ml/L).",
            "Spray Copper Hydroxide @ 2g/L of water.",
            "Ensure proper field drainage during rainy spells."
        ],
        "chemical_management": [
            "Difenoconazole 25% EC @ 1ml/L or Hexaconazole 5% SC @ 2ml/L water with sticking agent."
        ],
        "prevention": "Maintain 15cm x 10cm bulb spacing; burn post-harvest crop residue; follow 3-year crop rotation.",
        "translations": {
            "hi": {
                "disease_name": "प्याज का बैंगनी धब्बा रोग (Purple Blotch)",
                "severity": "मध्यम से गंभीर प्रकोप",
                "symptoms": [
                    "पत्तियों पर जल-सिक्त धब्बे जो बाद में बैंगनी रंग में बदल जाते हैं",
                    "पत्तियों का ऊपर से नीचे की ओर सूखना और लटकना",
                    "कंद का आकार छोटा रह जाना"
                ],
                "organic_remedies": [
                    "पंचगव्य (3%) और नीम तेल (5 मिली/लीटर) का छिड़काव करें।",
                    "कॉपर हाइड्रॉक्साइड @ 2 ग्राम/लीटर का छिड़काव करें।",
                    "खेत में पानी जमा न होने दें।"
                ],
                "chemical_management": [
                    "डिफेनोकोनाजोल 25% EC (स्कोर) @ 1 मिली/लीटर या हेक्साकोनाजोल @ 2 मिली/लीटर में स्टिकर मिलाकर छिड़कें।"
                ],
                "prevention": "उचित दूरी पर पौध लगाएं और फसल अवशेषों को नष्ट करें।",
                "speech_text": "प्याज में बैंगनी धब्बा रोग के नियंत्रण हेतु डिफेनोकोनाजोल स्कोर एक मिली प्रति लीटर पानी में स्टिकर मिलाकर छिड़काव करें।"
            },
            "mr": {
                "disease_name": "कांद्यावरील जांभळा करपा रोग (Purple Blotch)",
                "severity": "मध्यम ते तीव्र प्रादुर्भाव",
                "symptoms": [
                    "पानांवर पाण्यासारखे खोलगट ठिपके पडून नंतर जांभळट-तपकिरी होणे",
                    "पाने टोकाकडून खाली वाळत जाणे",
                    "कांद्याची वाढ खुंटणे व प्रत खराब होणे"
                ],
                "organic_remedies": [
                    "पंचगव्य (3%) + निंबोळी तेल (5 मिली/लिटर) फवारा.",
                    "कॉपर हायड्रॉक्साईड @ 2 ग्रॅम/लिटर पाण्यात मिसळून फवारा.",
                    "पावसाळ्यात शेतात पाणी साचू न देणे."
                ],
                "chemical_management": [
                    "डायफेनोकोनाझोल 25% EC (स्कोर) @ 1 मिली/लिटर किंवा हेक्झाकोनाझोल @ 2 मिली/लिटर सोबत स्टिकर (डिंक) मिसळून फवारा."
                ],
                "prevention": "15x10 सेमी अंतरावर लागवड करा; पिकांचे अवशेष जाळून नष्ट करा.",
                "speech_text": "कांदा पिकावरील जांभळा करपा रोगासाठी स्कोर एक मिली प्रति लिटर पाण्यात स्टिकर मिसळून फवारणी करा."
            },
            "te": {
                "disease_name": "ఉల్లి ఊదా రంగు మచ్చ తెగులు (Purple Blotch)",
                "severity": "తీవ్రత మధ్యస్థం",
                "symptoms": ["ఆకులపై ఊదా రంగు మచ్చలు", "ఆకులు పై నుండి ఎండిపోవడం"],
                "organic_remedies": ["పంచగవ్య మరియు వేపనూనె పిచికారీ చేయండి."],
                "chemical_management": ["డైఫెనోకోనాజోల్ @ 1 మి.లీ/లీటర్ పిచికారీ చేయండి."],
                "prevention": "సరైన మురుగునీటి పారుదల కల్పించండి.",
                "speech_text": "ఉల్లిలో ఊదా మచ్చ తెగులుకు డైఫెనోకోనాజోల్ 1 మి.లీ లీటరు నీటికి పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಈರುಳ್ಳಿ ನೇರಳೆ ಚುಕ್ಕೆ ರೋಗ (Purple Blotch)",
                "severity": "ಮಧ್ಯಮ ತೀವ್ರತೆ",
                "symptoms": ["ಎಲೆಗಳ ಮೇಲೆ ನೇರಳೆ ಚುಕ್ಕೆಗಳು", "ಎಲೆಗಳು ಒಣಗುವುದು"],
                "organic_remedies": ["ಪಂಚಗವ್ಯ ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ."],
                "chemical_management": ["ಡೈಫೆನೊಕೊನಾಜೋಲ್ @ 1 ಮಿ.ಲೀ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ."],
                "prevention": "ಸರಿಯಾದ ಅಂತರದಲ್ಲಿ ನಾಟಿ ಮಾಡಿ.",
                "speech_text": "ಈರುಳ್ಳಿ ನೇರಳೆ ಚುಕ್ಕೆ ರೋಗಕ್ಕೆ ಡೈಫೆನೊಕೊನಾಜೋಲ್ ಒಂದು ಮಿಲಿ ಸಿಂಪಡಿಸಿ."
            }
        }
    },
    "rice": {
        "disease_name": "Rice Blast (Magnaporthe oryzae)",
        "confidence": 0.92,
        "severity": "Severe",
        "symptoms": [
            "Spindle-shaped or diamond-shaped lesions with greyish center and brown margins",
            "Neck rot causing panicle breakage and empty white grains",
            "Rapid spread under cloudy, humid conditions with morning dew"
        ],
        "organic_remedies": [
            "Seed treatment with Pseudomonas fluorescens @ 10g/kg seed.",
            "Spray fermented cow urine diluted @ 10% on nursery and transplanted crops."
        ],
        "chemical_management": [
            "Tricyclazole 75% WP @ 0.6g/L or Isoprothiolane 40% EC @ 1.5ml/L water."
        ],
        "prevention": "Avoid split application of excessive urea during booting stage; maintain balanced potash levels.",
        "translations": {
            "hi": {
                "disease_name": "धान का झोंका रोग / ब्लास्ट (Rice Blast)",
                "severity": "गंभीर प्रकोप",
                "symptoms": [
                    "पत्तियों पर नाव या आंख के आकार के धब्बे जिनका केंद्र राख के रंग का और किनारे कत्थई होते हैं",
                    "गर्दन तोड़ रोग जिससे बालियां टूट जाती हैं और दाने खोखले रह जाते हैं"
                ],
                "organic_remedies": [
                    "स्यूडोमोनास फ्लोरेसेंस @ 10 ग्राम/किग्रा बीज से बीजोपचार करें।",
                    "गोमूत्र (10% घोल) का छिड़काव करें।"
                ],
                "chemical_management": [
                    "ट्राईसाइक्लाजोल 75% WP (बाम) @ 0.6 ग्राम/लीटर या इसोप्रोथियोलेन @ 1.5 मिली/लीटर का छिड़काव करें।"
                ],
                "prevention": "अत्यधिक यूरिया के प्रयोग से बचें और पोटाश की संतुलित मात्रा दें।",
                "speech_text": "धान की फसल में झोंका या ब्लास्ट रोग से बचाव के लिए ट्राईसाइक्लाजोल बाम शून्य दशमलव छह ग्राम प्रति लीटर पानी में फवारें।"
            },
            "mr": {
                "disease_name": "भातावरील करपा / ब्लास्ट रोग (Rice Blast)",
                "severity": "तीव्र प्रादुर्भाव",
                "symptoms": [
                    "पानांवर डोळ्याच्या आकाराचे करड्या रंगाचे ठिपके",
                    "मानमोडीमुळे लोंब्या तुटून दाणे पोचट राहणे"
                ],
                "organic_remedies": [
                    "स्यूडोमोनास फ्लुरोसेन्स @ 10 ग्रॅम/किलो बियाण्यास चोळावे.",
                    "10% गोमूत्र अर्क फवारावा."
                ],
                "chemical_management": [
                    "ट्रायसायक्लॅझोल 75% WP (बाम) @ 0.6 ग्रॅम/लिटर पाण्यात मिसळून फवारा."
                ],
                "prevention": "जास्त नत्र खते देणे टाळा; पालाश खतांचा संतुलित वापर करा.",
                "speech_text": "भात पिकावरील करपा रोगासाठी ट्रायसायक्लॅझोल शून्य पॉईंट सहा ग्रॅम प्रति लिटर पाण्यात फवारा."
            },
            "te": {
                "disease_name": "వరి అగ్గి తెగులు / బ్లాస్ట్ (Rice Blast)",
                "severity": "తీవ్రమైనది",
                "symptoms": ["ఆకులపై కంటి ఆకారపు మచ్చలు", "మెడ విరుపు"],
                "organic_remedies": ["స్యూడోమోనాస్ తో విత్తన శుద్ధి చేయండి."],
                "chemical_management": ["ట్రైసైక్లాజోల్ @ 0.6 గ్రా/లీటర్ పిచికారీ చేయండి."],
                "prevention": "నత్రజని అధికంగా వాడవద్దు.",
                "speech_text": "వరి అగ్గి తెగులు నివారణకు ట్రైసైక్లాజోల్ 0.6 గ్రాములు లీటరు నీటికి కలిపి పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಭತ್ತದ ಬೆಂಕಿ ರೋಗ (Rice Blast)",
                "severity": "ತೀವ್ರತೆ ಹೆಚ್ಚು",
                "symptoms": ["ಎಲೆಗಳ ಮೇಲೆ ಕಣ್ಣಿನ ಆಕಾರದ ಚುಕ್ಕೆಗಳು", "ತೆನೆ ಮುರಿತ"],
                "organic_remedies": ["ಬೀಜೋಪಚಾರ ಮಾಡಿ."],
                "chemical_management": ["ಟ್ರೈಸೈಕ್ಲಾಜೋಲ್ @ 0.6 ಗ್ರಾಂ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ."],
                "prevention": "ಸಾರಜನಕ ಹೆಚ್ಚಾಗಿ ಬಳಸಬೇಡಿ.",
                "speech_text": "ಭತ್ತದ ಬೆಂಕಿ ರೋಗಕ್ಕೆ ಟ್ರೈಸೈಕ್ಲಾಜೋಲ್ ಸೊನ್ನೆ ಬಿಂದು ಆರು ಗ್ರಾಂ ಸಿಂಪಡಿಸಿ."
            }
        }
    },
    "cotton": {
        "disease_name": "Cotton Leaf Curl Virus (CLCuV)",
        "confidence": 0.89,
        "severity": "Moderate",
        "symptoms": [
            "Upward and downward curling of leaf margins",
            "Thickening and dark greening of veins with enations underneath",
            "Stunted plant growth and square/boll shedding"
        ],
        "organic_remedies": [
            "Install yellow sticky traps (10 traps/acre) to control Whitefly insect vectors.",
            "Spray Neem Oil 10,000 ppm @ 2.5ml/L to manage vector nymphs."
        ],
        "chemical_management": [
            "Diafenthiuron 50% WP @ 1.2g/L or Pyriproxyfen 10% EC @ 2ml/L to suppress whitefly vectors."
        ],
        "prevention": "Eradicate weed hosts (Parthenium, Sida) around field borders; grow tolerant hybrid varieties.",
        "translations": {
            "hi": {
                "disease_name": "कपास का पत्ती मरोड़ विषाणु रोग (Leaf Curl Virus)",
                "severity": "मध्यम प्रकोप",
                "symptoms": [
                    "पत्तियों के किनारों का ऊपर या नीचे की ओर मुड़ना (मरोड़िया)",
                    "पत्तियों की नसों का मोटा होना और पौधे का बौना रह जाना"
                ],
                "organic_remedies": [
                    "सफेद मक्खी नियंत्रण हेतु पीले चिपचिपे कार्ड (10 प्रति एकड़) लगाएं।",
                    "नीम तेल @ 2.5 मिली/लीटर का छिड़काव करें।"
                ],
                "chemical_management": [
                    "डायफेंथियूरॉन 50% WP @ 1.2 ग्राम/लीटर या पाइरीप्रॉक्सिफेन @ 2 मिली/लीटर का छिड़काव करें।"
                ],
                "prevention": "खेत की मेड़ों से गाजरघास हटाएं और रोगरोधी किस्में लगाएं।",
                "speech_text": "कपास में पत्ती मरोड़ रोग सफेद मक्खी से फैलता है। नियंत्रण के लिए पीले चिपचिपे ट्रैप लगाएं और नीम तेल का छिड़काव करें।"
            },
            "mr": {
                "disease_name": "कापसावरील चुरडा-मुरडा / पान बोकड्या रोग (Leaf Curl)",
                "severity": "मध्यम प्रादुर्भाव",
                "symptoms": [
                    "पानांच्या कडा वर किंवा खाली वळणे (बोकड्या)",
                    "शिरा जाड होऊन झाडांची वाढ खुंटणे"
                ],
                "organic_remedies": [
                    "पांढरी माशी नियंत्रणासाठी पिवळे चिकट सापळे (10 प्रति एकर) लावा.",
                    "निंबोळी तेल @ 2.5 मिली/लिटर फवारा."
                ],
                "chemical_management": [
                    "डायफेनथियुरॉन 50% WP @ 1.2 ग्रॅम/लिटर किंवा पायरीप्रॉक्सिफेन @ 2 मिली/लिटर फवारा."
                ],
                "prevention": "बांधावरील तण नष्ट करा; सहनशील वाण निवडा.",
                "speech_text": "कापसावरील पान बोकड्या रोगासाठी पांढऱ्या माशीचे नियंत्रण आवश्यक आहे. पिवळे चिकट सापळे लावा आणि निंबोळी तेल फवारा."
            },
            "te": {
                "disease_name": "పత్తి ఆకు ముడత వైరస్ (Leaf Curl Virus)",
                "severity": "మధ్యస్థం",
                "symptoms": ["ఆకులు ముడుచుకుపోవడం", "ఈనెలు మందంగా మారడం"],
                "organic_remedies": ["పసుపు రంగు జిగురు కార్డులు పెట్టండి.", "వేప నూనె పిచికారీ చేయండి."],
                "chemical_management": ["డయాఫెంథియురాన్ @ 1.2 గ్రా/లీటర్ పిచికారీ చేయండి."],
                "prevention": "తెల్లదోమ నివారణ చర్యలు చేపట్టండి.",
                "speech_text": "పత్తిలో ఆకు ముడత నివారణకు పసుపు జిగురు అట్టలు మరియు వేపనూనె వాడండి."
            },
            "kn": {
                "disease_name": "ಹತ್ತಿ ಎಲೆ ಮುಟುರು ರೋಗ (Leaf Curl)",
                "severity": "ಮಧ್ಯಮ",
                "symptoms": ["ಎಲೆಗಳು ಮುದುರಿಕೊಳ್ಳುವುದು", "ಗಿಡಗಳ ಬೆಳವಣಿಗೆ ಕುಂಠಿತ"],
                "organic_remedies": ["ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳನ್ನು ಬಳಸಿ.", "ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ."],
                "chemical_management": ["ಡಯಾಫೆಂಥಿಯುರಾನ್ @ 1.2 ಗ್ರಾಂ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ."],
                "prevention": "ಬಿಳಿ ನೊಣ ನಿಯಂತ್ರಿಸಿ.",
                "speech_text": "ಹತ್ತಿ ಎಲೆ ಮುಟುರು ರೋಗ ನಿಯಂತ್ರಣಕ್ಕೆ ಹಳದಿ ಬಲೆಗಳನ್ನು ಮತ್ತು ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ."
            }
        }
    },
    "soybean": {
        "disease_name": "Soybean Rust (Phakopsora pachyrhizi)",
        "confidence": 0.90,
        "severity": "Moderate",
        "symptoms": [
            "Tiny tan to dark brown lesions on the underside of lower leaves",
            "Volcano-shaped pustules releasing yellow-brown spores",
            "Rapid defoliation during pod filling stage"
        ],
        "organic_remedies": [
            "Foliar spray of bio-formulation Bacillus subtilis @ 5ml/L.",
            "Apply wettable sulfur @ 2.5g/L."
        ],
        "chemical_management": [
            "Pyraclostrobin + Epoxiconazole @ 1.5ml/L or Hexaconazole 5% EC @ 2ml/L."
        ],
        "prevention": "Adopt early planting; practice wider row spacing (45 cm) for good sunlight penetration.",
        "translations": {
            "hi": {
                "disease_name": "सोयाबीन का गेरुआ / रतुआ रोग (Soybean Rust)",
                "severity": "मध्यम प्रकोप",
                "symptoms": [
                    "निचली पत्तियों की निचली सतह पर छोटे भूरे रंग के धब्बे",
                    "फलियां भरते समय पत्तियों का तेजी से झड़ना"
                ],
                "organic_remedies": [
                    "घुलनशील गंधक (वेटेबल सल्फर) @ 2.5 ग्राम/लीटर का छिड़काव करें।",
                    "बैसिलस सबटिलिस @ 5 मिली/लीटर का प्रयोग करें।"
                ],
                "chemical_management": [
                    "हेक्साकोनाजोल 5% EC @ 2 मिली/लीटर या पायराक्लोस्ट्रोबिन @ 1.5 मिली/लीटर का छिड़काव करें।"
                ],
                "prevention": "उचित कतार दूरी (45 सेमी) पर बुवाई करें ताकि धूप और हवा मिल सके।",
                "speech_text": "सोयाबीन में गेरुआ रोग दिखने पर घुलनशील सल्फर ढाई ग्राम या हेक्साकोनाजोल दो मिली प्रति लीटर पानी में फवारें।"
            },
            "mr": {
                "disease_name": "सोयाबीनवरील तांबेरा रोग (Soybean Rust)",
                "severity": "मध्यम प्रादुर्भाव",
                "symptoms": [
                    "पानांच्या खालच्या बाजूवर बारीक तांबूस-तपकिरी ठिपके",
                    "शेंगा भरण्याच्या अवस्थेत पाने झपाट्याने गळणे"
                ],
                "organic_remedies": [
                    "पाण्यात विरघळणारे गंधक @ 2.5 ग्रॅम/लिटर फवारा.",
                    "बॅसिलस सबटिलिस @ 5 मिली/लिटर फवारा."
                ],
                "chemical_management": [
                    "हेक्झाकोनाझोल 5% EC @ 2 मिली/लिटर किंवा पायरॅक्लोस्ट्रॉबिन @ 1.5 मिली/लिटर फवारा."
                ],
                "prevention": "योग्य अंतरावर (45 सेमी) पेरणी करा जेणेकरून सूर्यप्रकाश पोहोचेल.",
                "speech_text": "सोयाबीन पिकावरील तांबेरा रोगासाठी विद्राव्य गंधक अडीच ग्रॅम किंवा हेक्झाकोनाझोल दोन मिली प्रति लिटर पाण्यात फवारा."
            },
            "te": {
                "disease_name": "సోయాబీన్ తుప్పు తెగులు (Soybean Rust)",
                "severity": "మధ్యస్థం",
                "symptoms": ["ఆకుల అడుగు భాగంలో గోధుమ రంగు మచ్చలు", "ఆకులు రాలిపోవడం"],
                "organic_remedies": ["గంధకం పొడి 2.5 గ్రా/లీటర్ పిచికారీ చేయండి."],
                "chemical_management": ["హెక్సాకోనాజోల్ @ 2 మి.లీ/లీటర్ పిచికారీ చేయండి."],
                "prevention": "సరైన దూరం పాటించండి.",
                "speech_text": "సోయాబీన్ తుప్పు తెగులుకు గంధకం లేదా హెక్సాకోనాజోల్ పిచికారీ చేయండి."
            },
            "kn": {
                "disease_name": "ಸೋಯಾಬೀನ್ ತುಕ್ಕು ರೋಗ (Soybean Rust)",
                "severity": "ಮಧ್ಯಮ",
                "symptoms": ["ಎಲೆಗಳ ತಳಭಾಗದಲ್ಲಿ ಕಂದು ಚುಕ್ಕೆಗಳು", "ಎಲೆಗಳು ಉದುರುವುದು"],
                "organic_remedies": ["ಗಂಧಕದ ಪುಡಿ 2.5 ಗ್ರಾಂ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ."],
                "chemical_management": ["ಹೆಕ್ಸಾಕೊನಾಜೋಲ್ @ 2 ಮಿ.ಲೀ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ."],
                "prevention": "ಸರಿಯಾದ ಅಂತರದಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ.",
                "speech_text": "ಸೋಯಾಬೀನ್ ತುಕ್ಕು ರೋಗಕ್ಕೆ ಗಂಧಕ ಅಥವಾ ಹೆಕ್ಸಾಕೊನಾಜೋಲ್ ಸಿಂಪಡಿಸಿ."
            }
        }
    }
}

class DiseasePredictor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DiseasePredictor, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        self.mode = "Development & Production Decision Support"
        self.knowledge_base = PATHOLOGY_KNOWLEDGE_BASE

    def predict(self, crop_name: str, image_path: str = None, lang: str = "en") -> dict:
        if not image_path:
            raise ValueError("An uploaded leaf image is required.")

        result = None
        try:
            result = get_plant_model().predict(image_path)
        except Exception as e:
            return {
                "success": False,
                "is_valid_plant": False,
                "error_code": "IMAGE_READ_ERROR",
                "crop": crop_name,
                "status": "Invalid Image File",
                "disease_name": "Invalid Image File",
                "error": f"Could not process the uploaded image file: {str(e)}",
                "speech_text": "Invalid image file uploaded. Please upload a clear photo of an authentic plant leaf.",
                "disclaimer": "The AI vision model only analyzes real agricultural crop leaves."
            }

        if result and not result.get("is_valid_plant", True):
            lang_key = (lang or "en").lower().strip()
            
            error_titles = {
                "en": "Invalid Leaf Image Detected",
                "hi": "अमान्य पत्ती की तस्वीर (Invalid Leaf Image)",
                "mr": "अवैध पानाचा फोटो (Invalid Leaf Image)",
                "te": "చెల్లని ఆకు చిత్రం (Invalid Leaf Image)",
                "kn": "ಅಮಾನ್ಯ ಎಲೆಯ ಚಿತ್ರ (Invalid Leaf Image)"
            }
            error_messages = {
                "en": result.get("message", "Uploaded photo does not contain a valid crop leaf."),
                "hi": "अपलोड की गई तस्वीर किसी फसल की पत्ती नहीं है (नोटबुक पेज, कागज या अन्य गैर-कृषि वस्तु)। कृपया फसल की असली पत्ती की साफ फोटो अपलोड करें।",
                "mr": "अपलोड केलेला फोटो पिकाच्या पानाचा नाही (वहीचे पान, कागद किंवा इतर वस्तू आढळली). कृपया पिकाच्या खऱ्या पानाचा स्पष्ट फोटो अपलोड करा.",
                "te": "అప్‌లోడ్ చేసిన చిత్రం పంట ఆకు కాదు (నోట్‌బుక్ లేదా కాగితం). దయచేసి నిజమైన పంట ఆకు ఫోటోను అప్‌లోడ్ చేయండి.",
                "kn": "ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಚಿತ್ರವು ಬೆಳೆಯ ಎಲೆಯಲ್ಲ (ನೋಟ್‌ಬುಕ್ ಅಥವಾ ಕಾಗದ). ದಯವಿಟ್ಟು ನಿಜವಾದ ಬೆಳೆಯ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
            }
            voice_scripts = {
                "en": "Invalid image detected. Please upload a clear, close-up photo of an authentic crop leaf, not a notebook page or document.",
                "hi": "किसान भाई, यह फोटो किसी पत्ती की नहीं है। कृपया नोटबुक या कागज के बजाय फसल की असली पत्ती की साफ फोटो अपलोड करें।",
                "mr": "शेतकरी बंधूंनो, हा फोटो पिकाच्या पानाचा नाही. कृपया वहीच्या पानाऐवजी पिकाच्या खऱ्या पानाचा स्पष्ट फोटो अपलोड करा.",
                "te": "రైతు సోదరులారా, ఇది పంట ఆకు చిత్రం కాదు. దయచేసి పంట ఆకు యొక్క స్పష్టమైన ఫోటోను అప్‌లోడ్ చేయండి.",
                "kn": "ರೈತ ಬಾಂಧವರೇ, ಇದು ಬೆಳೆಯ ಎಲೆಯ ಚಿತ್ರವಲ್ಲ. ದಯವಿಟ್ಟು ನಿಜವಾದ ಬೆಳೆಯ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
            }
            
            return {
                "success": False,
                "is_valid_plant": False,
                "error_code": result.get("error_code", "INVALID_LEAF_IMAGE"),
                "crop": crop_name,
                "status": "Invalid Leaf Image",
                "disease_name": error_titles.get(lang_key, error_titles["en"]),
                "error": error_messages.get(lang_key, error_messages["en"]),
                "reason": result.get("reason", "non_plant_image"),
                "instructions": result.get("instructions", [
                    "Take a direct close-up photo of a crop plant leaf (e.g. Tomato, Corn, Bell Pepper).",
                    "Make sure the leaf covers the central frame of the camera.",
                    "Ensure clear natural lighting without shadows, glare, or blur.",
                    "Do not upload drawings, notebook pages, documents, or screenshots."
                ]),
                "speech_text": voice_scripts.get(lang_key, voice_scripts["en"]),
                "confidence": result.get("confidence", 0.0),
                "confidence_percent": result.get("confidence_percent", 0.0),
                "botanical_pct": result.get("botanical_pct", 0.0),
                "neutral_pct": result.get("neutral_pct", 0.0),
                "translations": {
                    "en": {"disease_name": error_titles["en"], "speech_text": voice_scripts["en"]},
                    "hi": {"disease_name": error_titles["hi"], "speech_text": voice_scripts["hi"]},
                    "mr": {"disease_name": error_titles["mr"], "speech_text": voice_scripts["mr"]},
                    "te": {"disease_name": error_titles["te"], "speech_text": voice_scripts["te"]},
                    "kn": {"disease_name": error_titles["kn"], "speech_text": voice_scripts["kn"]}
                },
                "disclaimer": "The AI vision model only analyzes real agricultural crop leaves. Non-plant images, notebook pages, documents, or screenshots are rejected to ensure diagnostic accuracy."
            }

        label = result["label"]
        confidence = result["confidence"]
        confidence_percent = result["confidence_percent"]

        # 16-class Model Pathology Information
        model_details = {
            "Tomato___Bacterial_spot": {
                "crop": "Tomato",
                "disease_name": "Bacterial Spot (Xanthomonas perforans)",
                "severity": "Moderate to High",
                "symptoms": [
                    "Small water-soaked circular lesions on lower foliage",
                    "Yellow halo surrounding dark circular leaf spots",
                    "Scab-like raised spots on fruit surfaces"
                ],
                "organic_remedies": [
                    "Spray Copper Oxychloride 50% WP @ 2.5g/L water.",
                    "Apply Bacillus subtilis bio-bactericide @ 5ml/L.",
                    "Remove and destroy heavily blighted plants immediately."
                ],
                "chemical_management": [
                    "Streptocycline 1-2g in 10L water mixed with Copper Oxychloride 25g/10L at 7-10 day intervals."
                ],
                "prevention": "Use certified disease-free seeds; avoid overhead irrigation; practice 3-year crop rotation."
            },
            "Tomato___Early_blight": {
                "crop": "Tomato",
                "disease_name": "Early Blight (Alternaria solani)",
                "severity": "Moderate",
                "symptoms": [
                    "Concentric dark brown rings on lower leaves (target-board spots)",
                    "Yellow halo surrounding necrotic leaf spots",
                    "Foliage drying and premature leaf drop"
                ],
                "organic_remedies": [
                    "Spray Copper Oxychloride 50% WP @ 2.5g per litre of water.",
                    "Apply Trichoderma viride bio-fungicide @ 5g/L on foliage.",
                    "Prune infected bottom leaves and dispose of them far from the field.",
                    "Avoid overhead sprinkler irrigation to keep foliage dry."
                ],
                "chemical_management": [
                    "Mancozeb 75% WP @ 2g/L or Azoxystrobin 23% SC @ 1ml/L water at 10-day intervals."
                ],
                "prevention": "Rotate crops with non-solanaceous crops for 2-3 years; ensure well-drained soil and optimal plant spacing."
            },
            "Tomato___Late_blight": {
                "crop": "Tomato",
                "disease_name": "Late Blight (Phytophthora infestans)",
                "severity": "High / Severe",
                "symptoms": [
                    "Water-soaked irregular pale-green to dark brown lesions on leaves",
                    "White fungal mold growth on leaf undersides in humid weather",
                    "Rapid whole-plant wilting and collapse"
                ],
                "organic_remedies": [
                    "Apply Copper Oxychloride 50% WP @ 3g/L as preventative foliage barrier.",
                    "Remove and burn severely infected foliage immediately."
                ],
                "chemical_management": [
                    "Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ) @ 2g/L or Dimethomorph 50% WP @ 1g/L."
                ],
                "prevention": "Plant resistant cultivars; avoid wet foliage overnight; eliminate volunteer tomato/potato plants."
            },
            "Tomato___Leaf_Mold": {
                "crop": "Tomato",
                "disease_name": "Leaf Mold (Passalora fulva)",
                "severity": "Moderate",
                "symptoms": [
                    "Pale green or yellowish spots on upper leaf surfaces",
                    "Olive green to gray velvety mold growth on lower leaf surfaces"
                ],
                "organic_remedies": [
                    "Improve greenhouse ventilation and air circulation to reduce humidity below 85%.",
                    "Spray Neem oil (10,000 ppm) @ 2ml/L water."
                ],
                "chemical_management": [
                    "Chlorothalonil 75% WP @ 2g/L or Difenoconazole 25% EC @ 0.5ml/L."
                ],
                "prevention": "Maintain adequate plant spacing; ensure proper aeration; drip irrigate instead of overhead."
            },
            "Tomato___Septoria_leaf_spot": {
                "crop": "Tomato",
                "disease_name": "Septoria Leaf Spot (Septoria lycopersici)",
                "severity": "Moderate",
                "symptoms": [
                    "Numerous small, circular spots with dark brown margins and gray centers",
                    "Tiny black specks (pycnidia) visible inside older leaf lesions"
                ],
                "organic_remedies": [
                    "Mulch heavily around base of tomato plants to prevent splash dispersal.",
                    "Apply Copper Oxychloride @ 2.5g/L or bio-fungicide Bacillus amyloliquefaciens."
                ],
                "chemical_management": [
                    "Mancozeb 75% WP @ 2.5g/L or Chlorothalonil @ 2g/L at 7-10 day intervals."
                ],
                "prevention": "Stake plants upright; avoid working in wet foliage; destroy crop debris after harvest."
            },
            "Tomato___Spider_mites Two-spotted_spider_mite": {
                "crop": "Tomato",
                "disease_name": "Two-Spotted Spider Mite (Tetranychus urticae)",
                "severity": "Moderate",
                "symptoms": [
                    "Yellow or bronze stippling / flecking on leaf tops",
                    "Fine silk webbing on leaf undersides and growing tips"
                ],
                "organic_remedies": [
                    "Spray Neem oil 5ml/L or soap emulsion solution to suffocate mites.",
                    "Release predatory mites (Phytoseiulus persimilis) as biocontrol."
                ],
                "chemical_management": [
                    "Propargite 57% EC @ 2ml/L or Spiromesifen 22.9% SC @ 1ml/L water."
                ],
                "prevention": "Avoid drought stress and dusty conditions; weed field borders regularly."
            },
            "Tomato___Target_Spot": {
                "crop": "Tomato",
                "disease_name": "Target Spot (Corynespora cassiicola)",
                "severity": "Moderate",
                "symptoms": [
                    "Brown lesions with concentric rings and distinct yellow margins on foliage",
                    "Foliage collapse and defoliation under warm, wet conditions"
                ],
                "organic_remedies": [
                    "Apply Copper-based fungicides @ 2.5g/L.",
                    "Ensure high canopy airflow and wide crop row spacing."
                ],
                "chemical_management": [
                    "Azoxystrobin + Difenoconazole @ 1ml/L or Pyraclostrobin 20% WG @ 1g/L."
                ],
                "prevention": "Practice strict crop rotation; avoid overhead irrigation; remove lower senescing leaves."
            },
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
                "crop": "Tomato",
                "disease_name": "Tomato Yellow Leaf Curl Virus (TYLCV)",
                "severity": "Severe",
                "symptoms": [
                    "Stunted plant growth and bushy erect appearance",
                    "Upward curling and yellowing (chlorosis) of leaf margins",
                    "Severely reduced flower and fruit set"
                ],
                "organic_remedies": [
                    "Install yellow sticky traps (15-20 traps/acre) to trap whitefly vectors.",
                    "Spray 5% Neem Seed Kernel Extract (NSKE) or Neem oil @ 3ml/L."
                ],
                "chemical_management": [
                    "Imidacloprid 17.8% SL @ 0.5ml/L or Thiamethoxam 25% WG @ 0.3g/L to control vector whiteflies."
                ],
                "prevention": "Use virus-resistant cultivars; use insect-proof netting in nurseries; rogue out infected plants."
            },
            "Tomato___Tomato_mosaic_virus": {
                "crop": "Tomato",
                "disease_name": "Tomato Mosaic Virus (ToMV)",
                "severity": "Moderate to High",
                "symptoms": [
                    "Mottled light and dark green mosaic patterns on leaves",
                    "Distorted, blistered, or narrow leaves",
                    "Internal browning in fruit walls"
                ],
                "organic_remedies": [
                    "Soak pruning tools in 20% nonfat dry milk or 10% trisodium phosphate solution.",
                    "Remove and incinerate infected plants immediately."
                ],
                "chemical_management": [
                    "No chemical cure exists for viruses. Focus on strict sanitation and insect hygiene."
                ],
                "prevention": "Wash hands with soap before handling plants; plant certified ToMV-resistant seeds."
            },
            "Tomato___healthy": {
                "crop": "Tomato",
                "disease_name": "Healthy Tomato Leaf",
                "severity": "None detected",
                "symptoms": [
                    "Vibrant green leaf coloration with no necrotic lesions",
                    "Normal leaf architecture and vigorous tissue vigor"
                ],
                "organic_remedies": [
                    "Continue standard organic fertilization (vermicompost, Jeevamrut).",
                    "Maintain regular preventive foliar sprays of Trichoderma viride."
                ],
                "chemical_management": [
                    "No chemical fungicides or bactericides required."
                ],
                "prevention": "Maintain optimal irrigation, balanced N-P-K nutrition, and periodic scouting."
            },
            "Pepper,_bell___Bacterial_spot": {
                "crop": "Bell Pepper",
                "disease_name": "Bacterial Spot (Xanthomonas campestris)",
                "severity": "Moderate",
                "symptoms": [
                    "Small water-soaked green lesions on leaf undersides turning brown",
                    "Premature defoliation exposing bell peppers to sunscald"
                ],
                "organic_remedies": [
                    "Spray Copper Hydroxide @ 2.5g/L water during overcast, humid days.",
                    "Apply Trichoderma harzianum or Pseudomonas fluorescens as bio-protectants."
                ],
                "chemical_management": [
                    "Copper Oxychloride 50% WP @ 2.5g/L tank-mixed with Streptocycline @ 1g/10L water."
                ],
                "prevention": "Sow certified disease-free seeds; eliminate solanaceous weeds; rotate fields."
            },
            "Pepper,_bell___healthy": {
                "crop": "Bell Pepper",
                "disease_name": "Healthy Bell Pepper Leaf",
                "severity": "None detected",
                "symptoms": [
                    "Deep green glossy foliage with clean margins",
                    "Uniform leaf blade texture with no chlorosis or spots"
                ],
                "organic_remedies": [
                    "Maintain soil organic carbon with regular compost applications.",
                    "Apply micro-nutrient foliar spray (Zinc, Boron) during flowering."
                ],
                "chemical_management": [
                    "No chemical treatment required."
                ],
                "prevention": "Ensure well-drained raised beds and consistent drip irrigation."
            },
            "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
                "crop": "Corn (Maize)",
                "disease_name": "Gray Leaf Spot (Cercospora zeae-maydis)",
                "severity": "Moderate to High",
                "symptoms": [
                    "Small tan spots with yellow halos expanding into long, narrow rectangular lesions",
                    "Lesions restricted by leaf veins giving distinct squared-off edges"
                ],
                "organic_remedies": [
                    "Tillage to bury residue and accelerate decomposition of infected maize stalks.",
                    "Spray bio-fungicide Bacillus subtilis @ 5g/L."
                ],
                "chemical_management": [
                    "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/L or Pyraclostrobin @ 1ml/L."
                ],
                "prevention": "Rotate with non-host crops like soybean or cotton; plant resistant corn hybrids."
            },
            "Corn_(maize)___Common_rust_": {
                "crop": "Corn (Maize)",
                "disease_name": "Common Rust (Puccinia sorghi)",
                "severity": "Moderate",
                "symptoms": [
                    "Golden-brown to cinnamon-brown powdery pustules scattered over both leaf surfaces",
                    "Pustules erupting through leaf epidermis shedding orange rust spores"
                ],
                "organic_remedies": [
                    "Foliar spray of sour buttermilk solution (1:10) or fermented cow urine extract.",
                    "Apply sulfur-based wettable powder @ 2g/L."
                ],
                "chemical_management": [
                    "Mancozeb 75% WP @ 2g/L or Propiconazole 25% EC @ 1ml/L water."
                ],
                "prevention": "Plant rust-tolerant hybrid corn; early season planting avoids peak spore flights."
            },
            "Corn_(maize)___Northern_Leaf_Blight": {
                "crop": "Corn (Maize)",
                "disease_name": "Northern Corn Leaf Blight (Exserohilum turcicum)",
                "severity": "Moderate to High",
                "symptoms": [
                    "Large, elliptical cigar-shaped grayish-green to tan lesions on foliage",
                    "Dark concentric zones of fungal sporulation visible during damp mornings"
                ],
                "organic_remedies": [
                    "Apply Trichoderma viride @ 5g/L on lower foliage.",
                    "Prompt disposal of crop residue after cob harvest."
                ],
                "chemical_management": [
                    "Carbendazim 12% + Mancozeb 63% WP (Saaf) @ 2g/L or Azoxystrobin @ 1ml/L."
                ],
                "prevention": "Select Northern Corn Leaf Blight resistant hybrids; clean plow tillage."
            },
            "Corn_(maize)___healthy": {
                "crop": "Corn (Maize)",
                "disease_name": "Healthy Corn Leaf",
                "severity": "None detected",
                "symptoms": [
                    "Vibrant green wide blades with strong central midribs",
                    "Clean leaf canopy with no fungal pustules or blight"
                ],
                "organic_remedies": [
                    "Apply balanced bio-fertilizers (Azospirillum and PSB).",
                    "Provide balanced zinc and nitrogen nutrition."
                ],
                "chemical_management": [
                    "No chemical sprays necessary."
                ],
                "prevention": "Maintain optimal plant population and soil moisture management."
            }
        }

        crop_key = (crop_name or "").lower().strip()
        matched_kb_crop = "tomato"
        for k in self.knowledge_base.keys():
            if k in crop_key:
                matched_kb_crop = k
                break

        kb_fallback = self.knowledge_base[matched_kb_crop]

        if label in model_details:
            info = model_details[label]
            crop_display = info["crop"]
            disease_name = info["disease_name"]
            severity = info["severity"]
            symptoms = info["symptoms"]
            organic_remedies = info["organic_remedies"]
            chemical_management = info["chemical_management"]
            prevention = info["prevention"]
        else:
            disease_name = label.split("___", 1)[-1].replace("_", " ").title()
            crop_display = crop_name.capitalize() if crop_name else "Crop"
            severity = kb_fallback["severity"]
            symptoms = kb_fallback["symptoms"]
            organic_remedies = kb_fallback["organic_remedies"]
            chemical_management = kb_fallback["chemical_management"]
            prevention = kb_fallback["prevention"]

        healthy = "healthy" in label.lower()
        status = "Healthy leaf predicted" if healthy else "Possible disease detected"
        if healthy:
            severity = "None detected"

        # Translations & speech synthesis
        trans = kb_fallback.get("translations", {})
        lang_key = (lang or "en").lower().strip()
        speech_text = (
            f"Diagnosis for {crop_display}: {disease_name}. "
            f"Model confidence: {confidence_percent} percent."
        )
        if lang_key in trans:
            speech_text = trans[lang_key].get("speech_text", speech_text)

        return {
            "success": True,
            "is_valid_plant": True,
            "crop": crop_display,
            "status": status,
            "disease_name": disease_name,
            "confidence": confidence,
            "confidence_percent": confidence_percent,
            "severity": severity,
            "symptoms": symptoms,
            "organic_remedies": organic_remedies,
            "chemical_management": chemical_management,
            "prevention": prevention,
            "model_mode": "Trained Plant Disease Vision Model (PyTorch)",
            "speech_text": speech_text,
            "translations": trans,
            "selected_lang": lang_key,
            "disclaimer": "AI outputs are decision-support recommendations based on leaf image analysis and are not 100% guaranteed diagnostic facts. For critical infestations, verify with your local Krishi Vigyan Kendra (KVK) extension officer."
        }


predictor = DiseasePredictor()

def get_disease_predictor():
    return predictor


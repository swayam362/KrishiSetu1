/**
 * KrushiSetu Agronomy & Crop Doctor Multilingual & Voice Engine (i18n-agri.js)
 * Provides translations across 5 languages: English, Hindi, Marathi, Telugu, Kannada
 * and Web Speech API Text-to-Speech (TTS) + Speech Recognition (STT).
 */

const AGRI_I18N = {
  currentLang: localStorage.getItem('krushisetu_lang') || 'en',

  languages: {
    en: { name: 'English', native: 'English', voiceCode: 'en-IN', flag: '🇬🇧' },
    hi: { name: 'Hindi', native: 'हिन्दी', voiceCode: 'hi-IN', flag: '🇮🇳' },
    mr: { name: 'Marathi', native: 'मराठी', voiceCode: 'mr-IN', flag: '🚩' },
    te: { name: 'Telugu', native: 'తెలుగు', voiceCode: 'te-IN', flag: '🌾' },
    kn: { name: 'Kannada', native: 'ಕನ್ನಡ', voiceCode: 'kn-IN', flag: '🌱' }
  },

  translations: {
    en: {
      crop_doctor_title: 'KrushiSetu AI Crop Doctor',
      crop_doctor_tag: 'AI Plant Pathology & Soil Advisor',
      crop_doctor_sub: 'Upload or capture a photo of infected crop leaves for instant disease diagnosis, organic remedies, voice advisory, and soil fertilizer scheduling.',
      upload_box_title: 'Upload Crop Leaf Photo',
      upload_box_sub: 'Click to upload or drag & drop (JPG, PNG)',
      select_image_btn: '📸 Select Image',
      speak_crop_btn: '🎙️ Speak Crop / Symptoms',
      speak_crop_listening: '🎙️ Listening... Speak now',
      diagnosis_result_badge: 'Diagnosis Result',
      confidence_label: 'Confidence Match',
      symptoms_heading: 'Detected Symptoms:',
      organic_heading: '🌿 Recommended Organic Treatment:',
      chemical_heading: '🧪 Chemical Treatment (If severe):',
      prevention_heading: '🛡️ Prevention & Agronomy Advice:',
      voice_play_btn: '🔊 Listen Voice Advisory',
      voice_pause_btn: '⏸️ Pause Voice',
      voice_resume_btn: '▶️ Resume Voice',
      voice_stop_btn: '⏹️ Stop',
      voice_speaking_now: 'Speaking advisory in English...',
      soil_title: 'Soil Nutrient & Fertilizer Dosage Calculator',
      soil_tag: 'Soil Health Intelligence',
      soil_sub: 'Enter your soil test values (N-P-K & pH) to receive crop-specific fertilizer plans and reduce excessive chemical costs.',
      target_crop_label: 'Target Crop',
      nitrogen_label: 'Nitrogen (N) kg/ha',
      phosphorus_label: 'Phosphorus (P) kg/ha',
      potassium_label: 'Potassium (K) kg/ha',
      ph_label: 'Soil pH Level',
      calc_soil_btn: '🌱 Calculate Soil Fertilizer Plan',
      voice_listen_soil: '🔊 Listen Soil Health Report',
      causes_heading: '🔬 Pathogen & Potential Causes:',
      fertilizer_heading: '🌱 Condition-Specific Fertilizer & Nutrition Advice:',
      auto_crop_detected: '🔍 Auto-Detected Plant Species',
      pathogen_label: 'Pathogen',
      disclaimer_label: 'Advisory Note: AI outputs are decision-support recommendations. Consult local KVK officers for severe infestations.'
    },
    hi: {
      crop_doctor_title: 'कृषिसेतु एआई क्रॉप डॉक्टर',
      crop_doctor_tag: 'एआई पादप रोग एवं मृदा स्वास्थ्य सलाहकार',
      crop_doctor_sub: 'फसल की रोगग्रस्त पत्ती की फोटो अपलोड करें और तुरंत सटीक रोग पहचान, जैविक उपचार, रासायनिक दवाएं एवं आवाज में सलाह प्राप्त करें।',
      upload_box_title: 'फसल की पत्ती की फोटो अपलोड करें',
      upload_box_sub: 'फोटो चुनने या खींचने के लिए यहां क्लिक करें (JPG, PNG)',
      select_image_btn: '📸 फोटो चुनें',
      speak_crop_btn: '🎙️ बोलकर फसल या लक्षण बताएं',
      speak_crop_listening: '🎙️ सुन रहे हैं... कृपया बोलें',
      diagnosis_result_badge: 'रोग निदान रिपोर्ट',
      confidence_label: 'सटीकता मिलान',
      symptoms_heading: 'पहचाने गए रोग लक्षण:',
      organic_heading: '🌿 अनुशंसित जैविक उपचार:',
      chemical_heading: '🧪 रासायनिक नियंत्रण (गंभीर प्रकोप पर):',
      prevention_heading: '🛡️ रोकथाम व कृषि सावधानियां:',
      voice_play_btn: '🔊 आवाज में सलाह सुनें (Audio)',
      voice_pause_btn: '⏸️ रोकें',
      voice_resume_btn: '▶️ फिर से सुनें',
      voice_stop_btn: '⏹️ बंद करें',
      voice_speaking_now: 'हिन्दी में सलाह सुनाई जा रही है...',
      soil_title: 'मृदा पोषक तत्व एवं उर्वरक खुराक कैलकुलेटर',
      soil_tag: 'मृदा स्वास्थ्य विश्लेषण',
      soil_sub: 'मिट्टी जांच के मान (N-P-K व pH) दर्ज करें और यूरिया, डीएपी, पोटाश का संतुलित चार्ट प्राप्त करें।',
      target_crop_label: 'लक्षित फसल',
      nitrogen_label: 'नाइट्रोजन (N) किग्रा/हेक्टेयर',
      phosphorus_label: 'फॉस्फोरस (P) किग्रा/हेक्टेयर',
      potassium_label: 'पोटाश (K) किग्रा/हेक्टेयर',
      ph_label: 'मिट्टी का पीएच (pH) मान',
      calc_soil_btn: '🌱 उर्वरक योजना की गणना करें',
      voice_listen_soil: '🔊 मिट्टी रिपोर्ट आवाज में सुनें',
      causes_heading: '🔬 रोगकारक एवं संभावित कारण:',
      fertilizer_heading: '🌱 रोग नियंत्रण हेतु उर्वरक एवं पोषण सलाह:',
      auto_crop_detected: '🔍 एआई द्वारा स्वतः पहचानी गई फसल',
      pathogen_label: 'रोगकारक',
      disclaimer_label: 'सलाह नोट: एआई परिणाम निर्णय सहायता के लिए हैं। गंभीर स्थिति में स्थानीय कृषि विज्ञान केंद्र (KVK) से संपर्क करें।'
    },
    mr: {
      crop_doctor_title: 'कृषीसेतू पीक डॉक्टर (Crop Doctor)',
      crop_doctor_tag: 'एआय पीक रोग निदान व जमीन सल्लागार',
      crop_doctor_sub: 'पिकाच्या रोगट पानाचा फोटो अपलोड करा आणि तात्काळ अचूक रोग निदान, सेंद्रिय उपाय, रासायनिक फवारणी व ऑडिओ मार्गदर्शन मिळवा.',
      upload_box_title: 'पिकाच्या पानाचा फोटो अपलोड करा',
      upload_box_sub: 'फोटो निवडण्यासाठी किंवा ड्रॅग करण्यासाठी येथे क्लिक करा (JPG, PNG)',
      select_image_btn: '📸 फोटो निवडा',
      speak_crop_btn: '🎙️ बोलून पीक किंवा लक्षणे सांगा',
      speak_crop_listening: '🎙️ ऐकत आहे... कृपया बोला',
      diagnosis_result_badge: 'रोग निदान अहवाल',
      confidence_label: 'तंतोतंत खात्री',
      symptoms_heading: 'आढळलेली रोगाची लक्षणे:',
      organic_heading: '🌿 शिफारस केलेले सेंद्रिय / जैविक उपचार:',
      chemical_heading: '🧪 रासायनिक फवारणी (तीव्र प्रादुर्भाव असल्यास):',
      prevention_heading: '🛡️ प्रतिबंधात्मक कृषी उपाय:',
      voice_play_btn: '🔊 मराठीत आवाज ऐका (Audio)',
      voice_pause_btn: '⏸️ थांबवा',
      voice_resume_btn: '▶️ पुढे ऐका',
      voice_stop_btn: '⏹️ बंद करा',
      voice_speaking_now: 'मराठीत ऑडिओ सल्ला सुरू आहे...',
      soil_title: 'माती परीक्षण व खत मात्रा गणकयंत्र',
      soil_tag: 'जमीन आरोग्य बुद्धिमत्ता',
      soil_sub: 'माती परीक्षणातील नत्र, स्फुरद, पालाश व सामू टाका आणि पिकासाठी योग्य खत व्यवस्थापन मिळवा.',
      target_crop_label: 'निवडलेले पीक',
      nitrogen_label: 'उपलब्ध नत्र (N) किलो/हेक्टर',
      phosphorus_label: 'उपलब्ध स्फुरद (P) किलो/हेक्टर',
      potassium_label: 'उपलब्ध पालाश (K) किलो/हेक्टर',
      ph_label: 'जमिनीचा सामू (pH)',
      calc_soil_btn: '🌱 खत नियोजन तपासा',
      voice_listen_soil: '🔊 माती अहवाल ऑडिओमध्ये ऐका',
      causes_heading: '🔬 रोगकारक व संभाव्य कारणे:',
      fertilizer_heading: '🌱 रोग प्रतिबंधासाठी खत व पोषण व्यवस्थापन:',
      auto_crop_detected: '🔍 आपोआप ओळखलेले पीक',
      pathogen_label: 'रोगकारक घटक',
      disclaimer_label: 'सूचना: एआय शिफारशी मार्गदर्शनासाठी आहेत. आवश्यकतेनुसार स्थानिक कृषी तज्ज्ञ किंवा केव्हीकेशी संपर्क साधा.'
    },
    te: {
      crop_doctor_title: 'కృషిసేతు ఏఐ పంట డాక్టర్',
      crop_doctor_tag: 'ఏఐ మొక్కల వ్యాధి నిర్ధారణ & నేల సలహాదారు',
      crop_doctor_sub: 'వ్యాధి సోకిన పంట ఆకు ఫోటోను అప్‌లోడ్ చేయండి, తక్షణ చికిత్సలు మరియు ఆడియో సలహాలను పొందండి.',
      upload_box_title: 'పంట ఆకు ఫోటోను అప్‌లోడ్ చేయండి',
      upload_box_sub: 'ఫోటోను ఎంచుకోవడానికి ఇక్కడ క్లిక్ చేయండి',
      select_image_btn: '📸 ఫోటో ఎంచుకోండి',
      speak_crop_btn: '🎙️ మాట్లాడి పంట తెలపండి',
      speak_crop_listening: '🎙️ వింటున్నాము... మాట్లాడండి',
      diagnosis_result_badge: 'వ్యాధి నిర్ధారణ ఫలితం',
      confidence_label: 'ఖచ్చితత్వం',
      symptoms_heading: 'గుర్తించిన లక్షణాలు:',
      organic_heading: '🌿 సేంద్రీయ చికిత్సలు:',
      chemical_heading: '🧪 రసాయన నియంత్రణ:',
      prevention_heading: '🛡️ నివారణ చర్యలు:',
      voice_play_btn: '🔊 ఆడియో సలహా వినండి',
      voice_pause_btn: '⏸️ ఆపు',
      voice_resume_btn: '▶️ కొనసాగించు',
      voice_stop_btn: '⏹️ నిలిపివేయి',
      voice_speaking_now: 'తెలుగులో ఆడియో ప్లే అవుతోంది...',
      soil_title: 'నేల పోషకాలు & ఎరువుల కాలిక్యులేటర్',
      soil_tag: 'నేల ఆరోగ్య విశ్లేషణ',
      soil_sub: 'మీ నేల పరీక్ష విలువలను నమోదు చేసి పంటకు తగిన సమతుల్య ఎరువుల ప్రణాళికను పొందండి.',
      target_crop_label: 'పంట',
      nitrogen_label: 'నత్రజని (N) కిలో/హెక్టార్',
      phosphorus_label: 'భాస్వరం (P) కిలో/హెక్టార్',
      potassium_label: 'పొటాషియం (K) కిలో/హెక్టార్',
      ph_label: 'నేల pH విలువ',
      calc_soil_btn: '🌱 ఎరువుల ప్రణాళికను లెక్కించండి',
      voice_listen_soil: '🔊 నేల నివేదిక వినండి',
      causes_heading: '🔬 రోగకారకం & సంభావ్య కారణాలు:',
      fertilizer_heading: '🌱 ఎరువులు & పోషక నిర్వహణ సలహా:',
      auto_crop_detected: '🔍 స్వయంచాలకంగా గుర్తించిన పంట',
      pathogen_label: 'రోగకారకం',
      disclaimer_label: 'సలహా గమనిక: ఏఐ సూచనలు రైతులకు సహాయం కోసం మాత్రమే.'
    },
    kn: {
      crop_doctor_title: 'ಕೃಷಿಸೇತು ಎಐ ಕ್ರಾಪ್ ಡಾಕ್ಟರ್',
      crop_doctor_tag: 'ಎಐ ಸಸ್ಯ ರೋಗ ನಿದಾನ & ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಸಲಹೆಗಾರ',
      crop_doctor_sub: 'ರೋಗಪೀಡಿತ ಎಲೆಯ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ, ತ್ವರಿತ ರೋಗ ಪತ್ತೆ ಮತ್ತು ಧ್ವನಿ ಸಲಹೆಯನ್ನು ಪಡೆಯಿರಿ.',
      upload_box_title: 'ಬೆಳೆಯ ಎಲೆಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
      upload_box_sub: 'ಫೋಟೋ ಆಯ್ಕೆ ಮಾಡಲು ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ',
      select_image_btn: '📸 ಫೋಟೋ ಆಯ್ಕೆಮಾಡಿ',
      speak_crop_btn: '🎙️ ಧ್ವನಿ ಮೂಲಕ ಬೆಳೆ ತಿಳಿಸಿ',
      speak_crop_listening: '🎙️ ಆಲಿಸಲಾಗುತ್ತಿದೆ... ಮಾತನಾಡಿ',
      diagnosis_result_badge: 'ರೋಗ ಪತ್ತೆ ಫಲಿತಾಂಶ',
      confidence_label: 'ಖಚಿತತೆ',
      symptoms_heading: 'ಗುರುತಿಸಲಾದ ಲಕ್ಷಣಗಳು:',
      organic_heading: '🌿 ಸಾವಯವ ಚಿಕಿತ್ಸೆಗಳು:',
      chemical_heading: '🧪 ರಾಸಾಯನಿಕ ನಿರ್ವಹಣೆ:',
      prevention_heading: '🛡️ ಮುನ್ನೆಚ್ಚರಿಕೆ ಕ್ರಮಗಳು:',
      voice_play_btn: '🔊 ಆಡಿಯೋ ಸಲಹೆ ಕೇಳಿ',
      voice_pause_btn: '⏸️ ವಿರಾಮ',
      voice_resume_btn: '▶️ ಮುಂದುವರಿಸಿ',
      voice_stop_btn: '⏹️ ನಿಲ್ಲಿಸಿ',
      voice_speaking_now: 'ಕನ್ನಡದಲ್ಲಿ ಆಡಿಯೋ ಪ್ಲೇ ಆಗುತ್ತಿದೆ...',
      soil_title: 'ಮಣ್ಣಿನ ಪೋಷಕಾಂಶ & ರಸಗೊಬ್ಬರ ಕ್ಯಾಲ್ಕುಲೇಟರ್',
      soil_tag: 'ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಮಾಹಿತಿ',
      soil_sub: 'ಮಣ್ಣಿನ ಪರೀಕ್ಷಾ ಮೌಲ್ಯಗಳನ್ನು ನಮೂದಿಸಿ ಮತ್ತು ಸಮತೋಲಿತ ಗೊಬ್ಬರದ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಪಡೆಯಿರಿ.',
      target_crop_label: 'ಉದ್ದೇಶಿತ ಬೆಳೆ',
      nitrogen_label: 'ಸಾರಜನಕ (N) ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
      phosphorus_label: 'ರಂಜಕ (P) ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
      potassium_label: 'ಪೊಟ್ಯಾಶ್ (K) ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
      ph_label: 'ಮಣ್ಣಿನ ಪಿ.ಎಚ್ (pH)',
      calc_soil_btn: '🌱 ಗೊಬ್ಬರ ಯೋಜನೆ ಲೆಕ್ಕಾಚಾರ ಮಾಡಿ',
      voice_listen_soil: '🔊 ಮಣ್ಣಿನ ವರದಿ ಕೇಳಿ',
      causes_heading: '🔬 ರೋಗಕಾರಕ & ಸಂಭಾವ್ಯ ಕಾರಣಗಳು:',
      fertilizer_heading: '🌱 ರಸಗೊಬ್ಬರ & ಪೋಷಕಾಂಶ ನಿರ್ವಹಣೆ ಸಲಹೆ:',
      auto_crop_detected: '🔍 ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಪತ್ತೆಯಾದ ಬೆಳೆ',
      pathogen_label: 'ರೋಗಕಾರಕ',
      disclaimer_label: 'ಸಲಹಾ ಸೂಚನೆ: ಎಐ ಫಲಿತಾಂಶಗಳು ನಿರ್ಧಾರ ಬೆಂಬಲಕ್ಕಾಗಿ ಮಾತ್ರ.'
    }
  },

  t(key) {
    const lang = this.currentLang;
    if (this.translations[lang] && this.translations[lang][key]) {
      return this.translations[lang][key];
    }
    if (this.translations['en'] && this.translations['en'][key]) {
      return this.translations['en'][key];
    }
    return key;
  },

  setLanguage(lang) {
    if (!this.languages[lang]) lang = 'en';
    this.currentLang = lang;
    localStorage.setItem('krushisetu_lang', lang);
    this.applyPageTranslations();
  },

  applyPageTranslations() {
    // Update all elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const val = this.t(key);
      if (val) {
        if (el.tagName === 'INPUT' && el.getAttribute('placeholder')) {
          el.setAttribute('placeholder', val);
        } else {
          el.innerHTML = val;
        }
      }
    });

    // Update active state in language selector pills if present
    document.querySelectorAll('.lang-pill').forEach(btn => {
      const bLang = btn.getAttribute('data-lang');
      if (bLang === this.currentLang) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }
};

/**
 * KrushiSetu Agronomy Voice Speech Synthesizer (TTS) & Speech Recognizer (STT)
 */
const AGRI_VOICE = {
  synth: window.speechSynthesis,
  activeUtterance: null,
  isSpeaking: false,
  isPaused: false,

  speak(text, lang = null, onStateChange = null) {
    if (!this.synth) {
      alert('Speech synthesis is not supported on this browser.');
      return;
    }

    this.stop();
    const targetLang = lang || AGRI_I18N.currentLang;
    const voiceMeta = AGRI_I18N.languages[targetLang] || AGRI_I18N.languages['en'];
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = voiceMeta.voiceCode || 'hi-IN';
    utterance.rate = 0.95; // Slightly slower for clear farmer comprehension
    utterance.pitch = 1.0;

    // Pick best matching voice if available in browser
    const voices = this.synth.getVoices();
    const matchedVoice = voices.find(v => v.lang.startsWith(targetLang) || v.lang.replace('_', '-').startsWith(voiceMeta.voiceCode));
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.onstart = () => {
      this.isSpeaking = true;
      this.isPaused = false;
      if (typeof onStateChange === 'function') onStateChange('start');
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.isPaused = false;
      if (typeof onStateChange === 'function') onStateChange('end');
    };

    utterance.onerror = (e) => {
      console.warn('Speech synthesis error:', e);
      this.isSpeaking = false;
      this.isPaused = false;
      if (typeof onStateChange === 'function') onStateChange('error');
    };

    this.activeUtterance = utterance;
    this.synth.speak(utterance);
  },

  pause(onStateChange = null) {
    if (this.synth && this.synth.speaking && !this.synth.paused) {
      this.synth.pause();
      this.isPaused = true;
      if (typeof onStateChange === 'function') onStateChange('pause');
    }
  },

  resume(onStateChange = null) {
    if (this.synth && this.synth.paused) {
      this.synth.resume();
      this.isPaused = false;
      if (typeof onStateChange === 'function') onStateChange('resume');
    }
  },

  stop(onStateChange = null) {
    if (this.synth) {
      this.synth.cancel();
      this.isSpeaking = false;
      this.isPaused = false;
      if (typeof onStateChange === 'function') onStateChange('stop');
    }
  },

  /**
   * Listen to user speech and transcribe to text
   */
  startListening(onResult, onStatusChange) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      if (typeof showToast === 'function') {
        showToast('Speech recognition not supported on this browser. Please use Chrome/Edge.', 'warning');
      } else {
        alert('Speech recognition is not supported on this browser.');
      }
      return;
    }

    const recognition = new SpeechRecognition();
    const targetLang = AGRI_I18N.currentLang;
    const voiceMeta = AGRI_I18N.languages[targetLang] || AGRI_I18N.languages['hi'];
    
    recognition.lang = voiceMeta.voiceCode || 'hi-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    if (typeof onStatusChange === 'function') onStatusChange('listening');

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (typeof onResult === 'function') onResult(transcript);
      if (typeof onStatusChange === 'function') onStatusChange('success', transcript);
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      if (typeof onStatusChange === 'function') onStatusChange('error', event.error);
    };

    recognition.onend = () => {
      if (typeof onStatusChange === 'function') onStatusChange('end');
    };

    recognition.start();
  }
};

// Initialize voices on window load
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
  };
}

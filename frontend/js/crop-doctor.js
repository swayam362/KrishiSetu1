/**
 * KrushiSetu Crop Doctor & Soil Health Analyzer
 * Integrated with Multilingual Translation (EN, HI, MR, TE, KN) and Web Speech Voice Assistant
 */

let currentDiagnosisData = null;
let currentSoilData = null;
let isMicListening = false;
let activeDiagnosisSpeechScript = '';
let activeSoilSpeechScript = '';

/**
 * Handle Language Change
 */
function changeLanguage(lang) {
  if (typeof AGRI_I18N !== 'undefined' && AGRI_I18N.setLanguage) {
    AGRI_I18N.setLanguage(lang);
  }
  
  // Update active pill UI
  document.querySelectorAll('.lang-pill').forEach(pill => {
    if (pill.getAttribute('data-lang') === lang) {
      pill.classList.add('active');
    } else {
      pill.classList.remove('active');
    }
  });

  // Re-render active cards in the new language if already open
  if (currentDiagnosisData) {
    renderDiagnosis(currentDiagnosisData);
  }
  if (currentSoilData) {
    renderBackendSoilResult(
      currentSoilData.data,
      currentSoilData.crop,
      currentSoilData.n,
      currentSoilData.p,
      currentSoilData.k,
      currentSoilData.ph
    );
  }
  if (typeof showToast === 'function') {
    const langObj = (typeof AGRI_I18N !== 'undefined' && AGRI_I18N.languages) ? AGRI_I18N.languages[lang] : null;
    showToast(`Language switched to ${langObj ? langObj.native : lang}`, 'info');
  }
}

/**
 * Handle Crop Selector change
 */
function onScanCropChange() {
  const selectedCrop = document.getElementById('select-scan-crop')?.value;
  if (currentDiagnosisData && currentDiagnosisData.crop !== selectedCrop) {
    currentDiagnosisData.crop = selectedCrop;
    renderDiagnosis(currentDiagnosisData);
  }
}

/**
 * Speech Recognition Microphone Handler
 */
function toggleVoiceInput() {
  const micBtn = document.getElementById('btn-mic-listen');
  const micText = document.getElementById('mic-status-text');

  if (isMicListening) {
    isMicListening = false;
    if (micBtn) micBtn.classList.remove('listening');
    if (micText) micText.innerText = (typeof AGRI_I18N !== 'undefined') ? AGRI_I18N.t('speak_crop_btn') : '🎙️ Speak Crop';
    return;
  }

  if (typeof AGRI_VOICE === 'undefined' || !AGRI_VOICE.startListening) {
    if (typeof showToast === 'function') {
      showToast('Speech recognition is not supported in this browser.', 'warning');
    }
    return;
  }

  isMicListening = true;
  AGRI_VOICE.startListening(
    (transcript) => {
      console.log('Voice recognized:', transcript);
      const lower = transcript.toLowerCase();
      
      const cropSelect = document.getElementById('select-scan-crop');
      if (lower.includes('tomato') || lower.includes('टमाटर') || lower.includes('टोमॅटो') || lower.includes('టమాట') || lower.includes('ಟೊಮೆಟೊ')) {
        if (cropSelect) cropSelect.value = 'Tomato';
      } else if (lower.includes('wheat') || lower.includes('गेहूं') || lower.includes('गहू') || lower.includes('గోధుమ') || lower.includes('ಗೋಧಿ')) {
        if (cropSelect) cropSelect.value = 'Wheat';
      } else if (lower.includes('onion') || lower.includes('प्याज') || lower.includes('कांदा') || lower.includes('ఉల్లి') || lower.includes('ಈರುಳ್ಳಿ')) {
        if (cropSelect) cropSelect.value = 'Onion';
      } else if (lower.includes('rice') || lower.includes('paddy') || lower.includes('धान') || lower.includes('भात') || lower.includes('వరి') || lower.includes('ಭತ್ತ')) {
        if (cropSelect) cropSelect.value = 'Rice';
      } else if (lower.includes('cotton') || lower.includes('कपास') || lower.includes('कापूस') || lower.includes('పత్తి') || lower.includes('ಹತ್ತಿ')) {
        if (cropSelect) cropSelect.value = 'Cotton';
      } else if (lower.includes('soybean') || lower.includes('सोयाबीन') || lower.includes('సోయాబీన్') || lower.includes('ಸೋಯಾಬೀನ್')) {
        if (cropSelect) cropSelect.value = 'Soybean';
      }

      if (typeof showToast === 'function') {
        showToast(`Spoken Input: "${transcript}"`, 'success');
      }
    },
    (status) => {
      if (status === 'listening') {
        if (micBtn) micBtn.classList.add('listening');
        if (micText) micText.innerText = (typeof AGRI_I18N !== 'undefined') ? AGRI_I18N.t('speak_crop_listening') : '🎙️ Listening...';
      } else {
        isMicListening = false;
        if (micBtn) micBtn.classList.remove('listening');
        if (micText) micText.innerText = (typeof AGRI_I18N !== 'undefined') ? AGRI_I18N.t('speak_crop_btn') : '🎙️ Speak Crop';
      }
    }
  );
}

/**
 * Handle File Selection & Pathology Upload
 */
async function handleFileSelect(e) {
  const file = (e.target && e.target.files) ? e.target.files[0] : (e.dataTransfer ? e.dataTransfer.files[0] : null);
  if (!file) return;

  const preview = document.getElementById('preview-holder');
  const laser = document.getElementById('laser-line');
  const promptText = document.getElementById('upload-prompt-text');
  const card = document.getElementById('diagnosis-card');
  const cropSelect = document.getElementById('select-scan-crop');

  // Validate image
  if (!file.type.startsWith('image/')) {
    if (typeof showToast === 'function') {
      showToast('Please select a valid image file (JPG, PNG).', 'error');
    }
    if (e.target && e.target.value) e.target.value = '';
    return;
  }

  // Show image preview immediately
  const reader = new FileReader();

  reader.onload = async function (event) {
    if (preview) {
      preview.style.backgroundImage = `url(${event.target.result})`;
      preview.style.display = 'block';
    }

    if (promptText) promptText.style.display = 'none';
    if (laser) laser.style.display = 'block';

    // Show loading in diagnosis container
    if (card) {
      card.style.display = 'block';
      card.innerHTML = `
        <div style="text-align: center; padding: 2.5rem 1rem;">
          <div style="font-size: 2.5rem; margin-bottom: 1rem; animation: pulse 1.5s infinite;">🔬</div>
          <h3 style="color: var(--primary-900); font-size: 1.25rem; margin-bottom: 0.5rem;">Analyzing Leaf with Trained AI Model...</h3>
          <p style="color: var(--slate-500); font-size: 0.9rem;">Extracting pathology features and computing diagnostic confidence.</p>
        </div>
      `;
    }

    const crop = cropSelect ? cropSelect.value : 'Tomato';
    const lang = (typeof AGRI_I18N !== 'undefined' && AGRI_I18N.currentLang) ? AGRI_I18N.currentLang : 'en';

    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('crop', crop);
      formData.append('crop_type', crop);
      formData.append('lang', lang);

      const token = localStorage.getItem('krushisetu_token');
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      if (typeof showToast === 'function') {
        showToast('Uploading leaf image for AI diagnosis...', 'info');
      }

      const response = await fetch('/api/ai/crop-doctor/diagnose', {
        method: 'POST',
        headers: headers,
        body: formData
      });

      let data;
      try {
        data = await response.json();
      } catch (parseErr) {
        throw new Error('The server returned an invalid response.');
      }

      // 1. Intercept Invalid Leaf Image / Notebook / Document rejections
      if (data && (data.is_valid_plant === false || (data.diagnosis && data.diagnosis.is_valid_plant === false))) {
        const diag = data.diagnosis || data;
        renderInvalidImage(diag);
        if (typeof showToast === 'function') {
          showToast(diag.error || 'Invalid leaf image: Please upload a photo of a real crop leaf.', 'warning');
        }
        return;
      }

      if (!response.ok) {
        throw new Error(data.error || data.message || `Diagnosis failed (HTTP ${response.status}).`);
      }

      if (!data.success || !data.diagnosis) {
        throw new Error(data.error || data.message || 'Diagnosis failed.');
      }

      const diagnosis = data.diagnosis;
      currentDiagnosisData = {
        ...diagnosis,
        crop: diagnosis.crop || crop,
        image_url: data.image_url || event.target.result
      };

      renderDiagnosis(currentDiagnosisData);

      const confidence = Number(diagnosis.confidence_percent ?? (Number(diagnosis.confidence) * 100));

      if (typeof showToast === 'function') {
        showToast(
          `Diagnosis returned: ${diagnosis.disease_name}` +
          (Number.isFinite(confidence) ? ` (${confidence.toFixed(1)}% confidence)` : ''),
          'success'
        );
      }

    } catch (err) {
      console.error('Crop diagnosis error:', err);
      if (card) {
        card.style.display = 'block';
        card.innerHTML = `
          <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 2.25rem; margin-bottom: 0.75rem;">⚠️</div>
            <h4 style="color: var(--danger); font-size: 1.15rem; margin-bottom: 0.5rem;">Diagnosis Request Failed</h4>
            <p style="color: var(--slate-600); font-size: 0.9rem; margin-bottom: 1.25rem;">${err.message || 'Could not complete image diagnosis.'}</p>
            <button type="button" class="btn btn-outline-primary btn-sm" onclick="document.getElementById('crop-file-input').click()">
              Try Another Photo
            </button>
          </div>
        `;
      }
      if (typeof showToast === 'function') {
        showToast(err.message || 'Diagnosis failed. Please try again.', 'error');
      }
    } finally {
      if (laser) laser.style.display = 'none';
    }
  };

  reader.onerror = function () {
    if (laser) laser.style.display = 'none';
    if (typeof showToast === 'function') {
      showToast('Could not read the selected image file.', 'error');
    }
  };

  reader.readAsDataURL(file);
}

/**
 * Render Diagnosis Card with Multilingual Content and Speech
 */
function renderDiagnosis(diag) {
  const card = document.getElementById('diagnosis-card');
  if (!card) return;

  const currentLang = (typeof AGRI_I18N !== 'undefined' && AGRI_I18N.currentLang) ? AGRI_I18N.currentLang : 'en';
  let diseaseName = diag.disease_name || 'Plant Leaf Analysis';
  let severity = diag.severity || 'Moderate';
  let symptoms = diag.symptoms || [];
  let organicRemedies = diag.organic_remedies || [];
  let chemicalRemedies = diag.chemical_management || diag.chemical_remedies || [];
  let prevention = diag.prevention || '';
  let speechText = diag.speech_text || `${diseaseName}. Recommended treatment: ${organicRemedies[0] || 'Spray bio-fungicide.'}`;

  // Check if translation exists for current language
  if (diag.translations && diag.translations[currentLang]) {
    const t = diag.translations[currentLang];
    diseaseName = t.disease_name || diseaseName;
    severity = t.severity || severity;
    if (t.symptoms && t.symptoms.length > 0) symptoms = t.symptoms;
    if (t.organic_remedies && t.organic_remedies.length > 0) organicRemedies = t.organic_remedies;
    if (t.chemical_management && t.chemical_management.length > 0) chemicalRemedies = t.chemical_management;
    if (t.prevention) prevention = t.prevention;
    if (t.speech_text) speechText = t.speech_text;
  }

  const confidence = Math.round(Number(diag.confidence_percent ?? (Number(diag.confidence || 0.9) * 100)));
  const isHealthy = (diag.status && diag.status.toLowerCase().includes('healthy')) || diseaseName.toLowerCase().includes('healthy');

  let severityClass = 'severity-moderate';
  if (isHealthy) {
    severityClass = 'badge-success';
  } else if (severity.toLowerCase().includes('high') || severity.toLowerCase().includes('severe') || severity.toLowerCase().includes('गंभीर') || severity.toLowerCase().includes('तीव्र')) {
    severityClass = 'badge-danger';
  } else if (severity.toLowerCase().includes('low') || severity.toLowerCase().includes('mild') || severity.toLowerCase().includes('कमी') || severity.toLowerCase().includes('हल्का')) {
    severityClass = 'badge-info';
  }

  activeDiagnosisSpeechScript = speechText;

  card.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
      <div>
        <span class="badge ${isHealthy ? 'badge-success' : 'badge-warning'}" style="margin-bottom: 0.25rem;">
          ${isHealthy ? '✅ Healthy Plant' : '⚠️ ' + (typeof AGRI_I18N !== 'undefined' ? AGRI_I18N.t('diagnosis_result_badge') : 'Diagnosis Result')}
        </span>
        <h2 style="font-size: 1.45rem; color: var(--slate-900); margin: 0.25rem 0;">${diseaseName}</h2>
        <div style="font-size: 0.85rem; color: var(--slate-500);">
          ${typeof AGRI_I18N !== 'undefined' ? AGRI_I18N.t('confidence_label') : 'Confidence Match'}: 
          <strong style="color: var(--primary-700);">${confidence}% Match</strong>
        </div>
      </div>
      <div>
        <span class="severity-pill ${severityClass}" style="padding: 0.35rem 0.75rem; border-radius: var(--radius-full); font-size: 0.8rem; font-weight: 700;">
          ${severity}
        </span>
      </div>
    </div>

    <!-- Confidence Bar -->
    <div style="background: var(--slate-100); border-radius: var(--radius-full); height: 8px; overflow: hidden; margin-bottom: 1.25rem;">
      <div style="background: ${isHealthy ? 'var(--primary-600)' : (confidence > 80 ? 'var(--accent-amber)' : 'var(--primary-600)')}; width: ${confidence}%; height: 100%; transition: width 0.6s ease;"></div>
    </div>

    <!-- Voice Assistant Audio Bar -->
    <div class="voice-assistant-panel" style="margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between; background: var(--primary-50); padding: 0.75rem 1rem; border-radius: var(--radius-md); border: 1px solid var(--primary-200);">
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span id="diag-speaker-icon" style="font-size: 1.5rem;">🔊</span>
        <div>
          <strong style="font-size: 0.9rem; color: var(--primary-900);">${typeof AGRI_I18N !== 'undefined' ? AGRI_I18N.t('voice_play_btn') : 'Listen Audio Advisory'}</strong>
          <div style="font-size: 0.78rem; color: var(--slate-600);">Audio guidance in ${(typeof AGRI_I18N !== 'undefined' && AGRI_I18N.languages[currentLang]) ? AGRI_I18N.languages[currentLang].native : currentLang.toUpperCase()}</div>
        </div>
      </div>
      <button type="button" class="btn btn-primary btn-sm" onclick="playDiagnosisVoice()">
        🔊 Listen Voice
      </button>
    </div>

    <!-- Symptoms -->
    ${symptoms && symptoms.length > 0 ? `
      <div style="margin-bottom: 1.25rem;">
        <h4 style="font-size: 0.95rem; color: var(--slate-800); margin-bottom: 0.5rem;">
          ${typeof AGRI_I18N !== 'undefined' ? AGRI_I18N.t('symptoms_heading') : 'Detected Symptoms:'}
        </h4>
        <ul style="padding-left: 1.25rem; font-size: 0.88rem; color: var(--slate-600); line-height: 1.5;">
          ${symptoms.map(s => `<li>${s}</li>`).join('')}
        </ul>
      </div>
    ` : ''}

    <!-- Organic Remedies -->
    ${organicRemedies && organicRemedies.length > 0 ? `
      <div class="remedy-box" style="margin-bottom: 1rem; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: var(--radius-md); padding: 0.85rem 1rem;">
        <h4 style="font-size: 0.95rem; color: #166534; margin-bottom: 0.4rem;">
          ${typeof AGRI_I18N !== 'undefined' ? AGRI_I18N.t('organic_heading') : '🌿 Recommended Organic Treatment:'}
        </h4>
        <ul style="padding-left: 1.25rem; font-size: 0.88rem; color: #15803d; line-height: 1.5;">
          ${organicRemedies.map(r => `<li>${r}</li>`).join('')}
        </ul>
      </div>
    ` : ''}

    <!-- Chemical Remedies -->
    ${chemicalRemedies && chemicalRemedies.length > 0 ? `
      <div class="remedy-box" style="margin-bottom: 1rem; background: #fffbeb; border: 1px solid #fde68a; border-radius: var(--radius-md); padding: 0.85rem 1rem;">
        <h4 style="font-size: 0.95rem; color: #92400e; margin-bottom: 0.4rem;">
          ${typeof AGRI_I18N !== 'undefined' ? AGRI_I18N.t('chemical_heading') : '🧪 Chemical Treatment (If severe):'}
        </h4>
        <ul style="padding-left: 1.25rem; font-size: 0.88rem; color: #b45309; line-height: 1.5;">
          ${chemicalRemedies.map(c => `<li>${c}</li>`).join('')}
        </ul>
      </div>
    ` : ''}

    <!-- Prevention -->
    ${prevention ? `
      <div style="margin-bottom: 1rem;">
        <h4 style="font-size: 0.92rem; color: var(--slate-800); margin-bottom: 0.35rem;">
          ${typeof AGRI_I18N !== 'undefined' ? AGRI_I18N.t('prevention_heading') : '🛡️ Prevention & Agronomy Advice:'}
        </h4>
        <p style="font-size: 0.86rem; color: var(--slate-600); line-height: 1.5;">${prevention}</p>
      </div>
    ` : ''}

    <!-- Disclaimer -->
    <div style="margin-top: 1.25rem; padding-top: 0.75rem; border-top: 1px solid var(--slate-200); font-size: 0.78rem; color: var(--slate-500); line-height: 1.4;">
      ⚠️ <em>${diag.disclaimer || 'Advisory Note: AI outputs are decision-support recommendations. Consult local KVK officers for severe infestations.'}</em>
    </div>
  `;

  card.style.display = 'block';
  card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Render Dedicated Invalid Leaf Image Rejection Card
 */
function renderInvalidImage(diag) {
  const card = document.getElementById('diagnosis-card');
  if (!card) return;

  const currentLang = (typeof AGRI_I18N !== 'undefined' && AGRI_I18N.currentLang) ? AGRI_I18N.currentLang : 'en';
  let title = diag.disease_name || 'Invalid Leaf Image Detected';
  let message = diag.error || diag.message || 'The uploaded photo does not appear to be a crop leaf (e.g. notebook page, document, or non-plant object).';
  let instructions = diag.instructions || [
    'Take a direct close-up photo of a crop plant leaf (e.g. Tomato, Corn, Bell Pepper).',
    'Make sure the leaf covers the central frame of the camera.',
    'Ensure clear natural lighting without shadows, glare, or blur.',
    'Do not upload drawings, notebook pages, documents, or screenshots.'
  ];
  let speechText = diag.speech_text || 'Invalid image detected. Please upload a clear photo of an authentic plant leaf.';

  if (diag.translations && diag.translations[currentLang]) {
    const t = diag.translations[currentLang];
    if (t.disease_name) title = t.disease_name;
    if (t.speech_text) speechText = t.speech_text;
  }

  activeDiagnosisSpeechScript = speechText;

  card.innerHTML = `
    <div style="background: #fef2f2; border: 1.5px solid #fecaca; border-radius: var(--radius-lg); padding: 1.5rem; text-align: left; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.08);">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
        <div>
          <span class="badge" style="margin-bottom: 0.35rem; font-size: 0.8rem; background: #dc2626; color: white; padding: 0.25rem 0.65rem; border-radius: 999px;">
            🚫 Invalid Photo / Not a Leaf
          </span>
          <h2 style="font-size: 1.35rem; color: #991b1b; margin: 0.35rem 0 0.15rem;">${title}</h2>
          <div style="font-size: 0.82rem; color: #b91c1c; font-weight: 500;">
            Leaf Authenticity Verification Gate
          </div>
        </div>
        <div>
          <span style="display: inline-block; padding: 0.35rem 0.75rem; border-radius: var(--radius-full); font-size: 0.78rem; font-weight: 700; background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5;">
            Validation Failed
          </span>
        </div>
      </div>

      <div style="color: #7f1d1d; font-size: 0.92rem; line-height: 1.55; margin-bottom: 1.25rem; background: #ffffff; padding: 0.85rem 1rem; border-radius: var(--radius-md); border-left: 4px solid #dc2626;">
        <strong style="color: #991b1b;">Analysis:</strong> ${message}
      </div>

      <!-- Voice Assistant Audio Bar for Invalid Image -->
      <div class="voice-assistant-panel" style="margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between; background: #fff5f5; padding: 0.75rem 1rem; border-radius: var(--radius-md); border: 1px solid #fca5a5;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span id="diag-speaker-icon" style="font-size: 1.4rem;">🔊</span>
          <div>
            <strong style="font-size: 0.88rem; color: #991b1b;">Audio Notice</strong>
            <div style="font-size: 0.76rem; color: #7f1d1d;">Hear spoken instructions</div>
          </div>
        </div>
        <button type="button" class="btn btn-sm" style="background: #dc2626; color: white; border: none; padding: 0.4rem 0.85rem; border-radius: var(--radius-md); cursor: pointer;" onclick="playDiagnosisVoice()">
          🔊 Play Audio
        </button>
      </div>

      <!-- Instructions List -->
      <div style="background: #ffffff; border: 1px solid #fee2e2; border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1.25rem;">
        <h4 style="font-size: 0.9rem; color: #991b1b; margin-bottom: 0.5rem;">📸 How to capture an accurate leaf scan:</h4>
        <ul style="padding-left: 1.25rem; font-size: 0.85rem; color: #475569; line-height: 1.6; margin: 0;">
          ${instructions.map(inst => `<li>${inst}</li>`).join('')}
        </ul>
      </div>

      <!-- Action Button -->
      <div style="text-align: center;">
        <button type="button" class="btn btn-primary" onclick="document.getElementById('crop-file-input').click()" style="padding: 0.65rem 1.5rem; font-weight: 600;">
          📸 Upload Genuine Crop Leaf Photo
        </button>
      </div>

      <!-- Disclaimer -->
      <div style="margin-top: 1.25rem; padding-top: 0.75rem; border-top: 1px solid #fecaca; font-size: 0.76rem; color: #991b1b; line-height: 1.4;">
        ℹ️ <em>${diag.disclaimer || 'The AI model requires an authentic agricultural crop leaf to diagnose plant health.'}</em>
      </div>
    </div>
  `;

  card.style.display = 'block';
  card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Text-to-Speech Playback for Diagnosis
 */
function playDiagnosisVoice() {
  const script = activeDiagnosisSpeechScript;
  if (!script) return;

  const currentLang = (typeof AGRI_I18N !== 'undefined' && AGRI_I18N.currentLang) ? AGRI_I18N.currentLang : 'en';
  const speakerIcon = document.getElementById('diag-speaker-icon');

  if (typeof AGRI_VOICE !== 'undefined' && AGRI_VOICE.speak) {
    AGRI_VOICE.speak(script, currentLang, (state) => {
      if (state === 'start' && speakerIcon) speakerIcon.classList.add('speaking');
      if ((state === 'end' || state === 'stop' || state === 'error') && speakerIcon) speakerIcon.classList.remove('speaking');
    });
  } else if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(script);
    utterance.lang = currentLang === 'hi' ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : 'en-IN');
    window.speechSynthesis.speak(utterance);
  }
}

/**
 * Calculate Soil Health & Fertilizer Schedule
 */
async function calculateSoilHealth(e) {
  if (e && e.preventDefault) e.preventDefault();

  const crop = document.getElementById('soil-crop')?.value || 'Wheat';
  const n = parseFloat(document.getElementById('soil-n')?.value || 85);
  const p = parseFloat(document.getElementById('soil-p')?.value || 18);
  const k = parseFloat(document.getElementById('soil-k')?.value || 28);
  const ph = parseFloat(document.getElementById('soil-ph')?.value || 6.8);

  const payload = {
    crop: crop,
    nitrogen: n,
    phosphorus: p,
    potassium: k,
    ph: ph,
    organic_carbon: 0.5,
    growth_stage: 'Sowing/Basal',
    location: 'Maharashtra'
  };

  try {
    const token = localStorage.getItem('krushisetu_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch('/api/ai/soil-analysis', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const data = await res.json();
      if (data.success && data.data) {
        currentSoilData = { data: data.data, crop, n, p, k, ph };
        renderBackendSoilResult(data.data, crop, n, p, k, ph);
        return;
      }
    }
  } catch (err) {
    console.warn('Backend soil API offline, falling back to local heuristic calculation:', err);
  }

  // Fallback client calculation if backend is unavailable
  const mockSoil = {
    soil_health_score: Math.min(95, Math.max(45, Math.round(100 - Math.abs(ph - 6.8) * 9 - (n < 60 ? 20 : 0)))),
    parameters: {
      nitrogen: { status: n < 50 ? 'Deficient / Low' : (n > 140 ? 'Excessive' : 'Optimal') },
      phosphorus: { status: p < 20 ? 'Deficient / Low' : 'Optimal' },
      potassium: { status: k < 25 ? 'Deficient / Low' : 'Optimal' },
      ph: { status: ph >= 6.0 && ph <= 7.5 ? 'Neutral & Ideal' : (ph < 6.0 ? 'Acidic' : 'Alkaline') }
    },
    fertilizer_options: [
      {
        plan_name: "Option 1: Straight Fertilizer Combination (Urea + SSP + MOP)",
        components: [
          `Apply Urea @ ${Math.round(Math.max(20, (120 - n) * 0.45))} kg/acre in split doses for ${crop}.`,
          `Single Super Phosphate (SSP) @ ${Math.round(Math.max(25, (40 - p) * 1.5))} kg/acre as basal dose.`,
          `Muriate of Potash (MOP) @ ${Math.round(Math.max(15, (35 - k) * 0.8))} kg/acre before flowering.`
        ]
      },
      {
        plan_name: "Option 2: Bio-Fertilizer & Organic Schedule",
        components: [
          `Incorporate Well-rotted Vermicompost @ 2 tonnes/acre during field preparation.`,
          `Apply Azotobacter & PSB (Phosphorus Solubilizing Bacteria) bio-culture @ 250g/acre seed treatment.`,
          `Spray fermented Jeevamrut @ 200 L/acre with irrigation water every 15 days.`
        ]
      }
    ],
    speech_scripts: {
      en: `Soil health score for ${crop} is calculated. Nitrogen is ${n < 50 ? 'deficient' : 'optimal'}. Follow the balanced fertilizer plan.`,
      hi: `किसान भाई, ${crop} के लिए मिट्टी की रिपोर्ट तैयार है। यूरिया और सुपर फॉस्फेट का संतुलित प्रयोग करें।`,
      mr: `शेतकरी मित्रांनो, ${crop} पिकासाठी मातीचा अहवाल तयार आहे. संतुलित खत मात्रा द्या.`
    }
  };

  currentSoilData = { data: mockSoil, crop, n, p, k, ph };
  renderBackendSoilResult(mockSoil, crop, n, p, k, ph);
}

/**
 * Render Soil Results with Multilingual Voice Reader
 */
function renderBackendSoilResult(result, crop, n, p, k, ph) {
  const resultContainer = document.getElementById('soil-result-card');
  const details = document.getElementById('soil-recommendation-details');
  if (!resultContainer || !details) return;

  const currentLang = (typeof AGRI_I18N !== 'undefined' && AGRI_I18N.currentLang) ? AGRI_I18N.currentLang : 'en';
  const score = result.soil_health_score || 78;
  const nutrients = result.parameters || result.nutrients || {};

  const nStat = nutrients.nitrogen ? nutrients.nitrogen.status : (n < 50 ? 'Deficient' : 'Optimal');
  const pStat = nutrients.phosphorus ? nutrients.phosphorus.status : (p < 20 ? 'Low' : 'Optimal');
  const kStat = nutrients.potassium ? nutrients.potassium.status : (k < 25 ? 'Low' : 'Optimal');
  const phStat = nutrients.ph ? nutrients.ph.status : (ph >= 6.0 && ph <= 7.5 ? 'Neutral & Ideal' : (ph < 6.0 ? 'Acidic' : 'Alkaline'));

  const options = Array.isArray(result.fertilizer_options) && result.fertilizer_options.length > 0
    ? result.fertilizer_options
    : [
      { plan_name: "Option 1: Straight Fertilizer Combination", components: [`Apply Urea @ 28 kg/acre for ${crop}`, `SSP @ 40 kg/acre`] }
    ];

  const speechScript = (result.speech_scripts && result.speech_scripts[currentLang]) 
    ? result.speech_scripts[currentLang]
    : `Soil health score for ${crop} is ${score} out of 100. Follow the balanced fertilizer plan.`;

  activeSoilSpeechScript = speechScript;

  details.innerHTML = `
    <!-- Soil Header & Score -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 1rem;">
      <div>
        <h3 style="color: var(--slate-900); font-size: 1.35rem; margin-bottom: 0.25rem;">${crop} — Soil Advisory & Nutrient Balance</h3>
        <p style="color: var(--slate-500); font-size: 0.88rem;">Optimal balance maximizes harvest yield and lowers input fertilizer expenses.</p>
      </div>
      <div style="background: var(--primary-50); border: 2px solid var(--primary-400); border-radius: var(--radius-lg); padding: 0.5rem 1.25rem; text-align: center;">
        <div style="font-size: 0.75rem; font-weight: 700; color: var(--primary-800); text-transform: uppercase;">Soil Health Index</div>
        <div style="font-size: 1.6rem; font-weight: 800; color: var(--primary-700);">${score} / 100</div>
      </div>
    </div>

    <!-- Soil Voice Bar -->
    <div class="voice-assistant-panel" style="margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; background: var(--primary-50); padding: 0.75rem 1rem; border-radius: var(--radius-md); border: 1px solid var(--primary-200);">
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span id="soil-speaker-icon" style="font-size: 1.5rem;">🔊</span>
        <div>
          <div style="font-weight: 700; font-size: 0.92rem; color: var(--primary-900);">${(typeof AGRI_I18N !== 'undefined') ? AGRI_I18N.t('voice_listen_soil') : 'Listen Soil Report'}</div>
          <div style="font-size: 0.78rem; color: var(--slate-600);">Audio Soil Advisory in ${(typeof AGRI_I18N !== 'undefined' && AGRI_I18N.languages[currentLang]) ? AGRI_I18N.languages[currentLang].native : currentLang.toUpperCase()}</div>
        </div>
      </div>
      <button type="button" class="btn btn-primary btn-sm" onclick="playSoilVoice()">
        🔊 Listen Report
      </button>
    </div>

    <!-- Nutrient Cards -->
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin-bottom: 1.25rem;">
      <div style="background: var(--white); padding: 0.85rem; border-radius: var(--radius-md); border: 1px solid var(--slate-200); text-align:center;">
        <div style="font-size:0.8rem; color:var(--slate-500);">Nitrogen (N)</div>
        <strong style="color: ${String(nStat).includes('Deficient') ? 'var(--danger)' : 'var(--primary-700)'}; font-size: 0.95rem;">${n} kg/ha (${nStat})</strong>
      </div>
      <div style="background: var(--white); padding: 0.85rem; border-radius: var(--radius-md); border: 1px solid var(--slate-200); text-align:center;">
        <div style="font-size:0.8rem; color:var(--slate-500);">Phosphorus (P)</div>
        <strong style="color: ${String(pStat).includes('Low') || String(pStat).includes('Deficient') ? 'var(--accent-amber)' : 'var(--primary-700)'}; font-size: 0.95rem;">${p} kg/ha (${pStat})</strong>
      </div>
      <div style="background: var(--white); padding: 0.85rem; border-radius: var(--radius-md); border: 1px solid var(--slate-200); text-align:center;">
        <div style="font-size:0.8rem; color:var(--slate-500);">Potassium (K)</div>
        <strong style="color: ${String(kStat).includes('Low') || String(kStat).includes('Deficient') ? 'var(--accent-amber)' : 'var(--primary-700)'}; font-size: 0.95rem;">${k} kg/ha (${kStat})</strong>
      </div>
      <div style="background: var(--white); padding: 0.85rem; border-radius: var(--radius-md); border: 1px solid var(--slate-200); text-align:center;">
        <div style="font-size:0.8rem; color:var(--slate-500);">Soil pH Level</div>
        <strong style="color: var(--primary-700); font-size: 0.95rem;">${ph} (${phStat})</strong>
      </div>
    </div>

    <!-- Fertilizer Schedules -->
    <div style="margin-top: 1.25rem;">
      <h4 style="color: var(--primary-800); margin-bottom: 0.75rem;">🌱 ICAR Customized Fertilizer Schedules:</h4>
      ${options.map(opt => `
        <div class="remedy-box" style="margin-bottom: 0.75rem; background: var(--slate-50); border: 1px solid var(--slate-200); border-radius: var(--radius-md); padding: 0.85rem 1rem;">
          <h5 style="color: var(--primary-900); font-size: 0.92rem; margin-bottom: 0.35rem;">${opt.plan_name || 'Fertilizer Plan'}:</h5>
          <ul style="padding-left: 1.25rem; font-size: 0.88rem; color: var(--slate-700); line-height: 1.5;">
            ${(opt.components || []).map(c => `<li>${c}</li>`).join('')}
          </ul>
        </div>
      `).join('')}
    </div>
  `;

  resultContainer.style.display = 'block';
  resultContainer.scrollIntoView({ behavior: 'smooth' });
}

function playSoilVoice() {
  const script = activeSoilSpeechScript;
  if (!script) return;
  const currentLang = (typeof AGRI_I18N !== 'undefined' && AGRI_I18N.currentLang) ? AGRI_I18N.currentLang : 'en';
  const speakerIcon = document.getElementById('soil-speaker-icon');

  if (typeof AGRI_VOICE !== 'undefined' && AGRI_VOICE.speak) {
    AGRI_VOICE.speak(script, currentLang, (state) => {
      if (state === 'start' && speakerIcon) speakerIcon.classList.add('speaking');
      if ((state === 'end' || state === 'stop' || state === 'error') && speakerIcon) speakerIcon.classList.remove('speaking');
    });
  } else if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(script);
    utterance.lang = currentLang === 'hi' ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : 'en-IN');
    window.speechSynthesis.speak(utterance);
  }
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
  const cropFileInput = document.getElementById('crop-file-input');
  if (cropFileInput) {
    cropFileInput.addEventListener('change', handleFileSelect);
  }

  // Support drag-and-drop on upload zone
  const uploadZone = document.querySelector('.upload-zone');
  if (uploadZone) {
    ['dragenter', 'dragover'].forEach(evtName => {
      uploadZone.addEventListener(evtName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.style.borderColor = 'var(--primary-600)';
        uploadZone.style.background = '#e8f9ee';
      });
    });

    ['dragleave', 'drop'].forEach(evtName => {
      uploadZone.addEventListener(evtName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.style.borderColor = '';
        uploadZone.style.background = '';
      });
    });

    uploadZone.addEventListener('drop', (e) => {
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelect(e);
      }
    });
  }

  // Apply saved language preferences
  const savedLang = localStorage.getItem('krushisetu_lang') || 'en';
  if (typeof AGRI_I18N !== 'undefined' && AGRI_I18N.setLanguage) {
    AGRI_I18N.setLanguage(savedLang);
  }
});
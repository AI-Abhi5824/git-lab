window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

async function loadLanguage(lang) {
  try {
    const response = await fetch(`/static/lang_${lang}.json`);
    const translations = await response.json();
    document.querySelectorAll('[data-i18n]').forEach((element) => {
      const key = element.getAttribute('data-i18n');
      if (translations[key]) {
        element.textContent = translations[key];
      }
    });
    localStorage.setItem('selectedLanguage', lang);
  } catch (error) {
    console.error('Language load failed:', error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const languageSelect = document.getElementById('languageSelect');
  const selectedLang = localStorage.getItem('selectedLanguage') || 'en';
  if (languageSelect) {
    languageSelect.value = selectedLang;
    languageSelect.addEventListener('change', (e) => loadLanguage(e.target.value));
  }
  loadLanguage(selectedLang);

  const micBtn = document.getElementById('micBtn');
  const prnText = document.getElementById('prnText');
  const verifyForm = document.getElementById('verifyForm');
  const voiceStatus = document.getElementById('voiceStatus');

  if (micBtn && window.SpeechRecognition && prnText && verifyForm) {
    const recognition = new window.SpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.continuous = true;
    recognition.interimResults = true;

    let timeoutRef = null;

    micBtn.addEventListener('click', () => {
      voiceStatus.textContent = 'Listening...';
      recognition.start();
      if (timeoutRef) clearTimeout(timeoutRef);
      timeoutRef = setTimeout(() => {
        recognition.stop();
        voiceStatus.textContent = 'Timed out after 10 seconds.';
      }, 10000);
    });

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join(' ');
      const match = transcript.match(/\b\d{8,12}\b/);
      if (match) {
        prnText.value = `PRN ${match[0]}`;
        voiceStatus.textContent = `PRN detected: ${match[0]}`;
        recognition.stop();
        clearTimeout(timeoutRef);
        verifyForm.submit();
      } else {
        voiceStatus.textContent = `Heard: ${transcript}`;
      }
    };

    recognition.onerror = () => {
      voiceStatus.textContent = 'Microphone error. Please try again.';
      clearTimeout(timeoutRef);
    };
  } else if (micBtn) {
    micBtn.disabled = true;
    if (voiceStatus) voiceStatus.textContent = 'Speech recognition not supported in this browser.';
  }
});


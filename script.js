// --- Service Worker Registration ---
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js')
    .then(reg => console.log('✅ SW registered:', reg.scope))
    .catch(err => console.log('❌ SW failed:', err));
}

// --- PWA Install ---
let deferredPrompt;
const installBtn = document.getElementById('install-btn');

window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  deferredPrompt = e;
  installBtn.style.display = 'block';
});

installBtn.addEventListener('click', async () => {
  installBtn.style.display = 'none';
  if (deferredPrompt) {
    deferredPrompt.prompt();
    const choice = await deferredPrompt.userChoice;
    console.log('Install choice:', choice.outcome);
    deferredPrompt = null;
  }
});

window.addEventListener('appinstalled', () => console.log('App installed!'));

// --- Dhikr Logic ---
const setupScreen = document.getElementById('setup-screen');
const counterScreen = document.getElementById('counter-screen');
const darkModeToggle = document.getElementById('dark-mode-toggle');
const presetButtons = document.querySelectorAll('.preset-btn');
const customInputContainer = document.getElementById('custom-input-container');
const customBtn = document.getElementById('custom-btn');
const customTargetInput = document.getElementById('custom-target-input');
const customTextInput = document.getElementById('custom-text-input');
const useCustomBtn = document.getElementById('use-custom-btn');
const resetBtn = document.getElementById('reset-btn');
const manualResetBtn = document.getElementById('manual-reset-btn');
const tapArea = document.getElementById('tap-area');
const countDisplay = document.getElementById('count-display');
const targetDisplay = document.getElementById('target-display');
const currentDhikrText = document.getElementById('current-dhikr-text');
const progressCircle = document.querySelector('#progress-ring circle');

let currentCount = 0;
let targetCount = 100;
let dhikrText = 'Default';
const radius = progressCircle.r.baseVal.value;
const circumference = 2 * Math.PI * radius;
progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
progressCircle.style.strokeDashoffset = circumference;

function setProgress(count, target) {
  const offset = circumference - (count / target) * circumference;
  progressCircle.style.strokeDashoffset = offset;
}

function startCounter(target, text) {
  targetCount = target;
  dhikrText = text;
  currentCount = 0;
  updateDisplay();
  localStorage.setItem('dhikr_target', targetCount);
  localStorage.setItem('dhikr_text', dhikrText);
  localStorage.setItem('dhikr_count', currentCount);
  setupScreen.classList.remove('active');
  counterScreen.classList.add('active');
}

function updateDisplay() {
  countDisplay.textContent = currentCount;
  targetDisplay.textContent = `/ ${targetCount}`;
  currentDhikrText.textContent = dhikrText;
  setProgress(currentCount, targetCount);
}

function handleTap() {
  if (currentCount < targetCount) {
    currentCount++;
    updateDisplay();
    localStorage.setItem('dhikr_count', currentCount);
    if (navigator.vibrate) navigator.vibrate(50);
    if (currentCount === targetCount && navigator.vibrate) navigator.vibrate([100,50,100]);
  }
}

function goBackToSetup() {
  counterScreen.classList.remove('active');
  setupScreen.classList.add('active');
  localStorage.removeItem('dhikr_target');
  localStorage.removeItem('dhikr_text');
  localStorage.removeItem('dhikr_count');
}

function resetCurrentCount() {
  currentCount = 0;
  updateDisplay();
  localStorage.setItem('dhikr_count', currentCount);
}

// --- Event Listeners ---
presetButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    if (btn.classList.contains('custom')) {
      customInputContainer.style.display = 'flex';
    } else {
      const target = parseInt(btn.dataset.target, 10);
      const text = btn.dataset.text;
      startCounter(target, text);
    }
  });
});

useCustomBtn.addEventListener('click', () => {
  const target = parseInt(customTargetInput.value,10);
  const text = customTextInput.value || `Custom (${target})`;
  if(target>0) {
    startCounter(target,text);
    customTargetInput.value = '';
    customTextInput.value = '';
    customInputContainer.style.display = 'none';
  } else alert('Enter a valid number > 0');
});

tapArea.addEventListener('click', handleTap);
resetBtn.addEventListener('click', goBackToSetup);
manualResetBtn.addEventListener('click', resetCurrentCount);

darkModeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
  const isDark = document.body.classList.contains('dark-mode');
  localStorage.setItem('dhikr_dark_mode', isDark);
  darkModeToggle.textContent = isDark ? '☀️' : '🌙';
});

// Load saved data
const savedTarget = localStorage.getItem('dhikr_target');
if(savedTarget){
  targetCount = parseInt(savedTarget,10);
  dhikrText = localStorage.getItem('dhikr_text');
  currentCount = parseInt(localStorage.getItem('dhikr_count')||0,10);
  updateDisplay();
  setupScreen.classList.remove('active');
  counterScreen.classList.add('active');
}
if(localStorage.getItem('dhikr_dark_mode')==='true'){
  document.body.classList.add('dark-mode');
  darkModeToggle.textContent='☀️';
  }

const I18N_STORAGE_KEY = "teamap_lang";

const STRINGS = {
  zh: {
    pageTitle: "🍃 TEA MAP",
    tagline: "輕鬆找到附近的飲料店",
    searchRadius: "搜尋半徑",
    addressLabel: "手動輸入地址或地標",
    addressPlaceholder: "例如：台北車站、台中一中、高雄85大樓",
    search: "搜尋",
    useMyLocation: "使用我的位置",
    mapAria: "選擇搜尋位置的地圖",
    searchResultCount: "搜尋結果：共找到 {count} 間店",
    searchResultCountOne: "搜尋結果：共找到 1 間店",
    browseHint: "滾輪或拖曳下方捲軸左右選店，點卡片在下方查看詳情",
    initializing: "正在初始化…",
    emptyTitle: "附近沒有找到手搖飲店",
    emptyBody: "試試加大搜尋半徑，或換個地址再搜尋一次。",
    secureWarning:
      "瀏覽器定位需要 HTTPS 或 localhost。若無法自動定位，請改用手動輸入地址或在下方地圖點選位置。",
    setupTitle: "需要先設定 Google API 金鑰",
    setupBody:
      "複製 .env.example 為 .env，填入 GOOGLE_MAPS_API_KEY，並在 Google Cloud 啟用 Places API 與 Geocoding API。",
    openNow: "目前營業中",
    closed: "休息中",
    starsAria: "{rating} 顆星",
    markerTitle: "拖曳或點擊地圖以設定搜尋中心",
    loadingShop: "正在載入 {name} 的資訊…",
    directions: "規劃路線",
    call: "撥打電話",
    website: "網站",
    openInMaps: "在 Google 地圖開啟 →",
    locating: "正在取得你的位置…",
    geocoding: "正在查詢地址…",
    searching: "正在搜尋附近手搖飲店…",
    enterAddress: "請先輸入地址或地標。",
    defaultLocation: "台北車站附近（預設）",
    selectedLocation: "已選擇位置",
    apiKeyMissing: "請先設定 Google API 金鑰後重新整理頁面。",
    mapsLoadFailed: "無法載入 Google 地圖，請確認 API 金鑰設定。",
    requestFailed: "請求失敗，請稍後再試。",
    geoDenied: "定位權限被拒絕。請在瀏覽器設定中允許定位，或改用手動輸入地址。",
    geoUnavailable: "目前無法取得 GPS 位置。請改用手動輸入地址或在地圖上點選位置。",
    geoTimeout: "定位逾時。請確認已開啟定位服務，或改用手動輸入地址。",
    geoFailed: "無法取得位置。請改用手動輸入地址或在地圖上點選位置。",
    geoUnsupported: "你的瀏覽器不支援定位功能，請改用手動輸入地址。",
    geoInsecure:
      "自動定位需要 HTTPS 或 localhost。請改用手動輸入地址，或在地圖上點選位置。",
    langLabel: "語言",
  },
  en: {
    pageTitle: "🍃 TEA MAP",
    tagline: "Find drink shops near you",
    searchRadius: "Search radius",
    addressLabel: "Enter an address or landmark",
    addressPlaceholder: "e.g. Taipei Main Station, Taichung Park",
    search: "Search",
    useMyLocation: "Use my location",
    mapAria: "Map for choosing search location",
    searchResultCount: "Search results: {count} shops found",
    searchResultCountOne: "Search results: 1 shop found",
    browseHint: "Scroll the bar below to browse shops, then tap a card for details",
    initializing: "Starting up…",
    emptyTitle: "No drink shops found nearby",
    emptyBody: "Try a larger radius or search a different area.",
    secureWarning:
      "Location needs HTTPS or localhost. Enter an address manually or tap the map to set a search point.",
    setupTitle: "Google API key required",
    setupBody:
      "Copy .env.example to .env, set GOOGLE_MAPS_API_KEY, and enable Places API and Geocoding API in Google Cloud.",
    openNow: "Open now",
    closed: "Closed",
    starsAria: "{rating} stars",
    markerTitle: "Drag or tap the map to set search center",
    loadingShop: "Loading {name}…",
    directions: "Directions",
    call: "Call",
    website: "Website",
    openInMaps: "Open in Google Maps →",
    locating: "Getting your location…",
    geocoding: "Looking up address…",
    searching: "Searching for drink shops nearby…",
    enterAddress: "Please enter an address or landmark first.",
    defaultLocation: "Near Taipei Main Station (default)",
    selectedLocation: "Selected location",
    apiKeyMissing: "Set your Google API key, then refresh the page.",
    mapsLoadFailed: "Could not load Google Maps. Check your API key.",
    requestFailed: "Request failed. Please try again later.",
    geoDenied:
      "Location permission denied. Allow location in your browser or enter an address manually.",
    geoUnavailable:
      "GPS is unavailable. Enter an address manually or tap a location on the map.",
    geoTimeout: "Location timed out. Turn on location services or enter an address manually.",
    geoFailed: "Could not get your location. Enter an address or tap the map.",
    geoUnsupported: "Your browser does not support geolocation. Enter an address manually.",
    geoInsecure:
      "Auto-location needs HTTPS or localhost. Enter an address or tap the map instead.",
    langLabel: "Language",
  },
};

function detectLanguage() {
  const saved = localStorage.getItem(I18N_STORAGE_KEY);
  if (saved === "zh" || saved === "en") {
    return saved;
  }

  const browser = (navigator.language || "zh").toLowerCase();
  return browser.startsWith("en") ? "en" : "zh";
}

let currentLang = detectLanguage();

function t(key, vars = {}) {
  const text = STRINGS[currentLang][key] ?? STRINGS.zh[key] ?? key;
  return Object.entries(vars).reduce(
    (result, [name, value]) => result.replaceAll(`{${name}}`, String(value)),
    text
  );
}

function getApiLang() {
  return currentLang === "en" ? "en" : "zh-TW";
}

function getMapsLang() {
  return currentLang === "en" ? "en" : "zh-TW";
}

function setLanguage(lang) {
  if (lang !== "zh" && lang !== "en") {
    return;
  }
  localStorage.setItem(I18N_STORAGE_KEY, lang);
  window.location.reload();
}

function applyStaticTranslations() {
  document.documentElement.lang = currentLang === "en" ? "en" : "zh-Hant";
  document.title = t("pageTitle");

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });

  document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAria));
  });

  document.querySelectorAll(".lang-switch__btn").forEach((button) => {
    const active = button.dataset.lang === currentLang;
    button.classList.toggle("lang-switch__btn--active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
}

function bindLanguageSwitch() {
  document.querySelectorAll(".lang-switch__btn").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.lang !== currentLang) {
        setLanguage(button.dataset.lang);
      }
    });
  });
}

applyStaticTranslations();
bindLanguageSwitch();

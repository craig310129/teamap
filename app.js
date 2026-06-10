const DEFAULT_CENTER = { lat: 25.033964, lon: 121.564468 };
const SHOP_FOCUS_ZOOM = 17;

const geoBtn = document.getElementById("geoBtn");
const addressInput = document.getElementById("addressInput");
const addressSearchBtn = document.getElementById("addressSearchBtn");
const radiusSelect = document.getElementById("radiusSelect");
const statusPanel = document.getElementById("statusPanel");
const statusSpinner = document.getElementById("statusSpinner");
const statusText = document.getElementById("statusText");
const browseView = document.getElementById("browseView");
const shopStrip = document.getElementById("shopStrip");
const shopStripScrollbar = document.getElementById("shopStripScrollbar");
const shopStripTrack = document.getElementById("shopStripTrack");
const shopStripThumb = document.getElementById("shopStripThumb");
const shopDetail = document.getElementById("shopDetail");
const shopDetailContent = document.getElementById("shopDetailContent");
const emptyState = document.getElementById("emptyState");
const setupPanel = document.getElementById("setupPanel");
const secureWarning = document.getElementById("secureWarning");
const mapElement = document.getElementById("map");

let shopStripWheelReady = false;
let shopStripControlsReady = false;
let shopStripSyncing = false;
let shopStripDragState = null;

let googleMapsApiKey = "";
let map = null;
let centerMarker = null;
let radiusCircle = null;
let autocomplete = null;
let currentPosition = null;
let searchRadiusMeters = 5000;
let activeSearchId = 0;
let activeDetailId = 0;
let currentShops = [];
let selectedShopId = null;
let shopMarkers = new Map();

geoBtn.addEventListener("click", () => {
  void locateWithGeolocation();
});
addressSearchBtn.addEventListener("click", () => {
  void searchByAddressInput();
});
radiusSelect.addEventListener("change", () => {
  searchRadiusMeters = Number(radiusSelect.value);

  if (currentPosition) {
    setMapToSearchRadius(currentPosition.lat, currentPosition.lon);
    void searchNearbyShops(currentPosition.lat, currentPosition.lon);
    return;
  }

  if (map && centerMarker) {
    const position = centerMarker.getPosition();
    setMapToSearchRadius(position.lat(), position.lng());
  }
});
addressInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    void searchByAddressInput();
  }
});
function setLoading(loading) {
  geoBtn.disabled = loading;
  addressSearchBtn.disabled = loading;
  radiusSelect.disabled = loading;
}

function showLoadingStatus(message) {
  statusPanel.classList.add("is-active");
  statusPanel.classList.remove("status-panel--error", "status-panel--done");
  statusSpinner.hidden = false;
  statusText.textContent = message;
  browseView.hidden = true;
  emptyState.hidden = true;
}

function showErrorStatus(message) {
  statusPanel.classList.add("is-active", "status-panel--error");
  statusPanel.classList.remove("status-panel--done");
  statusSpinner.hidden = true;
  statusText.textContent = message;
  browseView.hidden = true;
  emptyState.hidden = true;
}

function hideStatusPanel() {
  statusPanel.classList.remove("is-active", "status-panel--error", "status-panel--done");
  statusSpinner.hidden = false;
}

function formatDistance(meters) {
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }

  return `${(meters / 1000).toFixed(1)} km`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderShopTitle(shop) {
  return `
    <div class="shop-card__title-wrap shop-card__title-wrap--no-logo">
      <h2 class="shop-card__title">${escapeHtml(shop.name)}</h2>
    </div>
  `;
}

function getShopStripScrollRange() {
  return Math.max(0, shopStrip.scrollWidth - shopStrip.clientWidth);
}

function syncShopStripScrollbar() {
  if (!shopStripTrack || !shopStripThumb || shopStripSyncing) {
    return;
  }

  const range = getShopStripScrollRange();
  if (!shopStripScrollbar) {
    return;
  }

  if (range <= 0) {
    shopStripScrollbar.hidden = true;
    return;
  }

  shopStripScrollbar.hidden = false;
  const trackWidth = shopStripTrack.clientWidth;
  const thumbWidth = Math.max(48, Math.round((shopStrip.clientWidth / shopStrip.scrollWidth) * trackWidth));
  const maxThumbOffset = trackWidth - thumbWidth;
  const thumbOffset = range > 0 ? (shopStrip.scrollLeft / range) * maxThumbOffset : 0;

  shopStripThumb.style.width = `${thumbWidth}px`;
  shopStripThumb.style.transform = `translateX(${thumbOffset}px)`;
}

function initShopStripWheel() {
  if (shopStripWheelReady) {
    return;
  }

  shopStrip.addEventListener(
    "wheel",
    (event) => {
      if (Math.abs(event.deltaY) <= Math.abs(event.deltaX)) {
        return;
      }

      event.preventDefault();
      shopStrip.scrollLeft += event.deltaY;
      syncShopStripScrollbar();
    },
    { passive: false }
  );

  shopStrip.addEventListener("scroll", () => {
    syncShopStripScrollbar();
  });

  shopStripWheelReady = true;
}

function scrollShopStripToThumbOffset(thumbOffset) {
  const range = getShopStripScrollRange();
  const trackWidth = shopStripTrack.clientWidth;
  const thumbWidth = shopStripThumb.offsetWidth;
  const maxThumbOffset = Math.max(1, trackWidth - thumbWidth);
  const ratio = thumbOffset / maxThumbOffset;

  shopStripSyncing = true;
  shopStrip.scrollLeft = ratio * range;
  shopStripSyncing = false;
  syncShopStripScrollbar();
}

function initShopStripControls() {
  if (shopStripControlsReady) {
    syncShopStripScrollbar();
    return;
  }

  shopStripTrack?.addEventListener("click", (event) => {
    if (event.target === shopStripThumb) {
      return;
    }

    const rect = shopStripTrack.getBoundingClientRect();
    const clickOffset = event.clientX - rect.left - shopStripThumb.offsetWidth / 2;
    scrollShopStripToThumbOffset(Math.max(0, clickOffset));
  });

  shopStripThumb?.addEventListener("pointerdown", (event) => {
    const range = getShopStripScrollRange();
    const trackWidth = shopStripTrack.clientWidth;
    const thumbWidth = shopStripThumb.offsetWidth;
    const maxThumbOffset = Math.max(0, trackWidth - thumbWidth);
    const thumbOffset = range > 0 ? (shopStrip.scrollLeft / range) * maxThumbOffset : 0;

    shopStripDragState = {
      startX: event.clientX,
      startThumbOffset: thumbOffset,
    };
    shopStripThumb.setPointerCapture(event.pointerId);
    shopStripThumb.classList.add("is-dragging");
  });

  shopStripThumb?.addEventListener("pointermove", (event) => {
    if (!shopStripDragState) {
      return;
    }

    const trackWidth = shopStripTrack.clientWidth;
    const thumbWidth = shopStripThumb.offsetWidth;
    const maxThumbOffset = Math.max(0, trackWidth - thumbWidth);
    const delta = event.clientX - shopStripDragState.startX;
    const nextOffset = Math.max(0, Math.min(maxThumbOffset, shopStripDragState.startThumbOffset + delta));
    scrollShopStripToThumbOffset(nextOffset);
  });

  const endDrag = (event) => {
    if (!shopStripDragState) {
      return;
    }

    shopStripThumb?.releasePointerCapture(event.pointerId);
    shopStripThumb?.classList.remove("is-dragging");
    shopStripDragState = null;
  };

  shopStripThumb?.addEventListener("pointerup", endDrag);
  shopStripThumb?.addEventListener("pointercancel", endDrag);

  window.addEventListener("resize", () => {
    syncShopStripScrollbar();
  });

  shopStripControlsReady = true;
  syncShopStripScrollbar();
}

function renderStarIcons(rating, { round = false } = {}) {
  const value = Math.max(0, Math.min(5, Number(rating) || 0));
  const filled = round ? Math.round(value) : Math.floor(value);
  return `${"★".repeat(filled)}${"☆".repeat(5 - filled)}`;
}

function renderStarRating(rating, options = {}) {
  if (rating == null || Number.isNaN(Number(rating))) {
    return "";
  }

  const { showValue = true, className = "star-rating" } = options;
  const valueText = showValue ? `<span class="star-rating__value">${rating}</span>` : "";

  return `<span class="${className}" aria-label="${escapeHtml(t("starsAria", { rating }))}">${renderStarIcons(rating)}${valueText}</span>`;
}

function renderOpenStatusBadge(isOpen) {
  if (isOpen == null) {
    return "";
  }

  if (isOpen) {
    return `<span class="status-badge status-badge--open">${escapeHtml(t("openNow"))}</span>`;
  }

  return `<span class="status-badge status-badge--closed">${escapeHtml(t("closed"))}</span>`;
}

function renderOpenStatusRow(shop) {
  if (shop.isOpen == null) {
    return "";
  }

  if (shop.isOpen) {
    return `<div class="shop-card__row">
      <span class="shop-card__icon">🕒</span>
      <span class="status-badge status-badge--open">${escapeHtml(t("openNow"))}</span>
    </div>`;
  }

  return `<div class="shop-card__row">
    <span class="shop-card__icon">🕒</span>
    <span class="status-badge status-badge--closed">${escapeHtml(t("closed"))}</span>
  </div>`;
}

async function apiGet(path) {
  const url = new URL(path, window.location.origin);
  url.searchParams.set("lang", getApiLang());
  const response = await fetch(url);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || t("requestFailed"));
  }

  return data;
}

function loadGoogleMaps(apiKey) {
  return new Promise((resolve, reject) => {
    if (window.google?.maps) {
      resolve(window.google.maps);
      return;
    }

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&libraries=places&language=${encodeURIComponent(getMapsLang())}&region=TW`;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve(window.google.maps);
    script.onerror = () => reject(new Error(t("mapsLoadFailed")));
    document.head.appendChild(script);
  });
}

function initMap(center) {
  map = new google.maps.Map(mapElement, {
    center: { lat: center.lat, lng: center.lon },
    zoom: 13,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
  });

  centerMarker = new google.maps.Marker({
    map,
    position: { lat: center.lat, lng: center.lon },
    draggable: true,
    title: t("markerTitle"),
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      scale: 9,
      fillColor: "#4a6741",
      fillOpacity: 1,
      strokeColor: "#ffffff",
      strokeWeight: 2,
    },
    zIndex: 1000,
  });

  map.addListener("click", (event) => {
    if (currentShops.length > 0) {
      return;
    }

    centerMarker.setPosition(event.latLng);
    void updateCenterFromMarker(false);
  });

  centerMarker.addListener("dragend", () => {
    void updateCenterFromMarker(false);
  });

  autocomplete = new google.maps.places.Autocomplete(addressInput, {
    fields: ["geometry", "formatted_address", "name"],
    componentRestrictions: { country: "tw" },
  });

  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();
    if (!place.geometry?.location) {
      return;
    }

    void setSearchCenter(
      place.geometry.location.lat(),
      place.geometry.location.lng(),
      place.formatted_address || place.name || t("selectedLocation"),
      false
    );
  });
}

function focusMapOnShop(shop) {
  if (!map) {
    return;
  }

  map.panTo({ lat: shop.lat, lng: shop.lon });

  if (map.getZoom() < SHOP_FOCUS_ZOOM) {
    map.setZoom(SHOP_FOCUS_ZOOM);
  }
}

function setMapToSearchRadius(lat, lon) {
  if (!map) {
    return;
  }

  if (radiusCircle) {
    radiusCircle.setMap(null);
  }

  radiusCircle = new google.maps.Circle({
    strokeColor: "#4a6741",
    strokeOpacity: 0.45,
    strokeWeight: 1.5,
    fillColor: "#4a6741",
    fillOpacity: 0.08,
    map,
    center: { lat, lng: lon },
    radius: searchRadiusMeters,
  });

  map.fitBounds(radiusCircle.getBounds(), 32);
}

function clearShopMarkers() {
  shopMarkers.forEach((marker) => marker.setMap(null));
  shopMarkers.clear();
  selectedShopId = null;
  shopDetail.hidden = true;
  shopDetailContent.innerHTML = "";
}

function createShopMarkerIcon(isSelected) {
  return {
    path: google.maps.SymbolPath.CIRCLE,
    scale: isSelected ? 11 : 7,
    fillColor: isSelected ? "#4a6741" : "#c45c26",
    fillOpacity: 1,
    strokeColor: "#ffffff",
    strokeWeight: 2,
  };
}

function updateMarkerVisibility() {
  shopMarkers.forEach((marker, placeId) => {
    const isSelected = placeId === selectedShopId;
    marker.setMap(currentShops.length > 0 ? map : null);
    marker.setIcon(createShopMarkerIcon(isSelected));
    marker.setZIndex(isSelected ? 500 : 100);
  });

  if (centerMarker) {
    centerMarker.setVisible(currentShops.length === 0);
  }
}

function renderShopStripCard(shop) {
  const isActive = shop.placeId === selectedShopId;

  return `
    <button
      class="shop-card shop-card--strip${isActive ? " shop-card--active" : ""}"
      type="button"
      data-place-id="${escapeHtml(shop.placeId)}"
      role="listitem"
    >
      <div class="shop-card__header">
        ${renderShopTitle(shop)}
        <span class="shop-card__distance">${formatDistance(shop.distance)}</span>
      </div>
      <div class="shop-card__meta">
        <div class="shop-card__row">
          <span class="shop-card__icon">📍</span>
          <span>${escapeHtml(shop.address)}</span>
        </div>
        ${
          shop.rating
            ? `<div class="shop-card__row">
                 <span class="shop-card__icon">⭐</span>
                 <span>${renderStarRating(shop.rating)}</span>
               </div>`
            : ""
        }
        ${renderOpenStatusRow(shop)}
      </div>
    </button>
  `;
}

function renderShopStrip() {
  shopStrip.innerHTML = currentShops.map((shop) => renderShopStripCard(shop)).join("");

  shopStrip.querySelectorAll(".shop-card--strip").forEach((card) => {
    card.addEventListener("click", () => {
      void selectShop(card.dataset.placeId, { scrollStrip: true });
    });

  });

  initShopStripWheel();
  initShopStripControls();
}

function scrollStripToSelected() {
  if (!selectedShopId) {
    return;
  }

  const card = shopStrip.querySelector(`[data-place-id="${selectedShopId}"]`);
  card?.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
  window.requestAnimationFrame(() => {
    syncShopStripScrollbar();
  });
}

function renderMapMarkers(shops) {
  clearShopMarkers();

  shops.forEach((shop) => {
    const marker = new google.maps.Marker({
      map: null,
      position: { lat: shop.lat, lng: shop.lon },
      title: shop.name,
      icon: createShopMarkerIcon(false),
    });

    marker.addListener("click", () => {
      void selectShop(shop.placeId, { scrollStrip: true });
    });

    shopMarkers.set(shop.placeId, marker);
  });
}

function showDetailLoading(shop) {
  shopDetail.hidden = false;
  shopDetailContent.innerHTML = `
    <div class="place-detail__loading">
      <div class="spinner" aria-hidden="true"></div>
      <p>${escapeHtml(t("loadingShop", { name: shop.name }))}</p>
    </div>
  `;
}

function renderPlaceDetail(shop, details) {
  const hoursText = details.hoursToday || (details.weekdayText?.[0] ?? "");

  shopDetailContent.innerHTML = `
    <div class="place-detail__body">
      <div class="place-detail__head">
        <div class="place-detail__title-wrap place-detail__title-wrap--no-logo">
          <div>
            <h2 class="place-detail__title">${escapeHtml(details.name)}</h2>
            <div class="place-detail__rating-row">
              ${
                details.rating
                  ? renderStarRating(details.rating, { className: "star-rating star-rating--large" })
                  : ""
              }
              <span class="place-detail__category">${escapeHtml(details.category)}</span>
            </div>
          </div>
        </div>
        <span class="shop-card__distance">${formatDistance(shop.distance)}</span>
      </div>

      <div class="place-detail__actions">
        <a class="place-action place-action--primary" href="${escapeHtml(details.googleMapsUrl)}" target="_blank" rel="noopener noreferrer">
          ${escapeHtml(t("directions"))}
        </a>
        ${
          details.phone
            ? `<a class="place-action" href="tel:${escapeHtml(details.phone)}">${escapeHtml(t("call"))}</a>`
            : ""
        }
        ${
          details.website
            ? `<a class="place-action" href="${escapeHtml(details.website)}" target="_blank" rel="noopener noreferrer">${escapeHtml(t("website"))}</a>`
            : ""
        }
      </div>

      <div class="place-detail__rows">
        <div class="place-detail__row">
          <span class="place-detail__icon">📍</span>
          <span>${escapeHtml(details.address)}</span>
        </div>
        ${
          hoursText || details.isOpen != null
            ? `<div class="place-detail__row">
                 <span class="place-detail__icon">🕒</span>
                 <span>
                   ${renderOpenStatusBadge(details.isOpen)}
                   ${hoursText ? `<span class="place-detail__hours">${escapeHtml(hoursText)}</span>` : ""}
                 </span>
               </div>`
            : ""
        }
        ${
          details.phone
            ? `<div class="place-detail__row">
                 <span class="place-detail__icon">📞</span>
                 <a href="tel:${escapeHtml(details.phone)}">${escapeHtml(details.phone)}</a>
               </div>`
            : ""
        }
        ${
          details.website
            ? `<div class="place-detail__row">
                 <span class="place-detail__icon">🌐</span>
                 <a href="${escapeHtml(details.website)}" target="_blank" rel="noopener noreferrer">${escapeHtml(details.website)}</a>
               </div>`
            : ""
        }
      </div>

      <a class="link-btn place-detail__maps-link" href="${escapeHtml(details.googleMapsUrl)}" target="_blank" rel="noopener noreferrer">
        ${escapeHtml(t("openInMaps"))}
      </a>
    </div>
  `;

}

async function selectShop(placeId, options = {}) {
  const { scrollStrip = false } = options;
  const shop = currentShops.find((item) => item.placeId === placeId);
  if (!shop) {
    return;
  }

  selectedShopId = placeId;
  renderShopStrip();
  updateMarkerVisibility();

  focusMapOnShop(shop);

  if (scrollStrip) {
    scrollStripToSelected();
  }

  const detailId = ++activeDetailId;
  showDetailLoading(shop);

  try {
    const details = await apiGet(`/api/place-details?placeId=${encodeURIComponent(placeId)}`);
    if (detailId !== activeDetailId) {
      return;
    }

    renderPlaceDetail(shop, details);
    shopDetail.hidden = false;
  } catch (error) {
    if (detailId !== activeDetailId) {
      return;
    }

    shopDetailContent.innerHTML = `
      <div class="place-detail__body">
        <div class="place-detail__head">
          <div class="place-detail__title-wrap place-detail__title-wrap--no-logo">
            <h2 class="place-detail__title">${escapeHtml(shop.name)}</h2>
          </div>
          <span class="shop-card__distance">${formatDistance(shop.distance)}</span>
        </div>
        <div class="place-detail__rows">
          <div class="place-detail__row">
            <span class="place-detail__icon">📍</span>
            <span>${escapeHtml(shop.address)}</span>
          </div>
          ${renderOpenStatusRow(shop)}
        </div>
        <p class="place-detail__error">${escapeHtml(error.message)}</p>
        <a class="link-btn" href="${escapeHtml(shop.googleMapsUrl)}" target="_blank" rel="noopener noreferrer">
          ${escapeHtml(t("openInMaps"))}
        </a>
      </div>
    `;
  }
}

async function updateCenterFromMarker(shouldSearch) {
  const position = centerMarker.getPosition();
  const lat = position.lat();
  const lon = position.lng();

  try {
    const data = await apiGet(`/api/reverse-geocode?lat=${lat}&lon=${lon}`);
    await setSearchCenter(lat, lon, data.label, shouldSearch);
  } catch {
    await setSearchCenter(lat, lon, `${lat.toFixed(5)}, ${lon.toFixed(5)}`, shouldSearch);
  }
}

async function setSearchCenter(lat, lon, label, shouldSearch = true) {
  currentPosition = { lat, lon, label };
  setMapToSearchRadius(lat, lon);

  if (map && centerMarker) {
    centerMarker.setPosition({ lat, lng: lon });
  }

  if (shouldSearch) {
    await searchNearbyShops(lat, lon);
  }
}

function getGeolocationErrorMessage(error) {
  switch (error.code) {
    case error.PERMISSION_DENIED:
      return t("geoDenied");
    case error.POSITION_UNAVAILABLE:
      return t("geoUnavailable");
    case error.TIMEOUT:
      return t("geoTimeout");
    default:
      return t("geoFailed");
  }
}

function getCurrentPosition() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error(t("geoUnsupported")));
      return;
    }

    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 20000,
      maximumAge: 0,
    });
  });
}

async function locateWithGeolocation() {
  if (!window.isSecureContext) {
    showErrorStatus(t("geoInsecure"));
    return;
  }

  setLoading(true);
  showLoadingStatus(t("locating"));

  try {
    const position = await getCurrentPosition();
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    let label = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
    try {
      const data = await apiGet(`/api/reverse-geocode?lat=${lat}&lon=${lon}`);
      label = data.label;
    } catch {
      // Keep coordinate fallback label.
    }

    await setSearchCenter(lat, lon, label, true);
  } catch (error) {
    const message = error.code != null ? getGeolocationErrorMessage(error) : error.message;
    showErrorStatus(message);
  } finally {
    setLoading(false);
  }
}

async function searchByAddressInput() {
  const address = addressInput.value.trim();
  if (!address) {
    showErrorStatus(t("enterAddress"));
    return;
  }

  setLoading(true);
  showLoadingStatus(t("geocoding"));

  try {
    const data = await apiGet(`/api/geocode?address=${encodeURIComponent(address)}`);
    await setSearchCenter(data.lat, data.lon, data.label, true);
  } catch (error) {
    showErrorStatus(error.message);
  } finally {
    setLoading(false);
  }
}

async function searchNearbyShops(lat, lon) {
  const searchId = ++activeSearchId;
  searchRadiusMeters = Number(radiusSelect.value);

  setLoading(true);
  showLoadingStatus(t("searching"));

  try {
    const data = await apiGet(
      `/api/nearby?lat=${lat}&lon=${lon}&radius=${searchRadiusMeters}`
    );

    if (searchId !== activeSearchId) {
      return;
    }

    if (data.count === 0) {
      clearShopMarkers();
      currentShops = [];
      mapElement.classList.remove("map--results");
      hideStatusPanel();
      browseView.hidden = true;
      emptyState.hidden = false;
      return;
    }

    renderResults(data.places, lat, lon);
  } catch (error) {
    if (searchId !== activeSearchId) {
      return;
    }

    showErrorStatus(error.message);
  } finally {
    if (searchId === activeSearchId) {
      setLoading(false);
    }
  }
}

function renderResults(shops, lat, lon) {
  currentShops = shops;
  renderMapMarkers(currentShops);
  renderShopStrip();
  setMapToSearchRadius(lat, lon);

  hideStatusPanel();
  browseView.hidden = false;
  emptyState.hidden = true;
  mapElement.classList.add("map--results");

  if (shops.length > 0) {
    void selectShop(shops[0].placeId);
  }
}

async function bootstrap() {
  if (!window.isSecureContext) {
    secureWarning.hidden = false;
  }

  showLoadingStatus(t("initializing"));

  try {
    const config = await apiGet("/api/config");

    if (!config.hasKey) {
      setupPanel.hidden = false;
      showErrorStatus(t("apiKeyMissing"));
      return;
    }

    googleMapsApiKey = config.apiKey;
    await loadGoogleMaps(googleMapsApiKey);
    initMap(DEFAULT_CENTER);
    currentPosition = {
      lat: DEFAULT_CENTER.lat,
      lon: DEFAULT_CENTER.lon,
      label: t("defaultLocation"),
    };
    setMapToSearchRadius(DEFAULT_CENTER.lat, DEFAULT_CENTER.lon);
    hideStatusPanel();
  } catch (error) {
    showErrorStatus(error.message);
  }
}

bootstrap();

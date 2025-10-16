{% load static %}
const CACHE_NAME = '{{ cache_name }}-v2'; // bumped version to invalidate old caches
const OFFLINE_URL = '{{ offline_url }}';
const PRECACHE_URLS = {{ precache_urls|safe }};

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => caches.delete(cacheName))
      );
    })
  );
  self.clients.claim();
});

function networkFetchWithTimeout(request, timeoutMs = 6000) {
  return Promise.race([
    fetch(request),
    new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), timeoutMs))
  ]);
}

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') {
    return;
  }

  const url = new URL(event.request.url);

  // Skip caching for API-like endpoints (JSON, geocoding, ping, stations data already special handled)
  const skipCache = (
    url.pathname.startsWith('/bird/geocode-found-location/') ||
    url.pathname.startsWith('/ping/') ||
    url.pathname.startsWith('/api/') ||
    url.pathname.startsWith('/stationen/daten/')
  );

  // Network-first Strategie für Stationsdaten um veraltete 3-Datensatz-Version zu vermeiden
  if (url.pathname.startsWith('/stationen/daten/')) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' })
        .then(resp => {
          if (resp && resp.ok) {
            return resp; // nicht im Cache speichern
          }
          // Fallback: vorhandene Cache-Version nur wenn wirklich keine Netzwerkantwort
          return caches.match(event.request).then(c => c || resp);
        })
        .catch(() => caches.match(event.request) || new Response('[]', { headers: { 'Content-Type': 'application/json' } }))
    );
    return;
  }

  if (event.request.mode === 'navigate') {
    event.respondWith(
      networkFetchWithTimeout(event.request, 5000)
        .then((response) => {
          if (response && response.status === 200) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          }
          return response;
        })
        .catch((err) => {
          // Try existing cached page
          return caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // Probe connectivity via ping endpoint before offline fallback
            return networkFetchWithTimeout('/ping/', 2500)
              .then(pingResp => {
                if (pingResp && pingResp.ok) {
                  // Connectivity ok -> show minimal error instead of offline (fallback to offline page though we could craft an error response)
                  return caches.match(OFFLINE_URL).then(r => r || new Response('<h1>Fehler</h1><p>Seite konnte nicht geladen werden.</p>', { headers: { 'Content-Type': 'text/html' } }));
                }
                return caches.match(OFFLINE_URL);
              })
              .catch(() => caches.match(OFFLINE_URL));
          });
        })
    );
    return;
  }

  if (skipCache) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(OFFLINE_URL))
    );
    return;
  }

  // Stale-while-revalidate für statische Assets
  event.respondWith(
    caches.open(CACHE_NAME).then(cache => {
      return cache.match(event.request).then(cached => {
        const fetchPromise = fetch(event.request)
          .then(response => {
            if (response && response.status === 200 && response.type === 'basic') {
              cache.put(event.request, response.clone());
            }
            return response;
          })
          .catch(() => cached || caches.match(OFFLINE_URL));
        return cached || fetchPromise;
      });
    })
  );
});

const CACHE_NAME = "venebistro-cache-1786353988";
const STATIC_ASSETS = [
  "./",
  "./index.html",
  "./index_redesign.html",
  "./trends.js",
  "./manifest.json",
  "./app_icon_192.png",
  "./app_icon_512.png",
  "./logo-99.png",
  "./logo-ifood.png",
  "./logo.jpg",
  // Arepas
  "./arepa_camarao.jpg",
  "./arepa_catira.jpg",
  "./arepa_pabellon.jpg",
  "./arepa_pelua.jpg",
  "./arepa_pernil.jpg",
  "./arepa_reinapepeada.jpg",
  "./arepa_vegetariana.jpg",
  // Cachapas
  "./cachapa_carne.jpg",
  "./cachapa_chicharrones.jpg",
  "./cachapa_pabellon.jpg",
  "./cachapa_pernil.jpg",
  "./cachapa_queijo.jpg",
  "./cachapa_veg.jpg",
  // Combos
  "./combo_caracas.jpg",
  "./combo_duo_venezuelano.jpg",
  "./combo_empanadas_papelon.jpg",
  "./combo_experiencia_1.jpg",
  "./combo_experiencia_2.jpg",
  "./combo_llanero.jpg",
  // Empanadas
  "./empanada_carne.jpg",
  "./empanada_cazon.jpg",
  "./empanada_pabellon.png",
  "./empanada_pelua.jpg",
  "./empanada_presunto_queijo.jpg",
  "./empanada_queijo.jpg",
  // Extras/Bebidas
  "./papelon_com_limao.jpg",
  "./pastelito_andino.jpg",
  "./tequenos.jpg",
  "./agua.jpg",
  "./coca_cola.jpg",
  "./coca_cola_original.jpg",
  "./coca_cola_zero.jpg",
  "./fanta.jpg",
  "./guarana.jpg",
  // Trends
  "./trend_canada_arepa.png",
  "./trend_peru_arepa.png",
  "./trend_mexico_arepas.png",
  "./trend_spain_pabellon.png",
  "./trend_usa_arepa.png"
];

// Installation: Cache static assets
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log("[Service Worker] Caching static assets");
      // Add assets, ignore individual failures if any image doesn't exist
      return Promise.allSettled(
        STATIC_ASSETS.map(asset => {
          return cache.add(asset).catch(err => {
            console.warn(`[Service Worker] Failed to cache: ${asset}`, err);
          });
        })
      );
    })
  );
  self.skipWaiting();
});

// Activation: Clear old caches
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log("[Service Worker] Removing old cache", key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetching: Network First for HTML navigation, Stale-While-Revalidate for static assets
self.addEventListener("fetch", event => {
  // Avoid caching Google Apps Script Webhook or POST requests
  if (event.request.method !== "GET") {
    return;
  }

  // 1. Network First strategy for HTML pages/navigation to keep stock/hours live
  if (event.request.mode === "navigate" || event.request.url.endsWith(".html") || event.request.url.endsWith("/")) {
    event.respondWith(
      fetch(event.request).then(networkResponse => {
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseToCache));
          return networkResponse;
        }
        return networkResponse;
      }).catch(() => {
        return caches.match(event.request).then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }
          return caches.match("./index.html") || caches.match("./index_redesign.html");
        });
      })
    );
    return;
  }

  // 2. Stale-While-Revalidate strategy for assets and images
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      if (cachedResponse) {
        const isCDN = event.request.url.includes("googleapis") || 
                      event.request.url.includes("gstatic") || 
                      event.request.url.includes("unpkg.com") || 
                      event.request.url.includes("tailwindcss.com");
                      
        if (!isCDN) {
          fetch(event.request).then(networkResponse => {
            if (networkResponse && networkResponse.status === 200) {
              caches.open(CACHE_NAME).then(cache => cache.put(event.request, networkResponse));
            }
          }).catch(() => {/* ignore background fetch errors */});
        }
        
        return cachedResponse;
      }

      // If not in cache, fetch and cache dynamically
      return fetch(event.request).then(networkResponse => {
        if (!networkResponse || networkResponse.status !== 200) {
          return networkResponse;
        }

        const isImage = event.request.destination === "image" ||
                        event.request.url.match(/\.(png|jpe?g|gif|svg|webp|ico)/i);

        const isCachable = event.request.type === "basic" || 
                           isImage ||
                           event.request.url.includes("tailwindcss.com") || 
                           event.request.url.includes("unpkg.com") || 
                           event.request.url.includes("googleapis") || 
                           event.request.url.includes("gstatic");

        if (isCachable) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
        }

        return networkResponse;
      }).catch(() => {
        // Fallback offline response
        return caches.match("./index.html") || caches.match("./index_redesign.html");
      });
    })
  );
});

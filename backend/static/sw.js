// Service Worker for BandSync PWA
const CACHE_NAME = 'bandsync-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico',
  // Add other critical assets
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .catch((error) => {
        console.error('Cache installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
      .catch(() => {
        // Fallback for offline scenarios
        if (event.request.destination === 'document') {
          return caches.match('/');
        }
      })
  );
});

// Background sync for offline RSVP
self.addEventListener('sync', (event) => {
  if (event.tag === 'rsvp-sync') {
    event.waitUntil(syncOfflineRSVPs());
  }
});

// Push notification handler
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New notification from BandSync',
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Details',
        icon: '/favicon.ico'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/favicon.ico'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('BandSync', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'explore') {
    // Open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Function to sync offline RSVPs
async function syncOfflineRSVPs() {
  try {
    const db = await openDB();
    const tx = db.transaction(['offline_rsvps'], 'readonly');
    const store = tx.objectStore('offline_rsvps');
    const rsvps = await store.getAll();

    for (const rsvp of rsvps) {
      try {
        const response = await fetch('/api/rsvp', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(rsvp.data)
        });

        if (response.ok) {
          // Remove from offline storage
          const deleteTx = db.transaction(['offline_rsvps'], 'readwrite');
          const deleteStore = deleteTx.objectStore('offline_rsvps');
          await deleteStore.delete(rsvp.id);
        }
      } catch (error) {
        console.error('Failed to sync RSVP:', error);
      }
    }
  } catch (error) {
    console.error('Failed to sync offline RSVPs:', error);
  }
}

// Helper function to open IndexedDB
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('BandSyncDB', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('offline_rsvps')) {
        db.createObjectStore('offline_rsvps', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

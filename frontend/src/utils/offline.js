// Offline utilities for PWA functionality
class OfflineManager {
  constructor() {
    this.dbName = 'BandSyncDB';
    this.dbVersion = 1;
    this.db = null;
    this.init();
  }

  async init() {
    try {
      this.db = await this.openDB();
    } catch (error) {
      console.error('Failed to initialize offline database:', error);
    }
  }

  openDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create offline RSVP store
        if (!db.objectStoreNames.contains('offline_rsvps')) {
          const rsvpStore = db.createObjectStore('offline_rsvps', { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          rsvpStore.createIndex('event_id', 'event_id', { unique: false });
          rsvpStore.createIndex('user_id', 'user_id', { unique: false });
          rsvpStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
        
        // Create offline events cache
        if (!db.objectStoreNames.contains('events_cache')) {
          const eventsStore = db.createObjectStore('events_cache', { 
            keyPath: 'id' 
          });
          eventsStore.createIndex('organization_id', 'organization_id', { unique: false });
          eventsStore.createIndex('date', 'date', { unique: false });
        }
      };
    });
  }

  async saveOfflineRSVP(eventId, userId, response, notes = '') {
    try {
      const tx = this.db.transaction(['offline_rsvps'], 'readwrite');
      const store = tx.objectStore('offline_rsvps');
      
      const rsvpData = {
        event_id: eventId,
        user_id: userId,
        response: response,
        notes: notes,
        timestamp: new Date().toISOString(),
        data: {
          event_id: eventId,
          response: response,
          notes: notes
        }
      };
      
      await store.add(rsvpData);
      console.log('RSVP saved offline:', rsvpData);
      
      // Request background sync
      if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
        const registration = await navigator.serviceWorker.ready;
        await registration.sync.register('rsvp-sync');
      }
      
      return true;
    } catch (error) {
      console.error('Failed to save offline RSVP:', error);
      return false;
    }
  }

  async getOfflineRSVPs() {
    try {
      const tx = this.db.transaction(['offline_rsvps'], 'readonly');
      const store = tx.objectStore('offline_rsvps');
      return await store.getAll();
    } catch (error) {
      console.error('Failed to get offline RSVPs:', error);
      return [];
    }
  }

  async cacheEvents(events) {
    try {
      const tx = this.db.transaction(['events_cache'], 'readwrite');
      const store = tx.objectStore('events_cache');
      
      for (const event of events) {
        await store.put({
          ...event,
          cached_at: new Date().toISOString()
        });
      }
      
      console.log('Events cached for offline use');
    } catch (error) {
      console.error('Failed to cache events:', error);
    }
  }

  async getCachedEvents() {
    try {
      const tx = this.db.transaction(['events_cache'], 'readonly');
      const store = tx.objectStore('events_cache');
      return await store.getAll();
    } catch (error) {
      console.error('Failed to get cached events:', error);
      return [];
    }
  }

  async clearOfflineData() {
    try {
      const tx = this.db.transaction(['offline_rsvps', 'events_cache'], 'readwrite');
      await tx.objectStore('offline_rsvps').clear();
      await tx.objectStore('events_cache').clear();
      console.log('Offline data cleared');
    } catch (error) {
      console.error('Failed to clear offline data:', error);
    }
  }

  isOnline() {
    return navigator.onLine;
  }
}

// Network status utilities
class NetworkManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.listeners = [];
    
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.notifyListeners('online');
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.notifyListeners('offline');
    });
  }

  addListener(callback) {
    this.listeners.push(callback);
  }

  removeListener(callback) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  notifyListeners(status) {
    this.listeners.forEach(callback => callback(status));
  }
}

// Push notification utilities
class NotificationManager {
  constructor() {
    this.permission = typeof Notification !== 'undefined' ? Notification.permission : 'denied';
  }

  async requestPermission() {
    if (typeof Notification !== 'undefined' && 'Notification' in window) {
      const permission = await Notification.requestPermission();
      this.permission = permission;
      return permission === 'granted';
    }
    return false;
  }

  async showNotification(title, options = {}) {
    if (this.permission === 'granted') {
      const defaultOptions = {
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        vibrate: [100, 50, 100],
        requireInteraction: false,
        ...options
      };

      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.ready;
        return registration.showNotification(title, defaultOptions);
      } else if (typeof Notification !== 'undefined') {
        return new Notification(title, defaultOptions);
      } else {
        console.warn('Notifications not supported on this device');
        return null;
      }
    }
  }

  async subscribeToNotifications() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: this.urlBase64ToUint8Array(
            // Replace with your VAPID public key
            'BEl62iUYgUivxIkv69yViEuiBIa40HI0aKQ1rCu9XLjFVGlLlOvn9VwVvJZJSzVSsZWdOLHVy1qmfhRvPlQyxvw'
          )
        });
        
        // Send subscription to server
        await fetch('/api/push-subscription', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(subscription)
        });
        
        return subscription;
      } catch (error) {
        console.error('Failed to subscribe to push notifications:', error);
        return null;
      }
    }
    return null;
  }

  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
}

// Installation prompt utilities
class InstallManager {
  constructor() {
    this.deferredPrompt = null;
    this.isInstalled = false;
    
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
    });
    
    window.addEventListener('appinstalled', () => {
      this.isInstalled = true;
      this.deferredPrompt = null;
    });
  }

  canInstall() {
    return this.deferredPrompt !== null;
  }

  async promptInstall() {
    if (this.deferredPrompt) {
      this.deferredPrompt.prompt();
      const { outcome } = await this.deferredPrompt.userChoice;
      this.deferredPrompt = null;
      return outcome === 'accepted';
    }
    return false;
  }
}

// Export singleton instances
export const offlineManager = new OfflineManager();
export const networkManager = new NetworkManager();
export const notificationManager = new NotificationManager();
export const installManager = new InstallManager();

self.addEventListener('push', function(event) {
  const data = event.data ? event.data.json() : {};
  self.registration.showNotification(data.title || 'Notificação', {
    body: data.body || '',
    icon: '/static/pwa/icons/icon-192x192.png',
    data: data.url || '/'
  });
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  if (event.notification.data) {
    event.waitUntil(
      clients.openWindow(event.notification.data)
    );
  }
}); 
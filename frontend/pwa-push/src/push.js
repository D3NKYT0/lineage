let VAPID_PUBLIC_KEY = null;

export async function getVapidPublicKey() {
  if (VAPID_PUBLIC_KEY) return VAPID_PUBLIC_KEY;
  const res = await fetch("/api/v1/vapid-public-key/");
  const data = await res.json();
  VAPID_PUBLIC_KEY = data.vapid_public_key;
  return VAPID_PUBLIC_KEY;
}

export async function subscribeUserToPush(token) {
  if (!('serviceWorker' in navigator)) {
    console.log("Service worker não suportado");
    return false;
  }
  const registration = await navigator.serviceWorker.ready;
  let permission = Notification.permission;
  if (permission !== "granted") {
    permission = await Notification.requestPermission();
    console.log("Permissão de notificação:", permission);
    if (permission !== "granted") return false;
  }
  try {
    const vapidKey = await getVapidPublicKey();
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidKey)
    });
    console.log("Subscription criada:", subscription);
    const res = await fetch("/api/v1/push-subscription/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(subscription)
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      return { success: false, error: data.error || 'Erro desconhecido ao cadastrar push' };
    }
    return { success: true };
  } catch (e) {
    console.error("Erro ao subscrever push:", e);
    return { success: false, error: e.message || 'Erro desconhecido' };
  }
}

export async function unsubscribeUserFromPush(token, subscription) {
  if (!subscription) return false;
  try {
    await fetch("/api/v1/push-subscription/", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ endpoint: subscription.endpoint })
    });
    return true;
  } catch (e) {
    console.error("Erro ao remover push subscription:", e);
    return false;
  }
}

function urlBase64ToUint8Array(base64String) {
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
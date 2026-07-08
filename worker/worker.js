// Daily Pulse push worker: stores PWA push subscriptions and fans out
// notifications to them. Deployed on Cloudflare Workers (free tier).
//
// POST /subscribe          — body: PushSubscription JSON (from the app)
// POST /send               — body: {title, body, url}; needs Bearer SEND_SECRET
import { buildPushPayload } from "@block65/webcrypto-web-push";

async function endpointKey(endpoint) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(endpoint));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const cors = {
      "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    };
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });

    if (url.pathname === "/subscribe" && req.method === "POST") {
      const sub = await req.json().catch(() => null);
      if (!sub?.endpoint || !sub?.keys?.p256dh) {
        return new Response("bad subscription", { status: 400, headers: cors });
      }
      await env.SUBS.put(await endpointKey(sub.endpoint), JSON.stringify(sub));
      return Response.json({ ok: true }, { headers: cors });
    }

    if (url.pathname === "/send" && req.method === "POST") {
      if (req.headers.get("Authorization") !== `Bearer ${env.SEND_SECRET}`) {
        return new Response("unauthorized", { status: 401, headers: cors });
      }
      const msg = await req.json().catch(() => ({}));
      const payload = {
        data: JSON.stringify({
          title: msg.title || "Daily Pulse",
          body: msg.body || "Your brief is ready.",
          url: msg.url || "./",
        }),
        options: { ttl: 12 * 3600, urgency: "normal" },
      };
      const vapid = {
        subject: "mailto:karthikmr281@gmail.com",
        publicKey: env.VAPID_PUBLIC,
        privateKey: env.VAPID_PRIVATE,
      };

      let sent = 0, dropped = 0, failed = 0;
      const list = await env.SUBS.list();
      for (const { name } of list.keys) {
        const sub = JSON.parse(await env.SUBS.get(name));
        try {
          const init = await buildPushPayload(payload, sub, vapid);
          const res = await fetch(sub.endpoint, init);
          if (res.status === 404 || res.status === 410) {
            await env.SUBS.delete(name); // subscription expired/revoked
            dropped++;
          } else if (res.ok || res.status === 201) {
            sent++;
          } else {
            failed++;
          }
        } catch {
          failed++;
        }
      }
      return Response.json({ sent, dropped, failed }, { headers: cors });
    }

    return new Response("not found", { status: 404, headers: cors });
  },
};

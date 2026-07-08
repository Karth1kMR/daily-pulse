# Daily Pulse push worker — deploy steps

One-time setup (needs a free Cloudflare account; ~10 minutes):

```bash
cd worker
export PATH="$HOME/.local/node/bin:$PATH"
npm install
npx wrangler login                       # opens browser; log in to Cloudflare
npx wrangler kv namespace create SUBS    # prints an id
# → paste the id into wrangler.toml (kv_namespaces.id)
# → paste VAPID_PUBLIC from ../.vapid_keys into wrangler.toml [vars]
npx wrangler secret put VAPID_PRIVATE    # paste VAPID_PRIVATE from ../.vapid_keys
openssl rand -hex 24                     # generate a send secret
npx wrangler secret put SEND_SECRET      # paste it
npx wrangler deploy                      # prints https://daily-pulse-push.<acct>.workers.dev
```

Then wire the app:
1. In `app/config.js` set `pushWorkerUrl` to the workers.dev URL and
   `vapidPublicKey` to VAPID_PUBLIC. Commit and push.
2. Tighten CORS: set `ALLOWED_ORIGIN` in wrangler.toml to the GitHub Pages
   origin and redeploy.
3. On the iPhone: open the Pages URL in Safari → Share → Add to Home Screen →
   open the installed app → tap "Enable daily notifications".
4. Give the cloud routine the SEND_SECRET so it can call
   `POST <worker>/send` with `{"title", "body", "url"}` after each refresh.

Test a push once subscribed:

```bash
curl -X POST "https://daily-pulse-push.<acct>.workers.dev/send" \
  -H "Authorization: Bearer $SEND_SECRET" -H "Content-Type: application/json" \
  -d '{"title":"Daily Pulse test","body":"PWA push works!"}'
```

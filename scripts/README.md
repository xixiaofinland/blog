# WeChat book-thread drafts

Turn a book thread in `src/` into a WeChat Official Account (公众号) **draft**.
It never publishes: you approve every draft by hand in the MP backend. Same
draft-only pattern as viikkoja.

## Flow

1. Write and commit a book thread `src/<book>.md`.
2. (Optional) add a metadata comment at the very top for the cover / a short
   title override:

   ```markdown
   <!-- wechat: cover: https://images.example.com/book.jpg; title: Short Title -->

   # Full H1 Title Of The Post
   ```

   - `cover` optional. Present → that image is downloaded and used as the WeChat
     cover. Absent → falls back to `src/img/wechat/book-cover.png`.
   - `title` optional. Use it when the H1 is longer than WeChat's 64-char limit.

3. Trigger the draft (locally or in CI):

   ```bash
   gh workflow run wechat-books.yml -f thread=src/<book>.md
   ```

   or run it directly:

   ```bash
   WECHAT_TOKEN=... python3 scripts/publish_book_wechat.py --thread src/<book>.md
   ```

4. Open <https://mp.weixin.qq.com>, review the draft, click Publish.

Each run creates a **new** draft. Delete superseded ones by hand.

## Scripts

- `wechat_client.py` — stdlib-only MP API client: token, cover upload, draft
  create. No publish call.
- `md_to_wechat.py` — Markdown → WeChat-safe inline-styled HTML + flag parser.
- `publish_book_wechat.py` — entrypoint tying them together.

## Token setup (one-time, on the static VM)

WeChat's token endpoint only answers IP-whitelisted callers, so GitHub runners
can't fetch it. A static VM pre-fetches the token and pushes it to this repo's
`WECHAT_TOKEN` secret. The books channel uses a **different appid** than
viikkoja, so it needs its own refresh script and cron entry.

1. Whitelist the VM's static IP for the **books** appid at
   mp.weixin.qq.com → Settings → Security → IP Whitelist.
2. On the VM, create `/home/ubuntu/refresh-wechat-token-books.sh` (mirrors
   viikkoja's, with the books appid/secret and this repo):

   ```bash
   #!/bin/bash
   set -euo pipefail
   TOKEN=$(curl -sf -X POST "https://api.weixin.qq.com/cgi-bin/stable_token" \
     -H "Content-Type: application/json" \
     -d "{\"grant_type\":\"client_credential\",\"appid\":\"$BOOKS_APPID\",\"secret\":\"$BOOKS_APPSECRET\",\"force_refresh\":true}" \
     | jq -r .access_token)
   [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ] || { echo "token fetch failed" >&2; exit 1; }
   gh secret set WECHAT_TOKEN --repo xixiaofinland/blog --body "$TOKEN"
   ```

3. Add to the VM crontab (stable_token has ~2h TTL; refresh well inside that):

   ```
   17 */1 * * * BOOKS_APPID=wx58a2a09b2cb42870 BOOKS_APPSECRET=... /home/ubuntu/refresh-wechat-token-books.sh >> /home/ubuntu/wechat-books-token.log 2>&1
   ```

`gh` on the VM is already authed as `xixiaofinland`, which owns this repo, so no
extra auth is needed.

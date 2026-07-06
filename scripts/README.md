# WeChat book-thread drafts

Turn a book thread in `src/` into a WeChat Official Account (公众号) **draft**.
It never publishes: you approve every draft by hand in the MP backend. Same
draft-only pattern as viikkoja.

## Flow

1. Write and commit a book thread `src/<book>.md`.
2. Show the book cover in the thread with a normal Markdown image near the top.
   The **same image becomes the WeChat draft cover**, so you set it once and it
   works in both places:

   ```markdown
   # Trillion Dollar Coach: The Ruler I Didn't Know I Was Missing

   _Eric Schmidt, Jonathan Rosenberg, Alan Eagle_

   ![Trillion Dollar Coach book cover](img/trillion-dollar-coach/cover.jpg)

   First paragraph...
   ```

   The image can be a committed local file (`img/<slug>/cover.jpg`, renders in
   the blog and is uploaded to WeChat) or a remote URL. It doubles as the WeChat
   draft cover (the card thumbnail).

   **Inline images carry through to the draft.** Every standalone Markdown image
   in the thread (`![alt](img/<slug>/pic.jpg)`, one per line) is uploaded and
   embedded in the WeChat body at the same spot it sits in the blog. The first
   image renders in-body at its markdown position, so it is not additionally
   pinned to the top. If the thread has no inline image at all (cover came from
   a `cover:` override or an Open Library match), that cover is prepended once to
   the body as before. Local images must be committed so CI can read them; remote
   image URLs are downloaded and re-uploaded to WeChat.

   Grab a cover fast from Open Library:

   ```bash
   curl -sL "https://covers.openlibrary.org/b/id/<cover_id>-L.jpg" \
     -o src/img/<slug>/cover.jpg
   ```

   **Cover resolution order** (first match wins):
   1. `<!-- cover: https://... -->` metadata comment (explicit override)
   2. first inline Markdown image in the thread (the recommended path above)
   3. Open Library lookup by book title: `<!-- book: Exact Title -->`, or if that
      comment is absent, the H1 text before the first colon
   4. default `src/img/wechat/book-cover.png` (the channel icon)

   Optional metadata comments (invisible in the rendered blog):
   - `<!-- cover: URL -->` force a specific cover image.
   - `<!-- book: Exact Title -->` book title for the Open Library fallback, when
     no inline image is present and the H1 is not a clean title.
   - `<!-- title: Shorter Title -->` WeChat article title, when the H1 exceeds
     WeChat's 64-char limit.

   For Chinese books (often missing from Open Library) just commit a local cover
   image, or paste a 豆瓣 image URL in `<!-- cover: ... -->`.

   **Adding images while drafting.** Every standalone Markdown image line
   (`![alt](img/<slug>/pic.jpg)`, one per line) flows into the WeChat body at the
   same spot, so the convenient loop is:
   - While writing, mark each spot an image belongs with a comment marker.
     mdBook ignores it, so the blog still builds and it acts as a to-do:

     ```markdown
     Some paragraph about the ruler.

     <!-- IMG: the ruler diagram, before the "why it matters" section -->

     Why it matters...
     ```

   - Get the file onto disk (save/screenshot into `src/img/<slug>/`, drop it in
     `~/Downloads`, or, for a web image, just use its URL), then say where it
     goes ("the screenshot in Downloads goes at the first IMG marker").
   - The `<!-- IMG: ... -->` marker is replaced with a real
     `![alt](img/<slug>/name.ext)` link. Commit the image so CI can read it;
     remote URLs are downloaded and re-uploaded to WeChat.

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
   gh secret set WECHAT_TOKEN --repo <owner>/blog --body "$TOKEN"
   ```

3. Add to the VM crontab (stable_token has ~2h TTL; refresh well inside that):

   ```
   17 */1 * * * BOOKS_APPID=<your-appid> BOOKS_APPSECRET=<your-appsecret> /home/ubuntu/refresh-wechat-token-books.sh >> /home/ubuntu/wechat-books-token.log 2>&1
   ```

`gh` on the VM is already authed as the repo owner, so no
extra auth is needed.

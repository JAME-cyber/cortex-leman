# X/Twitter Thread Recovery — Full Text Extraction

> Technique validated Jul 2026 for recovering full prompt text from X/Twitter threads
> where the author posts multi-part content ("prompts below ⬇️") across multiple replies.

## When to use
- A tweet references "prompts/storyboard below" in a thread
- fxtwitter API returns truncated text with "Voir plus" / "Show more"
- You need the full untruncated text of long tweet replies

## Method

### Step 1: fxtwitter API (metadata first)
```bash
curl -sL --max-time 15 "https://api.fxtwitter.com/i/status/{TWEET_ID}" -o /tmp/tweet.json
```
Extracts: author, engagement, media URLs, truncated reply text.
**Limitation:** reply text is truncated to ~280 chars with no "Show more" expansion.

### Step 2: Browser navigation to the tweet
```
browser_navigate → https://x.com/{author}/status/{TWEET_ID}
```

### Step 3: Expand all "Voir plus" / "Show more" buttons via JS console
```javascript
// browser_console with expression:
(() => {
    const buttons = document.querySelectorAll('button');
    let clicked = 0;
    buttons.forEach(btn => {
        const text = btn.innerText.trim();
        if (text === 'Voir plus' || text === 'Show more') {
            btn.click();
            clicked++;
        }
    });
    return `Clicked ${clicked} expand buttons`;
})()
```
**Important:** Click ALL buttons in one pass — the page re-renders after each click.

### Step 4: Extract full article text via JS console
```javascript
// browser_console with expression:
(() => {
    const articles = document.querySelectorAll('article');
    const out = [];
    articles.forEach((article, i) => {
        const allText = article.innerText;
        if (allText && allText.length > 50 && allText.includes('{author_handle}')) {
            out.push({index: i, full_text: allText});
        }
    });
    return JSON.stringify(out);
})()
```
**Pitfall:** Use an IIFE `(() => { ... })()` wrapping — bare `const` declarations collide across console evaluations and throw `SyntaxError: Identifier has already been declared`.

### Step 5 (optional): Extract video frames for pixel analysis
```bash
# Download video from fxtwitter media URL
curl -sL -o video.mp4 "https://video.twimg.com/amplify_video/{id}/vid/avc1/1080x1440/{hash}.mp4?tag=29"

# Extract frames at 1-per-4-seconds for sequence analysis
ffmpeg -y -i video.mp4 -vf "fps=1/4" -q:v 2 frame_%02d.jpg

# Pixel analysis (when vision tool is down)
python3 -c "
from PIL import Image
import collections
img = Image.open('frame_01.jpg').convert('RGB')
small = img.resize((50, 67))
colors = collections.Counter(small.getdata())
for color, count in colors.most_common(5):
    r,g,b = color[:3]
    pct = count / (50*67) * 100
    print(f'RGB({r},{g},{b}) {pct:.0f}%')
"
```

## Limitations
- **X login wall:** some threads require login to see all replies. The method above works for public threads visible without login.
- **"A lu X réponses de plus" / "X more replies"**: may need additional click to load hidden replies.
- **Dynamic DOM:** X heavily uses dynamic rendering — `browser_snapshot` alone may not capture expanded text. The JS console approach is more reliable.

## X Articles (Long-form)

X Articles (formerly Twitter Articles) are long-form posts with rich text formatting. They appear as a quote-tweeted link. The full article content is embedded in the tweet JSON.

### Extraction via fxtwitter API
```bash
curl -sL --max-time 15 "https://api.fxtwitter.com/i/status/{TWEET_ID}" -o /tmp/tweet.json
python3 -c "
import json
with open('/tmp/tweet.json') as f:
    data = json.load(f)
# The article is nested in quote.article.content.blocks[]
quote = data['tweet'].get('quote', {})
article = quote.get('article', {})
blocks = article.get('content', {}).get('blocks', [])
for block in blocks:
    text = block.get('text', '')
    btype = block.get('type', 'unstyled')
    if btype == 'header-two':
        print(f'\n## {text}\n')
    elif btype == 'blockquote':
        print(f'> {text}')
    elif text.strip():
        print(text)
"
```

### Key fields
- `quote.article.title` — article title
- `quote.article.preview_text` — summary
- `quote.article.content.blocks[]` — array of text blocks with types: `unstyled`, `header-two`, `blockquote`, `atomic` (images)
- `quote.article.content.entityMap` — media references
- `quote.views` — view count (can be 1M+ for viral articles)

### When to use
- A tweet links to an "Article" (not a thread) — the content is self-contained in the JSON, no browser needed.
- Pattern: tweet text says "read the full breakdown in the article below 👇" + quote-tweets their own article tweet.

### Alternative: Article as card link (not quote-tweeted)
When the article is NOT quote-tweeted but linked as a card (fxtwitter shows `twitter_card: player`, no `quote` field), the `quote.article.content.blocks[]` path doesn't work. Use browser DOM extraction instead:

```javascript
// Step 1: Navigate to the tweet, find the article link in DOM
(() => {
    const links = document.querySelectorAll('a');
    const articleLink = Array.from(links).find(a => a.href && a.href.includes('/i/article/'));
    if (articleLink) {
        articleLink.click();
        return 'Article ID: ' + articleLink.href;
    }
    return 'No article link found';
})()

// Step 2: After navigation, extract body text in 8000-char chunks
document.body.innerText.substring(0, 8000)
document.body.innerText.substring(8000, 16000)
// Continue until content ends (you'll see X footer/nav text)
```

**Validated:** Jul 2026 on @apob_ai anime playbook article (tweet 2075533727560831068 → article 2075484415753617710). The article ID differs from the tweet ID.

#!/usr/bin/env python3
"""
Local Firecrawl replacement — no external deps beyond stdlib.
Does 3 things Firecrawl does for Level 6 (Finding the Data):
  1. Batch scrape competitor sites → clean text
  2. Extract design tokens (colors, fonts, spacing) from CSS
  3. Download logos and key images

Usage:
  python3 competitor_scraper.py scrape <urls_file> <output_dir>
  python3 competitor_scraper.py design <url>
  python3 competitor_scraper.py batch-design <urls_file> <output_json>
  python3 competitor_scraper.py logos <url> <output_dir>

Validated on: tailwindcss.com, vercel.com, linear.app
"""

import sys
import os
import re
import json
import hashlib
import urllib.request
import urllib.parse
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    SKIP_TAGS = {'script', 'style', 'noscript', 'svg', 'path', 'meta', 'link', 'head'}

    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip_depth = 0
        self._current_tag = None
        self._headings = []
        self._links = []
        self._images = []
        self._cta_candidates = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return
        self._current_tag = tag
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._headings.append({'tag': tag, 'text': ''})
        if tag == 'a' and 'href' in attrs_dict:
            self._links.append(attrs_dict['href'])
        if tag == 'img':
            src = attrs_dict.get('src', '') or attrs_dict.get('data-src', '')
            alt = attrs_dict.get('alt', '')
            if src:
                self._images.append({'src': src, 'alt': alt})
        cls = attrs_dict.get('class', '').lower()
        role = attrs_dict.get('role', '').lower()
        text_content = attrs_dict.get('aria-label', '').lower()
        if any(kw in cls for kw in ['cta', 'button', 'btn', 'call-to-action', 'submit']):
            self._cta_candidates.append({'type': 'class', 'value': attrs_dict.get('class', '')})
        if role == 'button':
            self._cta_candidates.append({'type': 'role', 'value': text_content or cls})

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        self._current_tag = None

    def handle_data(self, data):
        if self._skip_depth > 0:
            return
        text = data.strip()
        if text:
            self.parts.append(text)
            if self._headings and self._current_tag in ('h1','h2','h3','h4','h5','h6'):
                self._headings[-1]['text'] += ' ' + text

    def get_text(self):
        return '\n'.join(self.parts)

    def get_structure(self):
        return {
            'headings': [h for h in self._headings if h['text'].strip()],
            'links_count': len(self._links),
            'links_sample': self._links[:20],
            'images': self._images[:30],
            'cta_candidates': self._cta_candidates[:10],
        }


def fetch_url(url, timeout=15):
    if not url.startswith('http'):
        url = 'https://' + url
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get('Content-Type', '')
            charset = content_type.split('charset=')[-1].split(';')[0].strip() if 'charset=' in content_type else 'utf-8'
            return resp.read().decode(charset, errors='replace')
    except Exception:
        return None


def scrape_page(url):
    html = fetch_url(url)
    if not html:
        return {'url': url, 'error': 'Failed to fetch'}
    parser = TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass
    return {
        'url': url,
        'text': parser.get_text(),
        'char_count': len(parser.get_text()),
        'structure': parser.get_structure(),
    }


def extract_design_tokens(url):
    html = fetch_url(url)
    if not html:
        return {'url': url, 'error': 'Failed to fetch'}

    inline_css = []
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    inline_css.extend(style_blocks)
    inline_attrs = re.findall(r'style="([^"]*)"', html)
    inline_css.extend(inline_attrs)

    css_links = re.findall(r'<link[^>]+href="([^"]*\.css[^"]*)"', html, re.IGNORECASE)
    for css_url in css_links[:10]:
        abs_url = urllib.parse.urljoin(url, css_url)
        css_content = fetch_url(abs_url, timeout=10)
        if css_content:
            inline_css.append(css_content)

    all_css = '\n'.join(inline_css)

    hex_colors = re.findall(r'#([0-9a-fA-F]{6})\b', all_css)
    rgb_colors = re.findall(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', all_css)

    color_freq = {}
    for c in hex_colors:
        c_upper = '#' + c.upper()
        color_freq[c_upper] = color_freq.get(c_upper, 0) + 1
    for r, g, b in rgb_colors:
        hex_val = f'#{int(r):02X}{int(g):02X}{int(b):02X}'
        color_freq[hex_val] = color_freq.get(hex_val, 0) + 1
    top_colors = sorted(color_freq.items(), key=lambda x: -x[1])[:15]

    font_families = re.findall(r'font-family:\s*([^;}{]+)', all_css)
    font_freq = {}
    for ff in font_families:
        primary = ff.split(',')[0].strip().strip("'\"").lower()
        if primary:
            font_freq[primary] = font_freq.get(primary, 0) + 1
    top_fonts = sorted(font_freq.items(), key=lambda x: -x[1])[:8]

    font_sizes = re.findall(r'font-size:\s*(\d+(?:\.\d+)?)(px|rem|em)', all_css)
    spacing_values = re.findall(r'(?:margin|padding|gap):\s*(\d+(?:\.\d+)?)(px|rem|em)', all_css)
    border_radius = re.findall(r'border-radius:\s*(\d+(?:\.\d+)?)(px|rem|em|%)', all_css)

    parser = TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass
    structure = parser.get_structure()

    has_hero = bool(re.search(r'class="[^"]*hero[^"]*"', html, re.IGNORECASE))
    has_sticky_nav = bool(re.search(r'class="[^"]*(?:sticky|fixed-nav|navbar-fixed)[^"]*"', html, re.IGNORECASE))
    has_animation = 'gsap' in html.lower() or 'framer-motion' in html.lower() or 'aos' in html.lower()
    has_dark_mode = 'dark:' in all_css or 'prefers-color-scheme: dark' in all_css

    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    description_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html, re.IGNORECASE)

    return {
        'url': url,
        'title': title_match.group(1).strip() if title_match else None,
        'description': description_match.group(1) if description_match else None,
        'colors': {'top': top_colors, 'total_unique': len(color_freq)},
        'fonts': {'top': top_fonts, 'total_unique': len(font_freq)},
        'typography': {
            'font_sizes_px': sorted(set(float(s) for s, u in font_sizes if u == 'px'))[:10],
            'units_used': list(set(u for _, u in font_sizes + spacing_values)),
        },
        'spacing': {'values_px': sorted(set(float(s) for s, u in spacing_values if u == 'px'))[:10]},
        'border_radius': {'values': sorted(set(float(s) for s, u, in border_radius))[:8]},
        'layout': {
            'has_hero': has_hero, 'has_sticky_nav': has_sticky_nav,
            'has_animation_lib': has_animation, 'has_dark_mode': has_dark_mode,
        },
        'structure': structure,
        'css_chars_analyzed': len(all_css),
    }


def cmd_scrape(urls_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with open(urls_file) as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    results = []
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Scraping {url}...")
        data = scrape_page(url)
        results.append(data)
        slug = hashlib.md5(url.encode()).hexdigest()[:8]
        with open(os.path.join(output_dir, f'{slug}.json'), 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    summary_path = os.path.join(output_dir, '_summary.json')
    summary = [{'url': r['url'], 'chars': r.get('char_count', 0),
                'headings': len(r.get('structure', {}).get('headings', [])),
                'images': len(r.get('structure', {}).get('images', [])),
                'ctas': len(r.get('structure', {}).get('cta_candidates', [])),
                'error': r.get('error')} for r in results]
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nDone. {len(results)} pages scraped -> {output_dir}/")


def cmd_design(url):
    data = extract_design_tokens(url)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_batch_design(urls_file, output_json):
    with open(urls_file) as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    results = []
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Extracting design from {url}...")
        results.append(extract_design_tokens(url))
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nDone. {len(results)} sites analyzed -> {output_json}\n")
    print("="*80)
    print("DESIGN COMPARISON TABLE")
    print("="*80)
    for r in results:
        if 'error' in r:
            print(f"\n[X] {r['url']}: {r['error']}")
            continue
        colors = [c for c, _ in r['colors']['top'][:5]]
        fonts = [f for f, _ in r['fonts']['top'][:3]]
        print(f"\n  {r['url']}")
        print(f"   Title: {(r.get('title') or 'N/A')[:60]}")
        print(f"   Colors: {', '.join(colors)}")
        print(f"   Fonts: {', '.join(fonts)}")
        print(f"   Hero: {'Y' if r['layout']['has_hero'] else 'N'} | "
              f"Sticky Nav: {'Y' if r['layout']['has_sticky_nav'] else 'N'} | "
              f"Animation: {'Y' if r['layout']['has_animation_lib'] else 'N'}")
        print(f"   Headings: {len(r['structure']['headings'])} | "
              f"Images: {len(r['structure']['images'])} | "
              f"CTAs: {len(r['structure']['cta_candidates'])}")


def cmd_logos(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    html = fetch_url(url)
    if not html:
        print(f"Failed to fetch {url}")
        return
    logo_patterns = [
        r'<img[^>]+src="([^"]*logo[^"]*)"',
        r'<img[^>]+class="[^"]*logo[^"]*"[^>]+src="([^"]*)"',
        r'<link[^>]+rel="icon"[^>]+href="([^"]*)"',
        r'<link[^>]+rel="apple-touch-icon"[^>]+href="([^"]*)"',
        r'<link[^>]+rel="shortcut icon"[^>]+href="([^"]*)"',
    ]
    logos_found = []
    for pattern in logo_patterns:
        logos_found.extend(re.findall(pattern, html, re.IGNORECASE))
    svg_logos = re.findall(r'<svg[^>]*class="[^"]*logo[^"]*"[^>]*>.*?</svg>', html, re.DOTALL | re.IGNORECASE)
    print(f"Found {len(logos_found)} logo candidates + {len(svg_logos)} SVG logos")
    for i, logo_url in enumerate(logos_found[:10]):
        abs_url = urllib.parse.urljoin(url, logo_url)
        print(f"  Downloading: {abs_url}")
        try:
            req = urllib.request.Request(abs_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                ext = abs_url.split('.')[-1].split('?')[0][:4]
                fname = f'logo_{i}.{ext}'
                with open(os.path.join(output_dir, fname), 'wb') as f:
                    f.write(data)
                print(f"    -> {fname} ({len(data)} bytes)")
        except Exception as e:
            print(f"    [X] Failed: {e}")
    for i, svg in enumerate(svg_logos):
        with open(os.path.join(output_dir, f'logo_svg_{i}.svg'), 'w') as f:
            f.write(svg)
    print(f"\nLogos saved -> {output_dir}/")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'scrape':
        cmd_scrape(sys.argv[2], sys.argv[3])
    elif cmd == 'design':
        cmd_design(sys.argv[2])
    elif cmd == 'batch-design':
        cmd_batch_design(sys.argv[2], sys.argv[3])
    elif cmd == 'logos':
        cmd_logos(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}\n{__doc__}")
        sys.exit(1)

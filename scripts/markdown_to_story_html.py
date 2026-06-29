#!/usr/bin/env python3
"""Convert short story markdown to e-book style HTML."""

import re
import sys
from pathlib import Path


STORY_ID_MAP = {
    'watchdog_patrol': 'watchdog_patrol',
    'ice_run': 'ice_run',
    'black_ice_dream': 'black_ice_dream',
    'case_jackout-30sec': 'first_jack',
    'dixies_last_run': 'dixies_offer',
    'wigan_zavijava': 'aleph_fragment',
    'loa_voodoo_contact': 'voodoo_loa_encounter',
    'the_choice': 'final_choice',
    'flatline_again': 'craft_job',
    'kumiko_manarase-midnight': 'sense_net_tip',
    'marly_louisiana-god': 'mollys_razor',
    'sally_sandii-3am': 'ta_heist',
    'sally_returns': 'delivery_to_finn',
    'sense_net_trace': 'sense_net_tip',
    'yakuza_deal': 'yakuza_deal',
    'first_trace': 'first_trace',
    'tutorial_maze': 'tutorial_maze',
    'first_contact': 'first_contact',
    'data_retrieval': 'data_retrieval',
    'mollys_market': 'mollys_market',
    'zion_express': 'zion_express',
    'vegas_stakeout': 'vegas_stakeout',
    'winter_infiltrate': 'winter_infiltrate',
    'neuromancer_whisper': 'neuromancer_whisper',
    'matrix_revelation': 'matrix_revelation',
    'dixies_choice': 'dixies_choice',
    'neuromancer_merger': 'neuromancer_merger',
}


STORY_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Roguelike Sprawl</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #faf8f5;
            --text-color: #2c2c2c;
            --accent-color: #e94560;
            --meta-color: #666666;
            --font-serif: "Crimson Pro", "Source Serif 4", Georgia, serif;
            --max-width: 680px;
            --line-height: 1.8;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 18px; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: var(--font-serif);
            line-height: var(--line-height);
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
        }}
        .container {{ max-width: var(--max-width); margin: 0 auto; padding: 4rem 2rem 8rem; }}

        .story-header {{ margin-bottom: 3rem; padding-bottom: 2rem; border-bottom: 1px solid #e0ddd8; }}
        .character-badge {{
            display: inline-block;
            font-family: monospace;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--accent-color);
            background: #1a1a2e15;
            padding: 0.25rem 0.75rem;
            border-radius: 2px;
            margin-bottom: 1rem;
        }}
        .story-title {{ font-size: 2.25rem; font-weight: 600; line-height: 1.2; margin-bottom: 0.5rem; }}
        .story-subtitle {{ font-size: 1.1rem; font-style: italic; color: var(--meta-color); }}
        .story-meta {{ margin-top: 1rem; font-size: 0.85rem; color: var(--meta-color); }}
        .story-meta span {{ margin-right: 1rem; }}

        .story-body {{ text-align: justify; hyphens: auto; }}
        .story-body p {{ margin-bottom: 1.5rem; }}
        .story-body h2 {{
            font-size: 1.4rem; font-weight: 600;
            color: var(--accent-color); margin: 2.5rem 0 1rem;
        }}
        .story-body blockquote {{
            font-style: italic; color: var(--meta-color);
            border-left: 3px solid var(--accent-color);
            padding-left: 1rem; margin: 2rem 0;
        }}
        .story-body hr {{ border: none; border-top: 1px solid #e0ddd8; margin: 2rem 0; }}
        .story-body ul {{ margin: 1.5rem 0; padding-left: 1.5rem; }}
        .story-body li {{ margin-bottom: 0.5rem; }}
        em {{ font-style: italic; }}
        strong {{ font-weight: 600; }}

        .story-footer {{ margin-top: 4rem; padding-top: 2rem; border-top: 1px solid #e0ddd8; text-align: center; }}
        .story-footer p {{ font-size: 0.85rem; color: var(--meta-color); font-family: monospace; text-transform: uppercase; letter-spacing: 0.1em; }}

        .lang-indicator {{
            position: fixed; top: 1rem; right: 1rem;
            font-family: monospace; font-size: 0.7rem;
            text-transform: uppercase; letter-spacing: 0.1em;
            color: var(--meta-color); background: var(--bg-color);
            padding: 0.25rem 0.5rem; border-radius: 2px; opacity: 0.7;
        }}
        .lang-indicator a {{ color: inherit; text-decoration: none; }}
        .lang-indicator a:hover {{ text-decoration: underline; }}

        @media (max-width: 600px) {{ html {{ font-size: 16px; }} .container {{ padding: 2rem 1.5rem 6rem; }} .story-title {{ font-size: 1.75rem; }} }}
    </style>
</head>
<body>
    <div class="lang-indicator">{lang_indicator}</div>
    <div class="container">
        <header class="story-header">
            <div class="character-badge">{character_badge}</div>
            <h1 class="story-title">{title}</h1>
            <p class="story-subtitle">{subtitle}</p>
            <div class="story-meta"><span>{word_count} words</span><span>Sprawl Trilogy</span></div>
        </header>
        <article class="story-body">
{body}
        </article>
        <footer class="story-footer">
            <p>Roguelike Sprawl — Derivative Fiction</p>
            <p>Based on William Gibson's Sprawl Trilogy</p>
        </footer>
    </div>
</body>
</html>"""


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    import yaml
    try:
        frontmatter = yaml.safe_load(parts[1])
    except:
        frontmatter = {}

    return frontmatter, parts[2].strip()


def markdown_to_html(text: str, lang: str) -> str:
    """Convert markdown to HTML."""
    html_parts = []
    lines = text.strip().split('\n')
    in_blockquote = False
    blockquote_content = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Horizontal rule
        if re.match(r'^---+$', line.strip()):
            if blockquote_content:
                html_parts.append(f'<blockquote>{"".join(blockquote_content)}</blockquote>')
                blockquote_content = []
                in_blockquote = False
            html_parts.append('<hr>')
            i += 1
            continue

        # Headers - skip H1 title at start (already in header)
        if i == 0:
            h1_match = re.match(r'^# (.+)$', line.strip())
            if h1_match:
                i += 1
                continue

        header_match = re.match(r'^## (.+)$', line.strip())
        if header_match:
            if blockquote_content:
                html_parts.append(f'<blockquote>{"".join(blockquote_content)}</blockquote>')
                blockquote_content = []
                in_blockquote = False
            title = header_match.group(1)
            title = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', title)
            title = re.sub(r'\*(.+?)\*', r'<em>\1</em>', title)
            html_parts.append(f'<h2>{title}</h2>')
            i += 1
            continue

        # Blockquote lines
        if line.strip().startswith('>'):
            if blockquote_content:
                html_parts.append(f'<blockquote>{"".join(blockquote_content)}</blockquote>')
                blockquote_content = []
            blockquote_content.append(f'<p>{line.strip()[1:].strip()}</p>')
            in_blockquote = True
            i += 1
            continue
        elif in_blockquote and not line.strip():
            html_parts.append(f'<blockquote>{"".join(blockquote_content)}</blockquote>')
            blockquote_content = []
            in_blockquote = False
            i += 1
            continue
        elif in_blockquote:
            html_parts.append(f'<blockquote>{"".join(blockquote_content)}</blockquote>')
            blockquote_content = []
            in_blockquote = False
            continue

        # List items
        list_match = re.match(r'^(- .+)$', line.strip())
        if list_match:
            items = []
            while i < len(lines) and re.match(r'^(- .+)$', lines[i].strip()):
                item_text = lines[i].strip()[2:]
                item_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item_text)
                item_text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', item_text)
                item_text = re.sub(r'\[\[(.+?)\]\]', r'<em>\1</em>', item_text)
                items.append(f'<li>{item_text}</li>')
                i += 1
            html_parts.append(f'<ul>{"".join(items)}</ul>')
            continue

        # Regular paragraph
        if line.strip():
            para = line.strip()
            para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)
            para = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)
            para = re.sub(r'\[\[(.+?)\]\]', r'<em>\1</em>', para)
            html_parts.append(f'<p>{para}</p>')
        elif html_parts and html_parts[-1].endswith('</p>'):
            pass  # Skip empty lines between paragraphs
        i += 1

    if blockquote_content:
        html_parts.append(f'<blockquote>{"".join(blockquote_content)}</blockquote>')

    return '\n'.join(html_parts)


def get_story_id(md_path: Path) -> str:
    """Extract story ID from markdown filename."""
    stem = md_path.stem
    if stem.endswith('.ko'):
        stem = stem[:-3]

    for md_id, html_id in STORY_ID_MAP.items():
        if stem.endswith(md_id):
            return html_id

    for md_id, html_id in STORY_ID_MAP.items():
        if md_id in stem:
            return html_id

    return stem.split('_', 2)[-1]


def convert_markdown_to_html(md_path: Path, output_dir: Path, lang: str) -> Path:
    """Convert a single markdown file to HTML."""
    content = md_path.read_text(encoding='utf-8')
    frontmatter, body = parse_frontmatter(content)

    title = frontmatter.get(f'title_{lang}', frontmatter.get('title', 'Untitled'))
    subtitle = frontmatter.get(f'subtitle_{lang}', frontmatter.get('subtitle', ''))
    word_count = frontmatter.get('word_count', 0)

    character = frontmatter.get('character', [{}])
    if isinstance(character, list) and character:
        char_info = character[0]
        char_id = char_info.get('id', 'unknown')
        char_archetype = char_info.get('archetype', '')
    else:
        char_id = 'unknown'
        char_archetype = ''

    char_badge = char_id.capitalize()
    if char_archetype:
        char_badge = f"{char_badge} — {char_archetype.capitalize()}"

    other_lang = 'ko' if lang == 'en' else 'en'
    story_id = get_story_id(md_path)
    lang_indicator = f'{lang.upper()} · <a href="{story_id}_{other_lang}.html">{other_lang.upper()}</a>'

    body_html = markdown_to_html(body, lang)

    html = STORY_HTML_TEMPLATE.format(
        lang=lang,
        title=title,
        subtitle=subtitle,
        character_badge=char_badge,
        word_count=word_count,
        lang_indicator=lang_indicator,
        body=body_html
    )

    output_path = output_dir / f"{story_id}_{lang}.html"
    output_path.write_text(html, encoding='utf-8')

    return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert short story markdown to HTML')
    parser.add_argument('--source-dir', default='/Users/emilio/projects/Projects/Fiction/derivative/sprawl-trilogy/short-stories', help='Source markdown directory')
    parser.add_argument('--output-dir', default='/Users/emilio/projects/Projects/Game/roguelike_sprawl/dashboard/stories/short-stories', help='Output HTML directory')
    parser.add_argument('--lang', choices=['en', 'ko', 'both'], default='both', help='Language to convert')
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    languages = ['en', 'ko'] if args.lang == 'both' else [args.lang]

    en_files = sorted(f for f in source_dir.glob('2026-06-*_*.md') if '.ko.' not in f.name)
    ko_files = sorted(source_dir.glob('2026-06-*_*.ko.md'))

    for md_path in en_files:
        if 'en' in languages:
            try:
                output_path = convert_markdown_to_html(md_path, output_dir, 'en')
                print(f"Generated: {output_path.name}")
            except Exception as e:
                print(f"Error processing {md_path.name}: {e}")

    for md_path in ko_files:
        if 'ko' in languages:
            try:
                output_path = convert_markdown_to_html(md_path, output_dir, 'ko')
                print(f"Generated: {output_path.name}")
            except Exception as e:
                print(f"Error processing {md_path.name}: {e}")


if __name__ == '__main__':
    main()
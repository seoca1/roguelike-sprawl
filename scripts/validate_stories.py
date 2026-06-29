#!/usr/bin/env python3
"""
Story Validator — 단편소설 품질 검증기 (개선版)
Improvements:
- Context-aware language detection (line-by-line)
- Better distinction between intentional bilingual and contamination
- Specific checks for Chinese/Japanese character contamination
- Technical term whitelist for cyberpunk vocabulary
"""

import re
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set, Dict
from pathlib import Path
from collections import Counter

@dataclass
class Issue:
    severity: str  # error, warning, info
    category: str   # encoding, mixed_lang, gibberish, formatting, content
    message: str
    line: Optional[int] = None
    context: Optional[str] = None

@dataclass
class StoryReport:
    title: str
    file_path: str
    language: str
    word_count: int
    issues: List[Issue] = field(default_factory=list)
    is_english: bool = True

    @property
    def has_errors(self) -> bool:
        return any(i.severity == 'error' for i in self.issues)

    @property
    def status(self) -> str:
        if not self.issues:
            return "✅ PASS"
        if self.has_errors:
            return "❌ FAIL"
        return "⚠️ WARN"


class StoryValidator:
    # Character ranges
    HANGUL_START = 0xAC00
    HANGUL_END = 0xD7A3
    HANJA_START = 0x4E00
    HANJA_END = 0x9FFF
    HIRAGANA_START = 0x3040
    HIRAGANA_END = 0x309F
    KATAKANA_START = 0x30A0
    KATAKANA_END = 0x30FF

    # Technical terms that are OK in English text (not contamination)
    TECHNICAL_TERMS: Set[str] = {
        'matrix', 'ice', 'deck', 'decking', 'jack', 'jacking', 'jack-in', 'jack-out',
        'cowboy', 'runner', 'sprawl', 'simstim', ' construct', 'rom', 'program',
        'corporate', 'corp', 'tessier-ashpool', 'sense/net', 'freeside', 'chiba',
        'neuromancer', 'cyberpunk', 'wetware', 'hardware', 'software', 'firewall',
        'proxy', 'node', 'architecture', 'data', 'trace', 'ghost', 'signal', 'frequency',
        'channel', 'dead drop', 'burn', 'burned', 'crack', 'cracker',
        'ice-breaking', 'breach', 'scan', 'trace', 'protocol', 'memory', 'storage',
        'corporation', 'megacorp', 'startup', 'shutdown', 'login', 'logout',
        'backup', 'restore', 'archive', 'retrieval', 'extraction', 'injection',
        'trojan', 'virus', 'worm', 'daemon', 'agent', 'bot', 'ice',
        'shard', 'failsafe', 'failsafes', 'bypass', 'override', 'shutdown',
        'neural', 'synapse', 'axon', 'dendrite', 'cortex', 'brain', 'meat',
        'modem', 'cable', 'fiber', 'wireless', 'satellite', 'uplink', 'downlink',
    }

    # Characters that indicate contamination (not intentional bilingual)
    CHINESE_CHARS: Set[str] = {
        '它', '他', '她', '们', '的', '了', '在', '是', '我', '你', '和', '与', '对', '就', '也',
        '都', '被', '给', '把', '而', '且', '使', '所', '之', '則', '若', '因', '通過', '輸入',
        '輸出', '順序列', '運營', '運行', '選擇', '存在', '獲得', '價格', '美麗', '主要',
        '基本', '系統', '技術', '使用', '実装', '開発', '提供', '機能', '処理', '操作',
        '管理', '連絡', '状態', '状況', '現在', '問題', '理解', '説明', '証明', '確認',
        '実現', '作成', '生成', '実行', '完了', '終了', '開始', '停止', '中断', '継続',
        '接続', '通信', '送信', '受信', '有効', '無効', '必要', '不要', '可能', '不可能',
        '簡単', '複雑', '新しい', '古い', '大きい', '小さい', '高い', '低い', '長い', '短い',
    }

    JAPANESE_CHARS: Set[str] = {
        'の', 'は', 'が', 'を', 'に', 'で', 'と', 'も', 'や', 'から', 'まで', 'より',
        'です', 'ます', 'した', 'する', 'した', 'され', 'これ', 'それ', 'あれ', 'ここ',
        'そこ', 'どこ', '誰', '何', '哪种', '怎样', '为什么', '哪里', '何时', '多么',
        '最初', 'もう', 'いない', '至る', '存在', '商品', '新鮮', '鮮な', 'alert', '暗い',
        '暗く', '取得', '選択', '存在', '同じ', '異なる', '非常に', '大きな', '小さな',
        '様々な', '異なる', '実際', '必ずしも', '允许', '獲得', '選擇', '終瞭', '終末',
        '美丽', '美しい', '主要な', '基本的な', 'システム', '技術', '使用', '実装',
        '開発', '提供', '機能', '処理', '操作', '管理', '連絡', '状態', '状況',
    }

    # Patterns that are contamination
    CONTAMINATION_PATTERNS: List[Tuple[str, str]] = [
        # Chinese particles in Korean context
        ('它', '그것'), ('他', '그'), ('她', '그녀'), ('的', '의'), ('了', '다'),
        ('在', '에'), ('是', '이다'), ('我', '나'), ('你', '너'), ('和', '과'),
        ('与', '와'), ('对', '대'), ('就', '한다'), ('也', '도'), ('都', '모두'),
        ('被', '받'), ('给', '주'), ('把', '을'), ('而', '그러나'), ('且', '그리고'),
        # Japanese patterns
        ('の', '의'), ('です', '이다'), ('ます', 'ます'), ('した', '했다'),
        ('する', '하다'), ('これ', '이것'), ('それ', '그것'), ('あれ', '저것'),
        ('から', '때문'), ('まで', '까지'), ('より', '보다'),
        # Common mixed errors
        ('最初', '처음'), ('存在', '존재'), ('商品化', '상품화'),
        ('選択', '선택'), ('獲得', '획득'), ('終瞭', '종료'), ('運行', '운행'),
    ]

    def __init__(self, base_path: str = '/'):
        self.base_path = Path(base_path)

    def is_hangul(self, char: str) -> bool:
        return self.HANGUL_START <= ord(char) <= self.HANGUL_END

    def is_hanja(self, char: str) -> bool:
        return self.HANJA_START <= ord(char) <= self.HANJA_END

    def is_hiragana(self, char: str) -> bool:
        return self.HIRAGANA_START <= ord(char) <= self.HIRAGANA_END

    def is_katakana(self, char: str) -> bool:
        return self.KATAKANA_START <= ord(char) <= self.KATAKANA_END

    def is_latin(self, char: str) -> bool:
        return ('A' <= char <= 'Z') or ('a' <= char <= 'z') or ('0' <= char <= '9')

    def analyze_line_language(self, line: str) -> Dict[str, int]:
        """Analyze a line for character composition."""
        counts = {
            'hangul': 0,    # Korean
            'hanja': 0,     # Chinese
            'hiragana': 0,  # Japanese hiragana
            'katakana': 0,  # Japanese katakana
            'latin': 0,     # Latin alphabet
            'other': 0,
        }
        for char in line:
            if self.is_hangul(char):
                counts['hangul'] += 1
            elif self.is_hanja(char):
                counts['hanja'] += 1
            elif self.is_hiragana(char):
                counts['hiragana'] += 1
            elif self.is_katakana(char):
                counts['katakana'] += 1
            elif self.is_latin(char):
                counts['latin'] += 1
            else:
                counts['other'] += 1
        return counts

    def check_encoding(self, text: str) -> List[Issue]:
        """Check for encoding issues."""
        issues = []

        if '\ufffd' in text:
            issues.append(Issue('error', 'encoding', 'Contains replacement character (�)'))

        if '\x00' in text:
            issues.append(Issue('error', 'encoding', 'Contains null bytes'))

        return issues

    def check_mixed_language(self, text: str, is_english: bool) -> List[Issue]:
        """Check for mixed language issues with context awareness."""
        issues = []
        lines = text.split('\n')

        # Line-by-line analysis
        problematic_lines = []
        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue

            counts = self.analyze_line_language(line)

            # Skip frontmatter
            if line.strip().startswith('---'):
                continue

            # Skip markdown headers
            if line.startswith('#'):
                continue

            # Skip blockquotes
            if line.startswith('>'):
                continue

            total_chars = sum(counts.values())
            if total_chars == 0:
                continue

            # Check for Chinese characters (contamination)
            if counts['hanja'] > 0:
                # Check if it's intentional (Chinese quote or reference)
                if not any(ref in line for ref in ['[[', ']]', 'Wikipedia', 'wiki']):
                    ratio = counts['hanja'] / total_chars
                    if ratio > 0.05 or counts['hanja'] > 2:
                        problematic_lines.append((i, line.strip()[:80], counts['hanja'], 'Chinese'))
                        issues.append(Issue('warning', 'mixed_lang',
                            f'Line {i}: {counts["hanja"]} Chinese characters detected',
                            context=line.strip()[:100]))

            # Check for Japanese hiragana (contamination when in Korean text)
            if counts['hiragana'] > 3 and not is_english:
                # Only flag if it's not just a few particles
                ratio = counts['hiragana'] / total_chars
                if ratio > 0.1 or counts['hiragana'] > 5:
                    problematic_lines.append((i, line.strip()[:80], counts['hiragana'], 'Japanese hiragana'))
                    issues.append(Issue('warning', 'mixed_lang',
                        f'Line {i}: {counts["hiragana"]} Japanese hiragana detected',
                        context=line.strip()[:100]))

            # Check for Japanese katakana (may be intentional for emphasis)
            if counts['katakana'] > 5 and not is_english:
                issues.append(Issue('info', 'mixed_lang',
                    f'Line {i}: {counts["katakana"]} Japanese katakana (may be intentional)',
                    context=line.strip()[:100]))

        return issues

    def check_gibberish(self, text: str, is_english: bool) -> List[Issue]:
        """Check for gibberish patterns."""
        issues = []

        # Check for specific contamination patterns
        for old, new in self.CONTAMINATION_PATTERNS:
            if old in text:
                count = text.count(old)
                issues.append(Issue('warning', 'gibberish',
                    f'Contamination pattern "{old}" found {count}x (should be "{new}")'))

        # Check for repeated characters
        for char in set(text):
            if char in ' \t\n':
                continue
            if text.count(char * 5) > 0:
                # Exception for CSS hex colors
                if char == '#':
                    continue
                issues.append(Issue('warning', 'gibberish',
                    f'Repeated character "{char}" found'))

        return issues

    def check_formatting(self, text: str, is_english: bool) -> List[Issue]:
        """Check formatting issues."""
        issues = []

        lines = text.split('\n')

        # Check for very long lines
        long_lines = [(i, len(line)) for i, line in enumerate(lines) if len(line) > 200]
        if len(long_lines) > 10:
            issues.append(Issue('info', 'formatting',
                f'{len(long_lines)} lines exceed 200 characters'))

        return issues

    def check_content(self, text: str, is_english: bool) -> List[Issue]:
        """Check content completeness."""
        issues = []

        word_count = len(re.findall(r'\w+', text))

        if word_count < 200:
            issues.append(Issue('warning', 'content', f'Very short: only {word_count} words'))

        return issues

    def validate_file(self, file_path: str) -> StoryReport:
        """Validate a single story file."""
        path = Path(file_path)
        lang = 'ko' if '.ko.md' in path.name else 'en'
        is_english = lang == 'en'

        title = path.stem.replace('_', ' ').title()

        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            return StoryReport(title, str(path), lang, 0,
                             [Issue('error', 'encoding', 'Could not decode as UTF-8')], is_english)

        # Skip frontmatter for analysis
        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) >= 3:
                text = parts[2]

        all_issues = []
        all_issues.extend(self.check_encoding(text))
        all_issues.extend(self.check_mixed_language(text, is_english))
        all_issues.extend(self.check_gibberish(text, is_english))
        all_issues.extend(self.check_formatting(text, is_english))
        all_issues.extend(self.check_content(text, is_english))

        word_count = len(re.findall(r'\w+', text))

        return StoryReport(title, str(path), lang, word_count, all_issues, is_english)

    def validate_directory(self, dir_path: str, pattern: str = '*.md') -> List[StoryReport]:
        """Validate all story files in a directory."""
        reports = []
        path = Path(dir_path)

        for file_path in sorted(path.glob(pattern)):
            report = self.validate_file(str(file_path))
            reports.append(report)

        return reports

    def print_report(self, report: StoryReport) -> None:
        """Print a detailed report for a story."""
        print(f"\n{'='*60}")
        print(f"{report.status} {report.title} [{report.language.upper()}]")
        print(f"   Words: {report.word_count}")
        print(f"{'='*60}")

        if not report.issues:
            print("   No issues found")
            return

        by_severity = {'error': [], 'warning': [], 'info': []}
        for issue in report.issues:
            by_severity[issue.severity].append(issue)

        for severity in ['error', 'warning', 'info']:
            if by_severity[severity]:
                print(f"\n  [{severity.upper()}]")
                for issue in by_severity[severity]:
                    msg = f"    [{issue.category}] {issue.message}"
                    if issue.context:
                        msg += f"\n      Context: {issue.context[:100]}..."
                    print(msg)

    def print_summary(self, reports: List[StoryReport]) -> None:
        """Print summary of all reports."""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)

        passed = sum(1 for r in reports if r.status == "✅ PASS")
        failed = sum(1 for r in reports if r.status == "❌ FAIL")
        warned = sum(1 for r in reports if r.status == "⚠️ WARN")

        print(f"\nTotal: {len(reports)} stories")
        print(f"  ✅ PASS: {passed}")
        print(f"  ❌ FAIL: {failed}")
        print(f"  ⚠️ WARN: {warned}")

        print("\n--- FAILURES ---")
        for r in reports:
            if r.has_errors:
                print(f"  ❌ {r.title} [{r.language}]")
                for i in r.issues:
                    if i.severity == 'error':
                        print(f"      {i.category}: {i.message}")

        print("\n--- WARNINGS ---")
        for r in reports:
            if any(i.severity == 'warning' for i in r.issues) and not r.has_errors:
                print(f"  ⚠️ {r.title} [{r.language}]")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Validate short stories')
    parser.add_argument('path', help='Path to story file or directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--language', '-l', choices=['en', 'ko', 'both'], default='both',
                      help='Filter by language')
    args = parser.parse_args()

    validator = StoryValidator('/')

    path = Path(args.path)
    if path.is_file():
        reports = [validator.validate_file(str(path))]
    else:
        pattern = '*.md' if args.language == 'en' else ('*.ko.md' if args.language == 'ko' else '*.md')
        reports = validator.validate_directory(str(path), pattern)

    for report in reports:
        if args.verbose or report.issues:
            validator.print_report(report)

    validator.print_summary(reports)

    if any(r.has_errors for r in reports):
        exit(1)


if __name__ == '__main__':
    main()

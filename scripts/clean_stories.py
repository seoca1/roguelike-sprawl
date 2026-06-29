#!/usr/bin/env python3
"""
Language Cleaner — 한국어 텍스트에서 비한국어 문자 제거/교체
Cleans Korean text by removing or replacing non-Korean characters that are errors.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Common Japanese/Chinese characters that appear in Korean text (contamination)
CONTAMINATION_PATTERNS: List[Tuple[str, str, str]] = [
    # Japanese patterns
    (r'最初', '처음', 'Japanese 最初 → Korean 처음'),
    (r'もういない', '이미 없다', 'Japanese もういない → Korean 이미 없다'),
    (r'至る', '이르다', 'Japanese 至る → Korean 이르다'),
    (r'存在', '존재', 'Chinese/Japanese 存在 → Korean 존재'),
    (r'から', '때문', 'Japanese から → Korean 때문'),
    (r'商品化', '상품화', 'Chinese/Japanese 商品化 → Korean 상품화'),
    (r'新鮮', '신선한', 'Chinese 新鮮 → Korean 신선한'),
    (r'新鮮な', '신선한', 'Japanese 新鮮な → Korean 신선한'),
    (r'报警', '경보', 'Chinese 报警 → Korean 경보'),
    (r'暗い', '어두운', 'Japanese 暗い → Korean 어두운'),
    (r'暗く', '어두운', 'Japanese 暗く → Korean 어두운'),
    (r'取得した', '획득한', 'Japanese 取得한 → Korean 획득한'),
    (r'選択', '선택', 'Chinese/Japanese 選択 → Korean 선택'),
    (r'存在する', '존재하는', 'Japanese 存在する → Korean 존재하는'),
    (r'同じ', '같은', 'Japanese 同じ → Korean 같은'),
    (r'異なる', '다른', 'Japanese 異なる → Korean 다른'),
    (r'非常に', '매우', 'Japanese 非常に → Korean 매우'),
    (r'大きな', '큰', 'Japanese 大きな → Korean 큰'),
    (r'小さな', '작은', 'Japanese 小さな → Korean 작은'),
    (r' 빠른', '빠른', 'Korean but pattern'),
    (r'様々な', '다양한', 'Japanese 様々な → Korean 다양한'),
    (r'異なる', '다양한', 'Japanese 異なる → Korean 다양한'),
    (r'実際には', '실제로는', 'Japanese 実際には → Korean 실제로는'),
    (r'必ずしも', '반드시', 'Japanese 必ずしも → Korean 반드시'),
    (r'允许', '허용', 'Chinese 允许 → Korean 허용'),
    (r'獲得', '획득', 'Chinese/Japanese 獲得 → Korean 획득'),
    (r'選擇', '선택', 'Chinese 選擇 → Korean 선택'),
    (r'终瞭', '종료', 'Chinese 终瞭 → Korean 종료'),
    (r'終瞭', '종료', 'Japanese 終瞭 → Korean 종료'),
    (r'終末', '종말', 'Japanese 終末 → Korean 종말'),
    (r'美丽', '아름다운', 'Chinese 美丽 → Korean 아름다운'),
    (r'美しい', '아름다운', 'Japanese 美しい → Korean 아름다운'),
    (r'主要な', '주요한', 'Japanese 主要な → Korean 주요한'),
    (r'主要な', '주요한', 'Japanese 主要な → Korean 주요한'),
    (r'基本的な', '기본적인', 'Japanese 基本的な → Korean 기본적인'),
    (r'系统', '시스템', 'Chinese 系统 → Korean 시스템'),
    (r'システム', '시스템', 'Japanese システム → Korean 시스템'),
    (r'技術', '기술', 'Chinese/Japanese 技術 → Korean 기술'),
    (r'使用', '사용', 'Chinese/Japanese 使用 → Korean 사용'),
    (r'実装', '구현', 'Japanese 実装 → Korean 구현'),
    (r'開発', '개발', 'Japanese 開発 → Korean 개발'),
    (r'提供', '제공', 'Chinese/Japanese 提供 → Korean 제공'),
    (r'機能', '기능', 'Japanese 機能 → Korean 기능'),
    (r'処理', '처리', 'Japanese 処理 → Korean 처리'),
    (r'操作', '조작', 'Chinese/Japanese 操作 → Korean 조작'),
    (r'管理', '관리', 'Chinese/Japanese 管理 → Korean 관리'),
    (r'連絡', '연락', 'Japanese 連絡 → Korean 연락'),
    (r'連絡', '연락', 'Japanese 連絡 → Korean 연락'),
    (r'状態', '상태', 'Japanese 状態 → Korean 상태'),
    (r'状況', '상황', 'Japanese 状況 → Korean 상황'),
    (r'現在', '현재', 'Chinese/Japanese 現在 → Korean 현재'),
    (r'問題', '문제', 'Chinese/Japanese 問題 → Korean 문제'),
    (r'理解', '이해', 'Chinese/Japanese 理解 → Korean 이해'),
    (r'説明', '설명', 'Japanese 説明 → Korean 설명'),
    (r'証明', '증명', 'Chinese/Japanese 証明 → Korean 증명'),
    (r'確認', '확인', 'Japanese 確認 → Korean 확인'),
    (r'実現', '실현', 'Japanese 実現 → Korean 실현'),
    (r'開発', '개발', 'Japanese 開発 → Korean 개발'),
    (r'作成', '작성', 'Japanese 作成 → Korean 작성'),
    (r'生成', '생성', 'Chinese/Japanese 生成 → Korean 생성'),
    (r'処理', '처리', 'Japanese 処理 → Korean 처리'),
    (r'実行', '실행', 'Japanese 実行 → Korean 실행'),
    (r'完了', '완료', 'Chinese/Japanese 完了 → Korean 완료'),
    (r'終了', '종료', 'Japanese 終了 → Korean 종료'),
    (r'開始', '시작', 'Chinese/Japanese 開始 → Korean 시작'),
    (r'停止', '정지', 'Chinese/Japanese 停止 → Korean 정지'),
    (r'中断', '중단', 'Chinese/Japanese 中断 → Korean 중단'),
    (r'継続', '계속', 'Japanese 継続 → Korean 계속'),
    (r'接続', '연결', 'Japanese 接続 → Korean 연결'),
    (r'通信', '통신', 'Chinese/Japanese 通信 → Korean 통신'),
    (r'送信', '전송', 'Japanese 送信 → Korean 전송'),
    (r'受信', '수신', 'Japanese 受信 → Korean 수신'),
    (r'有効', '유효', 'Japanese 有効 → Korean 유효'),
    (r'無効', '무효', 'Japanese 無効 → Korean 무효'),
    (r'必要', '필요', 'Japanese 必要 → Korean 필요'),
    (r'不要', '불필요', 'Japanese 不要 → Korean 불필요'),
    (r'可能', '가능', 'Chinese/Japanese 可能 → Korean 가능'),
    (r'不可能', '불가능', 'Chinese/Japanese 不可能 → Korean 불가능'),
    (r'簡単', '간단', 'Japanese 簡単 → Korean 간단'),
    (r'複雑', '복잡', 'Japanese 複雑 → Korean 복잡'),
    (r'新しい', '새로운', 'Japanese 新しい → Korean 새로운'),
    (r'古い', '오래된', 'Japanese 古い → Korean 오래된'),
    (r'大きい', '큰', 'Japanese 大きい → Korean 큰'),
    (r'小さい', '작은', 'Japanese 小さい → Korean 작은'),
    (r'高い', '높은', 'Japanese 高い → Korean 높은'),
    (r'低い', '낮은', 'Japanese 低い → Korean 낮은'),
    (r'長い', '긴', 'Japanese 長い → Korean 긴'),
    (r'短い', '짧은', 'Japanese 短い → Korean 짧은'),
    (r'白い', '흰', 'Japanese 白い → Korean 흰'),
    (r'黒い', '검은', 'Japanese 黒い → Korean 검은'),
    (r'赤い', '빨간', 'Japanese 赤い → Korean 빨간'),
    (r'青い', '파란', 'Japanese 青い → Korean 파란'),
    (r' yellow', ' 노란', 'English yellow → Korean 노란'),
    (r' green', ' 초록', 'English green → Korean 초록'),
    (r' purple', ' 보라', 'English purple → Korean 보라'),
    (r' orange', ' 주황', 'English orange → Korean 주황'),
    (r' pink', ' 분홍', 'English pink → Korean 분홍'),
    (r' brown', ' 갈색', 'English brown → Korean 갈색'),
    (r' gray', ' 회색', 'English gray → Korean 회색'),
    (r' black', ' 검은', 'English black → Korean 검은'),
    (r' white', ' 흰', 'English white → Korean 흰'),
    (r' red', ' 빨간', 'English red → Korean 빨간'),
    (r' blue', ' 파란', 'English blue → Korean 파란'),
    (r'これ', '이것', 'Japanese これ → Korean 이것'),
    (r'それ', '그것', 'Japanese それ → Korean 그것'),
    (r'あれ', '저것', 'Japanese あれ → Korean 저것'),
    (r'この', '이', 'Japanese この → Korean 이'),
    (r'その', '그', 'Japanese その → Korean 그'),
    (r'あの', '저', 'Japanese あの → Korean 저'),
    (r' here', ' 여기', 'English here → Korean 여기'),
    (r' there', ' 거기', 'English there → Korean 거기'),
    (r'哪里', '어디', 'Chinese 哪里 → Korean 어디'),
    (r'何處', '어디', 'Chinese 何處 → Korean 어디'),
]

# Single character replacements
SINGLE_CHAR_REPLACEMENTS: Dict[str, str] = {
    '它': '그것',  # Chinese 'it'
    '他': '그',    # Chinese 'he'
    '她': '그녀',  # Chinese 'she'
    '的': '의',    # Chinese possessive
    '了': '다',    # Chinese perfective
    '在': '에',    # Chinese 'at/in'
    '是': '이다',  # Chinese 'is'
    '我': '나',    # Chinese 'I'
    '你': '너',    # Chinese 'you'
    '们': '들',    # Chinese plural
    '和': '과',    # Chinese 'and'
    '与': '와',    # Chinese 'with'
    '为': '위',    # Chinese 'for'
    '对': '대',    # Chinese 'for'
    '就': '한다',  # Chinese particle
    '也': '도',    # Chinese 'also'
    '都': '모두',  # Chinese 'all'
    '但': '그러나', # Chinese 'but'
    '或': '또는',  # Chinese 'or'
    '從': '로부터', # Chinese 'from'
    '至': '까지',  # Chinese 'to'
    '於': '에',    # Chinese 'at'
    '能': '할',    # Chinese 'can'
    '會': '할',    # Chinese 'will'
    '要': '해야',  # Chinese 'must'
    '有': '있',    # Chinese 'have'
    '没': '없',    # Chinese 'not'
    '被': '받',    # Chinese passive
    '给': '주',    # Chinese 'give'
    '把': '을',    # Chinese object marker
    '而': '그러나', # Chinese 'but'
    '且': '그리고', # Chinese 'and'
    '使': '시키',  # Chinese 'make'
    '被': '받',    # Chinese passive
    '所': '바',    # Chinese possessive
    '之': '의',    # Chinese possessive
    '而': '그러나', # Chinese conjunction
    '則': '것',    # Chinese 'then'
    '若': '만약',  # Chinese 'if'
    '因': '때문',  # Chinese 'because'
    '通過': '통과', # Chinese 'through'
    '輸入': '입력', # Chinese 'input'
    '輸出': '출력', # Chinese 'output'
    '順序列': '순서', # Chinese 'sequence'
    '運營': '운영',  # Chinese 'operation'
    '運行': '운행',  # Chinese 'run operation'
}


def clean_text(text: str, dry_run: bool = False) -> Tuple[str, List[str]]:
    """Clean contamination from Korean text."""
    changes = []
    original = text
    
    # Apply pattern replacements
    for pattern, replacement, desc in CONTAMINATION_PATTERNS:
        if pattern in text:
            text = text.replace(pattern, replacement)
            changes.append(f"{desc}: {pattern} → {replacement}")
    
    # Apply single character replacements (but be careful with Latin text)
    # Only replace if the character appears to be in Korean context
    for char, replacement in SINGLE_CHAR_REPLACEMENTS.items():
        # Skip if in English word context
        if char in ['i', 'a', 'I', 'A', 'o', 'O', 'e', 'E']:
            continue
        
        # Count occurrences
        count = text.count(char)
        if count > 0:
            # Check if this looks like Chinese contamination
            # by seeing if it's surrounded by Korean characters
            new_text = text
            for old_char in SINGLE_CHAR_REPLACEMENTS.keys():
                if old_char in ['i', 'a', 'I', 'A', 'o', 'O', 'e', 'E', 'l', 'L', 'n', 'N', 's', 'S', 't', 'T']:
                    continue
                if old_char in text:
                    new_text = new_text.replace(old_char, replacement)
            
            if new_text != text:
                text = new_text
                changes.append(f"Single char {repr(char)} → {replacement} ({count} occurrences)")
    
    return text, changes


def clean_file(file_path: str, dry_run: bool = False) -> List[str]:
    """Clean a single file."""
    path = Path(file_path)
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cleaned, changes = clean_text(content, dry_run)
    
    if not dry_run and changes:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
    
    return changes


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean language contamination in stories')
    parser.add_argument('path', help='Path to markdown file or directory')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        files = [str(path)]
    else:
        files = list(path.glob('*.md'))
    
    total_changes = 0
    for file_path in sorted(files):
        changes = clean_file(str(file_path), args.dry_run)
        if changes:
            print(f"\n{file_path}:")
            for change in changes:
                print(f"  {change}")
            total_changes += len(changes)
    
    if args.dry_run:
        print(f"\n[DRY RUN] Would make {total_changes} changes")
    else:
        print(f"\nMade {total_changes} changes")


if __name__ == '__main__':
    main()

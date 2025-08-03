# src/banner.py
import sys
from pathlib import Path
from rich.text import Text


def print_banner():
    banner = Path(__file__).with_name("banner.txt").read_text(encoding="utf-8")
    # 彩虹渐变，也可以改成固定颜色
    text = Text(banner)
    text.stylize("bold bright_cyan", 0, len(banner))
    print(text, file=sys.stderr)

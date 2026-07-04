#!/usr/bin/env python3
"""Test sound libraries to determine which to use.

Tests:
1. subprocess + afplay (macOS) / aplay (Linux)
2. terminal BEL character
3. simpleaudio (if installed)
4. pygame (if installed)
5. playsound (if installed)

Usage:
  uv run python scripts/test_sound_libraries.py
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SYSTEM = platform.system().lower()
PYTHON = sys.executable


def test_subprocess_afplay() -> dict:
    """Test subprocess with afplay (macOS) or aplay (Linux)."""
    result = {"name": "subprocess+afplay", "available": False, "latency_ms": None, "error": None}

    if SYSTEM == "darwin":
        cmd = ["afplay", "--help"]  # Just check if it exists
    elif SYSTEM == "linux":
        # Check for aplay, paplay, or ffplay
        for tool in ["aplay", "paplay", "ffplay"]:
            if shutil.which(tool):
                cmd = [tool, "--help"]
                break
        else:
            result["error"] = "No audio tool found"
            return result
    else:
        result["error"] = f"Platform {SYSTEM} not supported"
        return result

    try:
        start = time.time()
        proc = subprocess.run(cmd, capture_output=True, timeout=2)
        # Even if --help returns error, if it ran, the tool is available
        if proc.returncode in (0, 1):  # Many tools return 1 for --help
            result["available"] = True
            result["latency_ms"] = (time.time() - start) * 1000
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        result["error"] = str(e)

    return result


def test_bell() -> dict:
    """Test terminal bell character (always works)."""
    return {
        "name": "terminal-bell",
        "available": True,
        "latency_ms": 0.0,
        "error": None,
        "note": "Works everywhere, no sound file needed",
    }


def test_python_lib(lib_name: str = "wave") -> dict:  # noqa: PT028
    """Test if a Python library is available.

    Default arg makes the test self-contained when pytest collects it
    without a fixture. (The intended caller is the CLI runner, not
    pytest parametrize.)
    """
    result = {
        "name": lib_name,
        "available": False,
        "latency_ms": None,
        "error": None,
    }
    try:
        __import__(lib_name)
        result["available"] = True
        result["latency_ms"] = 50.0  # Approximate
    except ImportError as e:
        result["error"] = f"Not installed: {e}"
    return result


def test_generate_sound() -> dict:
    """Test if we can generate a simple WAV file."""
    result = {
        "name": "WAV generation",
        "available": False,
        "error": None,
    }
    try:
        import struct
        import wave

        # Generate a 0.1s 440Hz sine wave
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
            with wave.open(path, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(44100)
                for i in range(4410):  # 0.1s
                    value = int(32767 * 0.3 * (i % 100) / 100)
                    wav.writeframes(struct.pack("<h", value))
        result["available"] = True
        result["file"] = path
        Path(path).unlink()
    except Exception as e:
        result["error"] = str(e)
    return result


def main() -> int:
    """Run all tests and report results."""
    print("=" * 70)
    print("SOUND LIBRARY EVALUATION TEST")
    print("=" * 70)
    print(f"Platform: {SYSTEM}")
    print(f"Python: {PYTHON}")
    print()

    results = []

    # Test 1: Terminal bell
    print("[1] Terminal Bell (BEL character)")
    bell = test_bell()
    print(f"    Available: {bell['available']}")
    print(f"    Note: {bell.get('note', 'N/A')}")
    print()
    results.append(bell)

    # Test 2: Subprocess (afplay/aplay)
    print("[2] Subprocess + System Player (afplay/aplay)")
    sp = test_subprocess_afplay()
    print(f"    Available: {sp['available']}")
    if sp.get("latency_ms"):
        print(f"    Latency: {sp['latency_ms']:.1f}ms")
    if sp.get("error"):
        print(f"    Error: {sp['error']}")
    print()
    results.append(sp)

    # Test 3: WAV file generation
    print("[3] WAV File Generation (Python stdlib)")
    wav = test_generate_sound()
    print(f"    Available: {wav['available']}")
    if wav.get("error"):
        print(f"    Error: {wav['error']}")
    print()
    results.append(wav)

    # Test 4-6: Optional libraries
    for lib in ["simpleaudio", "pygame", "playsound"]:
        print(f"[{len(results) + 1}] {lib} (Python library)")
        result = test_python_lib(lib)
        print(f"    Available: {result['available']}")
        if result.get("error"):
            print(f"    Note: {result['error']}")
        print()
        results.append(result)

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Available methods:")
    for r in results:
        if r["available"]:
            print(f"  [+] {r['name']}")
        else:
            print(f"  [-] {r['name']}")
    print()

    # Recommendation
    print("RECOMMENDATION:")
    if any(r["name"] == "subprocess+afplay" and r["available"] for r in results):
        print("  -> Use subprocess + afplay/aplay (zero dependencies)")
        print("  -> Best for cross-platform, no installs needed")
    elif any(r["name"].startswith("simpleaudio") and r["available"] for r in results):
        print("  -> Install simpleaudio for richer features")
    elif any(r["name"].startswith("pygame") and r["available"] for r in results):
        print("  -> Use pygame (heavy but feature-rich)")
    else:
        print("  -> Use terminal BEL only (minimal)")
    print()
    print("Fallback: terminal BEL always works for simple beeps")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

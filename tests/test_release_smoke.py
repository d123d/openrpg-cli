import subprocess
import sys


def test_release_command_surface():
    for args in (["audit"], ["info"], ["roll", "1d6", "--seed", "1"],
                 ["character", "--help"], ["combat", "--help"], ["play", "--help"]):
        result = subprocess.run([sys.executable, "-m", "srd_cli", *args],
                                text=True, capture_output=True, timeout=30)
        assert result.returncode == 0, result.stderr

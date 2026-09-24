"""
Regression tests for tools/sigma/sigma-to-galaxy.py

Run manually with: python3 tools/sigma/test_sigma_to_galaxy.py
(The repository gate ./validate_all.sh only validates JSON files.)
"""

import importlib.util
import os
import sys

MODULE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sigma-to-galaxy.py")

spec = importlib.util.spec_from_file_location("sigma_to_galaxy", MODULE_PATH)
sigma_to_galaxy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sigma_to_galaxy)


def test_rule_without_logsource():
    """A Sigma rule with no logsource block must degrade to defaults, not crash."""
    valueData = sigma_to_galaxy.parse_sigma_to_cluster(
        {"title": "No logsource rule", "id": "d1e4a0d0-0000-0000-0000-000000000000"},
        "no_logsource.yml",
        "/windows",
    )
    assert valueData["meta"]["logsource.category"] == "No established category"
    assert valueData["meta"]["logsource.product"] == "No established product"


def test_rule_with_empty_logsource():
    """An empty (None) logsource block must also degrade to defaults."""
    valueData = sigma_to_galaxy.parse_sigma_to_cluster(
        {"title": "Empty logsource rule", "logsource": None}, "empty.yml", "/windows"
    )
    assert valueData["meta"]["logsource.category"] == "No established category"
    assert valueData["meta"]["logsource.product"] == "No established product"


def test_rule_with_logsource():
    """A complete logsource block is still read correctly."""
    valueData = sigma_to_galaxy.parse_sigma_to_cluster(
        {"title": "Full rule", "logsource": {"category": "process_creation", "product": "windows"}},
        "full.yml",
        "/windows",
    )
    assert valueData["meta"]["logsource.category"] == "process_creation"
    assert valueData["meta"]["logsource.product"] == "windows"


if __name__ == "__main__":
    failures = 0
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            try:
                func()
                print("PASS: %s" % name)
            except Exception as exc:
                failures += 1
                print("FAIL: %s: %r" % (name, exc))
    sys.exit(1 if failures else 0)

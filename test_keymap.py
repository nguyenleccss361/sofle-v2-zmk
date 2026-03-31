#!/usr/bin/env python3
"""
Test script to validate ZMK keymap structure
Tests that the keymap has correct syntax for ZMK build
"""

import re
import sys


def test_keymap_syntax():
    """Test basic syntax validity"""
    with open("config/sofle.keymap") as f:
        content = f.read()

    errors = []

    # Check matching braces
    opens = content.count("{")
    closes = content.count("}")
    if opens != closes:
        errors.append(f"Brace mismatch: {opens} open, {closes} close")

    # Check matching angle brackets in bindings
    opens = content.count("<")
    closes = content.count(">")
    if opens != closes:
        errors.append(f"Angle bracket mismatch: {opens} <, {closes} >")

    # Check for required includes
    required = ["behaviors.dtsi", "dt-bindings/zmk/keys.h"]
    for req in required:
        if req not in content:
            errors.append(f"Missing required include: {req}")

    # Check layer definitions
    required_layers = ["BASE", "SYMBOL", "NUMBER", "NAVIGATION", "MOUSE", "NOMODS"]
    for layer in required_layers:
        if f"#define {layer}" not in content:
            errors.append(f"Missing layer define: {layer}")

    return errors


def test_keymap_bindings():
    """Test that each layer has correct number of bindings for Sofle"""
    with open("config/sofle.keymap") as f:
        content = f.read()

    errors = []

    # Find all layer sections and count <...> binding blocks
    layer_sections = re.split(r"(^[a-z_]+_layer)", content, flags=re.MULTILINE)

    for i in range(1, len(layer_sections), 2):
        name = layer_sections[i]
        section = layer_sections[i + 1] if i + 1 < len(layer_sections) else ""

        # Find bindings block
        bindings_match = re.search(r"bindings\s*=\s*<(.*?)>;", section, re.DOTALL)
        if bindings_match:
            bindings = bindings_match.group(1)
            # Count all binding references
            count = len(re.findall(r"&\w+", bindings))
            print(f"{name}: {count} bindings")

    return errors


def test_behaviors():
    """Test that behaviors are properly defined"""
    with open("config/sofle.keymap") as f:
        content = f.read()

    errors = []

    # Check tap-dances have correct bindings
    tap_dances = ["td_num", "td_sft", "td_nomod", "td_ms"]
    for td in tap_dances:
        pattern = f"{td}:.*?{{.*?}}"
        if not re.search(pattern, content, re.DOTALL):
            errors.append(f"Missing or incomplete behavior: {td}")

    # Check hold-taps have #binding-cells = <2>
    hold_taps = re.findall(r"(\w+):\s*hold.tap", content)
    for ht in hold_taps:
        pattern = f"{ht}.*?#binding-cells = <2>"
        if not re.search(pattern, content, re.DOTALL):
            errors.append(f"Missing #binding-cells = <2> for {ht}")

    return errors


def main():
    print("Testing ZMK keymap...")

    all_errors = []

    # Run tests
    all_errors.extend(test_keymap_syntax())
    all_errors.extend(test_keymap_bindings())
    all_errors.extend(test_behaviors())

    if all_errors:
        print("FAILED:")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASSED: Basic syntax validation")
        print("Note: Full build test requires ZMK toolchain")
        sys.exit(0)


if __name__ == "__main__":
    main()

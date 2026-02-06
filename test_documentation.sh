#!/bin/bash
echo "Checking documentation files..."
test -f CUSTOMIZATION.md && echo "✓ CUSTOMIZATION.md" || echo "✗ CUSTOMIZATION.md"
test -f IMPROVEMENTS_TRACKER.md && echo "✓ IMPROVEMENTS_TRACKER.md" || echo "✗ IMPROVEMENTS_TRACKER.md"
test -f cloud-run/plugins/README.md && echo "✓ plugins/README.md" || echo "✗ plugins/README.md"
test -f README.md && echo "✓ README.md" || echo "✗ README.md"
test -f CLAUDE.md && echo "✓ CLAUDE.md" || echo "✗ CLAUDE.md"

echo ""
echo "Checking template files..."
test -f cloud-run/templates/categorization_prompt.txt && echo "✓ categorization_prompt.txt" || echo "✗ categorization_prompt.txt"
test -f cloud-run/config/tag_rules.yaml && echo "✓ tag_rules.yaml" || echo "✗ tag_rules.yaml"
test -f cloud-run/templates/note_template.md.j2 && echo "✓ note_template.md.j2" || echo "✗ note_template.md.j2"

echo ""
echo "Checking example plugins..."
test -f cloud-run/plugins/examples/logging_plugin.py && echo "✓ logging_plugin.py" || echo "✗ logging_plugin.py"
test -f cloud-run/plugins/examples/filter_plugin.py && echo "✓ filter_plugin.py" || echo "✗ filter_plugin.py"
test -f cloud-run/plugins/examples/slack_reaction_plugin.py && echo "✓ slack_reaction_plugin.py" || echo "✗ slack_reaction_plugin.py"

echo ""
echo "✓ All documentation files present"

#!/bin/bash
# run_all_tests.sh - Run all ObsidianSlack validation tests

set -e  # Exit on first error

echo "========================================"
echo "ObsidianSlack Test Suite"
echo "========================================"
echo ""

# Check if running from project root
if [ ! -d "cloud-run" ]; then
    echo "❌ Error: Must run from project root directory"
    echo "   Usage: ./tests/run_all_tests.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv-test" ]; then
    echo "⚠️  Warning: venv-test not found"
    echo "   Creating virtual environment..."
    python3 -m venv venv-test
    source venv-test/bin/activate
    pip install -q -r cloud-run/requirements.txt
    echo "✓ Virtual environment created"
    echo ""
else
    source venv-test/bin/activate
fi

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Function to run a test
run_test() {
    local test_name=$1
    local test_file=$2

    echo "----------------------------------------"
    echo "Running: $test_name"
    echo "----------------------------------------"

    if python3 "$test_file"; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo ""
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        FAILED_TESTS+=("$test_name")
        echo ""
        echo "❌ FAILED: $test_name"
        echo ""
    fi
}

# Run all Python tests
run_test "External Prompt Template Loading" "tests/test_prompt_template.py"
run_test "YAML Tag Rules Loading" "tests/test_tag_rules.py"
run_test "Jinja2 Note Template Loading" "tests/test_note_template.py"
run_test "Plugin System - Base Infrastructure" "tests/test_plugin_base.py"
run_test "Plugin System - Functionality" "tests/test_plugin_functionality.py"
run_test "Plugin System - Integration" "tests/test_plugin_integration.py"
run_test "Cross-Platform File Locking" "tests/test_file_locking.py"
run_test "Tag Generator with YAML Rules" "tests/test_tag_generator.py"
run_test "End-to-End Integration" "tests/test_integration.py"

# Run shell tests
echo "----------------------------------------"
echo "Running: Documentation Validation"
echo "----------------------------------------"
if bash tests/test_documentation.sh; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo ""
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS+=("Documentation Validation")
    echo ""
    echo "❌ FAILED: Documentation Validation"
    echo ""
fi

# Print summary
echo "========================================"
echo "Test Suite Complete"
echo "========================================"
echo ""
echo "✅ Passed: $TESTS_PASSED"
echo "❌ Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "🎉 All tests passed!"
    echo ""
    exit 0
else
    echo "Failed tests:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  - $test"
    done
    echo ""
    exit 1
fi

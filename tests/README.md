# ObsidianSlack Test Suite

This directory contains validation tests for all improvements implemented in the ObsidianSlack project.

## Test Organization

```
tests/
├── README.md                          # This file
├── run_all_tests.sh                   # Run all tests sequentially
├── fixtures/                          # Test fixtures and data
│   └── test_plugin.py                 # Test plugin for plugin system validation
├── test_prompt_template.py            # External prompt template loading
├── test_tag_rules.py                  # YAML tag rules loading
├── test_note_template.py              # Jinja2 note template rendering
├── test_plugin_base.py                # Plugin system base infrastructure
├── test_plugin_functionality.py       # Plugin hooks and state management
├── test_plugin_integration.py         # Plugin integration with main.py
├── test_file_locking.py               # Cross-platform file locking
├── test_tag_generator.py              # Tag generation with YAML rules
├── test_integration.py                # End-to-end pipeline simulation
└── test_documentation.sh              # Documentation file validation
```

## Prerequisites

1. **Python 3.8+** installed
2. **Virtual environment** (recommended)
3. **Dependencies** installed

## Setup

```bash
# From project root
python3 -m venv venv-test
source venv-test/bin/activate  # On Windows: venv-test\Scripts\activate
pip install -r cloud-run/requirements.txt
```

## Running Tests

### Run All Tests

```bash
# From project root
./tests/run_all_tests.sh
```

### Run Individual Tests

```bash
# From project root
source venv-test/bin/activate

# Test external configuration
python3 tests/test_prompt_template.py
python3 tests/test_tag_rules.py
python3 tests/test_note_template.py

# Test plugin system
python3 tests/test_plugin_base.py
python3 tests/test_plugin_functionality.py
python3 tests/test_plugin_integration.py

# Test improvements
python3 tests/test_file_locking.py
python3 tests/test_tag_generator.py

# Test integration
python3 tests/test_integration.py

# Test documentation
bash tests/test_documentation.sh
```

## What Each Test Validates

### 1. **test_prompt_template.py**
- Default prompt template loads from `templates/categorization_prompt.txt`
- Custom template loads via `PROMPT_TEMPLATE` env var
- Fallback to default when file missing

### 2. **test_tag_rules.py**
- YAML syntax validation for `config/tag_rules.yaml`
- All 4 sections present (domains, code_languages, keywords, content_types)
- Custom rules load via `TAG_RULES_FILE` env var

### 3. **test_note_template.py**
- Jinja2 template syntax validation
- Template renders with sample data
- ObsidianWriter template engine initialization
- Frontmatter and sections present

### 4. **test_plugin_base.py**
- ProcessorPlugin base class has all 5 hooks
- PluginLoader initializes correctly
- Plugin discovery works (examples/ dir skipped)
- `PLUGINS_ENABLED=false` disables loading

### 5. **test_plugin_functionality.py**
- Test plugin discovered and loaded
- All hooks callable
- State persists across calls
- Skip functionality works

### 6. **test_plugin_integration.py**
- main.py imports plugin system
- All 5 hooks integrated in main.py
- Skip handling present
- Metadata construction verified

### 7. **test_file_locking.py**
- FileLock import and functionality
- Lock acquisition and release
- Timeout behavior
- ObsidianWriter uses FileLock correctly
- Lock files in .gitignore

### 8. **test_tag_generator.py**
- TagGenerator initialization
- Domain-based tagging (github.com → dev/github)
- Code language tagging (python → code/python)
- Keyword tagging
- Tag deduplication
- Question tagging

### 9. **test_integration.py**
- Full pipeline end-to-end
- Note creation with all components
- Plugin hooks called in correct order
- Note content validation

### 10. **test_documentation.sh**
- All documentation files present
- Templates exist
- Example plugins present

## Expected Results

All tests should pass with ✓ indicators. If any test fails:

1. Check error message for specifics
2. Verify dependencies are installed
3. Check that you're running from project root
4. Ensure cloud-run/ directory structure is intact

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - run: pip install -r cloud-run/requirements.txt
      - run: ./tests/run_all_tests.sh
```

## Troubleshooting

**Import errors**: Make sure you're running from the project root directory.

**Missing files**: Verify all cloud-run/ files are present.

**Plugin not found**: The test plugin is in `tests/fixtures/test_plugin.py`.

**Environment variables**: Tests use mock data and don't require real API keys.

## Adding New Tests

When adding new features, create corresponding tests:

1. Create `tests/test_<feature_name>.py`
2. Follow existing test structure
3. Add to `run_all_tests.sh`
4. Update this README

## Test Coverage

These tests validate:
- ✅ External configuration (prompts, tag rules, templates)
- ✅ Plugin system (base, functionality, integration)
- ✅ Cross-platform file locking
- ✅ Tag generation with YAML rules
- ✅ End-to-end pipeline
- ✅ Documentation completeness

**Total Test Scripts**: 10
**Test Coverage**: All major improvements from 2026-02-06 session

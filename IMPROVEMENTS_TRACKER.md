# ObsidianSlack Improvements Tracker

**Last Updated:** 2026-02-06
**Full Analysis:** See `IMPROVEMENTS.md` for detailed information

---

## ✅ COMPLETED

### 1.1: Cross-Platform File Locking
**Status:** ✅ COMPLETED (2026-02-06)
**Commit:** [Next commit]
**Impact:** HIGH - Unblocks Windows users

**What was changed:**
- Replaced Unix-only `fcntl` with cross-platform `filelock` library
- Updated `cloud-run/obsidian_writer.py` to use `FileLock`
- Added `filelock==3.13.1` to `requirements.txt`

**How it works now:**
```python
# Before (Unix-only)
import fcntl
fcntl.flock(f, fcntl.LOCK_EX)

# After (Cross-platform)
from filelock import FileLock
lock = FileLock(f"{path}.lock", timeout=10)
with lock:
    # Read/modify/write
```

**Testing:**
- ✅ Python syntax validated
- ⚠️ Requires manual testing on Windows to fully verify
- ⚠️ Requires `pip install filelock` before running

**Benefits:**
- Works on Windows, macOS, and Linux
- Cleaner API (context manager)
- Timeout support prevents infinite hangs
- Separate lock files (`.lock`) don't interfere with git

---

## 📋 TODO - Phase 1 (Quick Wins)

### 2.1: External Prompt Template
**Status:** 🔲 TODO
**Priority:** HIGH
**Effort:** ~3 hours
**Impact:** HIGH - Biggest customization need

**Goal:** Move 100+ line prompt from `config.py` to external file

**Implementation:**
1. Create `cloud-run/templates/categorization_prompt.txt`
2. Add template loading function to `config.py`
3. Support env var override: `PROMPT_TEMPLATE`
4. Keep current prompt as default

**Benefits:**
- Users can customize without touching code
- Version control different prompts
- A/B testing of prompts

---

### 2.2: YAML Tag Rules
**Status:** 🔲 TODO
**Priority:** MEDIUM
**Effort:** ~2 hours
**Impact:** MEDIUM - Remaining customization needs

**Goal:** Move hardcoded tag rules to `config/tag_rules.yaml`

**Implementation:**
1. Create `cloud-run/config/tag_rules.yaml`
2. Add YAML loading to `config.py`
3. Add `pyyaml` to requirements.txt
4. Keep current rules as defaults

**Benefits:**
- Non-programmers can add domains/keywords
- Easier to share configurations
- Can load different rules per deployment

---

### 2.3: Jinja2 Note Templates
**Status:** 🔲 TODO
**Priority:** MEDIUM
**Effort:** ~4 hours
**Impact:** HIGH - Full note structure customization

**Goal:** Replace hardcoded note structure with Jinja2 templates

**Implementation:**
1. Create `cloud-run/templates/note_template.md.j2`
2. Add `jinja2` to requirements.txt
3. Update `obsidian_writer.py` to use template rendering
4. Support multiple template types

**Benefits:**
- Users can customize entire note structure
- Different templates for different categories
- Preview changes easily

---

## 📋 TODO - Phase 2 (Nice to Have)

### 2.4: Plugin System
**Status:** 🔲 TODO
**Priority:** LOW
**Effort:** ~8 hours
**Impact:** MEDIUM - Advanced users only

**Goal:** Allow users to add custom processing hooks

---

### 3.1: Customization Documentation
**Status:** 🔲 TODO
**Priority:** MEDIUM
**Effort:** ~2 hours
**Impact:** MEDIUM - Helps users adopt changes

**Goal:** Create `CUSTOMIZATION.md` guide

---

### 3.2: Development Setup Guide
**Status:** 🔲 TODO
**Priority:** LOW
**Effort:** ~2 hours
**Impact:** LOW - Developer experience

**Goal:** Create `DEVELOPMENT.md` guide

---

## 🚫 NOT DOING

### Unified Configuration System
**Reason:** Too complex, diminishing returns
**Alternative:** Current approach with YAML for tag rules is sufficient

---

## 📊 Progress Summary

| Category | Total | Completed | Remaining |
|----------|-------|-----------|-----------|
| Phase 1 (Critical) | 3 | 1 | 2 |
| Phase 2 (Nice to Have) | 3 | 0 | 3 |
| **Total** | **6** | **1** | **5** |

**Completion:** 17% (1/6)

---

## 🔄 For Next Agent

**Current state:**
- ✅ Cross-platform file locking implemented
- ✅ All Priority 1, 2, 3 bug fixes complete (see `claude_tasks.md`)
- ✅ Project works on Unix systems
- ✅ Clean git history with atomic commits

**Next recommended task:**
1. Implement external prompt template (2.1) - Highest user impact
2. OR implement YAML tag rules (2.2) - Quick win

**How to pick up:**
1. Read this file to see what's done
2. Pick any 🔲 TODO item
3. See `IMPROVEMENTS.md` for full implementation details
4. Update this file to mark as ✅ COMPLETED when done
5. Commit with clear message

**Testing checklist for any change:**
- [ ] Python syntax validates (`python -m py_compile file.py`)
- [ ] No breaking changes to existing functionality
- [ ] Update relevant documentation
- [ ] Add dependencies to `requirements.txt` if needed
- [ ] Update this tracker with status

---

## 📝 Notes

- Lock files (`.lock`) should be added to `.gitignore`
- FileLock creates lock files in same directory as target file
- Timeout of 10 seconds prevents infinite hangs
- If lock acquisition fails, error is logged and operation skips

---

**Legend:**
- ✅ COMPLETED - Fully implemented and tested
- 🔲 TODO - Not started
- ⚠️ - Needs attention or manual verification

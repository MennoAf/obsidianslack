# ObsidianSlack — Bug & Security Fix Guide

This document contains all identified issues from a full code review, organized by priority. Use this as a task list for a fresh Claude Code session.

Project root: `/Users/jasonbauman/Documents/code_projects/ObsidianSlack/`

**Important:** After 2026-02-06 restructure, all Python files referenced below are in `cloud-run/` directory. When fixing issues, prepend `cloud-run/` to file paths (e.g., `main.py` → `cloud-run/main.py`).

---

## ✅ Completed (Do Not Redo)

### Priority 1 Security Fixes — Completed in commit `73334d3` (2026-02-06)

All 8 Priority 1 security vulnerabilities have been fixed:

1. ✅ **Created `.dockerignore`** - Prevents secrets from being copied into Docker images
2. ✅ **Moved signature verification before JSON parsing** - Fixed authentication bypass in `main.py`
3. ✅ **Fixed Flask debug mode RCE risk** - Debug mode now binds to localhost only
4. ✅ **Added non-root user to Docker container** - Container runs as `appuser`, not root
5. ✅ **Removed `--allow-unauthenticated` from Cloud Run** - Improved infrastructure security
6. ✅ **Validated `CLAUDE_FOLDER_NAME` against path traversal** - Prevents directory escape in `config.py`
7. ✅ **Sanitized file paths in `github_sync.py`** - Prevents path traversal attacks
8. ✅ **Removed sensitive data from `/health` endpoint** - No longer exposes internal paths

**Do not reimplement these fixes** - they are already in the codebase.

---

## Priority 1: Security — Must Fix ~~(COMPLETED - See Above)~~

### 1.1 ~~Create `.dockerignore`~~ ✅ COMPLETED

**Why:** `COPY . .` in `Dockerfile:19` copies `.env`, `.git/`, logs, and secrets into the Docker image.

**Fix:** Create `.dockerignore` at project root:

```
.env
env.yaml
.git
.gitignore
__pycache__
venv/
brain_dump.log
*.md
!README.md
.claude/
.DS_Store
```

---

### 1.2 ~~Move signature verification before body parsing (`main.py`)~~ ✅ COMPLETED

**Why:** At `main.py:44-55`, `request.json` is parsed and the `url_verification` challenge is returned (line 47-49) BEFORE `slack_handler.verify_request()` runs on line 55. This bypasses authentication entirely for `url_verification` requests.

**Fix:** Restructure the `/slack/events` handler so that signature verification happens FIRST, before any `request.json` parsing or logic. The raw body (`request.get_data()`) is needed for HMAC verification anyway. Only after verification passes should you parse JSON and branch on event type.

Pseudocode:
```python
@app.route('/slack/events', methods=['POST'])
def slack_events():
    # 1. Verify signature FIRST (uses raw body)
    raw_body = request.get_data()
    if not slack_handler.verify_request(
        request.headers.get('X-Slack-Request-Timestamp', ''),
        raw_body.decode('utf-8'),
        request.headers.get('X-Slack-Signature', '')
    ):
        return jsonify({'error': 'Invalid request'}), 403

    # 2. THEN parse JSON
    data = request.json

    # 3. Handle url_verification
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge', '')})

    # 4. Process events...
```

Also use `.get('challenge', '')` instead of `data['challenge']` to avoid `KeyError`.

---

### 1.3 ~~Fix Flask debug mode RCE risk (`main.py:190-194`)~~ ✅ COMPLETED

**Why:** When `DEBUG_MODE=True`, the Werkzeug interactive debugger is exposed on `0.0.0.0` — this is remote code execution.

**Fix:** Never use Flask's debug mode with `host='0.0.0.0'`. Change the `app.run()` call:

```python
app.run(
    host='0.0.0.0',
    port=config.FLASK_PORT,
    debug=False  # Never enable debug in production; use env var only for local dev on 127.0.0.1
)
```

Or conditionally bind to localhost when debug is on:

```python
host = '127.0.0.1' if config.DEBUG_MODE else '0.0.0.0'
app.run(host=host, port=config.FLASK_PORT, debug=config.DEBUG_MODE)
```

---

### 1.4 ~~Add `USER` directive to `Dockerfile`~~ ✅ COMPLETED

**Why:** Container runs as root. If compromised, attacker has root inside the container.

**Fix:** Add before `CMD`:

```dockerfile
RUN useradd -m appuser
USER appuser
```

---

### 1.5 ~~Remove `--allow-unauthenticated` from `cloudbuild.yaml:24`~~ ✅ COMPLETED

**Why:** The Cloud Run service is publicly accessible to the entire internet. Even though Slack signature verification exists at the app layer, defense-in-depth says infrastructure should also restrict access.

**Fix:** Remove `--allow-unauthenticated` from the `gcloud run deploy` command. Configure Slack to authenticate via IAM, or at minimum document that the app-layer signature check is the sole auth gate and ensure it is airtight (see fix 1.2).

---

### 1.6 ~~Validate `CLAUDE_FOLDER_NAME` against path traversal (`config.py:23-24`)~~ ✅ COMPLETED

**Why:** If `CLAUDE_FOLDER_NAME` is set to `../../etc`, `CLAUDE_FOLDER_PATH` escapes the vault directory.

**Fix:** After computing `CLAUDE_FOLDER_PATH`, verify it is a child of `OBSIDIAN_VAULT_PATH`:

```python
CLAUDE_FOLDER_PATH = OBSIDIAN_VAULT_PATH / CLAUDE_FOLDER_NAME
# Add to validate_config():
if not str(CLAUDE_FOLDER_PATH.resolve()).startswith(str(OBSIDIAN_VAULT_PATH.resolve())):
    raise ValueError("CLAUDE_FOLDER_NAME must not escape OBSIDIAN_VAULT_PATH")
```

---

### 1.7 ~~Sanitize `folder`/`filename` in `github_sync.py` (lines 66, 125, 170)~~ ✅ COMPLETED

**Why:** `file_path = f"{folder}/{filename}"` — unsanitized inputs could write to unexpected locations.

**Fix:** Add a helper method to the `GitHubSync` class:

```python
def _safe_path(self, folder: str, filename: str) -> str:
    """Build a repo-relative path, rejecting traversal attempts."""
    import posixpath
    path = posixpath.normpath(f"{folder}/{filename}")
    if path.startswith('..') or path.startswith('/'):
        raise ValueError(f"Invalid path: {path}")
    return path
```

Use it everywhere `file_path` is constructed.

---

### 1.8 ~~Remove `/health` endpoint info disclosure (`main.py:154-161`)~~ ✅ COMPLETED

**Why:** Unauthenticated endpoint exposes filesystem path and Slack channel ID.

**Fix:** Return only status, no internal details:

```python
return jsonify({'status': 'healthy'}), 200
```

---

## Priority 2: Bugs — Should Fix

### 2.1 ~~Fix JSON extraction regexes (`claude_processor.py:122-131`)~~ ✅ COMPLETED

**Problem 1 — Line 122:** Non-greedy `*?` stops at the first `}`, breaking on nested JSON:
```python
r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
```

**Problem 2 — Line 128:** Greedy `*` matches from first `{` to last `}` in the entire text:
```python
r'(\{[\s\S]*\})'
```

**Fix:** Replace both with a proper brace-matching approach. One option is to find `{` and use `json.loads()` attempts at progressively longer substrings. A simpler fix:

```python
def _extract_json_from_markdown(self, text: str) -> dict:
    import json, re

    # Try code-fenced JSON first
    fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Find all { positions and try parsing from each
    for i, char in enumerate(text):
        if char == '{':
            try:
                obj = json.loads(text[i:])
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                # Try to find the matching } by progressively trimming
                depth = 0
                for j in range(i, len(text)):
                    if text[j] == '{':
                        depth += 1
                    elif text[j] == '}':
                        depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[i:j+1])
                        except json.JSONDecodeError:
                            break

    raise ValueError("No valid JSON found in response")
```

---

### 2.2 ~~Sanitize ALL YAML frontmatter values (`obsidian_writer.py:149-161`)~~ ✅ COMPLETED

**Why:** Only `title` uses `sanitize_for_yaml()`. `category`, `source_domain`, `priority`, `slack_ts` are raw.

**Fix:** Apply `sanitize_for_yaml()` to every value in the frontmatter block. In `_generate_frontmatter()`:

```python
frontmatter += f"category: {sanitize_for_yaml(category)}\n"
frontmatter += f"slack_ts: {sanitize_for_yaml(str(slack_ts))}\n"
frontmatter += f"source_domain: {sanitize_for_yaml(source_domain)}\n"
frontmatter += f"priority: {sanitize_for_yaml(str(priority))}\n"
```

Import `sanitize_for_yaml` from `utils` if not already imported.

---

### 2.3 ~~Fix `sanitize_for_yaml` to handle newlines and backslashes (`utils.py:267-282`)~~ ✅ COMPLETED

**Why:** Newlines bypass the special character check. Backslashes aren't escaped.

**Fix:**

```python
def sanitize_for_yaml(value: str) -> str:
    if not isinstance(value, str):
        value = str(value)
    # Always quote if contains newlines, special chars, or is empty
    special = [':', '#', '-', '[', ']', '{', '}', '|', '>', '*', '&', '!', '%', '?', '\n', '\r']
    if any(char in value for char in special) or not value.strip():
        value = value.replace('\\', '\\\\')
        value = value.replace('"', '\\"')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        return f'"{value}"'
    return value
```

---

### 2.4 ~~Sanitize tags for YAML (`utils.py:214-233`)~~ ✅ COMPLETED

**Why:** Tags like `source/evil: injected` are placed into YAML as-is, parsed as mappings.

**Fix:** In `format_tags_for_frontmatter`, quote tags containing special characters:

```python
for tag in sorted(tags):
    tag = tag.lstrip('#')
    if any(c in tag for c in [':', '#', '[', ']', '{', '}', '!', '&', '*']):
        tag = f'"{tag}"'
    formatted_tags.append(f"  - {tag}")
```

---

### 2.5 ~~Filter message subtypes with a whitelist (`slack_handler.py:195-197`)~~ ✅ COMPLETED

**Why:** Only `message_changed` and `message_deleted` are blocked. `channel_join`, `channel_topic`, etc. still get processed as user messages.

**Fix:** Replace the blacklist with a whitelist:

```python
# Only process regular messages (no subtype) and bot messages are already filtered above
if event.get('subtype') is not None:
    logger.debug(f"Ignoring message subtype: {event.get('subtype')}")
    return None
```

---

### 2.6 ~~Add event deduplication (`main.py`)~~ ✅ COMPLETED

**Why:** Synchronous processing means Slack retries (3s timeout) create duplicate notes.

**Fix:** Add a simple in-memory set to track processed event IDs:

```python
import threading

_processed_events = set()
_events_lock = threading.Lock()

def _is_duplicate(event_id: str) -> bool:
    with _events_lock:
        if event_id in _processed_events:
            return True
        _processed_events.add(event_id)
        # Keep set from growing forever
        if len(_processed_events) > 10000:
            _processed_events.clear()
        return False
```

In the handler, check `data.get('event_id')` before processing. Also, immediately return `200 OK` and process asynchronously if possible.

---

### 2.7 ~~Handle empty Claude response (`claude_processor.py:79`)~~ ✅ COMPLETED

**Why:** `response.content[0].text` crashes with `IndexError` if content list is empty.

**Fix:**

```python
if not response.content:
    logger.error("Claude returned empty response")
    return self._create_fallback_result(message_text)
response_text = response.content[0].text
```

---

### 2.8 ~~Fix domain cleaning (`tag_generator.py:78-84`)~~ ✅ COMPLETED

**Why:** Naive `.replace('.com', '')` mangles domains like `common.community.com` → `common.munity`.

**Fix:** Only strip the TLD from the end:

```python
import re as _re

def _clean_domain(self, domain: str) -> str:
    domain = _re.sub(r'^www\.', '', domain)
    domain = _re.sub(r'\.(com|org|io|net|dev|co|ai|edu|gov)$', '', domain)
    return domain
```

---

### 2.9 ~~Guard `int()` conversions in `config.py` (lines 14, 27)~~ ✅ COMPLETED

**Why:** Non-numeric env var values crash the app at import time with unhelpful `ValueError`.

**Fix:**

```python
def _safe_int(env_var: str, default: int) -> int:
    val = os.getenv(env_var, str(default))
    try:
        return int(val)
    except ValueError:
        raise ValueError(f"Environment variable {env_var} must be an integer, got: '{val}'")

MAX_TOKENS = _safe_int("MAX_TOKENS", 4096)
FLASK_PORT = _safe_int("FLASK_PORT", 5000)
```

---

### 2.10 ~~Fix race condition on parent note updates (`obsidian_writer.py:296-313`)~~ ✅ COMPLETED

**Why:** Concurrent read-modify-write with no locking. Two replies to the same thread = data loss.

**Fix:** Use file locking:

```python
import fcntl

def _append_reply_to_parent(self, parent_filename, reply_line):
    # ... find parent_path ...
    with open(parent_path, 'r+', encoding='utf-8') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            content = f.read()
            if "## Replies" not in content:
                content += "\n\n## Replies\n"
            content += reply_line
            f.seek(0)
            f.write(content)
            f.truncate()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
```

---

### 2.11 ~~Fix reply appended to wrong location (`obsidian_writer.py:299-310`)~~ ✅ COMPLETED

**Why:** Replies are always appended to the end of the file, not within the "## Replies" section.

**Fix:** Insert the reply line right after `## Replies\n` instead of appending to the end. Find the position of the section header and insert there.

---

## Priority 3: Operational — Nice to Fix

### 3.1 ~~Set gunicorn timeout (`Dockerfile:32`)~~ ✅ COMPLETED

Change `--timeout 0` to `--timeout 120` (or similar).

### 3.2 ~~Fix `parse_slack_timestamp` error handling (`utils.py:236-248`)~~ ✅ COMPLETED

Wrap `float(ts)` in try/except, return `None` or raise a clear error on invalid input.

### 3.3 ~~Fix filename collision / silent overwrite (`utils.py:44-74`, `obsidian_writer.py:262`)~~ ✅ COMPLETED

In `generate_filename` or `_write_file`, check if the file already exists and append a counter (e.g., `_2`, `_3`) if so.

### 3.4 Remove unused import (`tag_generator.py:6`)

`extract_code_blocks` is imported but never used. Remove it.

### 3.5 Add `--service-account`, `--max-instances`, `--memory` to `cloudbuild.yaml`

The Cloud Run deploy command should specify resource limits and a dedicated service account.

### 3.6 Pin Docker base image (`Dockerfile:2`)

Use a digest-pinned image for reproducibility: `python:3.11-slim@sha256:<hash>`.

### 3.7 Move inline imports to module level (`claude_processor.py:120, 200`)

`import re` and `from utils import truncate_text` are inside methods. Move to the top of the file so import errors surface at startup.

### 3.8 Add rate limiting / retry logic for Claude API (`claude_processor.py:67`)

No app-level guard against API cost explosion if Slack channel gets flooded. Consider a simple token bucket or queue.

---

## File Reference

**Note:** After project restructure (2026-02-06), all Python files are now in `cloud-run/` directory.

| File | Lines of Code | Primary Role |
|------|--------------|--------------|
| `cloud-run/main.py` | ~194 | Flask app, event routing |
| `cloud-run/config.py` | ~240 | Env vars, prompts, validation |
| `cloud-run/slack_handler.py` | ~197 | Slack API client, signature verification |
| `cloud-run/claude_processor.py` | ~216 | Claude API, JSON extraction |
| `cloud-run/obsidian_writer.py` | ~343 | File writing, frontmatter, replies |
| `cloud-run/tag_generator.py` | ~170 | Tag extraction from content |
| `cloud-run/utils.py` | ~282 | Helpers: YAML, URLs, filenames, timestamps |
| `cloud-run/github_sync.py` | ~248 | GitHub API for Cloud Run deployment |
| `cloud-run/Dockerfile` | ~32 | Container build |
| `cloud-run/cloudbuild.yaml` | ~27 | GCP Cloud Build pipeline |
| `local-sync/sync_from_github.sh` | ~40 | Unix/macOS sync script |
| `local-sync/sync_from_github.ps1` | ~60 | Windows PowerShell sync script |

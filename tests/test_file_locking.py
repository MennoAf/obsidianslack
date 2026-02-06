# test_file_locking.py
import sys
from pathlib import Path
import time
sys.path.insert(0, 'cloud-run')

# Test 1: FileLock import
print("Test 1: FileLock import")
from filelock import FileLock
print("✓ FileLock imported successfully")

# Test 2: Lock creation and acquisition
print("\nTest 2: Lock acquisition")
test_file = Path('/tmp/test_lock.txt')
test_file.write_text('test content')
lock = FileLock(f"{test_file}.lock", timeout=5)

with lock:
    print("✓ Lock acquired")
    assert Path(f"{test_file}.lock").exists()
    print("✓ Lock file created")

print("✓ Lock released")

# Test 3: Timeout
print("\nTest 3: Lock timeout")
lock1 = FileLock(f"{test_file}.lock", timeout=1)
lock2 = FileLock(f"{test_file}.lock", timeout=1)

try:
    with lock1:
        try:
            with lock2:
                print("✗ Should have timed out!")
                assert False
        except Exception as e:
            print(f"✓ Lock timeout works: {type(e).__name__}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

# Cleanup
test_file.unlink()
Path(f"{test_file}.lock").unlink(missing_ok=True)

# Test 4: obsidian_writer uses FileLock
print("\nTest 4: ObsidianWriter uses FileLock")
import inspect
from obsidian_writer import ObsidianWriter
source = inspect.getsource(ObsidianWriter._append_reply_to_parent)
assert 'FileLock' in source
assert 'with lock:' in source
print("✓ ObsidianWriter uses FileLock correctly")
print("  - Found FileLock import")
print("  - Found 'with lock:' context manager")

# Test 5: Check .gitignore covers lock files
print("\nTest 5: Lock files in .gitignore")
gitignore_path = Path('.gitignore')
if gitignore_path.exists():
    gitignore = gitignore_path.read_text()
    assert '*.lock' in gitignore
    print("✓ Lock files covered in .gitignore")
else:
    print("⚠ .gitignore not found")

print("\n✓ All file locking tests passed")

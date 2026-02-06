# test_tag_generator.py
import sys
sys.path.insert(0, 'cloud-run')

# Test 1: TagGenerator initialization
print("Test 1: TagGenerator initialization")
from tag_generator import TagGenerator
import config
tagger = TagGenerator()
print("✓ TagGenerator initialized")

# Test 2: Domain tagging
print("\nTest 2: Domain-based tagging")
message_with_github = "Check this out: https://github.com/user/repo"
tags = tagger.generate_tags(
    message_text=message_with_github,
    claude_base_tags=[],
    code_languages=[],
    is_question=False
)
assert any('github' in tag.lower() for tag in tags), f"Expected github tag in {tags}"
print(f"✓ Domain tags: {[t for t in tags if 'github' in t.lower()]}")
print(f"  Total tags: {len(tags)}")

# Test 3: Code language tagging
print("\nTest 3: Code language tagging")
tags = tagger.generate_tags(
    message_text="Some code here",
    claude_base_tags=[],
    code_languages=['python', 'javascript'],
    is_question=False
)
assert any('python' in tag.lower() for tag in tags), f"Expected python tag in {tags}"
print(f"✓ Language tags: {[t for t in tags if 'python' in t.lower() or 'javascript' in t.lower()]}")
print(f"  Total tags: {len(tags)}")

# Test 4: Keyword tagging
print("\nTest 4: Keyword-based tagging")
message_with_bug = "Found a bug in the API"
tags = tagger.generate_tags(
    message_text=message_with_bug,
    claude_base_tags=[],
    code_languages=[],
    is_question=False
)
# Should get bug-related tags from keywords
print(f"✓ Keyword tags generated: {len(tags)} tags")
print(f"  Tags: {tags}")

# Test 5: Tag deduplication
print("\nTest 5: Tag deduplication")
tags = tagger.generate_tags(
    message_text="test",
    claude_base_tags=['code', 'dev'],
    code_languages=['python'],  # Also adds 'code' tag
    is_question=False
)
assert len(tags) == len(set(tags)), f"Duplicate tags found! {tags}"
print(f"✓ No duplicate tags: {tags}")

# Test 6: Question tagging
print("\nTest 6: Question tagging")
tags = tagger.generate_tags(
    message_text="How do I fix this?",
    claude_base_tags=[],
    code_languages=[],
    is_question=True
)
assert 'question' in tags, f"Expected 'question' tag in {tags}"
print(f"✓ Question tag added: {tags}")

# Test 7: Multiple URLs from different domains
print("\nTest 7: Multiple domain tags")
message_multi_urls = "See https://github.com/repo and https://stackoverflow.com/questions/123"
tags = tagger.generate_tags(
    message_text=message_multi_urls,
    claude_base_tags=[],
    code_languages=[],
    is_question=False
)
print(f"✓ Multiple domain tags: {tags}")
print(f"  Total tags: {len(tags)}")

print("\n✓ All tag generator tests passed")

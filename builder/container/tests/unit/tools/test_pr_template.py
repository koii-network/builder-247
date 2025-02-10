"""Tests for PR template validation."""

from src.tools.pr_template import validate_pr_description


def test_valid_pr_description():
    """Test validation of a valid PR description."""
    description = """# Pull Request Description

## Type of Change

[x] New feature

## Description

This PR adds a new feature for handling PR templates.

## Related Issues

#123

## Testing Done

Added unit tests for PR template validation.

## Checklist

[x] I have tested my changes
[x] I have updated the documentation
[x] My changes generate no new warnings
[x] I have added tests that prove my fix/feature works
"""
    result = validate_pr_description(description)
    assert result["valid"]
    assert len(result["errors"]) == 0


def test_missing_sections():
    """Test validation of a PR description with missing sections."""
    description = """# Pull Request Description

## Type of Change

[x] New feature

## Description

This PR adds a new feature.
"""
    result = validate_pr_description(description)
    assert not result["valid"]
    assert "Missing required section: Testing Done" in result["errors"]
    assert "Missing required section: Related Issues" in result["errors"]
    assert "Missing required section: Checklist" in result["errors"]


def test_no_type_selected():
    """Test validation of a PR description with no type selected."""
    description = """# Pull Request Description

## Type of Change

[ ] Bug fix
[ ] New feature

## Description

This PR adds a new feature.

## Related Issues

#123

## Testing Done

Added unit tests.

## Checklist

[x] I have tested my changes
"""
    result = validate_pr_description(description)
    assert not result["valid"]
    assert "Must select at least one Type of Change" in result["errors"]


def test_short_description():
    """Test validation of a PR description with a too-short description."""
    description = """# Pull Request Description

## Type of Change

[x] New feature

## Description

Too short.

## Related Issues

#123

## Testing Done

Added unit tests.

## Checklist

[x] I have tested my changes
"""
    result = validate_pr_description(description)
    assert not result["valid"]
    assert "Description section is too short (minimum 10 words)" in result["errors"]
    assert "Testing Done section is too short (minimum 5 words)" in result["errors"]


def test_no_testing_confirmation():
    """Test validation of a PR description without testing confirmation."""
    description = """# Pull Request Description

## Type of Change

[x] New feature

## Description

This PR adds a new feature for handling PR templates.

## Related Issues

#123

## Testing Done

Added unit tests.

## Checklist

[ ] I have tested my changes
"""
    result = validate_pr_description(description)
    assert not result["valid"]
    assert "Must confirm testing in the checklist" in result["errors"]

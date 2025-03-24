"""
Linux compatibility tests for the Anthropic client tools.
Tests file permissions, path handling, and environment setup.
"""

import os
import stat
import pytest
from pathlib import Path


def test_script_permissions():
    """Test that verification scripts have correct permissions."""
    script_path = Path("testing/verify_hello_world.py")

    # Check script exists
    assert script_path.exists(), f"Script not found: {script_path}"

    # Check script is executable
    mode = os.stat(script_path).st_mode
    is_executable = bool(mode & stat.S_IXUSR)
    assert is_executable, f"Script {script_path} is not executable"

    # Check script has correct shebang
    with open(script_path) as f:
        first_line = f.readline().strip()
        assert first_line.startswith("#!/"), f"Script {script_path} missing shebang"
        assert (
            "python" in first_line.lower()
        ), f"Script {script_path} has incorrect interpreter"


def test_output_directory_permissions():
    """Test that output directory has correct permissions."""
    output_dir = Path("testing/output")

    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check directory exists
    assert output_dir.exists(), f"Output directory not found: {output_dir}"
    assert output_dir.is_dir(), f"Path is not a directory: {output_dir}"

    # Check directory is writable
    test_file = output_dir / "permission_test.txt"
    try:
        test_file.write_text("test")
        test_file.unlink()  # Clean up
    except PermissionError:
        pytest.fail(f"Output directory {output_dir} is not writable")


def test_path_handling():
    """Test path handling compatibility."""
    # Test relative imports
    import sys

    project_root = Path(__file__).parent.parent.parent
    assert project_root in [
        Path(p) for p in sys.path
    ], "Project root not in Python path"

    # Test importing client from different directory
    os.chdir(project_root)
    try:
        from src.anthropic_client import AnthropicClient

        assert AnthropicClient is not None
    except ImportError as e:
        pytest.fail(f"Failed to import client: {e}")

"""
Tests for file permission handling and error cases.
Part of [TODO-14] File Permission Error Handling.
"""
import os
import stat
import pytest
from pathlib import Path
from src.tools.filesystem import FileSystemTools, PermissionError

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path

@pytest.fixture
def read_only_file(temp_dir):
    """Create a read-only file for testing."""
    file_path = temp_dir / "readonly.txt"
    file_path.write_text("test content")
    # Remove write permission
    os.chmod(file_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return file_path

@pytest.fixture
def no_access_dir(temp_dir):
    """Create a directory without read/write access."""
    dir_path = temp_dir / "noaccess"
    dir_path.mkdir()
    # Remove all permissions
    os.chmod(dir_path, 0)
    return dir_path

def test_write_to_readonly_file(read_only_file):
    """Test writing to a read-only file."""
    with pytest.raises(PermissionError) as exc_info:
        FileSystemTools.write_file(read_only_file, "new content")
    assert "No write permission for file" in str(exc_info.value)
    assert str(read_only_file) in str(exc_info.value)
    # Verify content wasn't changed
    assert read_only_file.read_text() == "test content"

def test_read_from_noaccess_dir(no_access_dir):
    """Test reading from a directory without access."""
    test_file = no_access_dir / "test.txt"
    with pytest.raises(PermissionError) as exc_info:
        FileSystemTools.read_file(test_file)
    assert "No access to parent directory" in str(exc_info.value)
    assert str(no_access_dir) in str(exc_info.value)

def test_list_noaccess_dir(no_access_dir):
    """Test listing a directory without access."""
    with pytest.raises(PermissionError) as exc_info:
        FileSystemTools.list_directory(no_access_dir)
    assert "No read permission for directory" in str(exc_info.value)
    assert str(no_access_dir) in str(exc_info.value)

def test_create_file_in_readonly_dir(temp_dir):
    """Test creating a file in a read-only directory."""
    # Make directory read-only
    os.chmod(temp_dir, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    
    test_file = temp_dir / "newfile.txt"
    with pytest.raises(PermissionError) as exc_info:
        FileSystemTools.write_file(test_file, "test content")
    assert "No write permission for directory" in str(exc_info.value)
    assert str(temp_dir) in str(exc_info.value)
    # Use safe_exists to check file doesn't exist
    assert not FileSystemTools.safe_exists(test_file)

def test_execute_without_permission(temp_dir):
    """Test executing a script without execute permission."""
    script_path = temp_dir / "test_script.py"
    script_path.write_text("#!/usr/bin/env python3\nprint('test')")
    
    # Remove execute permission
    os.chmod(script_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    
    with pytest.raises(PermissionError) as exc_info:
        FileSystemTools.check_file_executable(script_path)
    assert "No execute permission for file" in str(exc_info.value)
    assert str(script_path) in str(exc_info.value) 
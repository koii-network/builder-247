import os
import pytest
import tempfile
from pathlib import Path

def test_write_to_readonly_file():
    """Test writing to a read-only file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test")
    
    # Make file read-only
    os.chmod(f.name, 0o444)
    
    try:
        with pytest.raises(PermissionError, match=f"No write permission for file {f.name}"):
            with open(f.name, 'w') as f2:
                f2.write("test")
    finally:
        os.chmod(f.name, 0o644)
        os.unlink(f.name)

def test_read_from_noaccess_dir():
    """Test reading from a directory without access."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "noaccess"
        test_dir.mkdir()
        test_file = test_dir / "test.txt"
        test_file.write_text("test")
        
        # Remove all permissions
        os.chmod(test_dir, 0o000)
        
        try:
            with pytest.raises(PermissionError, match=f"No read permission for directory {test_dir}"):
                test_file.read_text()
        finally:
            os.chmod(test_dir, 0o755)

def test_list_noaccess_dir():
    """Test listing a directory without access."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "noaccess"
        test_dir.mkdir()
        
        # Remove all permissions
        os.chmod(test_dir, 0o000)
        
        try:
            with pytest.raises(PermissionError, match=f"No read permission for directory {test_dir}"):
                list(test_dir.iterdir())
        finally:
            os.chmod(test_dir, 0o755)

def test_create_file_in_readonly_dir():
    """Test creating a file in a read-only directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Make directory read-only
        os.chmod(test_dir, 0o555)
        
        try:
            with pytest.raises(PermissionError, match=f"No write permission for directory {test_dir}"):
                (test_dir / "newfile.txt").write_text("test")
        finally:
            os.chmod(test_dir, 0o755)

def test_execute_without_permission():
    """Test executing a file without execute permission."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("#!/bin/sh\necho test")
    
    # Remove execute permission
    os.chmod(f.name, 0o644)
    
    try:
        with pytest.raises(PermissionError, match=f"No execute permission for file {f.name}"):
            os.execl(f.name, f.name)
    finally:
        os.unlink(f.name) 
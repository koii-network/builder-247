"""Tests for file operations module."""

import os
import pytest
import src.tools.file_operations as fo


def test_write_and_read_file(tmp_path):
    """Test that we can write to a file and read it back."""
    test_file = tmp_path / "test.txt"
    test_content = "Hello, World!"

    # Write the file
    write_result = fo.write_file(str(test_file), test_content)
    assert write_result["success"]

    # Read the file
    read_result = fo.read_file(str(test_file))
    assert read_result["success"]
    assert read_result["content"] == test_content


def test_write_file_with_path_creation(tmp_path):
    """Test that write_file creates intermediate directories."""
    test_file = tmp_path / "subdir" / "test.txt"
    test_content = "Hello from subdir!"

    write_result = fo.write_file(str(test_file), test_content)
    assert write_result["success"]
    assert os.path.exists(test_file)

    read_result = fo.read_file(str(test_file))
    assert read_result["success"]
    assert read_result["content"] == test_content


def test_read_nonexistent_file(tmp_path):
    """Test reading a file that doesn't exist."""
    test_file = tmp_path / "nonexistent.txt"

    result = fo.read_file(str(test_file))
    assert not result["success"]
    assert "File not found" in result["error"]


def test_write_file_invalid_path():
    """Test writing to an invalid path."""
    result = fo.write_file("", "test content")
    assert not result["success"]
    assert "Error writing file" in result["error"]


def test_copy_file(tmp_path):
    """Test copying a file."""
    source = tmp_path / "source.txt"
    destination = tmp_path / "subdir" / "destination.txt"
    test_content = "Copy me!"

    # Create source file
    write_result = fo.write_file(str(source), test_content)
    assert write_result["success"]

    # Copy the file
    copy_result = fo.copy_file(str(source), str(destination))
    assert copy_result["success"]

    # Verify the copy
    read_result = fo.read_file(str(destination))
    assert read_result["success"]
    assert read_result["content"] == test_content


def test_move_file(tmp_path):
    """Test moving a file."""
    source = tmp_path / "source.txt"
    destination = tmp_path / "subdir" / "moved.txt"
    test_content = "Move me!"

    # Create source file
    write_result = fo.write_file(str(source), test_content)
    assert write_result["success"]

    # Move the file
    move_result = fo.move_file(str(source), str(destination))
    assert move_result["success"]

    # Verify the move
    assert not os.path.exists(source)
    read_result = fo.read_file(str(destination))
    assert read_result["success"]
    assert read_result["content"] == test_content


def test_rename_file(tmp_path):
    """Test renaming a file."""
    source = tmp_path / "original.txt"
    destination = tmp_path / "renamed.txt"
    test_content = "Rename me!"

    # Create source file
    write_result = fo.write_file(str(source), test_content)
    assert write_result["success"]

    # Rename the file
    rename_result = fo.rename_file(str(source), str(destination))
    assert rename_result["success"]

    # Verify the rename
    assert not os.path.exists(source)
    read_result = fo.read_file(str(destination))
    assert read_result["success"]
    assert read_result["content"] == test_content


def test_delete_file(tmp_path):
    """Test deleting a file."""
    test_file = tmp_path / "delete_me.txt"
    test_content = "Delete me!"

    # Create file
    write_result = fo.write_file(str(test_file), test_content)
    assert write_result["success"]

    # Delete the file
    delete_result = fo.delete_file(str(test_file))
    assert delete_result["success"]

    # Verify the deletion
    assert not os.path.exists(test_file)


def test_operations_with_nonexistent_source(tmp_path):
    """Test operations with a nonexistent source file."""
    source = tmp_path / "nonexistent.txt"
    destination = tmp_path / "destination.txt"

    # Try to copy
    copy_result = fo.copy_file(str(source), str(destination))
    assert not copy_result["success"]
    assert "Source file not found" in copy_result["error"]

    # Try to move
    move_result = fo.move_file(str(source), str(destination))
    assert not move_result["success"]
    assert "Source file not found" in move_result["error"]

    # Try to rename
    rename_result = fo.rename_file(str(source), str(destination))
    assert not rename_result["success"]
    assert "Source file not found" in rename_result["error"]

    # Try to delete
    delete_result = fo.delete_file(str(source))
    assert not delete_result["success"]
    assert "File not found" in delete_result["error"]# Replace 'your_module' with the actual module name

def test_list_files_in_directory(tmp_path):
    subdir = tmp_path / "subdir"
    subdir.mkdir()

        # Create files in the temporary directory
    (tmp_path / "file1.txt").write_text("Content of file 1")
    (tmp_path / "file2.txt").write_text("Content of file 2")
    (subdir / "file3.txt").write_text("Content of file 3")
    (subdir / "file4.txt").write_text("Content of file 4")

    # Call the function with the temporary directory
    files = fo.list_files(tmp_path)

    print(files)

    # Expected relative paths based on the temp_path
    expected_files = [
        "file1.txt",
        "file2.txt",
        "subdir/file3.txt",
        "subdir/file4.txt"
    ]

    # Check if the returned list matches the expected list
    assert sorted(files) == sorted(expected_files)

def test_list_files_in_empty_directory(tmp_path):
    # Create a temporary directory using tempfile

    # Call the function with an empty directory
    files = fo.list_files(tmp_path)

    # Expect an empty list
    assert files == []

def test_list_files_in_nonexistent_directory():
    # Call the function with a nonexistent directory
    with pytest.raises(FileNotFoundError):
        fo.list_files("nonexistent_directory")

def test_copy_file_with_absolute_paths(tmp_path):
    """Test copying a file using absolute paths."""
    # Create source directory and file
    source_dir = tmp_path / "docs/agent"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "source.txt"
    source_file.write_text("Test content")

    # Create destination directory
    dest_dir = tmp_path / ".github"
    dest_dir.mkdir(parents=True)
    dest_file = dest_dir / "destination.txt"

    # Copy using absolute paths
    copy_result = fo.copy_file(str(source_file.absolute()), str(dest_file.absolute()))
    assert copy_result["success"]

    # Verify the copy
    assert dest_file.exists()
    assert dest_file.read_text() == "Test content"

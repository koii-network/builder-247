"""
File system operations for Anthropic CLI tools.
"""
import os
import stat
from pathlib import Path
from typing import List, Optional, Union

class PermissionError(Exception):
    """Custom exception for permission-related errors."""
    pass

class FileSystemTools:
    """Tools for file system operations."""
    
    @staticmethod
    def check_file_readable(path: Path) -> None:
        """Check if a file is readable."""
        try:
            if not os.access(path.parent, os.X_OK):
                raise PermissionError(f"No access to parent directory: {path.parent}")
            if path.exists() and not os.access(path, os.R_OK):
                raise PermissionError(f"No read permission for file: {path}")
        except OSError as e:
            if "Permission denied" in str(e):
                raise PermissionError(f"Permission denied accessing path: {path}")
            raise
    
    @staticmethod
    def check_file_writable(path: Path) -> None:
        """Check if a file or its parent directory is writable."""
        try:
            # Check parent directory first
            if not os.access(path.parent, os.X_OK | os.W_OK):
                raise PermissionError(f"No write permission for directory: {path.parent}")
            # Then check file if it exists
            if path.exists() and not os.access(path, os.W_OK):
                raise PermissionError(f"No write permission for file: {path}")
        except OSError as e:
            if "Permission denied" in str(e):
                raise PermissionError(f"Permission denied accessing path: {path}")
            raise
    
    @staticmethod
    def check_dir_readable(path: Path) -> None:
        """Check if a directory is readable."""
        try:
            if not os.access(path.parent, os.X_OK):
                raise PermissionError(f"No access to parent directory: {path.parent}")
            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")
            if not path.is_dir():
                raise NotADirectoryError(f"Not a directory: {path}")
            if not os.access(path, os.R_OK | os.X_OK):
                raise PermissionError(f"No read permission for directory: {path}")
        except OSError as e:
            if "Permission denied" in str(e):
                raise PermissionError(f"Permission denied accessing directory: {path}")
            raise
    
    @staticmethod
    def check_file_executable(path: Path) -> None:
        """Check if a file is executable."""
        try:
            if not os.access(path.parent, os.X_OK):
                raise PermissionError(f"No access to parent directory: {path.parent}")
            if not os.access(path, os.X_OK):
                raise PermissionError(f"No execute permission for file: {path}")
        except OSError as e:
            if "Permission denied" in str(e):
                raise PermissionError(f"Permission denied accessing file: {path}")
            raise
    
    @staticmethod
    def safe_exists(path: Path) -> bool:
        """Safely check if a path exists, handling permission errors."""
        try:
            return path.exists()
        except OSError:
            return False
    
    @staticmethod
    def read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Read contents of a file."""
        path = Path(file_path)
        
        # Check permissions before attempting to read
        FileSystemTools.check_file_readable(path)
        
        if not FileSystemTools.safe_exists(path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except IOError as e:
            if "Permission denied" in str(e):
                raise PermissionError(f"Permission denied reading file: {file_path}")
            raise IOError(f"Error reading file {file_path}: {str(e)}")
    
    @staticmethod
    def write_file(
        file_path: Union[str, Path],
        content: str,
        encoding: str = 'utf-8',
        create_dirs: bool = True
    ) -> None:
        """Write content to a file."""
        path = Path(file_path)
        
        # Check directory permissions before creating
        if create_dirs:
            try:
                if not path.parent.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                if "Permission denied" in str(e):
                    raise PermissionError(f"Permission denied creating directory: {path.parent}")
                raise
        
        # Check write permissions
        FileSystemTools.check_file_writable(path)
        
        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
        except IOError as e:
            if "Permission denied" in str(e):
                raise PermissionError(f"Permission denied writing to file: {file_path}")
            raise IOError(f"Error writing to file {file_path}: {str(e)}")
    
    @staticmethod
    def list_directory(
        directory: Union[str, Path],
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> List[Path]:
        """List contents of a directory."""
        path = Path(directory)
        
        # Check permissions before attempting to list
        FileSystemTools.check_dir_readable(path)
        
        try:
            if recursive:
                if pattern:
                    return list(path.rglob(pattern))
                return list(path.rglob("*"))
            else:
                if pattern:
                    return list(path.glob(pattern))
                return list(path.glob("*"))
        except OSError as e:
            if "Permission denied" in str(e):
                raise PermissionError(f"Permission denied listing directory: {directory}")
            raise IOError(f"Error listing directory {directory}: {str(e)}") 
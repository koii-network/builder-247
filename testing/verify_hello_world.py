#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from pathlib import Path

def main():
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"hello_world_{timestamp}.txt"
    
    try:
        # Write hello world message
        with open(output_file, "w") as f:
            f.write("Hello World from Linux!\n")
            f.write(f"Generated at: {datetime.now().isoformat()}\n")
            f.write(f"Python version: {sys.version}\n")
            f.write(f"Platform: {sys.platform}\n")
            f.write(f"Working directory: {os.getcwd()}\n")
        
        print(f"Successfully wrote output to: {output_file}")
        return 0
        
    except PermissionError as e:
        print(f"Error: No write permission for file {output_file}")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
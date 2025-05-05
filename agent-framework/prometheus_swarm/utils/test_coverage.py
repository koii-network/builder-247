import os
import subprocess
from typing import List, Optional

def run_test_coverage(
    test_paths: Optional[List[str]] = None, 
    output_format: str = 'term-missing', 
    output_file: Optional[str] = None
) -> int:
    """
    Run test coverage analysis.

    Args:
        test_paths (Optional[List[str]]): Specific test paths to run. 
                                          Defaults to all tests if None.
        output_format (str): Coverage report format. 
                             Defaults to 'term-missing'.
        output_file (Optional[str]): Path to save coverage report. 
                                     Defaults to None.

    Returns:
        int: Exit code of the test coverage run
    """
    # Construct base command
    cmd = [
        'pytest', 
        '-v', 
        f'--cov=prometheus_swarm', 
        f'--cov-report={output_format}'
    ]

    # Add output file if specified
    if output_file:
        cmd.append(f'--cov-report=xml:{output_file}')

    # Add specific test paths if provided
    if test_paths:
        cmd.extend(test_paths)
    
    # Run the coverage analysis
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f"Error running test coverage: {e}")
        return 1

def generate_coverage_badge():
    """
    Generate a coverage badge based on current test coverage.
    Requires coverage.py and coverage-badge to be installed.
    """
    try:
        subprocess.run(['coverage', 'xml'], check=True)
        subprocess.run(['coverage-badge', '-o', 'coverage.svg'], check=True)
        print("Coverage badge generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating coverage badge: {e}")
    except FileNotFoundError:
        print("coverage or coverage-badge not installed. Please install with: pip install coverage coverage-badge")

if __name__ == '__main__':
    # Allow direct script execution for coverage analysis
    run_test_coverage()
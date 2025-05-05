# Mock out problematic imports
import sys
sys.modules['openai'] = None
sys.modules['anthropic'] = None

# Existing init logic (if any) would go here
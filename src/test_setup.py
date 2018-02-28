"""
Sets up the path for pytest so that imports are resolved correctly
"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
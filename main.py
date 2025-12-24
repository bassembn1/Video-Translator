"""
Video Translator - Main Application Entry Point
A tool to transcribe, translate and add subtitles to videos
"""

import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Now import from src
try:
    from gui import VideoTranslatorApp
    print("✓ Modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)

def main():
    """Main function to start the application"""
    app = VideoTranslatorApp()
    app.run()

if __name__ == "__main__":
    main()
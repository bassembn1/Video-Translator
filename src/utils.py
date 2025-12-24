"""
Utility functions for the Video Translator application
"""

import os
import subprocess
import time

class FileUtils:
    """File utility functions"""
    
    @staticmethod
    def get_file_size(file_path):
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)  # Convert to MB
        except:
            return 0
    
    @staticmethod
    def get_base_name(file_path):
        """Get file name without extension"""
        return os.path.splitext(os.path.basename(file_path))[0]
    
    @staticmethod
    def safe_delete(file_path):
        """Safely delete a file if it exists"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Warning: Could not delete {file_path}: {e}")
        return False

class TimeUtils:
    """Time utility functions"""
    
    @staticmethod
    def format_timestamp(seconds):
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')
    
    @staticmethod
    def get_timestamp():
        """Get current timestamp"""
        return time.strftime("%H:%M:%S")
    
    @staticmethod
    def get_video_duration(video_path):
        """Get video duration using ffprobe"""
        try:
            cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", video_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, check=True)
            return float(result.stdout.decode().strip())
        except:
            return 60  # Default 60 seconds

class SystemChecker:
    """Check system requirements"""
    
    @staticmethod
    def check_ffmpeg():
        """Check if ffmpeg is installed"""
        try:
            subprocess.run(["ffmpeg", "-version"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            return True, "✓ ffmpeg is available and ready"
        except:
            return False, "⚠ Warning: ffmpeg is not installed or not in PATH"
    
    @staticmethod
    def check_pysrt():
        """Check if pysrt is installed"""
        try:
            import pysrt
            return True, "✓ pysrt is available"
        except ImportError:
            return False, "⚠ Warning: pysrt is not installed"
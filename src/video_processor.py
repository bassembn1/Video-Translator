"""
Video processing functions for the Video Translator application
"""

import os
import subprocess
import whisper

class VideoProcessor:
    """Handle video and audio processing"""
    
    AUDIO_TEMP = "temp_audio.wav"
    
    @staticmethod
    def extract_audio(video_path, out_audio=AUDIO_TEMP, progress_callback=None):
        """Extract audio from video using ffmpeg"""
        try:
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-ac", "1", "-ar", "16000", "-acodec", "pcm_s16le", out_audio
            ]
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL, check=True)
            if progress_callback:
                progress_callback(100, "Audio extraction complete")
            return out_audio
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error extracting audio: {e}")
    
    @staticmethod
    def transcribe_with_whisper(audio_path, model_size="small", progress_callback=None):
        """Convert audio to text using Whisper"""
        try:
            model = whisper.load_model(model_size)
            
            # Simulate progress for long operations
            if progress_callback:
                import time
                import threading
                
                def simulate_progress():
                    for i in range(0, 101, 10):
                        if progress_callback:
                            progress_callback(30 + int(i * 0.4), 
                                            f"Processing audio... {i}%")
                        time.sleep(0.5)
                
                progress_thread = threading.Thread(target=simulate_progress, 
                                                 daemon=True)
                progress_thread.start()
            
            result = model.transcribe(
                audio_path,
                fp16=False,  # Force FP32 to avoid warning
                language=None  # Auto-detect language
            )
            
            if progress_callback:
                progress_callback(70, "Audio transcription complete")
            
            return result
        except Exception as e:
            raise Exception(f"Error transcribing audio: {e}")
    
    @staticmethod
    def burn_subtitles(video_path, subtitle_path, output_path, progress_callback=None):
        """Burn subtitles to video with enhanced styling"""
        try:
            if progress_callback:
                progress_callback(95, "Burning subtitles to video...")
            
            # Enhanced styling for subtitles
            subtitle_style = (
                "force_style="
                "'FontName=Arial,"
                "FontSize=24,"
                "PrimaryColour=&H00FFFFFF,&"  # White
                "OutlineColour=&H00000000,&"  # Black outline
                "BackColour=&H80000000,&"     # Semi-transparent background
                "Bold=1,"                     # Bold
                "Alignment=2,"                # Bottom alignment
                "MarginL=10,MarginR=10,MarginV=30'"  # Margins
            )
            
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-vf", f"subtitles={subtitle_path}:{subtitle_style}",
                "-c:a", "copy",
                "-preset", "medium",
                output_path
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL, check=True)
            
            if progress_callback:
                progress_callback(100, "Subtitle burning complete")
            
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error burning subtitles to video: {e}")
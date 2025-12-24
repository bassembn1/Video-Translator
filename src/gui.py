"""
Graphical User Interface for the Video Translator application
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import time

from video_processor import VideoProcessor
from translator import TranslatorEngine
from subtitle_creator import SubtitleCreator
from utils import FileUtils, TimeUtils, SystemChecker

class VideoTranslatorApp:
    """Main application GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Translator - Add Subtitles to Video")
        self.root.geometry("1000x850")
        
        self.processing = False
        self.current_progress = 0
        self.translator = TranslatorEngine()
        
        self._setup_fonts()
        self._create_widgets()
        self._setup_bindings()
        
        # Check system requirements
        self._check_requirements()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
    
    def _setup_fonts(self):
        """Setup fonts for the application"""
        try:
            self.title_font = ("Arial", 16, "bold")
            self.button_font = ("Arial", 10)
            self.label_font = ("Arial", 10)
            self.text_font = ("Arial", 9)
        except:
            self.title_font = ("TkDefaultFont", 16, "bold")
            self.button_font = ("TkDefaultFont", 10)
            self.label_font = ("TkDefaultFont", 10)
            self.text_font = ("TkDefaultFont", 9)
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        self._create_title()
        self._create_control_frame()
        self._create_progress_frame()
        self._create_notebook()
    
    def _create_title(self):
        """Create application title"""
        title_label = tk.Label(self.root, 
                              text="Video Translator - Add Subtitles to Video", 
                              font=self.title_font, fg="blue")
        title_label.pack(pady=10)
    
    def _create_control_frame(self):
        """Create control buttons and settings"""
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        # Select video button
        self.open_btn = tk.Button(btn_frame, text="📁 Select Video File", 
                                 command=self.select_video, 
                                 font=self.button_font,
                                 bg="lightblue",
                                 padx=15,
                                 pady=5)
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        # Model settings
        self._create_model_settings(btn_frame)
        # Language settings
        self._create_language_settings(btn_frame)
        # Output settings
        self._create_output_settings(btn_frame)
        # Timing settings
        self._create_timing_settings(btn_frame)
    
    def _create_model_settings(self, parent):
        """Create model settings frame"""
        model_frame = tk.LabelFrame(parent, text="Model Settings", 
                                  font=self.label_font, padx=10, pady=5)
        model_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(model_frame, text="Whisper Model:", font=self.label_font).pack()
        self.model_var = tk.StringVar(value="small")
        model_menu = tk.OptionMenu(model_frame, self.model_var, 
                                 "tiny", "base", "small", "medium", "large")
        model_menu.config(font=self.button_font, width=8)
        model_menu.pack()
    
    def _create_language_settings(self, parent):
        """Create language settings frame"""
        lang_frame = tk.LabelFrame(parent, text="Language Settings", 
                                 font=self.label_font, padx=10, pady=5)
        lang_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(lang_frame, text="Target Language:", font=self.label_font).pack()
        self.lang_var = tk.StringVar(value="ar")
        lang_menu = tk.OptionMenu(lang_frame, self.lang_var, 
                                "ar", "en", "fr", "es", "de", "it", "ru", "zh-cn")
        lang_menu.config(font=self.button_font, width=8)
        lang_menu.pack()
    
    def _create_output_settings(self, parent):
        """Create output settings frame"""
        output_frame = tk.LabelFrame(parent, text="Output Options", 
                                   font=self.label_font, padx=10, pady=5)
        output_frame.pack(side=tk.LEFT, padx=10)
        
        self.create_video_var = tk.BooleanVar(value=True)
        video_check = tk.Checkbutton(output_frame, text="Create video with subtitles", 
                                   variable=self.create_video_var, font=self.label_font)
        video_check.pack(anchor=tk.W)
        
        self.subtitle_style_var = tk.StringVar(value="burned")
        style_frame = tk.Frame(output_frame)
        style_frame.pack()
        
        tk.Radiobutton(style_frame, text="Burned subtitles", 
                      variable=self.subtitle_style_var, 
                      value="burned", font=self.label_font).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(style_frame, text="Subtitle file only", 
                      variable=self.subtitle_style_var, 
                      value="separate", font=self.label_font).pack(side=tk.LEFT, padx=5)
    
    def _create_timing_settings(self, parent):
        """Create timing settings frame"""
        timing_frame = tk.LabelFrame(parent, text="Timing Control", 
                                   font=self.label_font, padx=10, pady=5)
        timing_frame.pack(side=tk.LEFT, padx=10)
        
        # Subtitle delay
        self._create_delay_control(timing_frame)
        # Reading speed
        self._create_speed_control(timing_frame)
        # Sync method
        self._create_sync_control(timing_frame)
    
    def _create_delay_control(self, parent):
        """Create delay control"""
        delay_frame = tk.Frame(parent)
        delay_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(delay_frame, text="Subtitle delay:", 
                font=self.label_font, width=15).pack(side=tk.LEFT)
        self.delay_var = tk.DoubleVar(value=2.0)
        self.delay_label = tk.Label(delay_frame, text="2.0 seconds", 
                                  font=self.label_font, width=10)
        self.delay_label.pack(side=tk.LEFT)
        
        delay_scale = tk.Scale(parent, from_=0.0, to=5.0, resolution=0.5,
                              orient=tk.HORIZONTAL, variable=self.delay_var,
                              font=self.label_font, length=120,
                              command=self._update_delay_label)
        delay_scale.pack(pady=2)
    
    def _create_speed_control(self, parent):
        """Create speed control"""
        speed_frame = tk.Frame(parent)
        speed_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(speed_frame, text="Reading speed:", 
                font=self.label_font, width=15).pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=0.8)
        self.speed_label = tk.Label(speed_frame, text="0.8 (medium)", 
                                  font=self.label_font, width=15)
        self.speed_label.pack(side=tk.LEFT)
        
        speed_scale = tk.Scale(parent, from_=0.5, to=1.5, resolution=0.1,
                              orient=tk.HORIZONTAL, variable=self.speed_var,
                              font=self.label_font, length=120,
                              command=self._update_speed_label)
        speed_scale.pack(pady=2)
    
    def _create_sync_control(self, parent):
        """Create sync method control"""
        sync_frame = tk.Frame(parent)
        sync_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(sync_frame, text="Sync method:", font=self.label_font).pack()
        self.sync_method_var = tk.StringVar(value="smart")
        sync_menu = tk.OptionMenu(sync_frame, self.sync_method_var, 
                                 "basic", "delayed", "smart")
        sync_menu.config(font=self.button_font, width=10)
        sync_menu.pack()
    
    def _create_progress_frame(self):
        """Create progress bar frame"""
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                          orient=tk.HORIZONTAL, 
                                          length=400, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Percentage label
        self.percent_label = tk.Label(self.progress_frame, text="0%", 
                                    font=self.label_font, fg="blue")
        self.percent_label.pack()
        
        # Status label
        self.status_label = tk.Label(self.progress_frame, text="Ready", 
                                   font=self.label_font, fg="green")
        self.status_label.pack()
    
    def _create_notebook(self):
        """Create tabbed interface for results"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Original text tab
        self._create_original_text_tab()
        # Translation tab
        self._create_translation_tab()
        # Log tab
        self._create_log_tab()
    
    def _create_original_text_tab(self):
        """Create original text tab"""
        original_frame = tk.Frame(self.notebook)
        self.notebook.add(original_frame, text="📝 Original Text")
        
        self.original_text = scrolledtext.ScrolledText(original_frame, 
                                                     font=self.text_font,
                                                     wrap=tk.WORD)
        self.original_text.pack(expand=True, fill=tk.BOTH)
    
    def _create_translation_tab(self):
        """Create translation tab"""
        translated_frame = tk.Frame(self.notebook)
        self.notebook.add(translated_frame, text="🌐 Translation")
        
        self.translated_text = scrolledtext.ScrolledText(translated_frame, 
                                                       font=self.text_font,
                                                       wrap=tk.WORD)
        self.translated_text.pack(expand=True, fill=tk.BOTH)
    
    def _create_log_tab(self):
        """Create log tab"""
        log_frame = tk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📋 Processing Log")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                font=self.text_font,
                                                wrap=tk.WORD)
        self.log_text.pack(expand=True, fill=tk.BOTH)
    
    def _setup_bindings(self):
        """Setup event bindings"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _check_requirements(self):
        """Check system requirements"""
        ffmpeg_status, ffmpeg_msg = SystemChecker.check_ffmpeg()
        print(ffmpeg_msg)
        
        pysrt_status, pysrt_msg = SystemChecker.check_pysrt()
        print(pysrt_msg)
        
        if not ffmpeg_status:
            messagebox.showwarning("Warning", 
                                 "ffmpeg is not installed or not in PATH.\n"
                                 "Install it to extract audio from videos.")
    
    def _update_delay_label(self, value):
        """Update delay label"""
        self.delay_label.config(text=f"{float(value):.1f} seconds")
    
    def _update_speed_label(self, value):
        """Update speed label"""
        speed = float(value)
        if speed < 0.7:
            desc = "(slow)"
        elif speed < 0.9:
            desc = "(medium)"
        elif speed < 1.2:
            desc = "(fast)"
        else:
            desc = "(very fast)"
        self.speed_label.config(text=f"{speed:.1f} {desc}")
    
    def update_progress(self, value, status=""):
        """Update progress bar and percentage"""
        self.current_progress = value
        self.progress_bar['value'] = value
        self.percent_label.config(text=f"{value}%")
        
        if status:
            self.status_label.config(text=status)
        
        # Change color based on progress
        if value < 30:
            color = "red"
        elif value < 70:
            color = "orange"
        else:
            color = "green"
        
        self.percent_label.config(fg=color)
        self.root.update_idletasks()
    
    def select_video(self):
        """Select video file"""
        if self.processing:
            messagebox.showwarning("Warning", "Already processing a video!")
            return
        
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.mov *.avi *.wmv *.flv *.webm"),
                ("MP4 files", "*.mp4"),
                ("MKV files", "*.mkv"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return
        
        self.update_progress(0, "Starting processing...")
        threading.Thread(target=self.process_video, args=(path,), daemon=True).start()
    
    def log(self, msg):
        """Add message to log"""
        timestamp = TimeUtils.get_timestamp()
        log_msg = f"[{timestamp}] {msg}"
        
        self.log_text.insert(tk.END, f"{log_msg}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_texts(self):
        """Clear previous texts"""
        self.original_text.delete("1.0", tk.END)
        self.translated_text.delete("1.0", tk.END)
        self.log_text.delete("1.0", tk.END)
    
    def process_video(self, video_path):
        """Process video to translated text and create video with subtitles"""
        self.processing = True
        self.open_btn.config(state=tk.DISABLED)
        
        temp_files = []
        
        try:
            self.clear_texts()
            self.log("=" * 60)
            self.log("Starting video processing...")
            self.log(f"File: {os.path.basename(video_path)}")
            self.log(f"Size: {FileUtils.get_file_size(video_path):.1f} MB")
            
            # 1) Extract audio
            self.update_progress(10, "Extracting audio...")
            self.log("Extracting audio from video...")
            
            audio = VideoProcessor.extract_audio(video_path, 
                                               progress_callback=self.update_progress)
            temp_files.append(audio)
            self.log("✓ Audio extracted successfully")
            
            # 2) Convert audio to text
            model_size = self.model_var.get()
            self.update_progress(30, f"Loading model ({model_size})...")
            self.log(f"Converting audio to text using {model_size} model...")
            
            result = VideoProcessor.transcribe_with_whisper(audio, model_size, 
                                                          progress_callback=self.update_progress)
            transcript = result.get("text", "").strip()
            segments = result.get("segments", [])
            
            self.log(f"✓ Audio converted to text ({len(transcript)} characters)")
            self.log(f"✓ {len(segments)} time segments identified")
            
            if segments:
                total_duration = segments[-1]['end'] - segments[0]['start']
                self.log(f"✓ Video duration: {total_duration:.1f} seconds")
            
            # Display original text
            self.original_text.insert(tk.END, transcript)
            self.notebook.select(0)
            
            # 3) Translation
            if transcript:
                dest_lang = self.lang_var.get()
                self.update_progress(70, f"Translating to {dest_lang}...")
                self.log(f"Translating text to {dest_lang} language...")
                
                translated = self.translator.translate_text(transcript, dest_lang, 
                                                          progress_callback=self.update_progress)
                self.log("✓ Translation completed successfully")
                self.log(f"✓ Translated text length: {len(translated)} characters")
                
                # Display translated text
                self.translated_text.insert(tk.END, translated)
                self.notebook.select(1)
                
                # 4) Save text files
                self.update_progress(90, "Saving text files...")
                base_name = FileUtils.get_base_name(video_path)
                transcript_file = f"{base_name}_transcript.txt"
                translation_file = f"{base_name}_translation_{dest_lang}.txt"
                
                with open(transcript_file, "w", encoding="utf-8") as f:
                    f.write(transcript)
                with open(translation_file, "w", encoding="utf-8") as f:
                    f.write(translated)
                
                self.log(f"✓ Original text saved to: {transcript_file}")
                self.log(f"✓ Translation saved to: {translation_file}")
                
                # 5) Create subtitle and video files
                if self.create_video_var.get():
                    self.log("-" * 40)
                    self.log("Creating subtitle and video files...")
                    
                    # Use appropriate method for creating subtitles
                    srt_file = f"{base_name}_translation_{dest_lang}.srt"
                    sync_method = self.sync_method_var.get()
                    
                    if sync_method == "basic":
                        self.log("Using basic method (no delay)...")
                        SubtitleCreator.create_basic_srt(segments, translated, srt_file, 
                                                        progress_callback=self.update_progress)
                    elif sync_method == "delayed":
                        delay_amount = self.delay_var.get()
                        self.log(f"Using delay method ({delay_amount} seconds)...")
                        SubtitleCreator.create_delayed_srt(segments, translated, srt_file, 
                                                         delay_seconds=delay_amount,
                                                         progress_callback=self.update_progress)
                    else:  # smart
                        delay_amount = self.delay_var.get()
                        speed_factor = self.speed_var.get()
                        self.log(f"Using smart sync (delay: {delay_amount}s, speed: {speed_factor})...")
                        SubtitleCreator.create_smart_srt(segments, translated, srt_file,
                                                        sync_adjustment=delay_amount,
                                                        reading_speed=speed_factor,
                                                        progress_callback=self.update_progress)
                    
                    self.log(f"✓ Subtitle file created: {srt_file}")
                    
                    # If user requested video with burned subtitles
                    if self.subtitle_style_var.get() == "burned":
                        output_video = f"{base_name}_with_subtitles_{dest_lang}.mp4"
                        self.log("Burning subtitles to video...")
                        VideoProcessor.burn_subtitles(video_path, srt_file, output_video, 
                                                     self.update_progress)
                        self.log(f"✓ Video with subtitles created: {output_video}")
                        
                        messagebox.showinfo("✅ Processing Complete", 
                                          f"Video processed successfully!\n\n"
                                          f"Files created:\n"
                                          f"• {transcript_file}\n"
                                          f"• {translation_file}\n"
                                          f"• {srt_file}\n"
                                          f"• {output_video}")
                    else:
                        messagebox.showinfo("✅ Processing Complete", 
                                          f"Video processed successfully!\n\n"
                                          f"Files created:\n"
                                          f"• {transcript_file}\n"
                                          f"• {translation_file}\n"
                                          f"• {srt_file}")
                else:
                    messagebox.showinfo("✅ Processing Complete", 
                                      f"Video processed successfully!\n\n"
                                      f"Files created:\n"
                                      f"• {transcript_file}\n"
                                      f"• {translation_file}")
            
            else:
                self.update_progress(100, "No text found")
                self.log("⚠ No text found for translation")
                messagebox.showwarning("Warning", "No text found in the video")
        
        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            self.update_progress(0, "Processing error")
            self.log(f"❌ {error_msg}")
            self.log(f"Error type: {type(e).__name__}")
            messagebox.showerror("Error", error_msg)
        
        finally:
            # Cleanup
            self.log("Cleaning temporary files...")
            for temp_file in temp_files:
                FileUtils.safe_delete(temp_file)
                self.log(f"✓ Deleted: {temp_file}")
            
            self.processing = False
            self.open_btn.config(state=tk.NORMAL)
            self.log("--- Processing finished ---")
            self.log("=" * 60)
    
    def _on_closing(self):
        """Handle window closing"""
        if self.processing:
            if messagebox.askokcancel("Quit", "Processing in progress. Are you sure you want to quit?"):
                self.root.destroy()
        else:
            self.root.destroy()
"""
Subtitle creation functions for the Video Translator application
"""

try:
    import pysrt
    PYSRT_AVAILABLE = True
except ImportError:
    pysrt = None
    PYSRT_AVAILABLE = False
    print("Warning: pysrt is not installed, will use basic methods")

from utils import TimeUtils

class SubtitleCreator:
    """Create subtitle files in different formats"""
    
    @staticmethod
    def create_basic_srt(segments, translated_text, output_path, progress_callback=None):
        """Create basic SRT file using Whisper timings"""
        try:
            if progress_callback:
                progress_callback(92, "Creating basic subtitles...")
            
            # Split translated text into sentences
            translated_sentences = [s.strip() for s in translated_text.split('. ') if s.strip()]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments):
                    if i >= len(translated_sentences):
                        break
                    
                    start_time = TimeUtils.format_timestamp(segment['start'])
                    end_time = TimeUtils.format_timestamp(segment['end'])
                    
                    # Use corresponding translated sentence
                    text = translated_sentences[i]
                    if text and not text.endswith('.'):
                        text += '.'
                    
                    f.write(f"{i + 1}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
            
            return output_path
        except Exception as e:
            raise Exception(f"Error creating basic subtitle file: {e}")
    
    @staticmethod
    def create_delayed_srt(segments, translated_text, output_path, 
                          delay_seconds=2.0, progress_callback=None):
        """Create SRT file with time delay"""
        try:
            if progress_callback:
                progress_callback(92, f"Creating delayed subtitles (delay: {delay_seconds}s)...")
            
            if not PYSRT_AVAILABLE:
                return SubtitleCreator.create_basic_srt(segments, translated_text, 
                                                       output_path, progress_callback)
            
            subs = pysrt.SubRipFile()
            
            # Split translated text considering length
            translated_sentences = []
            current_sentence = ""
            
            for word in translated_text.split():
                if len(current_sentence + " " + word) < 40:  # Max 40 chars per line
                    current_sentence += " " + word if current_sentence else word
                else:
                    if current_sentence:
                        translated_sentences.append(current_sentence.strip())
                    current_sentence = word
            
            if current_sentence:
                translated_sentences.append(current_sentence.strip())
            
            # Create subtitle items with delay
            for i, segment in enumerate(segments):
                if i >= len(translated_sentences):
                    break
                
                # Add delay to start and end
                start_time = segment['start'] + delay_seconds
                end_time = segment['end'] + delay_seconds
                
                # Ensure minimum display duration
                min_duration = max(3.0, len(translated_sentences[i]) * 0.15)
                if end_time - start_time < min_duration:
                    end_time = start_time + min_duration
                
                start_time_obj = pysrt.SubRipTime(
                    hours=int(start_time // 3600),
                    minutes=int((start_time % 3600) // 60),
                    seconds=int(start_time % 60),
                    milliseconds=int((start_time * 1000) % 1000)
                )
                
                end_time_obj = pysrt.SubRipTime(
                    hours=int(end_time // 3600),
                    minutes=int((end_time % 3600) // 60),
                    seconds=int(end_time % 60),
                    milliseconds=int((end_time * 1000) % 1000)
                )
                
                item = pysrt.SubRipItem(
                    index=i + 1,
                    start=start_time_obj,
                    end=end_time_obj,
                    text=translated_sentences[i]
                )
                subs.append(item)
            
            subs.save(output_path, encoding='utf-8')
            return output_path
            
        except Exception as e:
            raise Exception(f"Error creating delayed subtitle file: {e}")
    
    @staticmethod
    def create_smart_srt(segments, translated_text, output_path, 
                        sync_adjustment=2.0, reading_speed=0.8, progress_callback=None):
        """Create smart subtitles with automatic synchronization"""
        try:
            if progress_callback:
                progress_callback(92, "Synchronizing subtitles with speech...")
            
            if not PYSRT_AVAILABLE:
                return SubtitleCreator.create_delayed_srt(segments, translated_text, 
                                                         output_path, sync_adjustment, 
                                                         progress_callback)
            
            subs = pysrt.SubRipFile()
            
            # Smart splitting of translated text
            sentences = SubtitleCreator._split_text_smartly(translated_text)
            
            # Distribute sentences across segments
            sentence_index = 0
            total_sentences = len(sentences)
            
            for i, segment in enumerate(segments):
                if sentence_index >= total_sentences:
                    break
                
                subtitle_data = SubtitleCreator._calculate_subtitle_timing(
                    segment, sentences[sentence_index], sync_adjustment, 
                    reading_speed, i, segments
                )
                
                start_time_obj = pysrt.SubRipTime(
                    hours=int(subtitle_data['start'] // 3600),
                    minutes=int((subtitle_data['start'] % 3600) // 60),
                    seconds=int(subtitle_data['start'] % 60),
                    milliseconds=int((subtitle_data['start'] * 1000) % 1000)
                )
                
                end_time_obj = pysrt.SubRipTime(
                    hours=int(subtitle_data['end'] // 3600),
                    minutes=int((subtitle_data['end'] % 3600) // 60),
                    seconds=int(subtitle_data['end'] % 60),
                    milliseconds=int((subtitle_data['end'] * 1000) % 1000)
                )
                
                # Split long text
                display_text = SubtitleCreator._split_long_text(
                    sentences[sentence_index]
                )
                
                item = pysrt.SubRipItem(
                    index=i + 1,
                    start=start_time_obj,
                    end=end_time_obj,
                    text=display_text
                )
                subs.append(item)
                
                sentence_index += 1
            
            subs.save(output_path, encoding='utf-8')
            return output_path
            
        except Exception as e:
            raise Exception(f"Error in smart synchronization: {e}")
    
    @staticmethod
    def _split_text_smartly(text, max_length=40):
        """Split text into sentences considering length"""
        sentences = []
        current_sentence = []
        current_length = 0
        
        words = text.split()
        for word in words:
            word_length = len(word)
            if current_length + word_length + 1 <= max_length:  # +1 for space
                current_sentence.append(word)
                current_length += word_length + 1
            else:
                if current_sentence:
                    sentences.append(" ".join(current_sentence))
                current_sentence = [word]
                current_length = word_length
        
        if current_sentence:
            sentences.append(" ".join(current_sentence))
        
        return sentences if sentences else [text]
    
    @staticmethod
    def _calculate_subtitle_timing(segment, sentence, sync_adjustment, 
                                  reading_speed, current_idx, all_segments):
        """Calculate optimal timing for a subtitle"""
        sentence_length = len(sentence)
        display_start = segment['start'] + sync_adjustment
        
        # Calculate reading time
        reading_time_per_char = 0.15 / reading_speed
        required_duration = max(2.0, sentence_length * reading_time_per_char)
        display_end = display_start + required_duration
        
        # Avoid overlap with next segment
        if current_idx < len(all_segments) - 1:
            next_segment_start = all_segments[current_idx + 1]['start'] + sync_adjustment
            if display_end > next_segment_start:
                display_end = next_segment_start - 0.5  # Leave 0.5 second gap
        
        return {'start': display_start, 'end': display_end}
    
    @staticmethod
    def _split_long_text(text, max_line_length=35):
        """Split long text into two lines"""
        if len(text) <= max_line_length:
            return text
        
        words = text.split()
        if len(words) < 2:
            return text
        
        mid_point = len(words) // 2
        line1 = " ".join(words[:mid_point])
        line2 = " ".join(words[mid_point:])
        return f"{line1}\\n{line2}"
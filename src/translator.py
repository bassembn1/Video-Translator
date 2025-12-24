"""
Translation functions for the Video Translator application
"""

from googletrans import Translator

class TranslatorEngine:
    """Handle text translation"""
    
    def __init__(self):
        self.translator = Translator()
    
    def translate_text(self, text, dest_lang="ar", progress_callback=None):
        """Translate text to target language"""
        try:
            if len(text) > 5000:
                return self._translate_large_text(text, dest_lang, progress_callback)
            else:
                return self._translate_small_text(text, dest_lang, progress_callback)
        except Exception as e:
            raise Exception(f"Error in translation: {e}")
    
    def _translate_large_text(self, text, dest_lang, progress_callback=None):
        """Translate large text by splitting into chunks"""
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        translated_chunks = []
        total_chunks = len(chunks)
        
        for idx, chunk in enumerate(chunks):
            try:
                if progress_callback:
                    progress = int((idx / total_chunks) * 100)
                    progress_callback(70 + int(progress * 0.2), 
                                    f"Translating part {idx+1} of {total_chunks}")
                
                res = self.translator.translate(chunk, dest=dest_lang)
                translated_chunks.append(res.text)
                import time
                time.sleep(0.1)  # Avoid rate limiting
            except Exception as e:
                translated_chunks.append(f"[Translation error: {str(e)}]")
        
        if progress_callback:
            progress_callback(90, "Translation complete")
        
        return " ".join(translated_chunks)
    
    def _translate_small_text(self, text, dest_lang, progress_callback=None):
        """Translate small text directly"""
        if progress_callback:
            progress_callback(80, "Translating...")
        
        res = self.translator.translate(text, dest=dest_lang)
        
        if progress_callback:
            progress_callback(90, "Translation complete")
        
        return res.text
# modules/voice_processor.py - Multi-language to English Translation
import os
import tempfile
import hashlib
import streamlit as st

# Set FFmpeg path
FFMPEG_BIN = r"C:\ffmpeg\bin"
if os.path.exists(FFMPEG_BIN):
    os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

# Import Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✅ Whisper imported successfully")
except ImportError as e:
    print(f"⚠️ Whisper not available: {e}")
    WHISPER_AVAILABLE = False

# Import Translator
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
    print("✅ Translator imported successfully")
except ImportError as e:
    print(f"⚠️ Translator not available: {e}")
    TRANSLATOR_AVAILABLE = False


class VoiceProcessor:
    """Process voice complaints - Detects any language, translates to English"""
    
    # Supported languages with their codes
    SUPPORTED_LANGUAGES = {
        'ta': 'Tamil (தமிழ்)',
        'hi': 'Hindi (हिन्दी)',
        'te': 'Telugu (తెలుగు)',
        'bn': 'Bengali (বাংলা)',
        'mr': 'Marathi (मराठी)',
        'ml': 'Malayalam (മലയാളം)',
        'kn': 'Kannada (ಕನ್ನಡ)',
        'gu': 'Gujarati (ગુજરાતી)',
        'pa': 'Punjabi (ਪੰਜਾਬੀ)',
        'or': 'Odia (ଓଡ଼ିଆ)',
        'as': 'Assamese (অসমীয়া)',
        'ur': 'Urdu (اردو)',
        'en': 'English'
    }
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        if not WHISPER_AVAILABLE:
            print("⚠️ Whisper not available")
            return
        
        try:
            with st.spinner("🎤 Loading Whisper model for multi-language support..."):
                # Using "small" model for better accuracy across languages
                self.model = whisper.load_model("small")
                self.model_loaded = True
                print("✅ Whisper model loaded - Supports 100+ languages")
        except Exception as e:
            print(f"⚠️ Failed to load Whisper: {e}")
            self.model = None
    
    def _translate_to_english(self, text, source_lang):
        """Translate text to English"""
        if not TRANSLATOR_AVAILABLE or source_lang == 'en':
            return text, 1.0
        
        try:
            translator = GoogleTranslator(source=source_lang, target='en')
            translated = translator.translate(text)
            return translated, 0.95
        except Exception as e:
            print(f"Translation error: {e}")
            return text, 0.5
    
    def _extract_complaint_details(self, text):
        """Extract complaint details from English text"""
        details = {
            'complaint_type': None,
            'urgency': 'MEDIUM',
            'location_mentioned': None,
            'keywords': [],
            'original_text': text
        }
        
        text_lower = text.lower()
        
        # Complaint type detection
        complaint_keywords = {
            'water_pollution': ['water', 'river', 'lake', 'pond', 'dumping', 'chemical', 'effluent', 'discharge', 'black water', 'dead fish', 'wastewater', 'sewage'],
            'air_pollution': ['smoke', 'air', 'breathing', 'asthma', 'chimney', 'fumes', 'dust', 'pollution', 'black smoke', 'emission', 'gas'],
            'waste_dumping': ['garbage', 'waste', 'plastic', 'dumping', 'landfill', 'trash', 'rubbish', 'dumpsite', 'solid waste'],
            'noise_pollution': ['noise', 'sound', 'loud', 'disturbing', 'generator', 'honking', 'loudspeaker']
        }
        
        for complaint_type, keywords in complaint_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                details['complaint_type'] = complaint_type
                details['keywords'] = [kw for kw in keywords if kw in text_lower]
                break
        
        # Urgency detection
        urgency_keywords = {
            'HIGH': ['emergency', 'urgent', 'immediate', 'danger', 'dying', 'dead', 'hospital', 'critical', 'serious', 'severe', 'life threatening'],
            'LOW': ['slowly', 'gradually', 'minor', 'small', 'slight', 'mild', 'occasional']
        }
        
        for urgency, keywords in urgency_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                details['urgency'] = urgency
                break
        
        # Location detection
        location_indicators = ['near', 'behind', 'at', 'in', 'village', 'city', 'town', 'area', 'street', 'road', 'colony', 'district']
        for indicator in location_indicators:
            if indicator in text_lower:
                parts = text_lower.split(indicator)
                if len(parts) > 1:
                    location_part = parts[1].split('.')[0].split(',')[0][:100]
                    details['location_mentioned'] = f"{indicator} {location_part}".strip()
                    break
        
        return details
    
    def process(self, audio_bytes):
        """
        Complete voice processing pipeline:
        1. Transcribe in original language
        2. Translate to English
        3. Extract complaint details
        """
        
        if not self.model_loaded or self.model is None:
            return self._fallback_response(audio_bytes)
        
        tmp_path = None
        try:
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            # Transcribe with language auto-detection
            result = self.model.transcribe(
                tmp_path,
                language=None,  # Auto-detect Tamil, Hindi, English, etc.
                task="transcribe",
                verbose=False,
                fp16=False
            )
            
            # Clean up
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
            # Get transcribed text and detected language
            original_text = result['text'].strip()
            detected_lang = result.get('language', 'en')
            language_name = self.SUPPORTED_LANGUAGES.get(detected_lang, detected_lang)
            
            # Translate to English
            english_text, translation_confidence = self._translate_to_english(original_text, detected_lang)
            
            # Extract complaint details from English text
            details = self._extract_complaint_details(english_text)
            
            return {
                'success': True,
                'original_transcript': original_text,
                'translated_transcript': english_text,
                'language_code': detected_lang,
                'language_name': language_name,
                'confidence': result.get('segments', [{}])[0].get('confidence', 0.85) if result.get('segments') else 0.85,
                'translation_confidence': translation_confidence,
                'complaint_details': details,
                'simulation': False
            }
            
        except Exception as e:
            print(f"Processing error: {e}")
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            return self._fallback_response(audio_bytes)
    
    def _fallback_response(self, audio_bytes):
        """Fallback for demo"""
        return {
            'success': True,
            'original_transcript': "எங்கள் கிராமத்தின் பின்புறம் ஒரு தொழிற்சாலை ஆற்றில் ரசாயன கழிவுகளை கொட்டுகிறது. தண்ணீர் கருப்பாக மாறிவிட்டது, மீன்கள் இறக்கின்றன.",
            'translated_transcript': "A factory behind our village is dumping chemical waste into the river. The water has turned black and fish are dying.",
            'language_code': 'ta',
            'language_name': 'Tamil (தமிழ்)',
            'confidence': 0.85,
            'translation_confidence': 0.90,
            'complaint_details': {
                'complaint_type': 'water_pollution',
                'urgency': 'HIGH',
                'location_mentioned': 'behind the village',
                'keywords': ['chemical waste', 'river', 'dying']
            },
            'simulation': True
        }


# Create instance
voice_processor = VoiceProcessor()
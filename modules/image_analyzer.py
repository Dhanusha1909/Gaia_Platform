# modules/image_analyzer.py
from PIL import Image # pyright: ignore[reportMissingImports]
import numpy as np # pyright: ignore[reportMissingImports]
import io
import streamlit as st # type: ignore

class ImageAnalyzer:
    """Analyze citizen-uploaded images for environmental violations
    Uses lightweight MobileNet for object detection - Green AI optimized
    """
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load lightweight MobileNet model (16MB) - CPU efficient"""
        try:
            from transformers import pipeline # pyright: ignore[reportMissingImports]
            with st.spinner("📸 Loading MobileNet model (16MB)..."):
                self.model = pipeline(
                    "image-classification",
                    model="google/mobilenet_v2_1.0_224",
                    device=-1  # CPU only
                )
                self.model_loaded = True
                print("✅ MobileNet model loaded successfully")
        except Exception as e:
            print(f"⚠️ Model load failed: {e}")
            print("Using color-based fallback detection")
            self.model = None
            self.model_loaded = False
    
    def analyze_pollution_ml(self, image):
        """Analyze image using MobileNet ML model"""
        try:
            # Get predictions
            predictions = self.model(image)
            
            # Pollution-related labels (ImageNet classes)
            pollution_labels = {
                'smoke': ['smokestack', 'chimney', 'volcano', 'smoke'],
                'fire': ['fire', 'flame', 'bonfire', 'incinerator'],
                'waste': ['dump', 'landfill', 'trash', 'rubbish', 'garbage'],
                'water': ['river', 'lake', 'ocean', 'reservoir'],
                'factory': ['factory', 'industrial', 'power_plant', 'mill'],
                'vehicle': ['car', 'truck', 'bus', 'auto', 'vehicle']
            }
            
            detection = {
                'has_pollution': False,
                'pollution_type': None,
                'severity': 'LOW',
                'description': '',
                'confidence': 0,
                'detected_objects': []
            }
            
            # Analyze top predictions
            for pred in predictions[:5]:
                label = pred['label'].lower()
                confidence = pred['score']
                
                for pollution_type, keywords in pollution_labels.items():
                    if any(keyword in label for keyword in keywords):
                        detection['detected_objects'].append({
                            'label': label,
                            'confidence': confidence,
                            'type': pollution_type
                        })
                        
                        if pollution_type == 'smoke':
                            detection['has_pollution'] = True
                            detection['pollution_type'] = 'air_pollution'
                            detection['severity'] = 'HIGH' if confidence > 0.7 else 'MEDIUM'
                            detection['description'] = f"Smoke/emissions detected ({confidence*100:.0f}% confidence)"
                            detection['confidence'] = confidence
                        
                        elif pollution_type == 'fire':
                            detection['has_pollution'] = True
                            detection['pollution_type'] = 'air_pollution'
                            detection['severity'] = 'HIGH'
                            detection['description'] = f"Fire/burning detected - urgent action needed"
                            detection['confidence'] = confidence
                        
                        elif pollution_type == 'waste':
                            detection['has_pollution'] = True
                            detection['pollution_type'] = 'waste_dumping'
                            detection['severity'] = 'MEDIUM'
                            detection['description'] = f"Waste dumping site detected"
                            detection['confidence'] = confidence
                        
                        elif pollution_type == 'factory':
                            detection['has_pollution'] = True
                            detection['pollution_type'] = 'industrial'
                            detection['severity'] = 'MEDIUM'
                            detection['description'] = f"Industrial facility detected - verify compliance"
                            detection['confidence'] = confidence
            
            return detection
            
        except Exception as e:
            print(f"ML analysis error: {e}")
            return None
    
    def analyze_pollution_color(self, image):
        """Fallback: Analyze image using color-based detection"""
        # Convert to RGB array
        img_array = np.array(image)
        
        detection = {
            'has_pollution': False,
            'pollution_type': None,
            'severity': 'LOW',
            'description': '',
            'confidence': 0.6,
            'detected_objects': []
        }
        
        # Get average color
        avg_color = img_array.mean(axis=(0, 1))
        
        # Check for dark/discolored water (chemical spill)
        if avg_color[0] < 100 and avg_color[1] < 100 and avg_color[2] > 50:
            detection['has_pollution'] = True
            detection['pollution_type'] = 'water_pollution'
            detection['severity'] = 'HIGH'
            detection['description'] = 'Dark discoloration detected - possible chemical discharge into water'
            detection['confidence'] = 0.7
        
        # Check for smoke/smog (gray/white with low saturation)
        elif avg_color[0] > 150 and avg_color[1] > 150 and avg_color[2] > 150:
            # Check if it's grayish (all channels similar)
            if abs(avg_color[0] - avg_color[1]) < 50 and abs(avg_color[1] - avg_color[2]) < 50:
                detection['has_pollution'] = True
                detection['pollution_type'] = 'air_pollution'
                detection['severity'] = 'MEDIUM'
                detection['description'] = 'Smoke/smog detected - potential air pollution'
                detection['confidence'] = 0.65
        
        # Check for waste/plastic (bright unnatural colors)
        elif avg_color[2] < 100 and avg_color[1] > 150:  # Greenish with low blue
            detection['has_pollution'] = True
            detection['pollution_type'] = 'waste_dumping'
            detection['severity'] = 'MEDIUM'
            detection['description'] = 'Waste dumping detected - possible solid waste violation'
            detection['confidence'] = 0.6
        
        # Check for red/brown (chemical/industrial)
        elif avg_color[0] > 150 and avg_color[1] < 100 and avg_color[2] < 100:
            detection['has_pollution'] = True
            detection['pollution_type'] = 'chemical_waste'
            detection['severity'] = 'HIGH'
            detection['description'] = 'Red/brown discoloration - possible chemical contamination'
            detection['confidence'] = 0.7
        
        return detection
    
    def analyze_pollution(self, image):
        """Analyze image using ML if available, else color fallback"""
        
        # Try ML first if model is loaded
        if self.model_loaded:
            ml_result = self.analyze_pollution_ml(image)
            if ml_result and ml_result['has_pollution']:
                return ml_result
        
        # Fallback to color analysis
        return self.analyze_pollution_color(image)
    
    def generate_complaint_text(self, detection):
        """Generate detailed complaint text from image analysis"""
        if not detection['has_pollution']:
            return """✅ **No Immediate Violation Detected**

The image analysis did not identify clear environmental violations. However, if you have additional evidence or specific concerns, please submit a voice complaint with more details.

*Note: This is an automated analysis. Officer discretion advised.*"""
        
        # Map pollution type to readable format
        type_map = {
            'water_pollution': '💧 WATER POLLUTION',
            'air_pollution': '💨 AIR POLLUTION',
            'waste_dumping': '🗑️ WASTE DUMPING',
            'chemical_waste': '🧪 CHEMICAL WASTE',
            'industrial': '🏭 INDUSTRIAL VIOLATION'
        }
        
        pollution_display = type_map.get(detection['pollution_type'], detection['pollution_type'].upper())
        
        severity_icons = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }
        
        severity_icon = severity_icons.get(detection['severity'], '⚪')
        
        complaint = f"""
🚨 **VIOLATION DETECTED**

{pollution_display}
{severity_icon} **Severity:** {detection['severity']}

**Details:** {detection['description']}

**Confidence:** {detection.get('confidence', 0.7)*100:.0f}%

**Recommended Action:**
"""
        
        if detection['severity'] == 'HIGH':
            complaint += "- 🚨 **IMMEDIATE ACTION:** Dispatch inspection team within 24 hours\n"
            complaint += "- 📢 Issue public notice if health hazard confirmed\n"
            complaint += "- ⚖️ Consider legal action against violator\n"
        elif detection['severity'] == 'MEDIUM':
            complaint += "- 📋 Schedule inspection within 7 days\n"
            complaint += "- 📝 Send notice to facility for explanation\n"
            complaint += "- 🔍 Verify compliance records\n"
        else:
            complaint += "- 📌 Log for regular monitoring\n"
            complaint += "- 📞 Follow-up with local authorities\n"
        
        if detection.get('detected_objects'):
            complaint += "\n**Detected Objects:**\n"
            for obj in detection['detected_objects'][:3]:
                complaint += f"- {obj['label']} ({obj['confidence']*100:.0f}% confidence)\n"
        
        return complaint
    
    def analyze(self, image_bytes):
        """Complete image analysis pipeline"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Resize for faster processing (Green AI)
            image.thumbnail((224, 224))
            
            detection = self.analyze_pollution(image)
            complaint_text = self.generate_complaint_text(detection)
            
            # Determine if action needed
            action_needed = detection['has_pollution'] and detection['severity'] in ['HIGH', 'MEDIUM']
            
            return {
                'success': True,
                'detection': detection,
                'complaint_text': complaint_text,
                'has_violation': detection['has_pollution'],
                'action_needed': action_needed,
                'severity': detection['severity'],
                'model_used': 'mobilenet' if self.model_loaded else 'color_analysis'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'has_violation': False,
                'action_needed': False
            }
    
    def is_model_loaded(self):
        """Check if ML model is loaded"""
        return self.model_loaded

# Create instance
image_analyzer = ImageAnalyzer()
# modules/text_analyzer.py
import re
import streamlit as st # pyright: ignore[reportMissingImports]
from transformers import pipeline # pyright: ignore[reportMissingImports]

class TextAnalyzer:
    """Analyze sustainability reports using DistilBERT - Green AI optimized"""
    
    def __init__(self):
        self.classifier = None
        self.model_loaded = False
        self._load_model()
        
    def _load_model(self):
        """Load lightweight DistilBERT model (66MB) - CPU efficient"""
        try:
            with st.spinner("📝 Loading DistilBERT model (66MB)..."):
                self.classifier = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1  # Use CPU for lower carbon footprint
                )
                self.model_loaded = True
                print("✅ DistilBERT model loaded successfully")
        except Exception as e:
            print(f"⚠️ Model load failed: {e}")
            print("Text analysis will use keyword-based fallback")
            self.classifier = None
            self.model_loaded = False
    
    def extract_metrics(self, text):
        """Extract sustainability metrics from text - Enhanced for Indian context"""
        text_lower = text.lower()
        
        metrics = {
            'co2_emissions': None,
            'water_usage': None,
            'waste_generated': None,
            'renewable_percent': None,
            'energy_consumption': None,
            'effluent_treated': None,
            'tree_planted': None
        }
        
        # CO2 emissions - multiple formats
        co2_patterns = [
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:tons?|tonnes?|mt|metric\s*tons?)\s*(?:co2|carbon|ghg)',
            r'co2\s*emissions?\s*(?:of\s*)?(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:tons?|tonnes?)',
            r'carbon\s*footprint\s*(?:of\s*)?(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:tons?|tonnes?)',
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*mtco2',
        ]
        
        for pattern in co2_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    metrics['co2_emissions'] = float(match.group(1).replace(',', ''))
                    break
                except:
                    pass
        
        # Water usage - multiple formats
        water_patterns = [
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:million\s*liters?|mld|ml|m³)',
            r'water\s*usage\s*(?:of\s*)?(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:liters?|litres?)',
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*kl\s*(?:per\s*day)?',
        ]
        
        for pattern in water_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    metrics['water_usage'] = float(match.group(1).replace(',', ''))
                    break
                except:
                    pass
        
        # Renewable percentage
        renewable_patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*(?:renewable|solar|wind|green\s*energy)',
            r'renewable\s*(?:energy|power)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%',
            r'solar\s*(?:capacity|contribution)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%',
        ]
        
        for pattern in renewable_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    metrics['renewable_percent'] = float(match.group(1))
                    break
                except:
                    pass
        
        # Waste generated
        waste_patterns = [
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:tons?|tonnes?|mt)\s*(?:waste|solid\s*waste)',
            r'waste\s*generated\s*(?:of\s*)?(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:tons?|tonnes?)',
        ]
        
        for pattern in waste_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    metrics['waste_generated'] = float(match.group(1).replace(',', ''))
                    break
                except:
                    pass
        
        # Energy consumption
        energy_match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:mwh|gwh|kwh)', text_lower)
        if energy_match:
            try:
                metrics['energy_consumption'] = float(energy_match.group(1).replace(',', ''))
            except:
                pass
        
        # Tree plantation (Indian context)
        tree_match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:trees|saplings)', text_lower)
        if tree_match:
            try:
                metrics['tree_planted'] = float(tree_match.group(1).replace(',', ''))
            except:
                pass
        
        return metrics
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of the report with fallback"""
        if self.classifier is None:
            return self._keyword_sentiment(text)
        
        # Take first 500 chars for speed
        sample = text[:500]
        try:
            result = self.classifier(sample)[0]
            return {'score': result['score'], 'label': result['label']}
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return self._keyword_sentiment(text)
    
    def _keyword_sentiment(self, text):
        """Fallback sentiment analysis using keywords"""
        text_lower = text.lower()
        
        positive_keywords = ['reduced', 'decreased', 'improved', 'achieved', 'success', 
                            'excellent', 'good', 'positive', 'renewable', 'sustainable',
                            'green', 'conservation', 'restored', 'compliant']
        
        negative_keywords = ['increased', 'emissions', 'pollution', 'waste', 'violation',
                            'failed', 'crisis', 'shortfall', 'deforestation', 'spill',
                            'contamination', 'non-compliant', 'penalty']
        
        pos_count = sum(1 for kw in positive_keywords if kw in text_lower)
        neg_count = sum(1 for kw in negative_keywords if kw in text_lower)
        
        if pos_count + neg_count == 0:
            return {'score': 0.5, 'label': 'NEUTRAL'}
        
        score = pos_count / (pos_count + neg_count)
        label = 'POSITIVE' if score > 0.5 else 'NEGATIVE' if score < 0.5 else 'NEUTRAL'
        
        return {'score': score, 'label': label}
    
    def calculate_metric_score(self, metrics):
        """Convert metrics to scores (0-100) - Adjusted for Indian context"""
        scores = []
        
        # CO2 score - lower is better
        co2_value = metrics.get('co2_emissions')
        if co2_value is not None and co2_value > 0:
            if co2_value < 100:
                co2_score = 90
            elif co2_value < 500:
                co2_score = 70
            elif co2_value < 1000:
                co2_score = 50
            elif co2_value < 5000:
                co2_score = 30
            else:
                co2_score = 10
            scores.append(co2_score)
        
        # Water score - lower is better
        water_value = metrics.get('water_usage')
        if water_value is not None and water_value > 0:
            if water_value < 1000:
                water_score = 90
            elif water_value < 5000:
                water_score = 70
            elif water_value < 10000:
                water_score = 50
            elif water_value < 50000:
                water_score = 30
            else:
                water_score = 10
            scores.append(water_score)
        
        # Renewable score - higher is better
        renewable_value = metrics.get('renewable_percent')
        if renewable_value is not None:
            scores.append(renewable_value)
        
        # Waste score - lower is better
        waste_value = metrics.get('waste_generated')
        if waste_value is not None and waste_value > 0:
            if waste_value < 50:
                waste_score = 90
            elif waste_value < 200:
                waste_score = 70
            elif waste_value < 500:
                waste_score = 50
            else:
                waste_score = 30
            scores.append(waste_score)
        
        # Tree plantation score - higher is better
        tree_value = metrics.get('tree_planted')
        if tree_value is not None and tree_value > 0:
            if tree_value < 100:
                tree_score = 60
            elif tree_value < 500:
                tree_score = 75
            elif tree_value < 1000:
                tree_score = 85
            else:
                tree_score = 95
            scores.append(tree_score)
        
        if scores:
            return sum(scores) / len(scores)
        return 50  # Default score if no metrics found
    
    def generate_suggestions(self, metrics, score):
        """Generate improvement suggestions - Indian context"""
        suggestions = []
        
        # CO2 suggestions
        co2_value = metrics.get('co2_emissions')
        if co2_value is not None and co2_value > 500:
            suggestions.append("🔴 HIGH CARBON EMISSIONS: Consider PM-KUSUM solar scheme for renewable energy adoption.")
        elif co2_value is not None and co2_value > 200:
            suggestions.append("🟡 MODERATE EMISSIONS: Energy efficiency audits recommended. Government subsidies available.")
        
        # Water suggestions
        water_value = metrics.get('water_usage')
        if water_value is not None and water_value > 10000:
            suggestions.append("🔴 HIGH WATER USAGE: Implement rainwater harvesting. Jal Jeevan Mission provides support.")
        elif water_value is not None and water_value > 5000:
            suggestions.append("🟡 WATER CONSERVATION NEEDED: Install flow meters and recycle wastewater.")
        
        # Renewable suggestions
        renewable_value = metrics.get('renewable_percent')
        if renewable_value is not None and renewable_value < 30:
            suggestions.append("🟡 LOW RENEWABLE ADOPTION: Solar rooftop subsidy available under PM-Surya Ghar scheme.")
        
        # Score-based urgent suggestions
        if score < 40:
            suggestions.append("🚨 CRITICAL: Immediate action required. Submit compliance report within 15 days.")
        elif score < 60:
            suggestions.append("⚠️ IMPROVEMENT NEEDED: Address above issues within 60 days.")
        
        # Positive reinforcement
        if metrics.get('tree_planted') and metrics.get('tree_planted') > 500:
            suggestions.append("🌳 GOOD: Afforestation efforts recognized. Maintain momentum.")
        
        if not suggestions:
            suggestions.append("✅ GOOD COMPLIANCE: Maintain current practices. Regular monitoring recommended.")
        
        return suggestions
    
    def analyze(self, text):
        """Complete analysis of report"""
        if not text or len(text.strip()) == 0:
            return {
                'metrics': {},
                'sentiment': {'score': 0.5, 'label': 'NEUTRAL'},
                'gaia_score': 50,
                'suggestions': ["No text provided for analysis"],
                'status': 'NO DATA'
            }
        
        metrics = self.extract_metrics(text)
        sentiment = self.analyze_sentiment(text)
        metric_score = self.calculate_metric_score(metrics)
        
        # Combine metric score with sentiment
        sentiment_score = sentiment['score'] * 100 if sentiment['label'] == 'POSITIVE' else (1 - sentiment['score']) * 100
        gaia_score = (metric_score * 0.7) + (sentiment_score * 0.3)
        gaia_score = round(gaia_score, 1)
        
        suggestions = self.generate_suggestions(metrics, gaia_score)
        
        # Determine status
        if gaia_score >= 80:
            status = "EXCELLENT"
            status_icon = "🌟"
        elif gaia_score >= 60:
            status = "GOOD"
            status_icon = "📈"
        elif gaia_score >= 40:
            status = "POOR"
            status_icon = "⚠️"
        else:
            status = "CRITICAL"
            status_icon = "🚨"
        
        return {
            'metrics': metrics,
            'sentiment': sentiment,
            'gaia_score': gaia_score,
            'suggestions': suggestions,
            'status': status,
            'status_icon': status_icon
        }
    
    def is_model_loaded(self):
        """Check if model is loaded"""
        return self.model_loaded

# Create instance
text_analyzer = TextAnalyzer()
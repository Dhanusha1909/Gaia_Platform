# config.py
import os
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# APP CONFIGURATION
# ============================================================================

APP_NAME = os.getenv("APP_NAME", "GAIA - Sustainability Intelligence Platform")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "development")  # development, production, testing
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ============================================================================
# AI MODEL CONFIGURATION - Green AI Optimized
# ============================================================================

# Text Analysis - DistilBERT (66MB, CPU efficient)
TEXT_MODEL = os.getenv("TEXT_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
TEXT_MODEL_MAX_LENGTH = int(os.getenv("TEXT_MODEL_MAX_LENGTH", "512"))
TEXT_MODEL_DEVICE = os.getenv("TEXT_MODEL_DEVICE", "-1")  # -1 = CPU, 0 = GPU

# Image Analysis - MobileNetV3 (16MB, lightweight)
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "google/mobilenet_v2_1.0_224")
IMAGE_MODEL_SIZE = int(os.getenv("IMAGE_MODEL_SIZE", "224"))  # 224x224

# Voice Analysis - Whisper Tiny (39MB, most efficient)
VOICE_MODEL = os.getenv("VOICE_MODEL", "tiny")  # Options: tiny, base, small
VOICE_MODEL_SIZES = {
    "tiny": 39,      # MB
    "base": 139,     # MB
    "small": 465     # MB
}

# ============================================================================
# GREEN AI CONFIGURATION - Carbon Tracking
# ============================================================================

# Carbon intensity (gCO2 per kWh) - India grid average
# Source: Central Electricity Authority, India
CARBON_INTENSITY = float(os.getenv("CARBON_INTENSITY", "700"))

# Real-time carbon intensity API (optional)
CARBON_INTENSITY_API = os.getenv("CARBON_INTENSITY_API", "")
CARBON_INTENSITY_API_KEY = os.getenv("CARBON_INTENSITY_API_KEY", "")

# Power consumption estimates (watts)
CPU_POWER_WATTS = int(os.getenv("CPU_POWER_WATTS", "45"))  # Typical laptop CPU
GPU_POWER_WATTS = int(os.getenv("GPU_POWER_WATTS", "100"))  # If GPU used
IDLE_POWER_WATTS = int(os.getenv("IDLE_POWER_WATTS", "15"))

# Conventional AI comparison multiplier (how many times less efficient)
CONVENTIONAL_AI_MULTIPLIER = int(os.getenv("CONVENTIONAL_AI_MULTIPLIER", "50"))

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database path
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/gaia.db")
DATABASE_BACKUP_PATH = os.getenv("DATABASE_BACKUP_PATH", "data/backups/")

# Create directories if they don't exist
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(DATABASE_BACKUP_PATH).mkdir(parents=True, exist_ok=True)

# ============================================================================
# SCORE THRESHOLDS
# ============================================================================

GAIA_THRESHOLDS = {
    "excellent": int(os.getenv("THRESHOLD_EXCELLENT", "80")),
    "good": int(os.getenv("THRESHOLD_GOOD", "60")),
    "poor": int(os.getenv("THRESHOLD_POOR", "40")),
    "critical": int(os.getenv("THRESHOLD_CRITICAL", "20"))
}

# Status messages based on thresholds
STATUS_MESSAGES = {
    "excellent": "🌟 Excellent sustainability performance. You are a leader in environmental stewardship.",
    "good": "📈 Good performance. Minor improvements recommended to reach excellence.",
    "poor": "⚠️ Poor performance. Significant improvements required.",
    "critical": "🚨 CRITICAL CONDITION. Severe violations detected. Immediate action required."
}

# ============================================================================
# INDUSTRY BENCHMARKS (Indian Context)
# ============================================================================

INDUSTRY_BENCHMARKS = {
    "textile": {
        "co2_good": 500,      # tons/year
        "co2_critical": 5000,
        "water_good": 10000,   # million liters/year
        "water_critical": 50000,
        "waste_good": 100,     # tons/year
        "waste_critical": 1000
    },
    "chemical": {
        "co2_good": 1000,
        "co2_critical": 10000,
        "water_good": 20000,
        "water_critical": 100000,
        "waste_good": 200,
        "waste_critical": 2000
    },
    "steel": {
        "co2_good": 5000,
        "co2_critical": 50000,
        "water_good": 5000,
        "water_critical": 30000,
        "waste_good": 500,
        "waste_critical": 5000
    },
    "pharma": {
        "co2_good": 200,
        "co2_critical": 2000,
        "water_good": 5000,
        "water_critical": 25000,
        "waste_good": 50,
        "waste_critical": 500
    },
    "automobile": {
        "co2_good": 1000,
        "co2_critical": 8000,
        "water_good": 10000,
        "water_critical": 40000,
        "waste_good": 200,
        "waste_critical": 2000
    },
    "power": {
        "co2_good": 10000,
        "co2_critical": 100000,
        "water_good": 10000,
        "water_critical": 50000,
        "waste_good": 1000,
        "waste_critical": 10000
    },
    "food_processing": {
        "co2_good": 200,
        "co2_critical": 3000,
        "water_good": 5000,
        "water_critical": 20000,
        "waste_good": 100,
        "waste_critical": 1000
    },
    "default": {
        "co2_good": 1000,
        "co2_critical": 10000,
        "water_good": 10000,
        "water_critical": 50000,
        "waste_good": 100,
        "waste_critical": 1000
    }
}

# ============================================================================
# GOVERNMENT SCHEMES (Indian Context)
# ============================================================================

GOVERNMENT_SCHEMES = {
    "jal_jeevan_mission": {
        "name": "Jal Jeevan Mission",
        "description": "Har Ghar Jal - Tap water to every rural household",
        "applicable_for": ["water_conservation", "rural_development"],
        "subsidy_percent": 60,
        "website": "https://jaljeevanmission.gov.in"
    },
    "pm_kusum": {
        "name": "PM-KUSUM",
        "description": "Solar pumps for farmers and solarization of grid-connected pumps",
        "applicable_for": ["renewable_energy", "agriculture"],
        "subsidy_percent": 60,
        "website": "https://pmkusum.mnre.gov.in"
    },
    "ncap": {
        "name": "National Clean Air Programme",
        "description": "Air quality improvement in non-attainment cities",
        "applicable_for": ["air_pollution", "urban_development"],
        "subsidy_percent": 50,
        "website": "https://moef.gov.in/ncap"
    },
    "swachh_bharat": {
        "name": "Swachh Bharat Mission",
        "description": "Waste management and sanitation",
        "applicable_for": ["waste_management", "sanitation"],
        "subsidy_percent": 100,
        "website": "https://swachhbharatmission.gov.in"
    },
    "pm_surya_ghar": {
        "name": "PM Surya Ghar",
        "description": "Free electricity up to 300 units through rooftop solar",
        "applicable_for": ["renewable_energy", "residential"],
        "subsidy_percent": 40,
        "website": "https://pmsuryaghar.gov.in"
    }
}

# ============================================================================
# NOTIFICATION CONFIGURATION
# ============================================================================

NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "alerts@gaia.gov.in")
NOTIFICATION_SMS_ENABLED = os.getenv("NOTIFICATION_SMS_ENABLED", "False").lower() == "true"
NOTIFICATION_SMS_API_KEY = os.getenv("NOTIFICATION_SMS_API_KEY", "")

# ============================================================================
# API CONFIGURATION (External Services)
# ============================================================================

# Weather API for air quality context
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.openweathermap.org")

# Satellite imagery API
SATELLITE_API_KEY = os.getenv("SATELLITE_API_KEY", "")
SATELLITE_API_URL = os.getenv("SATELLITE_API_URL", "https://api.nasa.gov/planetary/earth")

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY", "gaia-sustainability-platform-secret-key-change-in-production")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_VOICE_PROCESSING = os.getenv("ENABLE_VOICE_PROCESSING", "True").lower() == "true"
ENABLE_IMAGE_ANALYSIS = os.getenv("ENABLE_IMAGE_ANALYSIS", "True").lower() == "true"
ENABLE_FRAUD_DETECTION = os.getenv("ENABLE_FRAUD_DETECTION", "True").lower() == "true"
ENABLE_REAL_TIME_CARBON = os.getenv("ENABLE_REAL_TIME_CARBON", "False").lower() == "true"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model_size(model_name):
    """Get model size in MB for given model"""
    if model_name in VOICE_MODEL_SIZES:
        return VOICE_MODEL_SIZES[model_name]
    return None

def get_industry_benchmarks(industry):
    """Get benchmarks for specific industry"""
    return INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["default"])

def get_threshold_status(score):
    """Get status based on score"""
    if score >= GAIA_THRESHOLDS["excellent"]:
        return "excellent"
    elif score >= GAIA_THRESHOLDS["good"]:
        return "good"
    elif score >= GAIA_THRESHOLDS["poor"]:
        return "poor"
    else:
        return "critical"

def get_status_message(score):
    """Get status message based on score"""
    status = get_threshold_status(score)
    return STATUS_MESSAGES[status]

def is_production():
    """Check if running in production mode"""
    return APP_ENV == "production"

def is_development():
    """Check if running in development mode"""
    return APP_ENV == "development"

# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_config():
    """Validate critical configuration settings"""
    issues = []
    
    # Check database path
    if not DATABASE_PATH:
        issues.append("DATABASE_PATH is not set")
    
    # Check model settings
    if VOICE_MODEL not in VOICE_MODEL_SIZES:
        issues.append(f"Invalid VOICE_MODEL: {VOICE_MODEL}. Must be one of {list(VOICE_MODEL_SIZES.keys())}")
    
    # Check thresholds
    if GAIA_THRESHOLDS["excellent"] <= GAIA_THRESHOLDS["good"]:
        issues.append("THRESHOLD_EXCELLENT must be greater than THRESHOLD_GOOD")
    
    if GAIA_THRESHOLDS["good"] <= GAIA_THRESHOLDS["poor"]:
        issues.append("THRESHOLD_GOOD must be greater than THRESHOLD_POOR")
    
    if issues:
        print("⚠️ Configuration Issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ Configuration validated successfully")
    return True

# Validate on import
if __name__ != "__main__":
    validate_config()
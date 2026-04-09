# app.py - Complete GAIA Platform
import streamlit as st # pyright: ignore[reportMissingImports]
import pandas as pd # pyright: ignore[reportMissingModuleSource]
import numpy as np # pyright: ignore[reportMissingImports]
import uuid
from datetime import datetime

# Import modules
from modules.text_analyzer import text_analyzer
from modules.fraud_detector import fraud_detector
from modules.image_analyzer import image_analyzer
from modules.voice_processor import voice_processor
from modules.score_calculator import score_calculator
from modules.notification import notification_system
from modules.carbon_tracker import tracker
from modules.database import db
import config

# Page configuration
st.set_page_config(
    page_title="GAIA - Sustainability Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-score {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    .excellent {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
    }
    .good {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
    }
    .poor {
        background-color: #fff3e0;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
    }
    .critical {
        background-color: #ffebee;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #f44336;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .voice-card {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🌍 GAIA - Sustainability Intelligence Platform")
st.caption("Green AI-Powered Environmental Compliance & Citizen Empowerment")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/earth-planet.png", width=80)
    st.header("GAIA Portal")
    
    portal = st.radio(
        "Select Portal",
        ["🏭 Officer Dashboard", "📱 Citizen Report", "🔍 Track Complaint", "📊 Analytics", "🌱 Green AI Metrics"]
    )
        
    st.divider()
    st.caption(f"Version {config.APP_VERSION}")
    st.caption("🌍 Sustainability for All")

# Main content
if portal == "🏭 Officer Dashboard":
    st.header("👩‍⚖️ Officer Dashboard")
    st.write("Analyze environmental reports, detect fraud, and take action.")
    
    tab1, tab2, tab3 = st.tabs(["📄 Analyze Report", "🚨 Fraud Alerts", "📋 Recent Reports"])
    
    with tab1:
        st.subheader("Upload Environmental Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            factory_name = st.text_input("Factory/Company Name", placeholder="e.g., ABC Textiles, Tirupur")
        
        with col2:
            industry = st.selectbox(
                "Industry Type", 
                ["Select Industry", "Textile", "Chemical", "Steel", "Pharma", "Automobile", "Power", "Food Processing", "Other"]
            )
            industry = None if industry == "Select Industry" else industry.lower()
        
        report_file = st.file_uploader("Upload Report (PDF/TXT)", type=['pdf', 'txt'])
        report_text = st.text_area("Or paste report text here", height=150, 
                                    placeholder="Paste sustainability report content here...")
        
        if st.button("🔍 Analyze Report", type="primary", use_container_width=True):
            if not factory_name:
                st.error("❌ Please enter factory/company name")
            elif not report_file and not report_text:
                st.error("❌ Please upload a file or paste report text")
            else:
                # Start carbon tracking
                tracker.start_operation("report_analysis")
                
                # Get text from file or text area
                if report_file:
                    with st.spinner("Reading file..."):
                        if report_file.type == "application/pdf":
                            try:
                                import pdfplumber
                                with pdfplumber.open(report_file) as pdf:
                                    text = "".join([page.extract_text() or "" for page in pdf.pages])
                            except Exception as e:
                                st.error(f"Error reading PDF: {e}")
                                text = ""
                        else:
                            text = report_file.read().decode()
                else:
                    text = report_text
                
                if not text.strip():
                    st.error("❌ No text content found in the file")
                else:
                    with st.spinner("Analyzing report with GAIA AI..."):
                        # Analyze text
                        analysis = text_analyzer.analyze(text)
                        
                        # Detect fraud with industry context
                        fraud = fraud_detector.detect(text, analysis['metrics'], industry=industry)
                        
                        # Calculate score
                        score = analysis['gaia_score']
                        status = score_calculator.get_status(score)
                        
                        # End tracking
                        emissions = tracker.end_operation()
                        
                        # Save to database
                        db.save_report(factory_name, text, score, fraud['is_fake'], fraud['fraud_score'], industry=industry)
                    
                    # Display Results
                    st.divider()
                    st.subheader("📊 Analysis Results")
                    
                    # Score display
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        status_class = status['status'].lower()
                        st.markdown(f"""
                        <div class="{status_class}">
                            <div class="big-score">{score}</div>
                            <h3 style="text-align:center">{status['icon']} {status['status']}</h3>
                            <p style="text-align:center">{status['message']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.subheader("📈 Key Metrics")
                        metrics = analysis['metrics']
                        for key, value in metrics.items():
                            if value:
                                metric_name = key.replace('_', ' ').title()
                                if key == 'co2_emissions':
                                    st.metric(metric_name, f"{value:,.0f} tons")
                                elif key == 'water_usage':
                                    st.metric(metric_name, f"{value:,.0f} ML")
                                elif key == 'waste_generated':
                                    st.metric(metric_name, f"{value:,.0f} tons")
                                elif key == 'renewable_percent':
                                    st.metric(metric_name, f"{value:.0f}%")
                                elif key == 'tree_planted':
                                    st.metric(metric_name, f"{value:,.0f}")
                                else:
                                    st.metric(metric_name, f"{value:,.0f}")
                            else:
                                st.metric(key.replace('_', ' ').title(), "Not Detected")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.subheader("🔍 Fraud Analysis")
                        if fraud['is_fake']:
                            st.error(f"⚠️ FAKE REPORT DETECTED")
                            st.warning(f"Fraud Score: {fraud['fraud_score']*100:.0f}%")
                            st.write("**Reasons:**")
                            for reason in fraud['reasons'][:3]:
                                st.write(f"• {reason}")
                        else:
                            st.success(f"✓ Report Appears Authentic")
                            st.info(f"Confidence: {(1-fraud['fraud_score'])*100:.0f}%")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Suggestions
                    st.subheader("💡 Improvement Suggestions")
                    for suggestion in analysis['suggestions']:
                        if "CRITICAL" in suggestion or "FINAL WARNING" in suggestion:
                            st.error(f"🚨 {suggestion}")
                        elif "WARNING" in suggestion:
                            st.warning(f"⚠️ {suggestion}")
                        else:
                            st.info(f"📌 {suggestion}")
                    
                    # Actions
                    st.divider()
                    st.subheader("📨 Automated Actions")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Generate and send warning
                        warning = notification_system.generate_warning(
                            factory_name, score, analysis['suggestions'], fraud['is_fake']
                        )
                        
                        if st.button("📧 Send Notification to Factory"):
                            notification_system.send(factory_name.replace(" ", ".").lower() + "@example.com", warning)
                            st.success(f"✅ Notification sent to {factory_name}")
                    
                    with col2:
                        if fraud['is_fake']:
                            st.error("🚨 This report has been flagged for fraud")
                            if st.button("📢 Escalate to Legal Department"):
                                st.warning("⚠️ Case escalated. Legal action initiated.")
                    
                    # Green AI Metrics
                    st.caption(f"🌱 AI Carbon Footprint for this analysis: **{emissions:.3f} gCO₂**")
    
    with tab2:
        st.subheader("🚨 Fraud Alerts")
        st.info("Reports flagged for fraud will appear here")
        reports = db.get_reports(10)
        if reports:
            fraud_alerts = [r for r in reports if r.get('is_fake', False)]
            if fraud_alerts:
                for report in fraud_alerts:
                    st.warning(f"⚠️ **{report.get('factory_name', 'Unknown')}** - Fraud Score: {report.get('fraud_score', 0)*100:.0f}%")
            else:
                st.success("✅ No fraud alerts. All reports appear authentic.")
        else:
            st.info("No reports analyzed yet")
    
    with tab3:
        st.subheader("📋 Recent Reports")
        reports = db.get_reports(10)
        if reports:
            for report in reports:
                status_icon = "🔴" if report.get('is_fake') else "🟢"
                st.write(f"{status_icon} **{report.get('factory_name', 'Unknown')}** - Score: {report.get('gaia_score', 0)} - {report.get('created_at', '')[:19]}")
        else:
            st.write("No reports analyzed yet")

elif portal == "📱 Citizen Report":
    st.header("📱 GAIA Citizen - Report Environmental Violation")
    st.write("Your voice matters. Report environmental violations easily.")
    
    # Add instructions
    st.info("📢 **How to report:** Upload photo evidence AND/OR record voice/type complaint")
    st.caption("🌐 GAIA will automatically translate your complaint to English for officers")
    
    # ============================================================
    # PHOTO UPLOAD SECTION (Always visible)
    # ============================================================
    st.subheader("📸 Upload Photo Evidence (Optional but Recommended)")
    
    photo = st.file_uploader(
        "Take or upload photo of the violation", 
        type=['jpg', 'png', 'jpeg'], 
        key="citizen_photo",
        help="Upload a clear photo of the environmental violation"
    )
    
    if photo:
        st.image(photo, caption="Uploaded Evidence", width=300)
        st.success("✅ Photo uploaded successfully!")
    
    st.divider()
    
    # ============================================================
    # INPUT METHOD SELECTION (Voice OR Text)
    # ============================================================
    st.subheader("📝 Describe the Issue")
    
    input_method = st.radio(
        "Choose how to describe your complaint:",
        ["🎤 Voice Input", "📝 Text Input"],
        horizontal=True,
        help="Choose either voice or text to describe the issue"
    )
    
    # Variables to store complaint data - Initialize with defaults
    complaint_text_original = ""
    complaint_text_translated = ""
    detected_lang = "en"
    lang_name = "English"
    complaint_type = "unknown"
    
    # ============================================================
    # VOICE INPUT SECTION
    # ============================================================
    if input_method == "🎤 Voice Input":
        st.write("Speak in any language - GAIA understands all!")
        st.caption("💡 Supported languages: Tamil, Hindi, Telugu, Bengali, Marathi, Malayalam, Kannada, Gujarati, Punjabi, English, and more")
        
        # Live voice recording
        voice_audio = st.audio_input("🎙️ Click the microphone to start recording", key="citizen_voice")
        
        if voice_audio:
            st.success("✅ Voice recording received!")
            st.audio(voice_audio, format="audio/wav")
            
            # Process voice automatically
            with st.spinner("Processing your voice complaint with GAIA AI..."):
                voice_bytes = voice_audio.getvalue()
                voice_result = voice_processor.process(voice_bytes)
                
                if voice_result and voice_result.get('success'):
                    # Store in session
                    st.session_state.voice_complaint = voice_result
                    
                    # Show detected language
                    st.write(f"**🌐 Detected Language:** {voice_result.get('language_name', 'English')}")
                    st.write(f"**📊 Confidence:** {voice_result.get('confidence', 0.85)*100:.0f}%")
                    
                    # Show original transcript
                    with st.expander("📝 Original Complaint (Your Language)", expanded=True):
                        if 'original_transcript' in voice_result:
                            st.write(voice_result['original_transcript'])
                            complaint_text_original = voice_result['original_transcript']
                        else:
                            st.write(voice_result.get('transcript', 'No transcript available'))
                            complaint_text_original = voice_result.get('transcript', '')
                    
                    # Show English translation
                    with st.expander("🇬🇧 English Translation (For Officers)", expanded=True):
                        if 'translated_transcript' in voice_result:
                            st.success(voice_result['translated_transcript'])
                            complaint_text_translated = voice_result['translated_transcript']
                        else:
                            st.write(voice_result.get('transcript', 'No translation available'))
                            complaint_text_translated = voice_result.get('transcript', '')
                    
                    # Show extracted details
                    details = voice_result.get('complaint_details', {})
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        if details.get('complaint_type'):
                            complaint_type = details.get('complaint_type')
                            type_icons = {
                                'water_pollution': '💧 Water Pollution',
                                'air_pollution': '💨 Air Pollution',
                                'waste_dumping': '🗑️ Waste Dumping',
                                'noise_pollution': '🔊 Noise Pollution'
                            }
                            st.info(f"{type_icons.get(complaint_type, '📋 ' + complaint_type)}")
                    
                    with col_d2:
                        if details.get('urgency') == 'HIGH':
                            st.warning("🚨 URGENT - Priority complaint")
                    
                    if details.get('location_mentioned'):
                        st.write(f"📍 **Location detected:** {details['location_mentioned']}")
                    
                    # Set language info
                    detected_lang = voice_result.get('language_code', 'en')
                    lang_name = voice_result.get('language_name', 'English')
                    
                    st.success("✅ Voice complaint processed and translated to English!")
                else:
                    st.error("Could not process voice. Please try again or use Text Input.")
    
    # ============================================================
    # TEXT INPUT SECTION
    # ============================================================
    else:  # Text Input
        st.write("Type your complaint in any language - GAIA will translate it!")
        
        # Language hint row
        st.caption("💡 Examples in different languages:")
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        with col_h1:
            st.caption("🇮🇳 Tamil: நீர் மாசு")
        with col_h2:
            st.caption("🇮🇳 Hindi: जल प्रदूषण")
        with col_h3:
            st.caption("🇮🇳 Telugu: నీటి కాలుష్యం")
        with col_h4:
            st.caption("🇮🇳 English: Water pollution")
        
        # Text area for complaint
        text_complaint = st.text_area(
            "Enter your complaint:",
            height=120,
            placeholder="Example in Tamil: எங்கள் கிராமத்தின் பின்புறம் ஒரு தொழிற்சாலை ஆற்றில் ரசாயன கழிவுகளை கொட்டுகிறது...\n\nOr in Hindi: हमारे गाँव के पास एक फैक्ट्री नदी में रासायनिक कचरा फेंक रही है...\n\nOr in English: Factory behind our village is dumping chemical waste into the river...",
            help="Type your complaint in any language. GAIA will detect and translate it."
        )
        
        # Language selection
        col_lang1, col_lang2 = st.columns([2, 1])
        with col_lang1:
            manual_lang = st.selectbox(
                "Select your language (optional):",
                ["Auto-detect", "Tamil (தமிழ்)", "Hindi (हिन्दी)", "Telugu (తెలుగు)", "Bengali (বাংলা)", 
                 "Marathi (मराठी)", "Malayalam (മലയാളം)", "Kannada (ಕನ್ನಡ)", "Gujarati (ગુજરાતી)", 
                 "Punjabi (ਪੰਜਾਬੀ)", "English"]
            )
        with col_lang2:
            st.write("")
            st.write("")
            process_text = st.button("🔄 Translate Complaint", use_container_width=True)
        
        if process_text and text_complaint:
            with st.spinner("Translating your complaint..."):
                try:
                    from deep_translator import GoogleTranslator
                    
                    # Determine source language
                    if manual_lang != "Auto-detect":
                        lang_map = {
                            "Tamil (தமிழ்)": 'ta', "Hindi (हिन्दी)": 'hi', "Telugu (తెలుగు)": 'te',
                            "Bengali (বাংলা)": 'bn', "Marathi (मराठी)": 'mr', "Malayalam (മലയാളം)": 'ml',
                            "Kannada (ಕನ್ನಡ)": 'kn', "Gujarati (ગુજરાતી)": 'gu', "Punjabi (ਪੰਜਾਬੀ)": 'pa',
                            "English": 'en'
                        }
                        source_lang = lang_map.get(manual_lang, 'auto')
                    else:
                        source_lang = 'auto'
                    
                    # Translate to English
                    translator = GoogleTranslator(source=source_lang, target='en')
                    translated_text = translator.translate(text_complaint)
                    
                    # Get language name
                    lang_names = {
                        'ta': 'Tamil (தமிழ்)', 'hi': 'Hindi (हिन्दी)', 'te': 'Telugu (తెలుగు)',
                        'bn': 'Bengali (বাংলা)', 'mr': 'Marathi (मराठी)', 'ml': 'Malayalam (മലയാളം)',
                        'kn': 'Kannada (ಕನ್ನಡ)', 'gu': 'Gujarati (ગુજરાતી)', 'pa': 'Punjabi (ਪੰਜਾਬੀ)',
                        'en': 'English'
                    }
                    detected_lang = source_lang if source_lang != 'auto' else 'en'
                    lang_name = lang_names.get(detected_lang, detected_lang)
                    
                    # Extract complaint details
                    details = voice_processor._extract_complaint_details(translated_text)
                    complaint_type = details.get('complaint_type', 'unknown')
                    
                    # Store in session
                    text_complaint_data = {
                        'original': text_complaint,
                        'translated': translated_text,
                        'language_code': detected_lang,
                        'language_name': lang_name,
                        'complaint_details': details
                    }
                    st.session_state.text_complaint_data = text_complaint_data
                    
                    # Set variables for submission
                    complaint_text_original = text_complaint
                    complaint_text_translated = translated_text
                    
                    # Display results
                    st.success(f"✅ Translation complete!")
                    st.write(f"**🌐 Detected Language:** {lang_name}")
                    
                    with st.expander("📝 Original Complaint (Your Language)", expanded=True):
                        st.write(text_complaint)
                    
                    with st.expander("🇬🇧 English Translation (For Officers)", expanded=True):
                        st.success(translated_text)
                    
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        if details.get('complaint_type'):
                            type_icons = {
                                'water_pollution': '💧 Water Pollution',
                                'air_pollution': '💨 Air Pollution',
                                'waste_dumping': '🗑️ Waste Dumping',
                                'noise_pollution': '🔊 Noise Pollution'
                            }
                            st.info(f"{type_icons.get(details['complaint_type'], details['complaint_type'])}")
                    with col_d2:
                        if details.get('urgency') == 'HIGH':
                            st.warning("🚨 URGENT - Priority complaint")
                    
                    if details.get('location_mentioned'):
                        st.write(f"📍 **Location detected:** {details['location_mentioned']}")
                    
                except Exception as e:
                    st.error(f"Translation error: {e}")
                    st.info("Please check your internet connection and try again.")
        
        elif process_text and not text_complaint:
            st.warning("Please enter your complaint text.")
        
        # If already processed, show stored data
        if 'text_complaint_data' in st.session_state and not process_text:
            text_complaint_data = st.session_state.text_complaint_data
            complaint_text_original = text_complaint_data['original']
            complaint_text_translated = text_complaint_data['translated']
            detected_lang = text_complaint_data['language_code']
            lang_name = text_complaint_data['language_name']
            complaint_type = text_complaint_data.get('complaint_details', {}).get('complaint_type', 'unknown')
            
            st.success(f"✅ Previously translated from {lang_name}")
            with st.expander("📝 Original Complaint", expanded=False):
                st.write(complaint_text_original)
            with st.expander("🇬🇧 English Translation", expanded=False):
                st.success(complaint_text_translated)
    
    st.divider()
    
    # ============================================================
    # LOCATION AND SUBMISSION (Common for all methods)
    # ============================================================
    st.subheader("📍 Location Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        location = st.text_input(
            "Location / Address", 
            placeholder="e.g., Near Noyyal River, Tirupur",
            help="Enter the exact location where the violation is happening"
        )
    
    with col2:
        anonymous = st.checkbox("Report anonymously (your identity will be protected)")
    
    # Show complaint summary
    if complaint_text_original:
        st.markdown("---")
        st.subheader("📋 Complaint Summary")
        st.info(f"📝 **Your complaint:** {complaint_text_original[:200]}...")
        if complaint_text_translated and complaint_text_translated != complaint_text_original:
            st.caption(f"🇬🇧 **English translation:** {complaint_text_translated[:200]}...")
        if photo:
            st.caption(f"📸 **Photo evidence:** Uploaded")
    
    # ============================================================
    # SUBMIT BUTTON
    # ============================================================
    if st.button("🚨 Submit Report", type="primary", use_container_width=True):
        # Validation
        has_voice = 'voice_complaint' in st.session_state and st.session_state.voice_complaint
        has_text = complaint_text_original and complaint_text_original.strip()
        
        if not has_voice and not has_text:
            st.error("❌ Please either record a voice complaint OR type your complaint")
        elif not location:
            st.error("❌ Please provide location")
        else:
            tracker.start_operation("citizen_report")
            
            with st.spinner("Processing your report with GAIA AI..."):
                tracking_id = f"GAIA-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                
                # Process photo if uploaded
                photo_result = None
                if photo:
                    photo_result = image_analyzer.analyze(photo.getvalue())
                
                # Get complaint data from voice or text
                if has_voice:
                    v_result = st.session_state.voice_complaint
                    complaint_type = v_result.get('complaint_details', {}).get('complaint_type', 'unknown')
                    original_text = v_result.get('original_transcript', v_result.get('transcript', ''))
                    translated_text = v_result.get('translated_transcript', '')
                    language_code = v_result.get('language_code', 'en')
                else:
                    original_text = complaint_text_original
                    translated_text = complaint_text_translated
                    language_code = detected_lang
                
                # Debug print
                print(f"🔍 Saving complaint - Tracking ID: {tracking_id}")
                print(f"   Type: {complaint_type}, Location: {location}")
                print(f"   Original: {original_text[:100]}...")
                print(f"   Translated: {translated_text[:100]}...")
                
                # Save to database (ONLY ONCE)
                result = db.save_complaint(tracking_id, complaint_type, location, original_text, translated_text, language_code)
                
                if result:
                    print(f"✅ Complaint saved successfully with ID: {result}")
                else:
                    print(f"❌ Failed to save complaint")
                
                # Generate acknowledgment
                ack = notification_system.generate_citizen_acknowledgment(tracking_id)
                
                # Send acknowledgment (simulated)
                if not anonymous:
                    notification_system.send("citizen@example.com", ack)
                
            emissions = tracker.end_operation()
            
            # Clear session data
            if 'voice_complaint' in st.session_state:
                del st.session_state.voice_complaint
            if 'text_complaint_data' in st.session_state:
                del st.session_state.text_complaint_data
            
            # Show success
            st.balloons()
            st.success(f"✅ Report Submitted Successfully!")
            st.info(f"📌 **Tracking ID:** `{tracking_id}`")
            
            # Show complete report summary
            st.write("---")
            st.write("**📋 Complete Report Summary:**")
            
            # Photo evidence
            if photo:
                st.write("📸 **Photo Evidence:** Uploaded and analyzed")
                if photo_result and photo_result.get('has_violation'):
                    st.warning(photo_result.get('complaint_text', 'Violation detected in photo'))
                else:
                    st.write("No violation detected in photo")
            
            # Complaint text
            st.write(f"**📝 Original Complaint ({language_code.upper()}):** {original_text[:300]}")
            if translated_text and translated_text != original_text:
                st.write(f"**🇬🇧 English Translation:** {translated_text[:300]}")
            
            # Location
            st.write(f"**📍 Location:** {location}")
            
            # Tracking info
            st.write("---")
            st.write("**🔍 Track your complaint:**")
            st.code(f"Tracking ID: {tracking_id}")
            st.info("Go to 'Track Complaint' portal and enter this ID to check status")
            
            st.write("---")
            st.write("**⏳ What happens next:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write("1️⃣ AI Analysis")
                st.write("✓ Complete")
            with col2:
                st.write("2️⃣ Officer Assigned")
                st.write("⏳ Within 24 hrs")
            with col3:
                st.write("3️⃣ Site Inspection")
                st.write("⏳ Within 7 days")
            with col4:
                st.write("4️⃣ Action Report")
                st.write("⏳ Sent via SMS/Email")
            
            st.caption(f"🌱 This report carbon footprint: **{emissions:.3f} gCO₂**")
            
            # Reset button
            if st.button("📝 Report Another Issue"):
                st.rerun()

elif portal == "🔍 Track Complaint":
    st.header("🔍 Track Your Complaint")
    st.write("Enter your Tracking ID to check the status of your complaint.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tracking_input = st.text_input(
            "Enter Tracking ID",
            placeholder="e.g., GAIA-20250407-ABC123",
            help="Enter the Tracking ID you received after submitting your complaint"
        ).upper().strip()
    
    with col2:
        track_button = st.button("🔍 Track Complaint", type="primary", use_container_width=True)
    
    if track_button and tracking_input:
        with st.spinner("Fetching complaint details..."):
            complaint = db.get_complaint_by_tracking_id(tracking_input)
            
            if complaint:
                st.success(f"✅ Complaint Found!")
                
                # Status display
                status = complaint.get('status', 'PENDING')
                status_icons = {
                    'PENDING': ('🟡', 'Pending Review'),
                    'IN_PROGRESS': ('🔵', 'Under Investigation'),
                    'RESOLVED': ('🟢', 'Resolved'),
                    'REJECTED': ('🔴', 'Rejected')
                }
                status_icon, status_text = status_icons.get(status, ('⚪', status))
                
                # Progress bar
                progress_map = {'PENDING': 25, 'IN_PROGRESS': 50, 'RESOLVED': 100, 'REJECTED': 100}
                progress_value = progress_map.get(status, 0)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a237e, #0d47a1); padding: 20px; border-radius: 15px; margin: 10px 0;">
                    <h2 style="color: white; text-align: center;">{status_icon} Status: {status_text}</h2>
                    <p style="color: white; text-align: center;">Tracking ID: {tracking_input}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.progress(progress_value / 100, text="Complaint Progress")
                
                # Status steps
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown("✅ **Submitted**" if progress_value >= 25 else "🟡 **Submitted**")
                with col2:
                    st.markdown("✅ **Under Review**" if progress_value >= 50 else "🟡 **Under Review**")
                with col3:
                    st.markdown("✅ **Action Taken**" if progress_value >= 75 else "🟡 **Action Taken**")
                with col4:
                    st.markdown("✅ **Completed**" if progress_value == 100 else "🟡 **Completed**")
                
                # Complaint details
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Complaint Type:** {complaint.get('complaint_type', 'Unknown').replace('_', ' ').title()}")
                    st.write(f"**Location:** {complaint.get('location', 'Not provided')}")
                    st.write(f"**Submitted:** {complaint.get('created_at', 'Unknown')}")
                    if complaint.get('officer_assigned'):
                        st.write(f"**Officer:** {complaint.get('officer_assigned')}")
                
                with col2:
                    if complaint.get('original_text'):
                        with st.expander("View Your Complaint"):
                            st.write(complaint.get('original_text'))
                    if complaint.get('translated_text') and complaint.get('translated_text') != complaint.get('original_text'):
                        with st.expander("View English Translation"):
                            st.write(complaint.get('translated_text'))
                
                # ============================================================
                # FEEDBACK SECTION (Only when status is RESOLVED)
                # ============================================================
                if status == 'RESOLVED':
                    st.markdown("---")
                    st.subheader("📝 Share Your Feedback")
                    st.write("How satisfied are you with the resolution of your complaint?")
                    
                    feedback_key = f"feedback_given_{tracking_input}"
                    if feedback_key not in st.session_state:
                        st.session_state[feedback_key] = False
                    
                    if not st.session_state[feedback_key]:
                        rating = st.select_slider(
                            "Rate your satisfaction",
                            options=["Very Poor", "Poor", "Average", "Good", "Excellent"],
                            value="Good"
                        )
                        
                        feedback_text = st.text_area("Your feedback (optional)", placeholder="Share your experience...")
                        
                        if st.button("Submit Feedback", type="primary"):
                            # Save feedback
                            feedback_data = {
                                'tracking_id': tracking_input,
                                'rating': rating,
                                'feedback': feedback_text,
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if 'feedbacks' not in st.session_state:
                                st.session_state.feedbacks = []
                            st.session_state.feedbacks.append(feedback_data)
                            
                            st.session_state[feedback_key] = True
                            st.success("✅ Thank you for your feedback!")
                            st.rerun()
                    else:
                        st.info("✅ Thank you for your feedback! Your response has been recorded.")
                
                # Next steps
                st.markdown("---")
                if status == 'PENDING':
                    st.info("🔄 Your complaint is pending review. An officer will be assigned within 24 hours.")
                elif status == 'IN_PROGRESS':
                    st.warning("🔍 Your complaint is under investigation.")
                elif status == 'RESOLVED':
                    st.success("✅ Your complaint has been resolved. Thank you for helping protect the environment!")
                elif status == 'REJECTED':
                    st.error("❌ Your complaint could not be verified. Please contact support for more information.")
                
            else:
                st.error(f"❌ No complaint found with Tracking ID: {tracking_input}")
    
    elif track_button and not tracking_input:
        st.warning("⚠️ Please enter your Tracking ID")

elif portal == "📊 Analytics":
    st.header("📊 Sustainability Analytics - Officer Dashboard")
    st.write("Manage and track citizen complaints, monitor fraud detection, and review feedback.")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Reports by Score Range", "🚨 Fraud Detection Stats", "📱 Citizen Complaints", "📨 Notifications Sent"])
    
    # ============================================================
    # TAB 1: Reports by Score Range
    # ============================================================
    with tab1:
        st.subheader("📈 Reports by Score Range")
        
        reports = db.get_reports(100)
        if reports:
            # Score distribution chart
            score_ranges = {
                "Excellent (80-100)": 0,
                "Good (60-79)": 0,
                "Poor (40-59)": 0,
                "Critical (0-39)": 0
            }
            
            for report in reports:
                score = report.get('gaia_score', 0)
                if score >= 80:
                    score_ranges["Excellent (80-100)"] += 1
                elif score >= 60:
                    score_ranges["Good (60-79)"] += 1
                elif score >= 40:
                    score_ranges["Poor (40-59)"] += 1
                else:
                    score_ranges["Critical (0-39)"] += 1
            
            # Create bar chart
            import plotly.express as px
            import pandas as pd
            
            df_scores = pd.DataFrame({
                'Range': list(score_ranges.keys()),
                'Count': list(score_ranges.values())
            })
            
            fig = px.bar(df_scores, x='Range', y='Count', title='Reports Distribution by Score',
                        color='Count', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Excellent", score_ranges["Excellent (80-100)"])
            with col2:
                st.metric("Good", score_ranges["Good (60-79)"])
            with col3:
                st.metric("Poor", score_ranges["Poor (40-59)"])
            with col4:
                st.metric("Critical", score_ranges["Critical (0-39)"])
            
            with st.expander("📋 Recent Reports Details"):
                for report in reports[:10]:
                    status_color = "🟢" if report.get('gaia_score', 0) >= 60 else "🔴"
                    st.write(f"{status_color} **{report.get('factory_name', 'Unknown')}** - Score: {report.get('gaia_score', 0)} - {report.get('created_at', '')[:19]}")
        else:
            st.info("No reports analyzed yet")
    
    # ============================================================
    # TAB 2: Fraud Detection Stats
    # ============================================================
    with tab2:
        st.subheader("🚨 Fraud Detection Statistics")
        
        reports = db.get_reports(100)
        if reports:
            fraud_count = sum(1 for r in reports if r.get('is_fake', False))
            authentic_count = len(reports) - fraud_count
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Reports", len(reports))
            with col2:
                st.metric("Fake Reports Detected", fraud_count, delta=f"{fraud_count/len(reports)*100:.0f}% of total" if reports else "0%")
            with col3:
                st.metric("Authentic Reports", authentic_count)
            
            # Fraud pie chart
            fig = px.pie(values=[fraud_count, authentic_count], names=['Fake Reports', 'Authentic Reports'],
                        title='Fraud Detection Analysis', color_discrete_sequence=['red', 'green'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Fraud alerts list
            st.subheader("🚨 Recent Fraud Alerts")
            fraud_reports = [r for r in reports if r.get('is_fake', False)]
            if fraud_reports:
                for report in fraud_reports[:10]:
                    st.warning(f"⚠️ **{report.get('factory_name', 'Unknown')}** - Fraud Score: {report.get('fraud_score', 0)*100:.0f}% - {report.get('created_at', '')[:19]}")
            else:
                st.success("✅ No fraud alerts detected")
        else:
            st.info("No reports analyzed yet")
    
    # ============================================================
    # TAB 3: Citizen Complaints (Officer Management)
    # ============================================================
    with tab3:
        st.subheader("📱 Citizen Complaints Management")
        st.write("Track, update status, and manage citizen complaints.")
        
        # ============================================================
        # SECTION A: Search by Tracking ID
        # ============================================================
        with st.expander("🔍 Search Complaint by Tracking ID", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                search_tracking = st.text_input("Enter Tracking ID", placeholder="e.g., GAIA-20250409-ABC123", key="search_tracking")
            with col2:
                search_button = st.button("🔍 Search", key="search_btn", use_container_width=True)
            
            if search_button and search_tracking:
                complaint = db.get_complaint_by_tracking_id(search_tracking.upper())
                if complaint:
                    st.session_state.selected_complaint = complaint
                    st.success(f"✅ Complaint found!")
                else:
                    st.error(f"No complaint found with Tracking ID: {search_tracking}")
        
        # ============================================================
        # SECTION B: Update Complaint Status
        # ============================================================
        if 'selected_complaint' in st.session_state:
            complaint = st.session_state.selected_complaint
            
            st.markdown("---")
            st.subheader(f"📋 Update Status - {complaint.get('tracking_id')}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Complaint Type:** {complaint.get('complaint_type', 'Unknown').replace('_', ' ').title()}")
                st.write(f"**Location:** {complaint.get('location', 'Not provided')}")
                st.write(f"**Current Status:** {complaint.get('status', 'PENDING')}")
                st.write(f"**Submitted On:** {complaint.get('created_at', 'Unknown')}")
            
            with col2:
                st.write(f"**Language:** {complaint.get('language_code', 'en').upper()}")
                if complaint.get('original_text'):
                    with st.expander("View Original Complaint"):
                        st.write(complaint.get('original_text'))
                if complaint.get('translated_text'):
                    with st.expander("View English Translation"):
                        st.write(complaint.get('translated_text'))
            
            # Status Update Form
            st.markdown("---")
            st.subheader("📌 Update Status")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                new_status = st.selectbox(
                    "Select New Status",
                    ["PENDING", "IN_PROGRESS", "RESOLVED", "REJECTED"],
                    index=["PENDING", "IN_PROGRESS", "RESOLVED", "REJECTED"].index(complaint.get('status', 'PENDING'))
                )
            
            with col2:
                officer_name = st.text_input("Officer Name", placeholder="e.g., Inspector Kumar", key="officer_name")
            
            with col3:
                inspection_date = st.date_input("Inspection Date", value=None, key="inspection_date")
            
            if st.button("✅ Update Status", type="primary", key="update_status_btn"):
                result = db.update_complaint_status(
                    complaint.get('tracking_id'),
                    new_status,
                    officer_name if officer_name else None,
                    str(inspection_date) if inspection_date else None
                )
                
                if result:
                    st.success(f"✅ Complaint status updated to {new_status}!")
                    # Refresh the complaint data
                    updated_complaint = db.get_complaint_by_tracking_id(complaint.get('tracking_id'))
                    st.session_state.selected_complaint = updated_complaint
                    st.rerun()
                else:
                    st.error("❌ Failed to update status")
        
        # ============================================================
        # SECTION C: All Complaints List
        # ============================================================
        st.markdown("---")
        st.subheader("📋 All Citizen Complaints")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "PENDING", "IN_PROGRESS", "RESOLVED", "REJECTED"], key="status_filter")
        with col2:
            type_filter = st.selectbox("Filter by Type", ["All", "water_pollution", "air_pollution", "waste_dumping", "noise_pollution"], key="type_filter")
        
        # Get complaints with filters
        complaints = db.get_complaints(50)
        
        if complaints:
            # Apply filters
            filtered_complaints = complaints
            if status_filter != "All":
                filtered_complaints = [c for c in filtered_complaints if c.get('status') == status_filter]
            if type_filter != "All":
                filtered_complaints = [c for c in filtered_complaints if c.get('complaint_type') == type_filter]
            
            # Display complaints in a table
            for complaint in filtered_complaints:
                status_icon = {
                    'PENDING': '🟡',
                    'IN_PROGRESS': '🔵',
                    'RESOLVED': '🟢',
                    'REJECTED': '🔴'
                }.get(complaint.get('status'), '⚪')
                
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                    with col1:
                        st.write(f"{status_icon} **{complaint.get('tracking_id')}**")
                    with col2:
                        st.write(complaint.get('complaint_type', 'Unknown').replace('_', ' ').title())
                    with col3:
                        st.write(complaint.get('location', 'N/A')[:30])
                    with col4:
                        st.write(complaint.get('status', 'PENDING'))
                    with col5:
                        if st.button("View", key=f"view_{complaint.get('tracking_id')}"):
                            st.session_state.selected_complaint = complaint
                            st.rerun()
                    st.divider()
        else:
            st.info("No complaints found")
        
        # ============================================================
        # SECTION D: Citizen Feedback View
        # ============================================================
        st.markdown("---")
        st.subheader("📝 Citizen Feedback")
        st.write("Feedback received from citizens after complaint resolution")
        
        if 'feedbacks' in st.session_state and st.session_state.feedbacks:
            for fb in st.session_state.feedbacks:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.write(f"**{fb['tracking_id']}**")
                    with col2:
                        st.write(f"⭐ **Rating:** {fb['rating']}")
                    st.write(f"**Feedback:** {fb['feedback']}")
                    st.write(f"**Date:** {fb['timestamp']}")
                    st.divider()
        else:
            st.info("No feedback received yet")
        
        # ============================================================
        # SECTION E: Delete Complaint (Officer Only)
        # ============================================================
        st.markdown("---")
        st.subheader("🗑️ Delete Complaint (Officer Only)")
        st.warning("⚠️ This action is permanent and cannot be undone! Only use this for completed cases.")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            delete_tracking_id = st.text_input("Enter Tracking ID to Delete", placeholder="GAIA-YYYYMMDD-XXXXXX", key="delete_tracking")
        with col2:
            confirm_delete = st.checkbox("Confirm Deletion", key="confirm_delete")
        
        if st.button("🗑️ Permanently Delete Complaint", type="secondary", key="delete_btn"):
            if not delete_tracking_id:
                st.error("❌ Please enter Tracking ID")
            elif not confirm_delete:
                st.error("❌ Please confirm deletion by checking the box")
            else:
                # Delete from database
                try:
                    import sqlite3
                    conn = sqlite3.connect("data/gaia.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM complaints WHERE tracking_id = ?", (delete_tracking_id.upper(),))
                    conn.commit()
                    rows_deleted = cursor.rowcount
                    conn.close()
                    
                    if rows_deleted > 0:
                        st.success(f"✅ Complaint {delete_tracking_id.upper()} has been permanently deleted!")
                        # Clear selected complaint if it was the deleted one
                        if 'selected_complaint' in st.session_state and st.session_state.selected_complaint.get('tracking_id') == delete_tracking_id.upper():
                            del st.session_state.selected_complaint
                        st.rerun()
                    else:
                        st.error(f"❌ No complaint found with Tracking ID: {delete_tracking_id}")
                except Exception as e:
                    st.error(f"Error deleting complaint: {e}")
    
    # ============================================================
    # TAB 4: Notifications Sent
    # ============================================================
    with tab4:
        st.subheader("📨 Notifications Sent History")
        
        history = notification_system.get_history()
        if history:
            st.metric("Total Notifications Sent", len(history))
            
            for notif in history[-20:]:
                with st.container():
                    st.write(f"**To:** {notif.get('to', 'Unknown')}")
                    st.write(f"**Type:** {notif.get('type', 'Unknown')}")
                    st.write(f"**Time:** {notif.get('timestamp', 'Unknown')}")
                    st.write(f"**Subject:** {notif.get('subject', 'N/A')}")
                    st.divider()
        else:
            st.info("No notifications sent yet")

elif portal == "🌱 Green AI Metrics":
    st.header("🌱 Green AI - Carbon Footprint Dashboard")
    st.write("GAIA is built with sustainability at its core. Here's our AI's environmental impact.")
    
    col1, col2, col3 = st.columns(3)
    
    summary = tracker.get_summary()
    
    with col1:
        st.metric("Total Carbon Emitted", f"{summary['total_emissions_g']:.3f} gCO₂")
        st.caption("Equivalent to driving a car for 0.01 km")
    
    with col2:
        st.metric("Total Energy Used", f"{summary['total_energy_kwh']:.6f} kWh")
        st.caption("Less than charging a smartphone once")
    
    with col3:
        st.metric("Operations Tracked", summary['operations_count'])
        st.caption("AI analyses performed")
    
    st.divider()
    
    st.subheader("📊 Comparison with Conventional AI")
    
    conventional = summary['total_emissions_g'] * 50
    saved = conventional - summary['total_emissions_g']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Conventional AI Would Emit", f"{conventional:.3f} gCO₂")
        st.progress(1.0, text="100%")
    
    with col2:
        st.metric("GAIA Actually Emitted", f"{summary['total_emissions_g']:.3f} gCO₂")
        st.progress(summary['total_emissions_g'] / max(conventional, 1), text=f"{summary['total_emissions_g']/conventional*100:.1f}%")
    
    st.success(f"💚 **GAIA saved {saved:.3f} gCO₂ compared to conventional AI solutions!**")
    
    # Display carbon equivalents if available
    if hasattr(tracker, 'get_equivalents'):
        equivalents = tracker.get_equivalents()
        st.divider()
        st.subheader("🌍 Carbon Equivalents")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🚗 Car Travel", f"{equivalents['car_km']} km")
        with col2:
            st.metric("📱 Phone Charges", f"{equivalents['smartphone_charges']:,}")
        with col3:
            st.metric("🌳 Tree Days", f"{equivalents['tree_days']:,}")
    
    st.divider()
    
    st.subheader("🌍 Why Green AI Matters")
    st.write("""
    - **Conventional AI** for sustainability often runs on cloud GPUs powered by fossil fuels
    - **GAIA** uses lightweight models (DistilBERT: 66MB, Whisper Tiny: 39MB, MobileNet: 16MB)
    - **Result:** Same insights with 98% less carbon footprint
    - **Our commitment:** We measure what we emit because we believe AI should be part of the solution, not the problem
    """)

# Footer
st.markdown("---")
st.caption("🌍 GAIA - Green AI for Sustainability | Empowering Officers, Citizens, and the Planet")
st.caption("© 2026 GAIA Platform | Carbon-Aware Intelligence")
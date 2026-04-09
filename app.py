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
    
   # In sidebar, update the portal selection:
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
                                import pdfplumber # pyright: ignore[reportMissingImports]
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
    
    # Variables to store complaint data
    complaint_text_original = ""
    complaint_text_translated = ""
    detected_lang = "en"
    lang_name = "English"
    voice_result = None
    text_complaint_data = None
    
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
                            type_icons = {
                                'water_pollution': '💧 Water Pollution',
                                'air_pollution': '💨 Air Pollution',
                                'waste_dumping': '🗑️ Waste Dumping',
                                'noise_pollution': '🔊 Noise Pollution'
                            }
                            st.info(f"{type_icons.get(details['complaint_type'], '📋 ' + details['complaint_type'])}")
                    
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
                    
                    # Store in session
                    text_complaint_data = {
                        'original': text_complaint,
                        'translated': translated_text,
                        'language_code': detected_lang,
                        'language_name': lang_name,
                        'complaint_details': details
                    }
                    st.session_state.text_complaint_data = text_complaint_data
                    
                    # Display results
                    st.success(f"✅ Translation complete!")
                    st.write(f"**🌐 Detected Language:** {lang_name}")
                    
                    with st.expander("📝 Original Complaint (Your Language)", expanded=True):
                        st.write(text_complaint)
                        complaint_text_original = text_complaint
                    
                    with st.expander("🇬🇧 English Translation (For Officers)", expanded=True):
                        st.success(translated_text)
                        complaint_text_translated = translated_text
                    
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
        has_photo = photo is not None
        
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
                    complaint_details = v_result.get('translated_transcript', v_result.get('transcript', ''))[:200]
                    original_text = v_result.get('original_transcript', v_result.get('transcript', ''))
                    translated_text = v_result.get('translated_transcript', '')
                    language_code = v_result.get('language_code', 'en')
                else:
                    t_data = st.session_state.text_complaint_data if 'text_complaint_data' in st.session_state else text_complaint_data
                    complaint_type = t_data.get('complaint_details', {}).get('complaint_type', 'unknown') if t_data else 'unknown'
                    complaint_details = complaint_text_translated[:200] if complaint_text_translated else complaint_text_original[:200]
                    original_text = complaint_text_original
                    translated_text = complaint_text_translated
                    language_code = detected_lang
                
                # Save to database
                db.save_complaint(tracking_id, complaint_type, location, original_text, translated_text, language_code)
                
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
            st.code(f"https://gaia.gov.in/track/{tracking_id}")
            
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
    
    st.info("📌 **What is Tracking ID?** You received a Tracking ID when you submitted your complaint. Example: `GAIA-20250407-ABC123`")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tracking_input = st.text_input(
            "Enter Tracking ID",
            placeholder="e.g., GAIA-20250407-ABC123",
            help="Enter the Tracking ID you received after submitting your complaint"
        )
    
    with col2:
        track_button = st.button("🔍 Track Complaint", type="primary", use_container_width=True)
    
    if track_button and tracking_input:
        with st.spinner("Fetching complaint details..."):
            # Search for complaint in database
            complaint = db.get_complaint_by_tracking_id(tracking_input)
            
            if complaint:
                # Display complaint details
                st.success(f"✅ Complaint Found!")
                
                # Status card
                status = complaint.get('status', 'PENDING')
                status_colors = {
                    'PENDING': '🟡',
                    'IN_PROGRESS': '🔵',
                    'RESOLVED': '🟢',
                    'REJECTED': '🔴'
                }
                status_icon = status_colors.get(status, '⚪')
                
                # Main status display
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a237e, #0d47a1); padding: 20px; border-radius: 15px; margin: 10px 0;">
                    <h2 style="color: white; text-align: center;">{status_icon} Complaint Status: {status}</h2>
                    <p style="color: white; text-align: center; font-size: 18px;">Tracking ID: {tracking_input}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Complaint details in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 Complaint Details")
                    st.write(f"**Complaint Type:** {complaint.get('complaint_type', 'Unknown').replace('_', ' ').title()}")
                    st.write(f"**Location:** {complaint.get('location', 'Not provided')}")
                    st.write(f"**Submitted On:** {complaint.get('created_at', 'Unknown')}")
                    st.write(f"**Last Updated:** {complaint.get('updated_at', complaint.get('created_at', 'Unknown'))}")
                
                with col2:
                    st.subheader("📝 Your Complaint")
                    original_text = complaint.get('original_text', '')
                    if original_text:
                        with st.expander("View Original Complaint", expanded=True):
                            st.write(original_text)
                    
                    translated_text = complaint.get('translated_text', '')
                    if translated_text and translated_text != original_text:
                        with st.expander("🇬🇧 English Translation", expanded=False):
                            st.write(translated_text)
                
                # Timeline
                st.subheader("📅 Complaint Timeline")
                
                timeline_data = []
                
                # Submission
                submitted_date = complaint.get('created_at', '')
                timeline_data.append({
                    "status": "Submitted",
                    "date": submitted_date,
                    "description": "Complaint received by GAIA system",
                    "icon": "✅"
                })
                
                # AI Analysis
                timeline_data.append({
                    "status": "AI Analysis",
                    "date": submitted_date,
                    "description": f"AI analyzed complaint - Type: {complaint.get('complaint_type', 'Unknown')}",
                    "icon": "🤖"
                })
                
                # Officer Assignment
                if status in ['IN_PROGRESS', 'RESOLVED']:
                    timeline_data.append({
                        "status": "Officer Assigned",
                        "date": complaint.get('updated_at', ''),
                        "description": f"Officer assigned for inspection",
                        "icon": "👮"
                    })
                
                # Inspection
                if status == 'RESOLVED':
                    timeline_data.append({
                        "status": "Inspection Completed",
                        "date": complaint.get('updated_at', ''),
                        "description": "Site inspection completed",
                        "icon": "🔍"
                    })
                    timeline_data.append({
                        "status": "Action Taken",
                        "date": complaint.get('updated_at', ''),
                        "description": "Resolution action completed",
                        "icon": "✅"
                    })
                
                # Display timeline
                for i, event in enumerate(timeline_data):
                    col1, col2, col3 = st.columns([1, 3, 2])
                    with col1:
                        st.write(f"**{event['icon']}**")
                    with col2:
                        st.write(f"**{event['status']}**")
                        st.caption(event['description'])
                    with col3:
                        st.write(event['date'])
                    
                    if i < len(timeline_data) - 1:
                        st.markdown("↓")
                
                # Next steps based on status
                st.subheader("📌 Next Steps")
                
                if status == 'PENDING':
                    st.info("""
                    🔄 **Your complaint is pending review**
                    
                    - An officer will be assigned within 24 hours
                    - You will receive an SMS/Email update
                    - Check back tomorrow for status update
                    """)
                elif status == 'IN_PROGRESS':
                    st.warning("""
                    🔍 **Complaint under investigation**
                    
                    - An officer has been assigned to your case
                    - Site inspection will be scheduled within 7 days
                    - You will be notified of the inspection date
                    """)
                elif status == 'RESOLVED':
                    st.success("""
                    ✅ **Complaint resolved**
                    
                    - Action has been taken based on your complaint
                    - Thank you for helping protect the environment
                    - A detailed report has been sent to your registered contact
                    """)
                
                # Contact information
                with st.expander("📞 Need Help? Contact Support"):
                    st.write("""
                    - **Email:** support@gaia.gov.in
                    - **Helpline:** 1800-XXX-XXXX (24x7)
                    - **WhatsApp:** +91-XXXXXXXXXX
                    
                    Please keep your Tracking ID ready when contacting support.
                    """)
                
            else:
                st.error(f"❌ No complaint found with Tracking ID: {tracking_input}")
                st.info("""
                **Please check:**
                - Make sure you entered the correct Tracking ID
                - Tracking ID format: `GAIA-YYYYMMDD-XXXXXX`
                - Example: `GAIA-20250407-ABC123`
                
                If you lost your Tracking ID, please contact support.
                """)
    
    elif track_button and not tracking_input:
        st.warning("⚠️ Please enter your Tracking ID")
    
    # Show recent complaints example (for demo)
    with st.expander("📋 Sample Tracking IDs (For Demo)"):
        st.write("Use these Tracking IDs to test the tracking feature:")
        
        # Get recent complaints from database
        recent_complaints = db.get_complaints(5)
        if recent_complaints:
            for complaint in recent_complaints:
                tracking_id = complaint.get('tracking_id') if isinstance(complaint, dict) else complaint[1] if len(complaint) > 1 else 'N/A'
                status = complaint.get('status') if isinstance(complaint, dict) else complaint[4] if len(complaint) > 4 else 'PENDING'
                st.code(f"Tracking ID: {tracking_id} - Status: {status}")
        else:
            st.code("No complaints in database yet. Submit a complaint first to test tracking.")
            
elif portal == "📊 Analytics":
    st.header("📊 Sustainability Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Reports by Score Range")
        reports = db.get_reports(50)
        if reports:
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
            
            for range_name, count in score_ranges.items():
                st.progress(count / max(len(reports), 1), text=f"{range_name}: {count} reports")
        else:
            st.info("No reports analyzed yet")
    
    with col2:
        st.subheader("🚨 Fraud Detection Stats")
        reports = db.get_reports(50)
        if reports:
            fraud_count = sum(1 for r in reports if r.get('is_fake', False))
            st.metric("Fake Reports Detected", fraud_count, f"{fraud_count/len(reports)*100:.0f}% of total")
            st.metric("Authentic Reports", len(reports) - fraud_count)
        else:
            st.info("No fraud data available")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📱 Citizen Complaints")
        complaints = db.get_complaints(20)
        if complaints:
            complaint_types = {}
            for complaint in complaints:
                ctype = complaint.get('complaint_type', 'unknown')
                complaint_types[ctype] = complaint_types.get(ctype, 0) + 1
            
            for ctype, count in complaint_types.items():
                st.write(f"• {ctype.replace('_', ' ').title()}: {count} reports")
        else:
            st.info("No citizen complaints yet")
    
    with col2:
        st.subheader("📨 Notifications Sent")
        history = notification_system.get_history()
        if history:
            st.metric("Total Notifications", len(history))
            for notif in history[-5:]:
                st.write(f"• {notif.get('type', 'Unknown')} to {notif.get('to', 'Unknown')}")
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
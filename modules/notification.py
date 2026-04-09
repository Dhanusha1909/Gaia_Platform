# modules/notification.py
from datetime import datetime, timedelta
import streamlit as st # pyright: ignore[reportMissingImports]

class NotificationSystem:
    """Send automated notifications with multilingual support"""
    
    def __init__(self):
        self.sent_notifications = []
        self.pending_reminders = []
    
    def _translate_notification(self, text, language='en'):
        """Translate notification to regional languages (simplified)"""
        # In production, use Google Translate API or IndicTrans
        # For hackathon, return as-is with language tag
        if language == 'hi':
            return text + "\n\n[हिंदी में जानकारी के लिए कृपया अधिकारी से संपर्क करें]"
        elif language == 'ta':
            return text + "\n\n[தகவல்கள் தமிழில்: அதிகாரியை தொடர்பு கொள்ளவும்]"
        return text
    
    def generate_warning(self, factory_name, score, suggestions, is_fake=False, language='en'):
        """Generate warning message with severity levels"""
        
        # Get status from score
        if score >= 80:
            severity = "EXCELLENT"
            icon = "✅"
            bg_color = "#e8f5e9"
        elif score >= 60:
            severity = "GOOD"
            icon = "📈"
            bg_color = "#e3f2fd"
        elif score >= 40:
            severity = "POOR"
            icon = "⚠️"
            bg_color = "#fff3e0"
        else:
            severity = "CRITICAL"
            icon = "🚨"
            bg_color = "#ffebee"
        
        if is_fake:
            notification = {
                'type': 'FRAUD_ALERT',
                'severity': 'HIGH',
                'icon': '🚨',
                'subject': f'URGENT: Fake Report Detected - {factory_name}',
                'body': f"""
🚨 **FRAUD ALERT - {factory_name}**

**Gaia Score:** {score}/100 (FLAGGED)
**Severity:** HIGH
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Issues Detected:**
{chr(10).join(['- ' + s for s in suggestions[:5]])}

**REQUIRED ACTION WITHIN 7 DAYS:**

1. **Submit Corrected Report** - Within 48 hours
2. **Provide Verification Documents** - Within 7 days
3. **Written Explanation** - Within 7 days

**PENALTIES FOR NON-COMPLIANCE:**
- Financial Penalty: ₹5,00,000 - ₹50,00,000
- Factory Sealing if persistent
- Legal Proceedings under Environmental Protection Act

**Contact:** Fraud Investigation Unit - fraud@gaia.gov.in
**Reference:** GAIA-FRAUD-{datetime.now().strftime('%Y%m%d')}

*This is an automated alert from GAIA Intelligence System*
""",
                'deadline_days': 7,
                'deadline_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'action_required': True,
                'escalation_level': 1
            }
        
        elif score < 40:
            notification = {
                'type': 'SEAL_WARNING',
                'severity': 'CRITICAL',
                'icon': '🔴',
                'subject': f'FINAL WARNING: Sealing Threat - {factory_name}',
                'body': f"""
🔴 **FINAL WARNING - SEALING THREAT**

**To:** {factory_name}
**Gaia Score:** {score}/100 (CRITICAL)
**Status:** Non-compliant
**Warning Count:** 3 (FINAL)

**CRITICAL VIOLATIONS:**
{chr(10).join(['- ' + s for s in suggestions[:4]])}

**DEADLINE:** 30 days from today ({datetime.now().strftime('%Y-%m-%d')})

**FAILURE WILL RESULT IN:**
1. 🔒 **Factory Sealing** under Section 31A of Environment Protection Act
2. ⚖️ **Criminal Proceedings** against Directors
3. 📢 **Public Notice** of violation
4. 💰 **Daily Penalty** of ₹1,00,000

**REQUIRED IMMEDIATELY:**
- Submit corrective action plan within 7 days
- Implement remediation within 30 days
- Pay environmental compensation: ₹25,00,000

**Emergency Contact:** National Green Tribunal - 1800-XXX-XXXX

*This is your FINAL WARNING. Legal action will commence after deadline.*
""",
                'deadline_days': 30,
                'deadline_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'action_required': True,
                'escalation_level': 3
            }
        
        elif score < 60:
            notification = {
                'type': 'IMPROVEMENT_NOTICE',
                'severity': 'MEDIUM',
                'icon': '🟡',
                'subject': f'Improvement Notice - {factory_name}',
                'body': f"""
🟡 **IMPROVEMENT NOTICE**

**To:** {factory_name}
**Gaia Score:** {score}/100 (POOR)
**Status:** Needs Improvement

**AREAS REQUIRING ATTENTION:**
{chr(10).join(['- ' + s for s in suggestions[:3]])}

**REQUIRED ACTIONS:**

1. **Submit Improvement Plan** - Within 15 days
2. **Implement Improvements** - Within 60 days
3. **Submit Progress Report** - Monthly

**GOVERNMENT ASSISTANCE AVAILABLE:**
- Solar Subsidy under PM-KUSUM
- Water Conservation under Jal Jeevan Mission
- Waste Management Grants

**Deadline:** {60} days ({datetime.now() + timedelta(days=60):%Y-%m-%d})

*Failure to comply will escalate to SEAL WARNING*
""",
                'deadline_days': 60,
                'deadline_date': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
                'action_required': True,
                'escalation_level': 1
            }
        
        else:
            notification = {
                'type': 'ACKNOWLEDGMENT',
                'severity': 'LOW',
                'icon': '✅',
                'subject': f'Report Acknowledged - {factory_name}',
                'body': f"""
✅ **REPORT ACKNOWLEDGED**

**To:** {factory_name}
**Gaia Score:** {score}/100 ({severity})
**Status:** Compliant

**FEEDBACK:**
{chr(10).join(['- ' + s for s in suggestions[:2]])}

**CERTIFICATE:**
- Valid for 12 months
- Eligible for Green Rating
- Fast-track renewal available

**Next Assessment:** {datetime.now() + timedelta(days=365):%Y-%m-%d}

**Benefits of Maintaining Compliance:**
- Tax benefits under Green Initiative
- Priority clearance for expansions
- Public recognition on GAIA portal

*Thank you for your commitment to sustainability*
""",
                'deadline_days': None,
                'deadline_date': None,
                'action_required': False,
                'escalation_level': 0
            }
        
        # Add common fields
        notification['score'] = score
        notification['factory_name'] = factory_name
        notification['timestamp'] = datetime.now().isoformat()
        notification['language'] = language
        
        # Translate if needed
        if language != 'en':
            notification['body_translated'] = self._translate_notification(notification['body'], language)
        
        return notification
    
    def generate_citizen_acknowledgment(self, tracking_id, language='en'):
        """Generate acknowledgment for citizen complaint"""
        notification = {
            'type': 'CITIZEN_ACKNOWLEDGMENT',
            'severity': 'LOW',
            'icon': '🙏',
            'tracking_id': tracking_id,
            'subject': f'Complaint Received - {tracking_id}',
            'body': f"""
✅ **COMPLAINT RECEIVED - GAIA Citizen Portal**

**Tracking ID:** {tracking_id}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**What Happens Next:**

| Step | Timeline | Status |
|------|----------|--------|
| 1. AI Analysis | Immediate | ✅ COMPLETE |
| 2. Officer Assignment | Within 24 hours | ⏳ PENDING |
| 3. Site Inspection | Within 7 days | ⏳ PENDING |
| 4. Action Report | Within 30 days | ⏳ PENDING |

**Track Your Complaint:**
🔗 https://gaia.gov.in/track/{tracking_id}
📱 SMS "GAIA {tracking_id}" to 12345

**Contact:** 
- For urgent issues: Call 24x7 Helpline: 1800-XXX-XXXX
- For status update: Reply to this email

**Your Voice Matters!** 
Thank you for helping protect our environment. Every complaint helps build a cleaner, greener India.

*This is an automated acknowledgment from GAIA Intelligence System*
""",
            'timestamp': datetime.now().isoformat(),
            'deadline_days': 30,
            'deadline_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'language': language
        }
        
        if language != 'en':
            notification['body_translated'] = self._translate_notification(notification['body'], language)
        
        return notification
    
    def generate_reminder(self, notification, days_remaining):
        """Generate reminder for upcoming deadlines"""
        return {
            'type': 'REMINDER',
            'severity': 'MEDIUM' if days_remaining <= 7 else 'LOW',
            'icon': '⏰',
            'subject': f'REMINDER: Action Required - {notification["factory_name"]}',
            'body': f"""
⏰ **DEADLINE REMINDER**

**To:** {notification['factory_name']}
**Original Notice:** {notification['type']}
**Days Remaining:** {days_remaining} days
**Deadline:** {notification['deadline_date']}

**Pending Actions:**
- Submit required documents
- Implement corrective measures
- Schedule compliance inspection

**Urgency:** {'HIGH - Immediate action required' if days_remaining <= 7 else 'MEDIUM - Action pending'}

*Please ensure compliance before deadline to avoid escalation*
""",
            'deadline_days': days_remaining,
            'timestamp': datetime.now().isoformat()
        }
    
    def send(self, to, notification):
        """Send notification with multiple channels"""
        
        # Prepare notification data
        notification_data = {
            'to': to,
            'type': notification['type'],
            'severity': notification.get('severity', 'MEDIUM'),
            'subject': notification.get('subject', 'GAIA Notification'),
            'body': notification['body'],
            'timestamp': datetime.now(),
            'timestamp_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'sent',
            'channel': 'email'  # Can be email, sms, whatsapp
        }
        
        # Add translated body if available
        if 'body_translated' in notification:
            notification_data['body_translated'] = notification['body_translated']
        
        # Add to history
        self.sent_notifications.append(notification_data)
        # ---------------- EMAIL SENDING (ADD THIS) ----------------
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            sender_email = "aarthi200611@gmail.com"       # 🔴 CHANGE THIS
            app_password = "eqxu qoyi ycce rixx"         # 🔴 CHANGE THIS

            subject = notification.get('subject', 'GAIA Notification')
            body = notification.get('body', '')

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            server.quit()

            print("✅ Email sent successfully")

        except Exception as e:
            print("❌ Email sending failed:", e)
        
        # Store for reminders if deadline exists
        if notification.get('deadline_days') and notification.get('action_required'):
            self.pending_reminders.append({
                'notification': notification,
                'to': to,
                'deadline': datetime.now() + timedelta(days=notification['deadline_days']),
                'sent_date': datetime.now()
            })
        
        # Display in Streamlit (for hackathon demo)
        with st.chat_message("assistant"):
            st.markdown(f"""
            **📧 Notification Sent to:** {to}
            **Type:** {notification['type']} {notification.get('icon', '')}
            **Severity:** {notification.get('severity', 'N/A')}
            **Subject:** {notification.get('subject', '')}
            **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)
            
            with st.expander("📄 View Full Notification"):
                st.text(notification['body'])
        
        # Simulate console output for debugging
        print(f"\n{'='*60}")
        print(f"[NOTIFICATION SENT]")
        print(f"To: {to}")
        print(f"Type: {notification['type']}")
        print(f"Severity: {notification.get('severity', 'N/A')}")
        print(f"Subject: {notification.get('subject', '')}")
        print(f"{'='*60}\n")
        
        return True
    
    def send_sms(self, phone_number, message):
        """Simulate SMS sending for urgent notifications"""
        sms_data = {
            'to': phone_number,
            'message': message[:160],  # SMS length limit
            'timestamp': datetime.now(),
            'status': 'sent'
        }
        print(f"[SMS SENT] To: {phone_number} | Message: {message[:50]}...")
        return True
    
    def get_history(self, limit=50):
        """Get all sent notifications"""
        return self.sent_notifications[-limit:]
    
    def get_pending_reminders(self):
        """Get pending reminders that need to be sent"""
        today = datetime.now()
        pending = []
        
        for reminder in self.pending_reminders:
            days_remaining = (reminder['deadline'] - today).days
            if days_remaining <= 7 and days_remaining > 0:
                pending.append({
                    'to': reminder['to'],
                    'notification': reminder['notification'],
                    'days_remaining': days_remaining
                })
        
        return pending
    
    def send_due_reminders(self):
        """Send reminders for upcoming deadlines"""
        pending = self.get_pending_reminders()
        for p in pending:
            reminder = self.generate_reminder(p['notification'], p['days_remaining'])
            self.send(p['to'], reminder)
        return len(pending)
    
    def get_statistics(self):
        """Get notification statistics"""
        stats = {
            'total_sent': len(self.sent_notifications),
            'by_type': {},
            'by_severity': {}
        }
        
        for notif in self.sent_notifications:
            # Count by type
            notif_type = notif['type']
            stats['by_type'][notif_type] = stats['by_type'].get(notif_type, 0) + 1
            
            # Count by severity
            severity = notif.get('severity', 'UNKNOWN')
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
        
        return stats

# Create instance
notification_system = NotificationSystem()
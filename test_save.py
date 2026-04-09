from modules.database import db

print("=" * 50)
print("Testing Save Feedback")
print("=" * 50)

# Test with a sample tracking ID
test_id = "TEST-FEEDBACK-001"
result = db.save_feedback(test_id, "Excellent", "This is a test feedback message")

if result:
    print(f"✅ Feedback saved successfully! ID: {result}")
else:
    print("❌ Failed to save feedback")

print("=" * 50)
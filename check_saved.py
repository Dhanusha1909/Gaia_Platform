from modules.database import db

print("=" * 50)
print("Checking Saved Feedback")
print("=" * 50)

all_feedback = db.get_all_feedback()

if all_feedback:
    print(f"Found {len(all_feedback)} feedback records:\n")
    for fb in all_feedback:
        print(f"  Tracking ID: {fb.get('tracking_id')}")
        print(f"  Rating: {fb.get('rating')}")
        print(f"  Feedback: {fb.get('feedback_text')[:50]}...")
        print(f"  Date: {fb.get('created_at')}")
        print("-" * 30)
else:
    print("No feedback found in database")

print("=" * 50)
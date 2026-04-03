from datetime import date, timedelta
from db import get_connection
from email_service import send_payment_email
from whatsapp_service import send_whatsapp_reminder


# ================= CONFIG =================
REMINDER_DAYS_BEFORE = 5   # Send reminder within next 5 days


# ================= PLAN → MONTHS MAP =================
PLAN_DURATION = {
    "1 Month": 1,
    "3 Months": 3,
    "6 Months": 6,
    "12 Months": 12
}


# ================= EXPIRY REMINDER =================
def send_expiry_reminders():
    today = date.today()
    reminder_limit = today + timedelta(days=REMINDER_DAYS_BEFORE)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, email, join_date, plan
        FROM members
        WHERE email IS NOT NULL
    """)
    members = cur.fetchall()
    conn.close()

    for member_id, name, email, join_date, plan in members:

        # --------- SAFETY CHECKS ---------
        if not join_date or not plan or not email:
            continue

        # --------- PLAN LOGIC ---------
        months = PLAN_DURATION.get(plan.strip(), 1)
        expiry_date = join_date + timedelta(days=30 * months)

        # --------- SEND REMINDER (CORRECT LOGIC) ---------
        if today <= expiry_date <= reminder_limit:
            try:
                send_payment_email(
                    to_email=email,
                    member_name=name,
                    amount="N/A",
                    payment_type="Membership Expiry Reminder",
                    join_date=join_date,
                    expiry_date=expiry_date,
                    subject="⚠ Membership Expiry Reminder"
                )
                print(f"📧 Reminder sent to {email}")

            except Exception as e:
                print(f"❌ Failed for {email}: {e}")


# ================= MANUAL RUN =================
if __name__ == "__main__":
    send_expiry_reminders()
    print("✅ Expiry reminder process completed")

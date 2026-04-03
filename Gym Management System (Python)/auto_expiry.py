from datetime import date, timedelta
from db import get_connection

PLAN_DURATION = {
    "1 Month": 30,
    "3 Months": 90,
    "6 Months": 180,
    "12 Months": 365
}

def deactivate_expired_members():
    today = date.today()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, join_date, plan FROM members WHERE status='Active'")
    members = cur.fetchall()

    for member_id, join_date, plan in members:
        days = PLAN_DURATION.get(plan, 30)
        expiry_date = join_date + timedelta(days=days)

        if expiry_date < today:
            cur.execute(
                "UPDATE members SET status='Expired' WHERE id=%s",
                (member_id,)
            )

    conn.commit()
    conn.close()
    print("✅ Expired members auto-updated")


if __name__ == "__main__":
    deactivate_expired_members()

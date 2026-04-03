import smtplib
from email.message import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
import os
import random
import datetime

# ================= SMTP CONFIG =================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

GYM_EMAIL = "bhavikkumbhar945@gmail.com"
APP_PASSWORD = "nhoujyjrqbcavhyg"

# ================= PREMIUM PDF GENERATOR =================
def generate_premium_invoice(member_name, amount, payment_type, join_date, expiry_date):

    invoice_no = f"INV-{random.randint(10000,99999)}"
    transaction_id = f"TXN-{random.randint(100000,999999)}"
    today = datetime.date.today()

    filename = f"invoice_{member_name.replace(' ', '_')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)

    width, height = A4

    # ===== HEADER =====
    c.setFillColor(colors.darkblue)
    c.rect(0, height - 100, width, 100, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, height - 60, "GYM INVOICE")

    c.setFont("Helvetica", 12)
    c.drawString(40, height - 85, "BHAVIKS GYM, 123 Fitness St, Wellness City")

    # ===== INVOICE DETAILS =====
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)

    c.drawString(40, height - 130, f"Invoice No      : {invoice_no}")
    c.drawString(40, height - 150, f"Transaction ID  : {transaction_id}")
    c.drawString(40, height - 170, f"Invoice Date    : {today}")

    # ===== MEMBER DETAILS =====
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, height - 210, "Bill To:")

    c.setFont("Helvetica", 11)
    c.drawString(40, height - 230, f"Member Name : {member_name}")
    c.drawString(40, height - 250, f"Join Date   : {join_date}")
    c.drawString(40, height - 270, f"Expiry Date : {expiry_date}")

    # ===== PAYMENT TABLE =====
    data = [
        ["Description", "Payment Method", "Amount (₹)"],
        ["Gym Membership Renewal", payment_type, f"{amount}"]
    ]

    table = Table(data, colWidths=[3 * inch, 2 * inch, 1.5 * inch])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('ALIGN', (2, 1), (2, 1), 'RIGHT')
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 40, height - 350)

    # ===== PAID STAMP =====
    c.setFillColor(colors.green)
    c.setFont("Helvetica-Bold", 40)
    c.drawString(width - 200, height - 250, "PAID")

    # ===== FOOTER =====
    c.setFillColor(colors.grey)
    c.setFont("Helvetica", 10)
    c.drawString(40, 60, "Thank you for choosing our gym.")
    c.drawString(40, 45, "Receipt has been generated electronically.")
    c.drawString(40, 30, "For support contact: bhavikkumbhar945@gmail.com")

    c.save()
    return filename


# ================= PREMIUM EMAIL SERVICE =================
def send_payment_email(
    to_email,
    member_name,
    amount,
    payment_type,
    join_date,
    expiry_date,
    subject="Gym Payment Confirmation"
):

    pdf_file = None

    try:
        # Generate Premium Invoice
        pdf_file = generate_premium_invoice(
            member_name,
            amount,
            payment_type,
            join_date,
            expiry_date
        )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = GYM_EMAIL
        msg["To"] = to_email

        msg.set_content(f"""
Hello {member_name},

🎉 Payment Successful!

We have successfully received your membership payment.

Payment Details:
---------------------------------------
Amount        : ₹{amount}
Payment Mode  : {payment_type}
Join Date     : {join_date}
Expiry Date   : {expiry_date}
---------------------------------------

Your premium invoice is attached to this email.

Thank you for being part of our fitness family 💪

Regards,
Gym Management Team
""")

        # Attach PDF
        with open(pdf_file, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=pdf_file
            )

        # Send Email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GYM_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"✅ Premium invoice sent to {to_email}")

    except Exception as e:
        print("❌ Email Error:", e)

    finally:
        if pdf_file and os.path.exists(pdf_file):
            os.remove(pdf_file)

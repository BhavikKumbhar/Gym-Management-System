from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import qrcode
import os
from datetime import date


def generate_invoice_pdf(
    member_name,
    email,
    amount,
    payment_type,
    join_date,
    expiry_date,
    invoice_id
):
    file_name = f"invoice_{invoice_id}.pdf"
    file_path = os.path.join(os.getcwd(), file_name)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # ================= HEADER =================
    c.setFont("Helvetica-Bold", 22)
    c.drawString(2 * cm, height - 2 * cm, "GYM MANAGEMENT SYSTEM")

    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, height - 2.8 * cm, "Official Payment Invoice")

    c.line(2 * cm, height - 3.2 * cm, width - 2 * cm, height - 3.2 * cm)

    # ================= DETAILS =================
    y = height - 4.5 * cm
    c.setFont("Helvetica", 12)

    details = [
        ("Invoice ID", invoice_id),
        ("Member Name", member_name),
        ("Email", email),
        ("Payment Type", payment_type),
        ("Amount Paid", f"₹ {amount}"),
        ("Join Date", str(join_date)),
        ("Expiry Date", str(expiry_date)),
        ("Payment Date", str(date.today()))
    ]

    for label, value in details:
        c.drawString(2 * cm, y, f"{label}:")
        c.drawString(7 * cm, y, str(value))
        y -= 0.8 * cm

    # ================= QR CODE =================
    qr_data = f"""
Gym Invoice
Invoice ID: {invoice_id}
Member: {member_name}
Amount: ₹{amount}
Valid Till: {expiry_date}
"""

    qr = qrcode.make(qr_data)
    qr_path = "temp_qr.png"
    qr.save(qr_path)

    c.drawImage(qr_path, width - 7 * cm, height - 12 * cm, 5 * cm, 5 * cm)
    os.remove(qr_path)

    # ================= FOOTER =================
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(
        2 * cm,
        2 * cm,
        "Thank you for choosing our Gym 💪 | This is a system-generated invoice."
    )

    c.showPage()
    c.save()

    return file_path

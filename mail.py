import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "linusrosenbeeger@gmail.com"
EMAIL_PASSWORD = "utzi csxj pkmu qkwe"   # das 16-stellige Passwort

def send_mail(to, subject, content):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

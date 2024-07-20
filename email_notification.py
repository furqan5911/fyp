import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email_alert():
    sender_email = "callmewhenyoudontneed@gmail.com"  # Replace with your email address
    receiver_email = "furqanmalick2001@gmail.com"  # Replace with recipient email address
    password = "wopc zhbq vvhb kvrd"  # Replace with your email password

    message = MIMEMultipart("alternative")
    message["Subject"] = "Accident Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = """\
    Accident detected! Please check and respond."""
    html = """\
    <html>
      <body>
        <p>Accident detected! Please check and respond.</p>
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

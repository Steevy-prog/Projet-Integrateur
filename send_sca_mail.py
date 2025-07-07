import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

def send_email(subject, to_email,orgid,orgname,idcolis,receivingorg):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "scarobot6@gmail.com"
    sender_password = "vpvqjnehxkkqaykf"
    sender_name = "SCA Robot"

    # HTML body
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
        <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
          <h2 style="color: #2c3e50;">📧 Message automatique - SCA Robot</h2>
          <p style="font-size: 15px; color: #2D3748;">
            Bonjour,
          </p>
          <h1>Organisation ID : </h1> <p>{orgid}</p>
          <h1>Organisation Name : </h1> <p>{orgname}</p>
          <h1>Package ID : </h1> <p>{idcolis}</p>
          <h1>Receiving Organisation</h1><p>{receivingorg}</p>
          <p style="font-size: 14px; color: #555555;">
            Cordialement,<br>
            <strong>SCA Robot</strong>
          </p>
        </div>
      </body>
    </html>
    """

    # Create message
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((sender_name, sender_email))
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the HTML version
    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        print(f"✅ Email envoyé à {to_email}")
        server.quit()
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {e}")


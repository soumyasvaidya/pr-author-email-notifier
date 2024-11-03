import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, pr_link, smtp_server, smtp_port, sender_email, sender_password):
    # Create the email content
    subject = "Request for Test Cases on Your PR"
    body = f"""Dear PR Author,

We are conducting research on memory leaks in real-world applications and would like to recreate 
the memory leak issue you addressed in your pull request. Your PR ({pr_link}) has been selected 
as part of our study.

If possible, could you please share any test cases or additional context needed to reproduce 
the memory leak?

Thank you for your time and contribution.

Best regards,
Research Team
"""
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable security
            server.login(sender_email, sender_password)  # Login to the email server
            server.sendmail(sender_email, to_email, msg.as_string())  # Send the email
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def process_csv_and_send_emails(input_file, smtp_server, smtp_port, sender_email, sender_password):
    with open(input_file, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            email = row.get("Email ID")
            commit_url = row.get("Commit URL")

            if email and commit_url:
                send_email(email, commit_url, smtp_server, smtp_port, sender_email, sender_password)

# Usage
input_file = "test_repo.csv"  # CSV file containing Email IDs and Commit URLs
smtp_server = "smtp.gmail.com"  # Replace with your SMTP server
smtp_port = 587  # Typically 587 for TLS
sender_email = "useername"  # Replace with your email address
sender_password = "password"  # Replace with your email password

process_csv_and_send_emails(input_file, smtp_server, smtp_port, sender_email, sender_password)

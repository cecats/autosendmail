import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser
import os
import csv
from time import sleep
import logging
import requests
from datetime import datetime

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

EMAIL = config['settings']['email']
PASSWORD = config['settings']['password']
SMTP_SERVER = config['settings']['smtp_server']
SMTP_PORT = config['settings']['smtp_port']
IMAP_SERVER = config['settings']['imap_server']
IMAP_PORT = config['settings']['imap_port']
CHECK_INTERVAL = int(config['settings']['check_interval'])
EMAIL_LOG_FILE = config['settings']['email_log_file']
LOG_FILE = config['settings']['log_file']
BOT_TOKEN = config['settings']['bot_token']
CHAT_ID = config['settings']['chat_id']

SUBJECT = config['message']['subject']
# BODY = config['message']['body']
BODY = config['message']['body'].replace('\\n', '\n')

# Setup logging
def setup_logging():
    """Set up the logger to record log messages to a CSV file."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Level', 'Message'])
    
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s,%(levelname)s,%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.FileHandler(LOG_FILE, mode='a'), logging.StreamHandler()])

def log_message(message, level, log_file_path):
    """Log a message to the specified log file and to console."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp},{level},{message}"
    print(log_entry)
    with open(log_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, level, message])

def log_email(email_address):
    """Log the email address to a CSV file without duplication."""
    if not os.path.exists(EMAIL_LOG_FILE):
        with open(EMAIL_LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Email'])
    
    with open(EMAIL_LOG_FILE, mode='r+', newline='') as file:
        reader = csv.reader(file)
        existing_emails = [row[1] for row in reader if row]  # Ensure row is not empty
        
        if email_address not in existing_emails:
            writer = csv.writer(file)
            writer.writerow([email.utils.formatdate(), email_address])

def send_email(receiver):
    """Send an email to the receiver with the configured subject and body."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = receiver
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY, 'plain'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, receiver, msg.as_string())
            logging.info(f"Email sent to {receiver}")
    except Exception as e:
        logging.error(f"Failed to send email to {receiver}: {str(e)}")
        raise

def send_message_to_telegram_chat(bot_token, chat_id, message, log_file_path):
    """Send a message to a specified Telegram chat and log the response."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        response_json = response.json()
        
        if response_json.get("ok"):
            log_message("Message sent to Telegram successfully.", "INFO", log_file_path)
            return True
        else:
            error_message = f"Telegram send message error: {response_json.get('description', 'Unknown error')}"
            log_message(error_message, "ERROR", log_file_path)
            return False
    except requests.RequestException as e:
        error_message = f"Network request exception: {str(e)}"
        log_message(error_message, "ERROR", log_file_path)
        return False

def check_and_respond():
    """Check for new emails and respond to them."""
    try:
        with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
            mail.login(EMAIL, PASSWORD)
            mail.select('inbox')
            typ, data = mail.search(None, 'ALL')
            mail_ids = data[0].split()
            
            for mail_id in mail_ids:
                typ, data = mail.fetch(mail_id, '(RFC822)')
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        mail_from = email.utils.parseaddr(msg['from'])[1]
                        
                        # Send email and log
                        send_email(mail_from)
                        log_email(mail_from)
                        
                        # Delete the email
                        mail.store(mail_id, '+FLAGS', '\\Deleted')
                mail.expunge()
            logging.info("All pending emails processed and responded to.")
    except Exception as e:
        logging.error(f"Failed to check or respond to emails: {str(e)}")
        raise

def main():
    """Main function to periodically check emails."""
    setup_logging()
    try:
        while True:
            check_and_respond()
            sleep(CHECK_INTERVAL)
    except Exception as e:
        error_message = f"Application crashed: {str(e)}"
        log_message(error_message, "CRITICAL", LOG_FILE)
        send_message_to_telegram_chat(BOT_TOKEN, CHAT_ID, f"ASM: "+error_message, LOG_FILE)

if __name__ == '__main__':
    main()
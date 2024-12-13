import os
import psutil
import time
import gzip
import shutil
import logging
from collections import Counter
from email.mime.text import MIMEText
from dotenv import load_dotenv
import smtplib

# Load environment variables
load_dotenv()

# Directory and file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
LOG_DIRECTORY = os.path.join(BASE_DIR, "system_logs")
CPU_MEMORY_LOG = os.path.join(LOG_DIRECTORY, "resource_usage.log")
COMPRESSED_LOG_ARCHIVE = os.path.join(LOG_DIRECTORY, "compressed_logs.gz")


# cấu hình cho Stmp server trong file .env
SMTP_HOST = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_RECEIVER = os.getenv("RECEIVER_EMAIL")

ERROR_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", 0.2))

# kiểm tra file log có tồn tại không, nếu không sẽ tạo một Log dir
os.makedirs(LOG_DIRECTORY, exist_ok=True)

# Logging setup
logging.basicConfig(
    filename=os.path.join(LOG_DIRECTORY, "application.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def send_alert_email(subject, content):
    """Send an email notification."""
    try:
        if not all([SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_SENDER, EMAIL_RECEIVER]):
            logging.error("Email configuration is missing. Email will not be sent.")
            return

        email_message = MIMEText(content)
        email_message["Subject"] = subject
        email_message["From"] = EMAIL_SENDER
        email_message["To"] = EMAIL_RECEIVER

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, email_message.as_string())

        logging.info(f"Email sent: {subject}")
    except Exception as ex:
        logging.error(f"Failed to send email: {ex}")


def log_system_resources():
    """Log the CPU and memory usage."""
    try:
        with open(CPU_MEMORY_LOG, "a") as log_file:
            cpu_load = psutil.cpu_percent(interval=1)
            memory_load = psutil.virtual_memory().percent
            log_file.write(f"CPU: {cpu_load}% | Memory: {memory_load}%\n")
            logging.info(f"Recorded CPU: {cpu_load}%, Memory: {memory_load}%")
    except Exception as ex:
        logging.error(f"Error logging system resources: {ex}")


def compress_daily_logs():
    """Compress daily logs."""
    try:
        with open(CPU_MEMORY_LOG, "rb") as original_file, gzip.open(COMPRESSED_LOG_ARCHIVE, "wb") as archive_file:
            shutil.copyfileobj(original_file, archive_file)
        open(CPU_MEMORY_LOG, "w").close()  # Reset the original log file
        logging.info("Daily logs compressed successfully.")
    except Exception as ex:
        logging.error(f"Error during log compression: {ex}")



def resource_monitoring_job():
    """Continuously monitor system resources."""
    print("Script is running!")
    logging.info("Resource monitoring initiated.")
    while True:
        log_system_resources()
        time.sleep(60)

if __name__ == "__main__":
    try:
        from multiprocessing import Process

        monitor_process = Process(target=resource_monitoring_job)
        monitor_process.start()

        while True:
            time.sleep(86400)
            compress_daily_logs()

    except KeyboardInterrupt:
        if monitor_process:
            monitor_process.terminate()
        logging.info("Process terminated by user.")
    except Exception as ex:
        logging.error(f"Unexpected error: {ex}")

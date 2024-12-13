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
ACCESS_LOG = os.path.join(LOG_DIRECTORY, "web_access.log")
LOG_ANALYSIS_REPORT = os.path.join(LOG_DIRECTORY, "log_analysis.txt")
COMPRESSED_LOG_ARCHIVE = os.path.join(LOG_DIRECTORY, "compressed_logs.gz")


# cấu hình cho Stmp server trong file .env
SMTP_HOST = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_RECEIVER = os.getenv("RECEIVER_EMAIL")

ERROR_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", 0.1))

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


def analyze_web_logs():
    """Analyze web access logs and generate a report."""
    try:
        if not os.path.exists(ACCESS_LOG):
            logging.warning("Web access log file is missing.")
            return

        with open(ACCESS_LOG, "r") as log_file:
            log_entries = log_file.readlines()

        ip_tracker = Counter()
        endpoint_tracker = Counter()
        total_requests = 0
        total_errors = 0

        for entry in log_entries:
            total_requests += 1
            components = entry.split()
            if len(components) < 9:
                continue

            ip_address = components[0]
            endpoint = components[6]
            status_code = components[8]

            ip_tracker[ip_address] += 1
            endpoint_tracker[endpoint] += 1

            if status_code.startswith("4") or status_code.startswith("5"):
                total_errors += 1

        error_rate = total_errors / total_requests if total_requests > 0 else 0
        analysis_result = {
            "top_ips": ip_tracker.most_common(5),
            "top_endpoints": endpoint_tracker.most_common(5),
            "error_rate": error_rate
        }

        with open(LOG_ANALYSIS_REPORT, "w") as report_file:
            report_file.write(f"Top IPs: {analysis_result['top_ips']}\n")
            report_file.write(f"Top Endpoints: {analysis_result['top_endpoints']}\n")
            report_file.write(f"Error Rate: {analysis_result['error_rate'] * 100:.2f}%\n")

        logging.info(f"Web log analysis completed: {analysis_result}")

        if error_rate > ERROR_THRESHOLD:
            send_alert_email(
                "High Error Rate Detected",
                f"Error rate: {error_rate * 100:.2f}% exceeded threshold."
            )
    except Exception as ex:
        logging.error(f"Error analyzing web logs: {ex}")


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
            analyze_web_logs()

    except KeyboardInterrupt:
        if monitor_process:
            monitor_process.terminate()
        logging.info("Process terminated by user.")
    except Exception as ex:
        logging.error(f"Unexpected error: {ex}")

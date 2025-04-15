import sys
import time
import os
import smtplib
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Get the URL from command-line arguments or use a default URL
if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = "https://www.ikea.com/sk/sk/p/linnaberg-dvere-zelena-vzorovany-40584401/"

def get_stock_result(target_url):
    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    # Open the target URL and wait for initial content to load
    driver.get(target_url)
    time.sleep(5)
    
    # Click the element that reveals the detailed stock panel
    try:
        status_elem = driver.find_element(By.CSS_SELECTOR, ".pip-status__label")
        status_elem.click()
        time.sleep(5)  # Adjust the sleep time if needed
    except Exception as e:
        print("Error clicking the pip-status__label element:", e)
    
    # Find all container elements that might include the stock details
    containers = driver.find_elements(By.CSS_SELECTOR, ".pip-store-availability-section__container")
    result_text = None
    for container in containers:
        text = container.text.strip()
        # Identify the container that contains "Skladová zásoba"
        if "Skladová zásoba" in text:
            # Remove the leading "Skladová zásoba —" part if present
            parts = text.split("Skladová zásoba —", 1)
            if len(parts) > 1:
                result_text = parts[1].strip()
            else:
                result_text = text
            break

    driver.quit()
    return result_text

def send_email(subject, body):
    # Get email credentials from environment variables
    EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
    EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
    
    if not (EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECEIVER):
        print("Email credentials not provided via environment variables.")
        return
    
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)

if __name__ == "__main__":
    result_expected = get_stock_result(url)
    if result_expected:
        print("RESULT-EXPECTED:")
        print(result_expected)
        # Use the extracted result as the email subject.
        email_subject = result_expected
        email_body = f"Stock status for {url}:\n{result_expected}"
        send_email(email_subject, email_body)
    else:
        print("Could not extract stock information.")

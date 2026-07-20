from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import smtplib
import boto3
import os
import re

client = boto3.client('ssm')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('flight_pricing')

def lambda_handler(event, context):

    #get parameters from SSM and store them in variables
    response = client.get_parameters(
        Names = [
            'RecipientCell', #cell number to text alerts to
            'RecipientEmail', #email to send alerts to
            'SenderEmail', #email to send alerts from
            'SenderEmailAppPassword' #app password for sender email
            ],
            WithDecryption=True
        )
        
    response = response.get('Parameters')

    for item in response:
        if item['Name'] == 'RecipientCell':
            RecipientCell = item['Value']
        elif item['Name'] == 'RecipientEmail':
            RecipientEmail = item['Value']
        elif item['Name'] == 'SenderEmail':
            SenderEmail = item['Value']
        elif item['Name'] == 'SenderEmailAppPassword':
            SenderEmailAppPassword = item['Value']

    def initialise_driver():
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.binary_location = "/opt/chrome/chrome-headless-shell-linux64/chrome-headless-shell"

        service = Service(
            executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
            service_log_path="/tmp/chromedriver.log"
        )

        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

        return driver

    flight_vars = {}
    url_vars = {}

    for name, value in os.environ.items():
        m = re.match(r"^FLIGHT(\d+)$", name)
        if m:
            flight_vars[m.group(1)] = int(value)
        m = re.match(r"^URL(\d+)$", name)
        if m:
            url_vars[m.group(1)] = value

    flights = []
    for suffix, flight_num in flight_vars.items():
        if suffix in url_vars:
            flights.append({"flight": flight_num, "url": url_vars[suffix]})
        else:
            print(f"Warning: FLIGHT{suffix} has no matching URL{suffix}, skipping")

    def check_price(flight_num):
        response =  table.get_item(Key={'flight': flight_num})
        current_price = response.get('Item')['price']
        return current_price

    # Create an App Password for gmail here https://myaccount.google.com/apppasswords
    def notify(flight_num, current_price, price, fare_num):
        email_message = (
            f"Subject: Price Drop for Flight {flight_num}\n\n"
            f"Flight {flight_num} ({fare_name}) has dropped from ${current_price} to ${price}"
        )
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(SenderEmail, SenderEmailAppPassword)
        s.sendmail(SenderEmail, RecipientEmail, email_message)  # This sends you an email
        s.sendmail(SenderEmail, RecipientCell, email_message)  # This sends you a text
        s.quit()

    def get_economy_fare(driver, exclude_keywords=("basic",)):
        """
        Finds all fare tier name/price pairs on a Google Flights booking page,
        excludes any tier matching exclude_keywords (e.g. Basic Economy),
        and returns the cheapest remaining tier (name, price) as (str, int).
        """
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )

        fare_names = driver.find_elements(By.TAG_NAME, "h3")
        fares = []

        for name_el in fare_names:
            name_text = name_el.text.strip()
            if not name_text:
                continue
            if any(kw.lower() in name_text.lower() for kw in exclude_keywords):
                continue
            try:
                container = name_el.find_element(By.XPATH, "./parent::*")
                price_text = container.find_element(By.CLASS_NAME, "tZe0ff").text
                price_value = int(re.sub(r"[^\d]", "", price_text))
                fares.append((name_text, price_value))
            except Exception:
                continue  # this h3 wasn't a fare card

        if not fares:
            return None

        return min(fares, key=lambda x: x[1])  # cheapest non-basic tier

    driver = initialise_driver()

    try:
        for flight in flights:
            try:
                driver.get(flight['url'])

                result = get_economy_fare(driver)
                if result is None:
                    print(f"No matching economy fare found for flight {flight['flight']}, skipping")
                    continue

                fare_name, price = result

                check = table.get_item(Key={'flight': flight['flight']})
                if check.get('Item') is None:
                    table.put_item(Item={'flight': flight['flight'], 'price': price})
                    current_price = price
                else:
                    current_price = check_price(flight['flight'])

                if price < current_price:
                    notify(flight['flight'], current_price, price, fare_name)
                    table.put_item(Item={'flight': flight['flight'], 'price': price})

            except Exception as e:
                print(f"Failed to check flight {flight['flight']}: {e}")
                continue

    finally:
        driver.quit()

    return {
        "statusCode": 200,
        "body": "Prices checked!!!"
    }

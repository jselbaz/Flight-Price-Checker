from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
import os.path

# Set this list of dicts with your flight number and flight url. See example below
flights = [{
    "flight": 801,
    "url": 'https://www.google.com/travel/flights/booking?tfs=CBwQAhpKEgoyMDI0LTEyLTMxIh8KA0VMUBIKMjAyNC0xMi0zMRoDSE9VKgJXTjIDODAxag0IAxIJL20vMDEwMG10cgwIAxIIL20vMDNsMm5AAUgBcAGCAQsI____________AZgBAg'
},
{
    "flight": 265,
    "url": 'https://www.google.com/travel/flights/booking?tfs=CBwQAhpKEgoyMDI0LTEyLTMxIh8KA0hPVRIKMjAyNC0xMi0zMRoDRUxQKgJXTjIDMjY1agwIAxIIL20vMDNsMm5yDQgDEgkvbS8wMTAwbXRAAUgBcAGCAQsI____________AZgBAg'
}]

def check_price(path):
    # path must be given as a raw string
    with open(path, "r") as text_file:
        current_price = text_file.read()
    text_file.close()
    return int(current_price)

# Create an App Password for gmail here https://myaccount.google.com/apppasswords
def notify(flight_num, current_price, price):
    email_message = f"Subject: Price Drop for Flight " + str(flight_num) + "\n\nFlight " + str(flight_num) + " has dropped from $" + str(current_price) + " to $" + str(price) 
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls() # Encrypts the email
    s.login("sender_email@gmail.com", "app_password_for_sender_email")  # The password is the app password you made
    s.sendmail("sender_email@gmail.com", "recipient_email@gmail.com", email_message)  # This sends you an email
    s.sendmail("sender_email@gmail.com", "12345678910@vtext.com", email_message)  # This send you a text - check readme for other cell service providers
    s.quit()

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--enable-javascript")
driver = webdriver.Chrome(options=chrome_options)

for flight in flights:
    driver.get(flight['url'])
    #if previously checked for price use that comparison, otherwise create new comparison point
    if os.path.exists(r"path_of_saved_price" + str(flights.index(flight)) + r".txt"):
        current_price=check_price(r"path_of_saved_price" + str(flights.index(flight)) + r".txt")
    else:
        current_price=999999
    driver.implicitly_wait(10)
    
    fare_name = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Delta Main Classic')]")))
    container = fare_name.find_element(By.XPATH, "./parent::*")
    price = container.find_element(By.CLASS_NAME, "tZe0ff").text
    price = int(price[1:])
    if price < current_price:
        # Send the notifications
        notify(flight['flight'], current_price, price)
        with open(r"path_of_saved_price" + str(flights.index(flight)) + r".txt", "w") as text_file:
            text_file.write(str(price))
        text_file.close()

driver.quit()

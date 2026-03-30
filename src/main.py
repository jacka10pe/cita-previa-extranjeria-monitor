"""
Entry point for the Cita Previa Extranjeria Monitor.
"""
import os
import random
from datetime import datetime

import requests
from selenium.webdriver.common.by import By
from termux_web_scraper.error_hook import ScreenshotErrorHook, NotificationErrorHook
from termux_web_scraper.helpers import select_option_by_text, random_sleep, click_element, send_keys, \
    get_optional_element
from termux_web_scraper.notifier import TelegramNotifier
from termux_web_scraper.scraper_builder import ScraperBuilder, get_default_driver_options
from selenium.webdriver.remote.webdriver import WebDriver

from config import SCRAPER_OUTPUT_DIR, TELEGRAM_API_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, PROVINCE, OFFICE, \
    PROCEDURE, NIE, FULL_NAME


def main():
    """
    Main function to run the Cita Previa Extranjeria Monitor.

    This function configures the scraper with defined steps and error hooks, and then runs the scraping process.
    """
    startup_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Starting up at: {startup_time}")

    # Build and run the application using the framework
    scraper = (
        ScraperBuilder()
        .with_notifier(
            TelegramNotifier(
                api_url=TELEGRAM_API_URL,
                bot_token=TELEGRAM_BOT_TOKEN,
                chat_id=TELEGRAM_CHAT_ID
            ))
        .with_driver_options(get_driver_options())
        .with_error_hook(ScreenshotErrorHook(os.path.join(SCRAPER_OUTPUT_DIR, "screenshots")))
        # .with_error_hook(NotificationErrorHook())
        .with_step("Navigating to the appointment website", navigate_to_website)
        .with_step("Select Province", select_province)
        .with_step("Select Office and Procedure", select_office_and_procedure)
        .with_step("Navigate through warning page", navigate_through_warning_page)
        .with_step("Fill in Personal Data", fill_in_personal_data)
        .with_step("Request Appointment", request_appointment)
        .with_step("Verify Response", verify_response)
        .build()
    )

    scraper.run()


def get_driver_options():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.1901.188",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/116.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    ]
    options = get_default_driver_options()
    user_agent = random.choice(user_agents)
    print(f"User Agent: {user_agent}")
    options.set_preference("general.useragent.override", user_agent)
    
    # Additional preferences to avoid detection
    options.set_preference("media.peerconnection.enabled", False)  # Disable WebRTC
    options.set_preference("devtools.jsonview.enabled", False)  # Disable devtools json view
    options.set_preference("privacy.trackingprotection.enabled", True)  # Enable tracking protection
    options.set_preference("browser.safebrowsing.enabled", False)  # Disable safe browsing
    options.set_preference("browser.safebrowsing.malware.enabled", False)  # Disable malware protection
    options.set_preference("browser.safebrowsing.phishing.enabled", False)  # Disable phishing protection
    options.set_preference("intl.accept_languages", "en-US, en;q=0.5")  # Set accepted languages

    return options


def navigate_to_website(driver, state, notify):
    driver.get('https://icp.administracionelectronica.gob.es/icpco/index')


def select_province(driver, state, notify):
    select_option_by_text(driver, (By.NAME, 'form'), PROVINCE)
    random_sleep(3000, 5000)
    click_element(driver, (By.ID, "btnAceptar"))


def select_office_and_procedure(driver, state, notify):
    # select_option_by_text(driver, (By.NAME, 'sede'), OFFICE)
    # random_sleep(1000, 2000)
    select_option_by_text(driver, (By.NAME, 'tramiteGrupo[0]'), PROCEDURE)
    random_sleep(3000, 5000)
    driver.execute_script("envia()")


def navigate_through_warning_page(driver, state, notify):
    random_sleep(3000, 5000)
    driver.execute_script("document.forms[0].submit()")


def fill_in_personal_data(driver, state, notify):
    send_keys(driver, (By.NAME, "txtIdCitado"), NIE)
    random_sleep(1000, 2000)
    send_keys(driver, (By.NAME, "txtDesCitado"), FULL_NAME)
    random_sleep(3000, 5000)
    driver.execute_script("envia()")


def request_appointment(driver, state, notify):
    random_sleep(3000, 5000)
    driver.execute_script("enviar('solicitud')")


def verify_response(driver, state, notify):
    error_message_element = get_optional_element(driver, (By.CLASS_NAME, "mf-msg__info"))
    if error_message_element and 'En este momento no hay citas disponibles' in error_message_element.text:
        print("No appointment slots available at the moment...")
    else:
        print("Appointment slot found!")
        notify("Cita Previa Extranjeria Monitor: Appointment slot found!")

        # save screenshot and send to telegram
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_name = f"{os.path.join(SCRAPER_OUTPUT_DIR, "screenshots")}/{timestamp}.png"
        save_screenshot(driver, screenshot_name)
        send_image(screenshot_name)


def save_screenshot(driver: WebDriver, screenshot_name: str) -> None:
    print(f"Save a screenshot to {screenshot_name}")
    driver.save_screenshot(screenshot_name)


def send_image(screenshot_name: str):
    url = f"https://api.telegram.org/botXXX:YYY/sendPhoto"
    with open(screenshot_name, 'rb') as photo:
        payload = {
            'chat_id': ZZZ
        }
        files = {
            'photo': photo
        }
        response = requests.post(url, data=payload, files=files)
    print(response.json())


if __name__ == "__main__":
    main()

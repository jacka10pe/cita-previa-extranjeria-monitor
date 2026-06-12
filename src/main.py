"""
Entry point for the Cita Previa Extranjeria Monitor.
"""
import os
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from termux_web_scraper.error_hook import ScreenshotErrorHook, NotificationErrorHook
from termux_web_scraper.helpers import select_option_by_text, random_sleep, click_element, send_keys, \
    get_optional_element, save_screenshot
from termux_web_scraper.notifier import TelegramNotifier
from termux_web_scraper.scraper_builder import ScraperBuilder

from config import SCRAPER_OUTPUT_DIR, TELEGRAM_API_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, PROVINCE, OFFICE, \
    PROCEDURE, NIE, FULL_NAME, NATIONALITY, TELEPHONE, EMAIL

import winsound


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
        .with_error_hook(ScreenshotErrorHook(os.path.join(SCRAPER_OUTPUT_DIR, "screenshots")))
        .with_error_hook(NotificationErrorHook())
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


def play_alert_sound():
    sound_path = "notification.wav"
    if os.path.exists(sound_path):
        for i in range(3):
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
            time.sleep(1.0)
    else:
        winsound.Beep(1000, 1000)  # 1000Hz 持续 1秒


def navigate_to_website(driver, state, notify):
    driver.get('https://icp.administracionelectronica.gob.es/icpco/index')


def select_province(driver, state, notify):
    select_option_by_text(driver, (By.NAME, 'form'), PROVINCE)
    random_sleep(3000, 5000)
    click_element(driver, (By.ID, "btnAceptar"))


def select_office_and_procedure(driver, state, notify):
    select_option_by_text(driver, (By.NAME, 'sede'), OFFICE)
    random_sleep(3000, 5000)
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
    random_sleep(1000, 2000)
    send_keys(driver, (By.NAME, "txtPaisNac"), NATIONALITY)
    random_sleep(2000, 3000)
    driver.execute_script("envia()")


def request_appointment(driver, state, notify):
    random_sleep(200, 800)
    driver.execute_script("enviar('solicitud')")


def verify_response(driver, state, notify):
    error_message_element = get_optional_element(driver, (By.CLASS_NAME, "mf-msg__info"))
    if error_message_element and 'En este momento no hay citas disponibles' in error_message_element.text:
        print("No appointment slots available at the moment...")
    else:
        print("Appointment slot found!")
        try:
            random_sleep(50, 100)
            send_keys(driver, (By.NAME, "txtEmail"), EMAIL)
            random_sleep(50, 100)
            send_keys(driver, (By.NAME, "emailDOS"), EMAIL)
            random_sleep(50, 100)
            send_keys(driver, (By.NAME, "txtTelefonoCitado"), TELEPHONE)
            random_sleep(100, 200)
            click_element(driver, (By.ID, "btnSiguiente"))
        except Exception as e:
            print(f"An error occurred: {e}")

        play_alert_sound()
        notify("Cita Previa Extranjeria Monitor: Appointment slot found!")
        save_screenshot(driver, os.path.join(SCRAPER_OUTPUT_DIR, "screenshots_success"))
        input("Please press Enter to continue...")


if __name__ == "__main__":
    main()

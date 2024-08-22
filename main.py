#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import argparse
import requests
import datetime
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import json

c = Options()
c.add_argument("--headless")
# Enable browser logging
d = DesiredCapabilities.CHROME
d['loggingPrefs'] = {'browser': 'ALL'}


# Help function, called when there are invalid arguments

def help():
    print
    '\nUsage: python TimeEdit.py -u -p -r -s -e\nSends a curl request to book a room using [-u] username, [-p] password, [-r] room, [-s] start-time, [-e] end-time\n\t-u\tYour feide username\n\t-p\tYour feide password\n\t-r\tRoom number [A062, A266, A267, A268, A269, A270]\n\t-s\tStart-time\n\t-e\tEnd-time\n\tExample: python TimeEdit.py user password A266 08:00 18:00\n'
    return


# Grab logincookie using selenium with chrome webdriver  (phantomjs does not work)


# Get the right room ID from room number.
def get_room_ID(room):
    room_ID = [300]  # Array with ID's with ID of room Axxx at index xxx
    for i in range(0, 300):
        room_ID.append(0)
    room_ID[266] = "162176"
    room_ID[267] = "162177"
    room_ID[268] = "162178"
    room_ID[269] = "162179"
    room_ID[270] = "162180"
    room_ID[300] = '161930'
    if room != "A062":
        room = str(room_ID[int(room[1:4])]) + '.185'
    else:
        room = str(161156.185)
    return room


# Create data dictionary to pass along with request. First arg is days ahead in time
# @start_time and @end_time is in format MMHH
def create_data_dict(name_reservation, days_ahead, room, start_time, end_time):
    date = datetime.date.today() + datetime.timedelta(days=days_ahead)
    date = '20' + str(date.strftime('%y%m%d'))
    data = {
        'fe49': name_reservation,
        'fe50': name_reservation + '@stud.uia.no',
        'id': '-1',
        'dates': date,
        'datesEnd': date,
        'startTime': start_time,
        'endTime': end_time,
        'o': room,
        'url': 'https%3A%2F%2Fno.timeedit.net%2Fweb%2Fhig%2Fdb1%2Fstudent%2Fr.html%3Fh%3Dt%26sid%3D5%26id%3D-1%26step%3D2%26id%3D-'
               + '1%26dates%3D' + date + '%26datesEnd%3D' + date + '%26startTime%3D8%253A00%26endTime%3D22%253A00%26o%3D' +
               room + '%252C10%252C%2BA' + room + '%252C%2Bgrupperom',
        'kind': 'reserve'}
    return data


help()

parser = argparse.ArgumentParser(description='Room reservation for UIA',
                                 formatter_class=argparse.RawDescriptionHelpFormatter, usage='main.py \
                                 USERNAME PASSWORD [--starttime {8|12}] [--room roomID] [--duration {4|8}]')
parser.add_argument('username', help='Your feide username', default='')
parser.add_argument('password', help='Your feide password', default='')
parser.add_argument('--duration', default='4', help='Duration of reservation in hours')
parser.add_argument('--starttime', default='9',
                    help='Either 8 or 12. Booking will be for starttime + 4 hours')
parser.add_argument('--room', default='510S313', help='The id of the room you wish to book.' +
                                                      'For S312 use 510S312 and for S313 use 510S313')
parser = parser.parse_args()

logger = logging.getLogger('Roomshark')
logger.setLevel(logging.DEBUG)
# Create file handler which logs even debug messages
fh = logging.FileHandler(str(os.path.dirname(os.path.realpath(__file__)) + '/debug.log'))
# Create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
# Log level information, debug messages visible in file console handler
ch.setLevel(logging.DEBUG)
fh.setLevel(logging.INFO)
# Logging
# Create format and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
daysahead = 6
today = datetime.datetime.now().date()
future_date = today + datetime.timedelta(days=daysahead)
date_str = future_date.strftime("%Y%m%d")

# Renaming som runtime arguments for readability
# Creating chromedriver
# Using virtualdisplay, will be running on server with no window manager
logger.info("Starting chromedriver")

try:

    driver = webdriver.Chrome("chromedriver", desired_capabilities=d)
    driver.set_window_size(1920,1080)

except Exception:
    logger.error("Connection to chromedriver dropped")


# Log in to feide and send reservation
# @param start_time should be either 8 or 12
# @param room should be '510S312' or '510S313'
def send_reservation(start_time, room):
    # Go directly to the date two weeks from now with the correct starting time
    # Days should be 14 if server has GMT+1 timezone
    date = str(datetime.date.today() + datetime.timedelta(days=14))
    logger.info("Reserving for date: " + date)
    logger.info("With start time: " + start_time)
    url = 'https://tp.uio.no/ntnu/rombestilling/?start=' + start_time + ':00&duration=4:00&preset_date=' + date + '&roomid=' + room
    driver.get(url)

    # Find the element which decides end time
    try:
        search_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "rb-bestill")))
        search_box.click()
        logger.debug("Clicked submit, waiting view to change")
    except Exception:
        logger.error("Wrong login, room already booked or no more bookings available for this user.")
        return False

    # Clicked submit, waiting up to 5 seconds for view to change
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "name")))
    try:
        element.send_keys("\ue004\ue004\ue004\ue006")
        logger.debug("Sending confirmation")
    except Exception:
        logger.exception("Selenium couldnt find confirmation button")
    finally:
        logger.info('Successfully created reservation')
        return True;


def create_cookie(username, password, driver, datestring):
    url = 'https://cloud.timeedit.net/uia/web'
    driver.get(url)

    driver.get(
        "https://cloud.timeedit.net/uia/web/tp/ri1Q59.html"
    )

    wait = WebDriverWait(driver, 100)
    time.sleep(2)
    link = driver.find_element_by_link_text("Feide pålogging")
    link.click()

    wait = WebDriverWait(driver, 100)
    time.sleep(2)
    search_box = wait.until(EC.presence_of_element_located((By.ID, "microsoft-signin-button")))
    search_box.click()
    wait = WebDriverWait(driver, 100)
    time.sleep(2)
    search_box = wait.until(EC.presence_of_element_located((By.ID, "i0116")))
    search_box.click()
    search_box.send_keys(username, Keys.ENTER)
    time.sleep(2)
    logger.info(f"Loggin into user {username}")

    wait = WebDriverWait(driver, 100)
    search_box = wait.until(EC.presence_of_element_located((By.ID, "idSIButton9")))
    search_box.click()
    try:
        wait = WebDriverWait(driver, 100)
        search_box = wait.until(EC.presence_of_element_located((By.ID, "i0118")))

        search_box.send_keys(password, Keys.ENTER)
        search_box.submit()
        time.sleep(5)
        logger.info(f"Password passed")
    except:
        logger.info(f"password failed")

    try:
        logger.info(f"Microsoft Authentication {username}")

        microsoft = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-row")))
        microsoft.click()

        logger.info(f"Successful login")
    except Exception:
        logger.exception("Couldnt select UIA when logging in to feide")
        return driver.quit()

    try:
        logger.info(f"Microsoft Text {username}")

        microsoft = wait.until(EC.presence_of_element_located((By.ID, "idChkBx_SAOTCAS_TD")))
        microsoft.click()
        wait = WebDriverWait(driver, 100)
        # checkbox = driver.find_element_by_id("idChkBx_SAOTCAS_TD")
        # checkbox.click()

        logger.info(f"Successful login")

        wait = WebDriverWait(driver, 200)

        # next_button = wait.until(EC.presence_of_element_located((By.ID, "idSIButton9")))
        # next_button.click()
    except Exception:
        logger.exception("Couldnt Microsoft authenticate  when logging in to feide")
        return driver.quit()

    wait = WebDriverWait(driver, 100)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='idSIButton9']"))).click()

    # driver.find_element_by_css_selector(By.ID,"idSIButton9").click()
    # next_box = wait.until(EC.presence_of_element_located((By.ID, "idSIButton9")))
    # next_box.click()
    # time.sleep(10)

    #driver.find_element_by_css_selector("label.weekZoomFirst.weekZoomDay.clickable").click()
    time.sleep(2)
    print("here")

    label = driver.find_element_by_css_selector("label.weekZoomDay")
    # Get the size of the element
    size = label.size

    # Get the location of the element
    location = label.location
    print(location)

    # Calculate the x and y coordinate to click
    x = location['x'] + size['width'] / 2
    y = location['y'] + size['height'] / 2

    # Execute the JavaScript to click on the element
    print(x,y)
    driver.execute_script("document.elementFromPoint({x}, {y}).click();".format(x=x, y=y))


    element = driver.find_element_by_xpath(
        "//div[contains(@class, 'weekDayHeader') and contains(@class, 'dateIsTodayHeader')]")

    print(daysahead)
    #for i in range(daysahead):
      #  time.sleep(2)
       # next_date = driver.find_element_by_id("leftresdateinc")
       # next_date.click()


    for i in range(daysahead):
        time.sleep(2)
        next_date = driver.find_element_by_id("leftresdateinc")
        next_date.click()

    # try:
    #     wait = WebDriverWait(driver, 100)
    #     time.sleep(2)
    #     print(datestring)
    #
    #     element = driver.find_element_by_xpath("//div[@class='slotfree2 slotfreetarget']")
    #
    #     # Get the size of the element
    #     size = element.size
    #
    #     # Get the location of the element
    #     location = element.location
    #
    #     # Calculate the x and y coordinate to click
    #     x = location['x'] + size['width'] / 2
    #     y = location['y'] + size['height'] / 2
    #
    #     # Execute the JavaScript to click on the element
    #     driver.execute_script("document.elementFromPoint({x}, {y}).click();".format(x=x, y=y))
    #
    #     time.sleep(2)
    # except Exception:
    #     return logger.exception("Cant fint date in the selection")
    #
    logger.info("success")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    #element = driver.find_element(By.XPATH, "//div[@data-dates='{datestring}' and @style='top: 1720px; left: 0.0%; width: 100.0%; height: 40px;']")
    #label = driver.find_element_by_xpath("//div[@class='slotfree2' and @data-object='117.4']")
    element = driver.find_element_by_css_selector("div.slotfree2[data-object='117.4']")
    size = element.size

         # Get the location of the element
    location = element.location

         # Calculate the x and y coordinate to click
    x = location['x'] + size['width'] / 2
    y = location['y'] + size['height'] / 2
    # Execute the JavaScript to click on the element
    #element = driver.find_element_by_xpath(f"//div[@data-dates='{datestring}' and @style='top: 1720px; left: 0.0%; width: 100.0%; height: 40px;']")
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(element, 0, 10)
    actions.click()
    actions.perform()
    time.sleep(2)








    return


def main():
    # Get arguments
    url = 'https://cloud.timeedit.net/uia/web'
    username = parser.__getattribute__('username')
    password = parser.__getattribute__('password')
    start_time = int(parser.__getattribute__('starttime'))
    room = parser.__getattribute__('room')
    duration = int(parser.__getattribute__('duration'))

    print(date_str)
    cookies = create_cookie(username, password, driver, date_str)
    driver.get("https://cloud.timeedit.net/uia/web")
    wait = WebDriverWait(driver, 100)
    # link = driver.find_element_by_css_selector("a.items")
    # link = driver.find_element_by_link_text("Timeplan")
    # link.click()

    wait = WebDriverWait(driver, 100)

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
        ,
        'cookie': 'sso-parameters=back=https%3A%2F%2Fcloud.timeedit.net%2Fuia%2Fweb%2Ftp%2Fri1Q59.html&ssoserver=feide; TEuiaweb='}

    # Print the headers
    # print(headers)
    # print(headers)
    # Get cookie
    # Send reservation for the default 4 hrs
    # if (not send_reservation(str(start_time), room)):
    #    # If the reservation doesnt go through just try to book room 312 instead
    #   logger.debug("Room booked it seems, trying S312")
    #   send_reservation(str(start_time), '510S312')
    # Check duration, if over 4 hours make two reservations
    # if (duration > 4):
    #   if (not send_reservation(str(start_time + 4), room)):
    #      # If the reservation doesnt go through just try to book room 312 instead
    #     logger.debug("Room booked it seems, trying S312")
    #    send_reservation(str(start_time + 4), '510S312')
    # Close the display driver when done
    driver.quit()
    logger.info("Done")


if __name__ == "__main__":
    main()

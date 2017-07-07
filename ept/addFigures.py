#!/usr/bin/python

import re
import os
import sys
from time import sleep
from selenium import webdriver
from termcolor import colored, cprint

def getTitleFromFilename(filename):
    title = os.path.basename(filename)
    title = os.path.splitext(title)[0]
    title = re.sub('\.\d+$', '', title)
    title = re.sub('http_', 'http://', title)
    title = re.sub('https_', 'https://', title)
    return title

def addFigure(filename):
    add_button = driver.find_element_by_xpath('//*[@id="tabContent"]/form/fieldset[3]/a')
    add_button.click()
    sleep(1)

    iframe = driver.find_element_by_css_selector('iframe')
    driver.switch_to.frame(iframe)
    upload_radio = driver.find_element_by_id('figureTypeImage')
    upload_radio.click()

    file_input = driver.find_element_by_css_selector('#figureFile')
    file_input.send_keys(filename)

    title_input = driver.find_element_by_css_selector('#title')
    title_input.send_keys(getTitleFromFilename(filename))
    driver.find_element_by_css_selector('#AttachButton > input[type="submit"]').click()
    driver.switch_to.default_content()


def checkInputFile(filename):
    if not os.path.isfile(filename):
        raise Exception(filename)
    with open(filename, 'r') as f:
        for img_file in f:
            img_file = img_file.strip()
            if not os.path.isfile(img_file):
                raise Exception(img_file)
    return True

def print_status(msg):
    p = colored("[*] ", color="blue", attrs=["bold"])
    p += colored(msg, color="green", attrs=["bold"])
    print p

def print_good(msg):
    p = colored("[+] ", color="green", attrs=["bold"])
    p += colored(msg, color="green", attrs=["bold"])
    print p

def print_error(msg):
    p = colored("[-] ", color="red", attrs=["bold"])
    p += colored(msg, color="red", attrs=["bold"])
    print p

def prompt(msg):
    p = colored("[?] ", color="yellow", attrs=["bold"])
    p += colored(msg, color="yellow", attrs=["bold"])
    raw_input(p)

print_status("Checking file " + sys.argv[1] + "...")
try:
    checkInputFile(sys.argv[1])
except Exception as e:
    print_error("File not found: " + e.message)
    exit(1)
print_status("Input file OK")
print_status("Opening webdriver...")
driver = webdriver.Chrome('/usr/lib/chromium/chromedriver')
driver.get('https://cso.tracesecurity.com/')
prompt("Navigate to the summaries tab in the report and press Enter")

with open(sys.argv[1], 'r') as f:
    for img_name in f:
        addFigure(os.path.realpath(img_name.strip()))
        sleep(1)


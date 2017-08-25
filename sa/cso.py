from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import os, re
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from interactive import *

def getTitleFromFilename(filename):
    title = os.path.basename(filename)
    title = os.path.splitext(title)[0]
    title = re.sub('\.\d+$', '', title)
    title = re.sub('%', '/', title)
    #if len(title) > 70:
    #   raise Exception("Figure title too long")
    return title[:70]

def repeatOnError(fn, test, *args, **kwargs):
    while(True):
        try:
            x = fn(*args, **kwargs)
        except:
            sleep(1)
            continue
        if(test(x)):
            return x

class CSO(object):
    def __init__(self, credfile=os.path.join(os.environ['HOME'], "credentials.ini"), headless=False):
        self.headless = headless
        cred_config = ConfigParser()
        cred_config.read(credfile)
        self.creds = {}
        try:
            self.creds['login'] = cred_config.get('CSO', 'login')
            self.creds['password'] = cred_config.get('CSO', 'password')
        except NoOptionError, NoSectionError:
            print_debug("Credentials for CSO not found")
            self.creds = None

    def start(self):
        self.driver = webdriver.Chrome('/usr/lib/chromium/chromedriver')
        self.driver.get('https://cso.tracesecurity.com/')
        self.login()

    def login(self):
        if self.creds is not None:
            self.driver.find_element_by_id('username').send_keys(self.creds['login'])
            self.driver.find_element_by_id('password').send_keys(self.creds['password'])
            self.driver.find_element_by_id('LoginButton').click()
        else:
            prompt('Enter credentials and hit enter when done')

    def setValue(self, element, value):
        if element.tag_name == 'textarea':
            self.driver.execute_script('arguments[0].innerText = arguments[1]', element, value)
        elif element.tag_name == 'select':
            self.driver.execute_script('arguments[0].value = arguments[1]', element, value)
        else:
            self.driver.execute_script('arguments[0].setAttribute("value", arguments[1])', element, value)
    def clickOn(self, s):
        self.driver.find_element_by_css_selector(s).click()

    #Timeout can be -1 for infinite
    def css(selector, timeout=5, msg=None):
        while timeout !== 0:
            timeout--
            try:
                return self.driver.find_element_by_css_selector(selector)
            except NoSuchElementException:
                if msg is not None:
                    print "msg".format(timeout=timeout, selector=selector)
        return None

    def createScan(self, name, ips, scan_times="always"):
        create_button = self.driver.find_element_by_xpath('//td[@class="MainItem" and div[contains(., "Create/Modify Schedules for Vulnerability and Configuration Scans")]]//span[contains(., "Create")]')
        create_button.click()
        sleep(2)
        name_input = self.driver.find_element_by_id('scanScheduleName')
        self.setValue(name_input, name)

        #Select first scanner
        self.driver.find_element_by_id('selectedScannerId').send_keys(Keys.DOWN)

        #Set TS Only
        self.driver.find_element_by_xpath('//input[@name="scan.scanTemplate.traceOnly"]').click()

        #Save and Next
        self.driver.find_element_by_xpath('//span[contains(., "Save and Next")]').click()
        print "Saving page 1..."
        sleep(3)

        #Skip setting start time
        self.driver.find_element_by_xpath('//span[contains(., "Save and Next")]').click()
        print "Saving start times..."
        sleep(3)

        if scan_times != "always":
            self.driver.find_element_by_xpath('//label[contains(., "Choose an existing scan time")]/input').click()
            scan_val = self.driver.find_element_by_xpath('//select[@id="rtaPauseScheduleId"]/option[contains(., "<{}>")]'.format(scan_times)).get_attribute('value')

            self.setValue(self.driver.find_element_by_xpath('//select[@id="rtaPauseScheduleId"]'), scan_val)
            sleep(2)
            #self.driver.find_element_by_xpath('//select[@id="rtaPauseScheduleId"]').send_keys("\t")
        self.driver.find_element_by_xpath('//span[contains(., "Save and Next")]').click()
        print "Saving scan times..."
        sleep(3)

        #Skip authenticated scanning
        self.driver.find_element_by_xpath('//span[contains(., "Save and Next")]').click()
        print "Saving authenticated scanning..."
        sleep(2)

        #Set targets
        self.setValue(self.driver.find_element_by_id('scanTemplateTargets'), ','.join(ips))
        self.driver.find_element_by_xpath('//span[contains(., "Save and Next")]').click()
        print "Saving targets..."
        sleep(2)

        #Activate
        self.setValue(self.driver.find_element_by_id('validIP'), '1.1.1.1')
        self.setValue(self.driver.find_element_by_id('invalidIP'), '1.1.1.1')
        self.driver.find_element_by_xpath('//input[@name="scan.scanTemplate.manualAssessment"]').click()
        self.driver.find_element_by_xpath('//span[contains(., "Save and Next")]').click()
        print "Saving activation..."
        sleep(2)

        #Complete
        self.driver.find_element_by_id('SaveAndCloseButtonScanSchedule').click()
        print "Completing scan setup..."
        sleep(2)

    def submitReport(self, number):
        while(True):
            #The link to the report is an anchor with the onclick set to "openOnsiteCSADialog(NUMBER)"
            #XXX There should be a better way of getting the number than inspecting element and then pasting
            #it into this program
            self.driver.execute_script('openOnsiteCSADialog(arguments[0])', number)
            tab_selector = '#tabstsactionbeansbackendadminOnsiteCSAReportSetupActionBean > ul'
            self.driver.execute_script("""
                    tabs = document.querySelector(arguments[0]);
                    tabs.children[tabs.children.length-1].querySelector('a').click();
                    """, tab_selector)
            #XXX This will wait for the checkbox to appear for 30 seconds
            check = self.css('input[name="deliverReport"]', timeout=30, msg="Wating for tab to load")
            #XXX Haven't verified anything after this point
            if check is not None:
                check.setAttribute('checked', 'true')
                self.driver.xpath('span[contains(., "Save and Close")]').click()
                break
            else:
                self.driver.xpath('span[contains(., "Save and Close")]').click()

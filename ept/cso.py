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
            prompt('Login and hit enter when done')

    def setValue(self, element, value):
        if element.tag_name == 'textarea':
            self.driver.execute_script('arguments[0].innerText = arguments[1]', element, value)
        elif element.tag_name == 'select':
            self.driver.execute_script('arguments[0].value = arguments[1]', element, value)
        else:
            self.driver.execute_script('arguments[0].setAttribute("value", arguments[1])', element, value)
    def clickOn(self, s):
        self.driver.find_element_by_css_selector(s).click()
    def analyzeVulnerabilities(self):
        self.clickOn('#MyAssignments')
        sleep(2)
        self.clickOn('#ui-accordion-accordion-panel-1 > div:nth-child(6) > a')
    def moveToTop(self, company):
        #self.driver.find_element_by_xpath('//a[@href="/secure/BackendAdmin/ViewClustScanners.html"]').click()
        self.driver.get('https://cso.tracesecurity.com/secure/BackendAdmin/ViewClustScanners.html')
        self.driver.find_element_by_xpath('//a[contains(., "5.0 Scanners")]').click()
        while True:
            try:
                print "moving %s up" % company
                self.driver.find_element_by_xpath('//table[@id="templatesTable"]/tbody/tr[td[contains(., "' + company + '")]]/td/a[img[@src="/images/arrowup.gif"]]').click()
                sleep(1)
            except NoSuchElementException:
                break
    def getVulnerabilities(self):
        vulns = []
        vulnLinks = self.driver.find_elements_by_css_selector('#vulnTable>tbody>tr>td:nth-child(2)>a')
        for idx in range(len(vulnLinks)):
            v = repeatOnError(
                    lambda: self.driver.find_elements_by_css_selector('#vulnTable>tbody>tr>td:nth-child(2)>a')[idx],
                    lambda: True)
            v.click()
            vInfo = repeatOnError(lambda: self.driver.find_element_by_id('Vulnerability'))
            name = vInfo.find_element_by_css_selector('table > tbody > tr:nth-child(1) > td.FormContent').text
            print "adding vulnerability", name

            nodes = repeatOnError(lambda: self.driver.find_elements_by_css_selector('#tableAssets>tbody>tr'),
                                lambda x: len(x) > 0)
            for n in nodes:
                parts = [x.text for x in n.find_elements_by_css_selector('td')]
                print "adding node", parts[7]
                vulns.append([name] + parts[7:])
            p = self.driver.find_element_by_xpath('//div[div[@id="dialogVulnDetails"]]')
            p.find_element_by_css_selector('button[title="close"]').click()
        return vulns
    #Timeout can be -1 for infinite
    def css(self, selector, timeout=5, msg=None):
        while timeout != 0:
            timeout -= 1
            try:
                return self.driver.find_element_by_css_selector(selector)
            except NoSuchElementException:
                if msg is not None:
                    print "msg".format(timeout=timeout, selector=selector)
        return None

    def addFigure(self, filename):
        iframe = self.css('iframe')
        self.driver.switch_to.frame(iframe)
        try:
            upload_radio = self.driver.find_element_by_id('figureTypeImage')
            upload_radio.click()

            file_input = self.driver.find_element_by_css_selector('#figureFile')
            file_input.send_keys(filename)

            title_input = self.driver.find_element_by_css_selector('#title')
            self.setValue(title_input, getTitleFromFilename(filename))
            #title_input.send_keys("\t")
            #sleep(.1)
            self.driver.find_element_by_css_selector('#AttachButton > input[type="submit"]').click()
        except:
            self.driver.switch_to.default_content()
            raise
        self.driver.switch_to.default_content()


    def openManualVulnerabilites(self):
        self.driver.find_element_by_xpath('//div[@class="InnerFormTitle" and contains(., "Manual Vulnerabilities")]/img[contains(@src, "plus.gif")]').click()

    def addVulnerability(self, directory):
        self.driver.find_element_by_xpath('//a[contains(., "Add Vulnerability")]').click()
        #block = self.driver.find_element_by_xpath('//div[@class="InnerFormTitle" and contains(., "Manual Vulnerabilities")]/following-sibling::div')
        #tbody = block.find_element_by_tag_name('tbody')
        #manvulns = tbody.find_elements_by_css_selector('.RowmanualVulnerabilites')
        #curvuln = manvulns[len(manvulns) - 1]
        inputs = self.driver.find_elements_by_xpath('//td[contains(., "Name:")]/following-sibling::td/textarea')
        with open(os.path.join(directory, "name")) as f:
            self.setValue(inputs[len(inputs) - 2], f.read())
            inputs[len(inputs) - 2].send_keys("\t")
        inputs = self.driver.find_elements_by_xpath('//td[contains(., "Description:")]/following-sibling::td/textarea')
        with open(os.path.join(directory, "description")) as f:
            self.setValue(inputs[len(inputs) - 2], f.read())
            inputs[len(inputs) - 2].send_keys("\t")
        inputs = self.driver.find_elements_by_xpath('//td[contains(., "Remediation:")]/following-sibling::td/textarea')
        with open(os.path.join(directory, "remediation")) as f:
            self.setValue(inputs[len(inputs) - 2], f.read())
            inputs[len(inputs) - 2].send_keys("\t")

        addnotes = self.driver.find_elements_by_xpath('//a[contains(., "Add/Update Notes")]')
        addnotes[len(addnotes) - 2].click()
        notesdir = os.path.join(directory, 'notes')
        is_first_note = True
        for rel_notedir in os.listdir(notesdir):
            notedir = os.path.join(notesdir, rel_notedir)
            if os.path.exists(os.path.join(notedir, 'figures')):
                if not is_first_note:
                    self.driver.find_element_by_xpath('//a[contains(., "Add Note")]').click()
                sleep(.2)
                notes = self.driver.find_elements_by_css_selector('.RowInitialNote textarea')
                with open(os.path.join(notedir, 'note')) as f:
                    self.setValue(notes[len(notes) - 2], f.read())
                
                with open(os.path.join(notedir, 'figures')) as f:
                    for fig in f:
                        print 'Adding "{}"'.format(fig.strip())
                        addfigures = self.driver.find_elements_by_xpath('//a[contains(., "Add Figure")]')
                        addfigures[len(addfigures) - 2].click()
                        sleep(1)
                        self.addFigure(fig.strip())
                        sleep(1)
                is_first_note = False
            else:
                print "Skipping", notedir

        self.driver.find_element_by_xpath('//input[@type="submit" and @value="Save"]').click()

    def addAppendixFigure(self, filename):
        add_button = self.driver.find_element_by_xpath('//*[@id="tabContent"]/form/fieldset[3]/a')
        add_button.click()
        sleep(1)
        self.addFigure(filename)

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

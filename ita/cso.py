from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from selenium import webdriver
import os, re
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from interactive import *
from time import strftime

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

def print_debug(msg):
    print msg

class CSO(object):
    def __init__(self, credfile=os.path.join(os.environ['HOME'],"credentials.ini"),headless=False, driver='firefox'):
        self.driver_type = driver
        self.controls = []
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
        if self.driver_type == 'chromium':
            self.driver = webdriver.Chrome('/usr/lib/chromium/chromedriver')
        elif self.driver_type == 'firefox':
            self.driver = webdriver.Firefox()
        else:
            raise Exception('Invalid driver %s' % self.driver_type)
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
    def addFileToRepo(self, filename, title_fmt="{title}"):
        self.waitFor(xpath='//a[contains(., "Upload File")]').click()
        title = os.path.basename(filename)
        title = os.path.splitext(title)[0]
        title = title_fmt.format(title = title)
        self.setValue(self.waitFor('#name'), title)
        self.waitFor('input[name="file"]').send_keys(os.path.realpath(filename))
        self.waitFor(xpath='//button[span[contains(., "Save and Next")]]').click()
        self.waitFor('tbody[role="alert"] tr:nth-child(2) input[type="checkbox"]', timeout=60).click()
        self.waitFor(xpath='//button[span[contains(., "Save and Close")]]').click()

    def getSiblingOfLabel(self, labelname):
        try:
            self.driver.find_element_by_xpath('//a[contains(@title, "Click to edit Control")]').click()
            sleep(1)
        except:
            pass
        try:
            return self.driver.find_element_by_xpath('//div[@id="editControl"]//td[contains(., "' 
                        + labelname + '")]/following-sibling::td')
        except:
            return self.driver.find_element_by_xpath('//div[@id="editControl"]//td[label[contains(., "'
                        + labelname + '")]]/following-sibling::td')
    def getFromNoEditControl(self, labelname):
        try:
            self.driver.find_element_by_xpath('//a[contains(@title, "Click to edit Control")]').click()
            sleep(1)
        except:
            pass
        try:
            return self.driver.find_element_by_xpath('//div[@id="editControl"]//td'
                        + '[label[contains(., "' + labelname + '")]]/following-sibling::td'
                        + '/textarea').get_attribute('value')
        except:
            try:
                #return self.driver.find_elements_by_xpath('//div[@id="noEditControl"]//td'
                #        + '[contains(., "' + labelname + '")]/following-sibling::td')[0].text
                return self.driver.find_element_by_xpath('//div[@id="editControl"]//td'
                         + '[label[contains(., "' + labelname + '")]]/following-sibling::td').text
            except:
                raise Exception("Error getting label '{}'".format(labelname))

    def waitFor(self, css="body", xpath=None, timeout=10):
        time = 0
        while True:
            try:
                if xpath is not None:
                    return self.driver.find_element_by_xpath(xpath)
                else:
                    return self.driver.find_element_by_css_selector(css)

            except NoSuchElementException as e:
                time += 1
                if time > timeout:
                    raise
                else:
                    sleep(1)

    def tryClick(self, css="body", xpath=None, timeout=10):
        time = 0
        while True:
            try:
                if xpath is not None:
                    return self.waitFor(xpath = xpath, timeout=timeout).click()
                else:
                    return self.waitFor(css = css, timeout=timeout).click()

            except ElementNotVisibleException as e:
                time += 1
                if time > timeout:
                    raise
                else:
                    sleep(1)

    def getAllControls(self):
        data = []
        while True:
            self.waitFor(css='#SaveAndCloseButtonQuestion')
            data.append(self.getControlData())
            try:
                print "Moving to next control"
                self.driver.find_element_by_id('SaveAndNextButtonQuestion')
                self.driver.execute_script('document.querySelector("#SaveAndNextButtonQuestion").click()')
            except NoSuchElementException:
                break
            sleep(2)
        return data

    def getControlData(self):
        data = {}
        self.editControl()
        data['asset'] = self.waitFor('#editControl>table>tbody>tr>td:nth-child(2)').text
        data['control'] = self.waitFor('#divChildParentControlEdit').text
        verify_mapping = {
                0: 'unverified',
                1: 'implemented',
                2: 'not implemented',
                4: 'in progress'
            }
        verification_elem = self.waitFor(xpath = '//input[starts-with(@id, "controlVerification") and @checked="checked"]')
        verification_value = verification_elem.get_attribute('value')
        data['verification'] = verify_mapping[int(verification_value)]
        resource_rows = self.driver.find_elements_by_css_selector('table#resourcesTable tr')[1:]
        resources = [r.find_elements_by_tag_name('td')[1].text for r in resource_rows ]
        data['resources'] = '|'.join(resources)
        data['observation'] = self.waitFor(css='#notes').get_attribute('value')
        data['recommendation'] = self.waitFor(css='#auditRecommendation').get_attribute('value')
        data['date'] = self.waitFor(css='#auditDate').get_attribute('value')
        method_mapping = {
                '0': '',
                '1': 'interview',
                '2': 'observation',
                '5': 'documentation',
                '6': 'testing'
            }
        try:
            method_value = self.waitFor(css='#grcAuditMethodTypeID').get_attribute('value')
            data['method'] = method_mapping[method_value]
        except:
            pass
        try:
            data['source'] = self.waitFor(css='#auditInterviewee').get_attribute('value')
        except:
            pass
        return data

    def getAllRiskControls(self):
        data = []
        while True:
            self.waitFor(css='#SaveAndCloseButtonQuestion')
            data.append(self.getRiskControlData())
            try:
                print "Moving to next control"
                self.driver.find_element_by_id('SaveAndNextButtonQuestion')
                self.driver.execute_script('document.querySelector("#SaveAndNextButtonQuestion").click()')
            except NoSuchElementException:
                break
            sleep(2)
        return data

    def getRiskControlData(self):
        data = {}
        self.editControl()
        data['asset'] = self.waitFor('#editControl>table>tbody>tr>td:nth-child(2)').text
        data['control'] = self.waitFor('#divChildParentControlEdit').text
        verify_mapping = {
                0: 'unverified',
                1: 'implemented',
                2: 'not implemented',
                3: 'NA',
                4: 'in progress'
            }
        verification_elem = self.waitFor(xpath = '//input[starts-with(@id, "controlImplementation") and @checked="checked"]')
        verification_value = verification_elem.get_attribute('value')
        data['verification'] = verify_mapping[int(verification_value)]
        resource_rows = self.driver.find_elements_by_css_selector('table#resourcesTable tr')[1:]
        resources = [r.find_elements_by_tag_name('td')[1].text for r in resource_rows ]
        data['resources'] = '|'.join(resources)
        data['observation'] = self.waitFor(css='#notes').get_attribute('value')
        data['recommendation'] = self.waitFor(css='#recommendation').get_attribute('value')
        data['date'] = self.waitFor(css='#dateOfAnalysis').get_attribute('value')
        try:
            data['source'] = self.waitFor(css='input[name="control.interviewee"]').get_attribute('value')
        except:
            pass
        return data

    def editControl(self):
        self.driver.execute_script("$('#editControl').show(); $('#noEditControl').hide(); $('#editingControl').val(true);")
    def batchAddData(self, data, selector):
        for row in data:
            self.waitFor(css='#SaveAndCloseButtonQuestion')
            #self.driver.execute_script("$('#editControl').show(); $('#noEditControl').hide(); $('#editingControl').val(true);")
            self.editControl()
            self.setAllData(row, selector)
            try:
                print "Moving to next control"
                self.driver.find_element_by_id('SaveAndNextButtonQuestion')
                self.driver.execute_script('document.querySelector("#SaveAndNextButtonQuestion").click()')
            except NoSuchElementException:
                break
            sleep(2)
    def setAllData(self, row, selector):
        virt = {'audit': 
                    {
                        'verification': self.setVerification,
                        'supporting documentation': self.addResources,
                        'resources': self.addResources,
                        'observation': self.setObservation,
                        'recommendation': self.setRecommendation,
                        'method': self.setMethod,
                        'source': self.setSource,
                        'date': self.setDate
                    },
                'risk': {
                        'implementation': self.setRiskImplementation,
                        'observation': self.setObservation,
                        'recommendation': self.setRiskRecommendation,
                        'source': self.setRiskSource,
                        'date': self.setRiskDate
                    }
                }
        for key, value in row.iteritems():
            if key in virt[selector] and value is not None:
                virt[selector][key](value)
        if 'date' not in row:
            virt[selector]['date']()
    def setRiskImplementation(self, implemented):
        mapping = {
                'unanswered': 0,
                'implemented': 1,
                'not implemented': 2,
                'unimplemented': 2,
                'n/a': 3,
                'partial': 4,
                'partially implemented': 4,
                'in progress': 4,
            }
        implemented = implemented.lower()
        if implemented not in mapping:
            print "WARNING:", implemented, "is not a valid verification string." 
        else:
            selector = "#controlImplementationLevel_%d" % mapping[implemented]
            self.waitFor(css=selector).click()

    def setVerification(self, implemented):
        mapping = {
                'unverified': 0,
                'implemented': 1,
                'not implemented': 2,
                'unimplemented': 2,
                'partial': 4,
                'partially implemented': 4,
                'in progress': 4
            }
        implemented = implemented.lower()
        if implemented not in mapping:
            print "WARNING:", implemented, "is not a valid verification string." 
        else:
            selector = "#controlVerificationStatus_%d" % mapping[implemented]
            self.waitFor(css=selector).click()
            #self.driver.execute_script('arguments[0].checked=true;', self.waitFor(css=selector))
    def setObservation(self, text):
        if text != '':
            self.setValue(self.waitFor(css='#notes'), text)
    def setRiskRecommendation(self, text):
        if text != '':
            self.setValue(self.waitFor(css='#recommendation'), text)
    def setRecommendation(self, text):
        if text != '':
            self.setValue(self.waitFor(css='#auditRecommendation'), text)
    def setRiskDate(self, date=None):
        if date is None:
            if len(self.waitFor(css='#dateOfAnalysis').get_attribute('value')) > 0:
                return
            date = strftime("%m/%d/%Y")
        self.setValue(self.waitFor(css='#dateOfAnalysis'), date)
    def setDate(self, date=None):
        if date is None:
            if len(self.waitFor(css='#auditDate').get_attribute('value')) > 0:
                return
            date = strftime("%m/%d/%Y")
        self.setValue(self.waitFor(css='#auditDate'), date)
    def setMethod(self, method):
        mapping = {
                '':         0,
                'interview': 1,
                'observation': 2,
                'documentation': 5,
                'testing': 6
            }
        method = method.lower()
        if method not in mapping:
            print method, "is not a valid verification method.  Skipping..."
        else:
            self.setValue(self.waitFor('#grcAuditMethodTypeID'), mapping[method])
    def setRiskSource(self, source):
        if source != '':
            self.setValue(self.waitFor('input[name="control.interviewee"]'), source)
    def setSource(self, source):
        if source != '':
            self.setValue(self.waitFor('#auditInterviewee'), source)
    def addResources(self, search_string):
        if search_string != "":
            addScript = self.waitFor(xpath='//a[@id="addResource"]|//div[@id="resourcesTable_wrapper"]//a').get_attribute('onclick')
            self.driver.execute_script(addScript)
            close_button =  self.waitFor(xpath='//div[span[contains(., "Create Control Resource")] ]//button')
            self.waitFor(xpath='//select[@id="selectedResourceID"]/option')
            opts = self.driver.find_elements_by_xpath('//select[@id="selectedResourceID"]/option')
            optdict = {}
            for opt in opts:
                if re.search(search_string, opt.text, re.I) is not None:
                    optdict[opt.get_attribute('value')] = opt.text
            optvalues = optdict.keys()
            if len(optvalues) == 0:
                print "NO MATCH for", search_string
                close_button.click()
            while len(optvalues) > 0:
                val = optvalues.pop()
                self.setValue(self.waitFor(css='#selectedResourceID'), val)
                self.driver.execute_script(""" document.querySelector(
                    "#SaveAndCloseButtontsactionbeansmyassignmentsVerifyAuditControlResourcePropertiesActionBean").click()
                    """)
                print "Added resource %s" % optdict[val]
                sleep(3)
                if(len(optvalues) > 0):
                        self.driver.execute_script(addScript)

    def batchAddAuditResources(self, search_strings):
        for search_str in search_strings:
            if search_str != "":
                addScript = self.waitFor(xpath='//a[@id="addResource"]').get_attribute('onclick')
                self.driver.execute_script(addScript)
                close_button =  self.waitFor(xpath='//div[span[contains(., "Create Control Resource")] ]//button')
                opts = self.driver.find_elements_by_xpath('//select[@id="selectedResourceID"]/option')
                optdict = {}
                for opt in opts:
                    if re.search(search_str, opt.text, re.I) is not None:
                        optdict[opt.get_attribute('value')] = opt.text
                optvalues = optdict.keys()
                if len(optvalues) == 0:
                    print "NO MATCH for", search_str
                    close_button.click()
                while len(optvalues) > 0:
                    val = optvalues.pop()
                    self.setValue(self.waitFor(css='#selectedResourceID'), val)
                    c.driver.execute_script(""" document.querySelector(
                        "#SaveAndCloseButtontsactionbeansmyassignmentsVerifyAuditControlResourcePropertiesActionBean").click()
                        """)
                    print "Added resource %s" % optdict[val]
                    sleep(3)
                    if(len(optvalues) > 0):
                        self.driver.execute_script(addScript)
            try:
                print "Moving to next control"
                self.driver.find_element_by_id('SaveAndNextButtonQuestion')
                self.driver.execute_script('document.querySelector("#SaveAndNextButtonQuestion").click()')
            except NoSuchElementException:
                break
            sleep(2)

    def getRiskControls(self):
        while True:
            self.control_fields = 'Asset Control Notes Recommendation'.split()
            control = []
            for k in self.control_fields:
                control.append(self.getFromNoEditControl(k))
            implemented = self.getSiblingOfLabel('Implementation')
            control.append(implemented.find_element_by_xpath('table/tbody/tr/td/label[input[@checked="checked"]]').text)
            print "Appending ", control
            self.controls.append(control)
            try:
                self.clickOn('#SaveAndNextButtonQuestion')
            except:
                break
            sleep(2)
    def getITAVerification(self):
        auditform = self.driver.find_element_by_id('auditControlsForm')
        tiers = self.driver.find_elements_by_id('manageThreatsTable')
        rows = self.driver.find_elements_by_css_selector('#manageThreatsTable tr')
        all_controls = []
        for r in rows:
            expander = r.find_element_by_css_selector('.TreeNode')
            expander.get_attribute('onclick')
            js = expander.get_attribute('onclick')
            m = re.search('expandCollapseChildControls\((\d+),', js)
            m.group(1)
            id="divChildControls"+m.group(1)
            expander.click()
            sleep(5)
            controls = self.driver.find_element_by_id(id)
            links = controls.find_elements_by_css_selector('div>a')
            for l in links:
                l.click()
                sleep(5)
                l.get_attribute('onclick')
                js = l.get_attribute('onclick')
                m = re.search('viewControl\(.*?,.*?,(\d+),', js)
                id = 'name' + m.group(1)
                name = self.driver.find_element_by_id(id).get_attribute('value')
                verify = self.driver.find_element_by_id('verificationProcedure').get_attribute('value')
                all_controls.append((name, verify))
                print "Adding control " + name
                possible = self.driver.find_elements_by_css_selector('.ui-dialog-buttons')
                for p in possible:
                    try:
                        p.find_element_by_id('verificationProcedure')
                    except:
                        pass
                    else:
                        close=p.find_element_by_css_selector('button.ui-dialog-titlebar-close[title="close"]')
                close.click()
            expander.click()
        return all_controls
    def analyzeVulnerabilities(self):
        self.clickOn('#MyAssignments')
        sleep(2)
        self.clickOn('#ui-accordion-accordion-panel-1 > div:nth-child(6) > a')
    def getVulnerabilities(self):
        vulns = []
        vulnLinks = self.driver.find_elements_by_css_selector('#vulnTable>tbody>tr>td:nth-child(2)>a')
        for idx in range(len(vulnLinks)):
            v = repeatOnError(
                    lambda: self.driver.find_elements_by_css_selector('#vulnTable>tbody>tr>td:nth-child(2)>a')[idx],
                    lambda x: True)
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
    def addFigure(self, filename):
        iframe = self.driver.find_element_by_css_selector('iframe')
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
    def close(self):
        self.driver.close()


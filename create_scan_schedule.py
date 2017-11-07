def splitIPs(ips, maxsz):
    split = []
    for i in range(0, len(ips), maxsz):
        if i+maxsz >= len(ips):
            highidx = len(ips)
        else:
            highidx = i+maxsz
        split.append([ips[jdx] for jdx in range(i, highidx)])
    return split

def createScan(name, scanner, times, ips):
    self.driver.execute_script("openDialogScanSchedule(0); return false;")
    self.setValue(self.waitFor('#scanScheduleName'), name)
    #We could set the input value and then run the JS manually
    #scanopt = self.waitFor(xpath='//select[@id="selectedScannerId"]/option[contains(., "{}")]'.format(scanner))
    #scanval = scanopt.get_attribute('value')
    #self.setValue(self.waitFor('#selectedScannerId'), scanval)
    #self.driver.execute_script('showOpenvasActions();')

    #Or we can just click on the option
    self.tryClick(xpath='//select[@id="selectedScannerId"]/option[contains(., "{}")]'.format(scanner))

    self.tryClick('input[name="scan.scanTemplate.traceOnly"]')
    sleep(2)
    self.tryClick(xpath = '//span[contains(., "Save and Next")]')
    sleep(2)
    self.tryClick(xpath = '//span[contains(., "Save and Next")]')

    #Set scan times
    if times != "always":
        self.tryClick(xpath = '//label[contains(., "Choose an existing scan time")]/input')
        #Simply setting the value fails to trigger some JS witchery
        #scan_val = self.waitFor(xpath = '//select[@id="rtaPauseScheduleId"]/option[contains(., "<{}>")]'.format(scan_times)).get_attribute('value')
        #self.setValue(self.waitFor(xpath = '//select[@id="rtaPauseScheduleId"]'), scan_val)

        #So, we click it instead
        self.tryClick(xpath = '//select[@id="rtaPauseScheduleId"]/option[contains(., "{}")]'.format(times))
    sleep(2)
    self.tryClick(xpath = '//span[contains(., "Save and Next")]')

    # configuration scan
    sleep(2)
    self.tryClick(xpath = '//span[contains(., "Save and Next")]')

    #Set targets
    self.setValue(self.waitFor('#scanTemplateTargets'), ','.join(ips))
    self.waitFor('#scanTemplateTargets').send_keys(Keys.TAB)
    sleep(2)
    self.tryClick(xpath = '//span[contains(., "Save and Next")]')
    
    #Activate
    self.setValue(self.waitFor('#validIP', timeout=60), '1.1.1.1')
    self.setValue(self.waitFor('#invalidIP'), '1.1.1.1')
    self.tryClick(xpath = '//input[@name="scan.scanTemplate.manualAssessment"]')
    sleep(2)
    self.tryClick(xpath = '//span[contains(., "Save and Next")]')

    #Complete
    sleep(2)
    self.tryClick('#SaveAndCloseButtonScanSchedule')

#nameform = '2017 IPT-10.6.0.0 #{number}'
#scansz = 1024
#scannername = 'HCBB 2017 Pen Test scanner'
#scan_times = "Nights and Weekends"
#with open('/tmp/ips') as f:
#    ips = [ln.strip() for ln in f]
def createMultiScan(nameform, scanner, times, scansz, ips):
    split = splitIPs(ips, scansz)
    for idx in range(len(split)):
        name = nameform.format(number = idx)
        createScan(name, scanner, times, split[idx])

#self = CSO()
#self.start()

from cso import CSO
from interactive import *

c = CSO()
c.start()
num = prompt("navigate to reports and type in client number")
c.submitReport(num)

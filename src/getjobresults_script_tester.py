from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport

username = "hinemos"
password = "hinemos"
ip = "10.94.1.71"
sessionId = "20180314224709-000"
jobunitId = "CS_JOB"

session = Session()
session.auth = HTTPBasicAuth(username, password)

client = Client("http://" + ip + ":8080/HinemosWS/JobEndpoint?wsdl",
                transport=Transport(session=session))

JobTreeItem = client.service.getJobDetailList(sessionId)

for job in JobTreeItem.children:
    if str(job.data.jobunitId) == jobunitId:
        print " Results for SessionId ( " + sessionId + " ) and JobUnitId ( " + jobunitId + " ):"
        print " - Start Date = " + str(job.detail.startDate)
        print " - End Date = " + str(job.detail.endDate)
        print " - End Status = {0}".format(str(job.detail.endStatus))
        print " - End Value = {0}".format(str(job.detail.endValue))

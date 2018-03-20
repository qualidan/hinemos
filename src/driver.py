from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
#from data_model import *  # run 'shellfoundry generate' to generate data model classes
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
import os
import subprocess

from cloudshell.core.logger.qs_logger import get_qs_logger
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport

import data_model


class HinemosDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    # <editor-fold desc="Discovery">
    '''
    def respository_addNode(self, context,MANAGERURL="http://192.168.0.1:8080/HinemosWS/",PASSWORD="hinemos",IPADDRESS="192.168.0.2",FACILITYID="WEBSERVER 1",FACILITYNAME='"Web Server 1"'):

    # Based on https://translate.google.com/translate?hl=en&sl=ja&u=http://www.hinemos.info/ja/option/commandlinetool&prev=search
    # $ python Repository_addNode.py - H http://192.168.0.1:8080/HinemosWS/ - w hinemos - A 192.168.0.2 - I WEBSERVER 1 - N "Web Server 1"


        python_script = "Repository_addNode.py"
        python_params = "- H {} - w {} - A {} - I {} - N {}".format(MANAGERURL,PASSWORD,IPADDRESS,FACILITYID,FACILITYNAME);
        python_command = "python " + python_script + " " + python_params
        with CloudShellSessionContext(context) as session:
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, 'Executing:{}'.format(python_command))

        logger = get_qs_logger(log_category=context.reservation.reservation_id, log_group=context.resource.name)

        logger.info("Executing : "+python_command)
        response = subprocess.check_output(python_command, cwd=r'c:\1')

        for line in response:
            logger.info("["+python_command+"] output : "+response)

        pass
    '''
    def SOAP_getJobResults(self, context, sessionId,jobunitId, Id):
        # based on https://github.com/hinemos/hinemos/blob/cb0b0c63d16f201e62b7802a50547abd2f5b1225/HinemosClient/src_jobmanagement/com/clustercontrol/jobmanagement/util/JobEndpointWrapper.java
        r_id = context.reservation.reservation_id
        HM = data_model.Hinemos.create_from_context(context)
        csapisession = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain=context.reservation.domain)
        if jobunitId is None:
            jobunitId=""
        if Id is None:
            Id = ""

        ip = context.resource.address
        username = HM.user
        password = csapisession.DecryptPassword(context.resource.attributes['Hinemos.Password']).Value

        with CloudShellSessionContext(context) as session:
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Hinemos GetJobResults:")
            session.WriteMessageToReservationOutput(r_id, "-Inputs: SessionID="+sessionId+" JobUnitId="+jobunitId+" Id="+Id)
            session.WriteMessageToReservationOutput(r_id, "-Results:")

        session = Session()
        session.auth = HTTPBasicAuth(username, password)

        client = Client("http://" + ip + ":8080/HinemosWS/JobEndpoint?wsdl",
                        transport=Transport(session=session))

        JobTreeItem = client.service.getJobDetailList(sessionId)

        for job in JobTreeItem.children:
            if jobunitId == "":
                for job_cmd in job.children:
                    jobunitId=job.data.jobunitId
                    self.printjobresults(context, job, jobunitId, job_cmd.data.id)
            else:
                if str(job.data.jobunitId) == jobunitId:
                    if Id == "":
                        for job_cmd in job.children:
                            self.printjobresults(context, job, jobunitId, job_cmd.data.id)
                    else:
                        for job_cmd in job.children:
                            if str(job_cmd.data.id) == Id:
                                self.printjobresults(context,job,jobunitId,Id)
        pass

    def printjobresults(self, context,job,jobunitId,Id):
        r_id = context.reservation.reservation_id
        with CloudShellSessionContext(context) as session:
            session.WriteMessageToReservationOutput(r_id, " * JobUnitId=" + jobunitId + " Id=" + Id)
            #session.WriteMessageToReservationOutput(r_id,"Results for SessionId (" + sessionId + ") JobUnitId (" + jobunitId + ") Id (" + Id + "):")
            #session.WriteMessageToReservationOutput(r_id," - Start Date = " + str(job.detail.startDate))
            #session.WriteMessageToReservationOutput(r_id," - End Date = " + str(job.detail.endDate))
            session.WriteMessageToReservationOutput(r_id, " - End Status = {0}".format(str(job.detail.endStatus)))
            #session.WriteMessageToReservationOutput(r_id, " - End Value = {0}".format(str(job.detail.endValue)))
        pass

    def SOAP_runJob(self, context, jobunitId, jobId,jobWM=1,jobWT=1):

        HM = data_model.Hinemos.create_from_context(context)
        csapisession = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain=context.reservation.domain)

        ip = context.resource.address
        username = HM.user
        password = csapisession.DecryptPassword(context.resource.attributes['Hinemos.Password']).Value

        #with CloudShellSessionContext(context) as session:
            #session.WriteMessageToReservationOutput(context.reservation.reservation_id, 'Password found : {}'.format(password))

        session = Session()
        session.auth = HTTPBasicAuth(username, password)

        client = Client("http://"+ip+":8080/HinemosWS/JobEndpoint?wsdl",
                        transport=Transport(session=session))

        factory = client.type_factory('http://jobmanagement.ws.clustercontrol.com')

        out = factory.outputBasicInfo()
        trig = factory.jobTriggerInfo()

        trig.trigger_type = 2
        trig.trigger_info = username

        out.priority = 0
        trig.jobCommand = ""
        trig.jobWaitMinute = jobWM
        trig.jobWaitTime = jobWT
        session_id = client.service.runJob(jobunitId, jobId, out, trig)

        with CloudShellSessionContext(context) as session:
            session.WriteMessageToReservationOutput(context.reservation.reservation_id,"Hinemos Runjob:")
            session.WriteMessageToReservationOutput(context.reservation.reservation_id,  "-Inputs: JobUnitId="+jobunitId+" JobId="+jobId)
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, '-RunJob Output (Session ID) = {}'.format(session_id))

        pass

    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """
        # See below some example code demonstrating how to return the resource structure and attributes
        # In real life, this code will be preceded by SNMP/other calls to the resource details and will not be static
        # run 'shellfoundry generate' in order to create classes that represent your data model

        '''
        resource = Hinemos.create_from_context(context)
        resource.vendor = 'specify the shell vendor'
        resource.model = 'specify the shell model'

        port1 = ResourcePort('Port 1')
        port1.ipv4_address = '192.168.10.7'
        resource.add_sub_resource('1', port1)

        return resource.create_autoload_details()
        '''
        return AutoLoadDetails([], [])

    # </editor-fold>

    # <editor-fold desc="Orchestration Save and Restore Standard">
    def orchestration_save(self, context, cancellation_context, mode, custom_params):
      """
      Saves the Shell state and returns a description of the saved artifacts and information
      This command is intended for API use only by sandbox orchestration scripts to implement
      a save and restore workflow
      :param ResourceCommandContext context: the context object containing resource and reservation info
      :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
      :param str mode: Snapshot save mode, can be one of two values 'shallow' (default) or 'deep'
      :param str custom_params: Set of custom parameters for the save operation
      :return: SavedResults serialized as JSON
      :rtype: OrchestrationSaveResult
      """

      # See below an example implementation, here we use jsonpickle for serialization,
      # to use this sample, you'll need to add jsonpickle to your requirements.txt file
      # The JSON schema is defined at:
      # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/saved_artifact_info.schema.json
      # You can find more information and examples examples in the spec document at
      # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/save%20%26%20restore%20standard.md
      '''
            # By convention, all dates should be UTC
            created_date = datetime.datetime.utcnow()

            # This can be any unique identifier which can later be used to retrieve the artifact
            # such as filepath etc.

            # By convention, all dates should be UTC
            created_date = datetime.datetime.utcnow()

            # This can be any unique identifier which can later be used to retrieve the artifact
            # such as filepath etc.
            identifier = created_date.strftime('%y_%m_%d %H_%M_%S_%f')

            orchestration_saved_artifact = OrchestrationSavedArtifact('REPLACE_WITH_ARTIFACT_TYPE', identifier)

            saved_artifacts_info = OrchestrationSavedArtifactInfo(
                resource_name="some_resource",
                created_date=created_date,
                restore_rules=OrchestrationRestoreRules(requires_same_resource=True),
                saved_artifact=orchestration_saved_artifact)

            return OrchestrationSaveResult(saved_artifacts_info)
      '''
      pass

    def orchestration_restore(self, context, cancellation_context, saved_artifact_info, custom_params):
        """
        Restores a saved artifact previously saved by this Shell driver using the orchestration_save function
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str saved_artifact_info: A JSON string representing the state to restore including saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        :return: None
        """
        '''
        # The saved_details JSON will be defined according to the JSON Schema and is the same object returned via the
        # orchestration save function.
        # Example input:
        # {
        #     "saved_artifact": {
        #      "artifact_type": "REPLACE_WITH_ARTIFACT_TYPE",
        #      "identifier": "16_08_09 11_21_35_657000"
        #     },
        #     "resource_name": "some_resource",
        #     "restore_rules": {
        #      "requires_same_resource": true
        #     },
        #     "created_date": "2016-08-09T11:21:35.657000"
        #    }

        # The example code below just parses and prints the saved artifact identifier
        saved_details_object = json.loads(saved_details)
        return saved_details_object[u'saved_artifact'][u'identifier']
        '''
        pass

    # </editor-fold>

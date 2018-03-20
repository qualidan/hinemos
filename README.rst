1) Hinemos Shell draft was tested against a v6 Hinemos server with CloudShell 8.2

2) Contains two main driver (SOAP based) functions:

2.1) SOAP_getJobResults
		
		- SessionID Input must be entered
		Will print all JobUnitID`s related to SessionID (the end status value)
		in case JobUnitId is also entered will only print Job`s related to SessionID+JobUnitID
		In case JobID is entered will only print the status value of that SessionID+JobUnitID+JobID
		

2.2) SOAP_runJob

		-JobUnitID and JobID Input must be entered
		OUTPUT windows will display Session ID on successful run

	
*username and password mussed be filled for the resource so SOAP login will be successful
	
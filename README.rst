1) Hinemos Shell draft was tested against a v6 Hinemos server with CloudShell 8.2

2) Contains two types of driver functions:

2.1) Calling the Command-line(python) API

		Described here : http://www.hinemos.info/ja/option/commandlinetool
		Currently calling dummy file (Repository_addNode.py) that needs to be placed in <C:\1>
		Once the function is called it shall create a hinemos_execution_log.txt file and enter a call log entry
	
	*Assuming the subscription based tool exists > Place all files in "C:\1" or edit driver.py and change the "cwd" 

2.2) 2 SOAP based functions

		The first function is RunJob (JobUnitID and JobID must be entered)
		OUTPUT windows will display Session ID on successful run
		*username and password mussed be filled for the resource so SOAP login will be successful

		Second Function is a dummy function awaiting to be edited
	
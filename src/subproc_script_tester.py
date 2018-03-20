import subprocess

MANAGERURL="http://192.168.0.1:8080/HinemosWS/"
PASSWORD="hinemos"
IPADDRESS="192.168.0.2"
FACILITYID="WEBSERVER 1"
FACILITYNAME='"Web Server 1"'

python_script = "Repository_addNode.py"
python_params = "- H {} - w {} - A {} - I {} - N {}".format(MANAGERURL, PASSWORD, IPADDRESS, FACILITYID, FACILITYNAME);
python_command = "python " + python_script + " " + python_params


response = subprocess.check_output(python_command, cwd=r'c:\1')

print response
import sys
import os
from datetime import datetime

filename = "hinemos_execution_log.txt"

if os.path.exists(filename):
    append_write = 'a' # append if already exists
else:
    append_write = 'w' # make a new file if not

file = open(filename,append_write)

file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " ")

file.write(' '.join(sys.argv[:]))
file.write("\n");
file.close()

#!/usr/bin/env python

from sys import argv, exit
from subprocess import Popen, PIPE
from hashlib import md5

try:
	i = 1000
	revision = Popen("git log --oneline | wc -l", shell=True, stdout=PIPE).stdout.read().rstrip()
	revision = str(int(revision) + 1)

	if len(revision) > 3:
		version = revision[:-3] + "." + revision[-3:]
	elif len(revision) == 3:
		version = "0." + revision
	elif len(revision) == 2:
		version = "0.0" + revision
	else:
		version = "0.00" + revision

	f = open("version", "w")
	f.write(version)
	f.close()
	Popen("git add .", shell=True).wait()

	if len(argv) > 1:
		commit = "["+revision+"] "+' '.join(argv[1:])
	else:
		commit = "["+revision+"] Other/Checksum: "+md5(revision).hexdigest()

	Popen("git commit -m '" + commit + "' -s", shell=True).wait()
	Popen("git push origin master", shell=True).wait()
except Exception,e:
	print(e)

exit(0)

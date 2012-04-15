#!/usr/bin/env python

from sys import argv, exit
from subprocess import Popen, PIPE
from hashlib import md5
from fnmatch import fnmatch
import os

try:
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

	if not os.access("list", os.R_OK):
		file_writer = open("list", "w")
		file_writer.write("")
		file_writer.close()

	for lists in open("list", "r"):
		filename = lists.rstrip().split()[0]
		list_checksum = lists.rstrip().split()[1]
		if not os.access(filename, os.R_OK):
			Popen("git rm " + filename, shell=True).wait()

	file_writer = open("list", "w")
	file_writer.write("")

	for root, dirs, files in os.walk("."):
		for name in files:
			if not os.path.join(root[2:], name) == "list" and not os.path.join(root[2:], name) == "version" and not os.path.join(root[2:], name) == ".gitignore" and not os.path.join(root[2:], name).startswith(".git/"):
				ignored = False

				if os.access(".gitignore", os.R_OK):
					for ignore in open(".gitignore", "r"):
						if fnmatch(os.path.join(root[2:], name), ignore.rstrip()) or fnmatch(name, ignore.rstrip()):
							ignored = True

				if not ignored:				
					file_reader = open(os.path.join(root[2:], name), "r")
					file_content = file_reader.read()
					file_reader.close()
					file_checksum = md5(file_content).hexdigest()
					file_writer.write(os.path.join(root[2:], name) + " " + file_checksum + "\n")

	file_writer.close()
	Popen("git add .", shell=True).wait()

	if len(argv) > 1:
		commit = "[" + revision + "] " + ' '.join(argv[1:])
	else:
		file_reader = open("list", "r")
		file_content = file_reader.read()
		file_reader.close()
		file_checksum = md5(file_content).hexdigest()
		commit = "[" + revision + "] Other/Checksum: " + file_checksum

	Popen("git commit -m '" + commit + "' -s", shell=True).wait()
	Popen("git push origin master", shell=True).wait()

except Exception,e:
	print(e)

exit(0)

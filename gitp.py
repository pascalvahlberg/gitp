#!/usr/bin/env python

from sys import argv, exit
from subprocess import Popen, PIPE
from hashlib import md5
from fnmatch import fnmatch
from os import access, walk, path, R_OK

try:
	refs = Popen("git remote", shell=True, stdout=PIPE).stdout.read().rstrip()

	for ref in refs.splitlines():
		Popen("git pull " + ref + " master", shell=True).wait()

	if not access("list", R_OK):
		file_writer = open("list", "w")
		file_writer.write("")
		file_writer.close()

	listfile = open("list", "r")
	listprehash = md5(listfile.read()).hexdigest()
	listfile.close()

	for lists in open("list", "r"):
		filename = lists.rstrip()[:-33]
		list_checksum = lists.rstrip().split()[-32:]
		if not access(filename, R_OK):
			Popen("git rm --cached " + filename.replace(" ", "\ "), shell=True).wait()

	file_writer = open("list", "w")
	file_writer.write("")

	for root, dirs, files in walk("."):
		for name in files:
			if not path.join(root[2:], name) == "list" and not path.join(root[2:], name) == "version" and not path.join(root[2:], name) == ".gitignore" and not path.join(root[2:], name).startswith(".git/"):
				ignored = False

				if access(".gitignore", R_OK):
					for ignore in open(".gitignore", "r"):
						if fnmatch(path.join(root[2:], name), ignore.rstrip()) or fnmatch(name, ignore.rstrip()):
							ignored = True

				if not ignored:				
					file_reader = open(path.join(root[2:], name), "r")
					file_content = file_reader.read()
					file_reader.close()
					file_checksum = md5(file_content).hexdigest()
					file_writer.write(path.join(root[2:], name) + " " + file_checksum + "\n")

	file_writer.close()

	listfile = open("list", "r")
	listhash = md5(listfile.read()).hexdigest()
	listfile.close()

	if listprehash != listhash:
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
			commit = "[" + revision + "] " + ' '.join(argv[1:])
		else:
			file_reader = open("list", "r")
			file_content = file_reader.read()
			file_reader.close()
			file_checksum = md5(file_content).hexdigest()
			commit = "[" + revision + "] Other/Checksum: " + file_checksum

		Popen("git commit -m '" + commit + "' -s", shell=True).wait()
		Popen("git push origin master", shell=True).wait()
	else:
		print("No update needed.")

except Exception,e:
	print(e)

exit(0)

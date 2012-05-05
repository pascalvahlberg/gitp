#!/usr/bin/env python

from sys import argv, exit
from subprocess import Popen, PIPE
from hashlib import md5
from fnmatch import fnmatch
from os import access, walk, path, R_OK

try:
	refs = Popen("git remote", shell=True, stdout=PIPE).stdout.read().rstrip()

	for ref in refs.splitlines():
		print("% Fetching '" + ref + "'")
		Popen("git pull " + ref + " master", shell=True, stdout=PIPE).stdout.read().rstrip()

	if not access("list", R_OK):
		print("% Creating list")
		file_writer = open("list", "w")
		file_writer.write("")
		file_writer.close()

	print("% Creating listprehash")
	listfile = open("list", "r")
	listprehash = md5(listfile.read()).hexdigest()
	listfile.close()

	for lists in open("list", "r"):
		filename = lists.rstrip()[:-33]
		list_checksum = lists.rstrip().split()[-32:]
		if not access(filename, R_OK):
			print("% Removing '" + filename + "'")
			Popen("git rm --cached " + filename.replace(" ", "\ "), shell=True, stdout=PIPE).stdout.read().rstrip()

	print("% Clearing list")
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
					print("% Adding '" + path.join(root[2:], name) + "' (" + file_checksum + ")")
					file_writer.write(path.join(root[2:], name) + " " + file_checksum + "\n")

	file_writer.close()

	print("% Creating listhash")
	listfile = open("list", "r")
	listhash = md5(listfile.read()).hexdigest()
	listfile.close()

	print("% Comparing listhashes")
	if listprehash != listhash:
		revision = Popen("git log --oneline | wc -l", shell=True, stdout=PIPE).stdout.read().rstrip()
		print("% Getting new revision")
		revision = str(int(revision) + 1)

		print("% Creating version")
		if len(revision) > 3:
			version = revision[:-3] + "." + revision[-3:]
		elif len(revision) == 3:
			version = "0." + revision
		elif len(revision) == 2:
			version = "0.0" + revision
		else:
			version = "0.00" + revision

		print("% Writing version")
		f = open("version", "w")
		f.write(version)
		f.close()

		Popen("git add .", shell=True).wait()

		if len(argv) > 1:
			commit = ' '.join(argv[1:])
		else:
			file_reader = open("list", "r")
			file_content = file_reader.read()
			file_reader.close()
			file_checksum = md5(file_content).hexdigest()
			commit = "Other/Checksum: " + file_checksum

		print("% Committing '" + commit + "'")
		Popen("git commit -m '[" + revision + "] " + commit + "' -s", shell=True, stdout=PIPE).stdout.read().rstrip()
		print("% Pushing to repository")
		Popen("git push origin master", shell=True).wait()
	else:
		print("% No update needed.")

except Exception,e:
	print(e)
	exit(0)
except KeyboardInterrupt,e:
	print("Ctrl + C")
	exit(0)

exit(0)

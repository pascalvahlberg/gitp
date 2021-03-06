#!/usr/bin/env python

from sys import argv, exit
from subprocess import Popen, PIPE
from hashlib import md5
from fnmatch import fnmatch
from os import access, walk, path, R_OK

try:
	def red(string):
		return("\033[91m" + string + "\033[0m")

	def blue(string):
		return("\033[94m" + string + "\033[0m")

	def green(string):
		return("\033[92m" + string + "\033[0m")

	refs = Popen("git remote", shell=True, stdout=PIPE).stdout.read().rstrip()
	removed_list = list()

	for ref in refs.splitlines():
		print(green("*") + " Pulling '" + ref + "'")
		raw_data = Popen("git pull --quiet " + ref + " master", shell=True, stdout=PIPE).stdout.read().rstrip()

		for data in raw_data.splitlines():
			print(red("*") + " " + data)

			if data.split()[0] == "Removing":
				removed_list.append(data.split()[0])

	if not access("list", R_OK):
		print(blue("*") + " Creating list")
		file_writer = open("list", "w")
		file_writer.write("")
		file_writer.close()

	print(blue("*") + " Creating listhash")
	listfile = open("list", "r")
	listprehash = md5(listfile.read()).hexdigest()
	listfile.close()

	print(blue("*") + " Removing non-existing files")
	for lists in open("list", "r"):
		removed = False
		filename = lists.rstrip()[:-33]
		list_checksum = lists.rstrip().split()[-32:]

		if not access(filename, R_OK):
			for removed_file in removed_list:
				if removed_file == filename:
					removed = True

			if not removed:
				raw_data = Popen("git rm --quiet --cached --force " + filename.replace(" ", "\ "), shell=True, stdout=PIPE).stdout.read().rstrip()

				for data in raw_data.splitlines():
					print(red("*") + " " + data)

	print(blue("*") + " Clearing list")
	file_writer = open("list", "w")
	file_writer.write("")
	print(blue("*") + " Adding existing files")

	for root, dirs, files in sorted(walk(".")):
		files.sort()

		for name in files:
			if not path.join(root[2:], name) == "list" and not path.join(root[2:], name) == "version" and not path.join(root[2:], name) == ".gitignore" and not path.join(root[2:], name).startswith(".git/"):
				ignored = False

				if access(".gitignore", R_OK):
					for ignore in open(".gitignore", "r"):
						if fnmatch(path.join(root[2:], name), ignore.rstrip()) or fnmatch(name, ignore.rstrip()):
							ignored = True

				if not ignored:
					file_checksum = md5("").hexdigest()

					if access(path.join(root[2:], name), R_OK):
						file_reader = open(path.join(root[2:], name), "r")
						file_content = file_reader.read()
						file_reader.close()
						file_checksum = md5(file_content).hexdigest()

					file_writer.write(path.join(root[2:], name) + " " + file_checksum + "\n")

	file_writer.close()
	print(blue("*") + " Creating listhash")
	listfile = open("list", "r")
	listhash = md5(listfile.read()).hexdigest()
	listfile.close()
	print(blue("*") + " Comparing listhashes")

	if listprehash != listhash:
		revision = Popen("git log --oneline | wc -l", shell=True, stdout=PIPE).stdout.read().rstrip()
		print(blue("*") + " Getting new revision")
		revision = str(int(revision) + 1)
		print(blue("*") + " Creating version")

		if len(revision) > 3:
			version = revision[:-3] + "." + revision[-3:]
		elif len(revision) == 3:
			version = "0." + revision
		elif len(revision) == 2:
			version = "0.0" + revision
		else:
			version = "0.00" + revision

		print(blue("*") + " Writing version")
		f = open("version", "w")
		f.write(version)
		f.close()
		raw_data = Popen("git add .", shell=True, stdout=PIPE).stdout.read().rstrip()

		for data in raw_data.splitlines():
			print(red("*") + " " + data)

		repository = "origin master"
		hascommit = False

		if len(argv) > 1:
			if len(argv) > 3:
				if argv[-3] == "-r":
					repository = ' '.join(argv[-2:])
					commit = ' '.join(argv[1:-3])

					if len(argv) > 4:
						hascommit = True
				else:
					commit = ' '.join(argv[1:])
					hascommit = True
			else:
				commit = ' '.join(argv[1:])
				hascommit = True

		if not hascommit:
			file_reader = open("list", "r")
			file_content = file_reader.read()
			file_reader.close()
			file_checksum = md5(file_content).hexdigest()
			commit = "Other/Checksum: " + file_checksum

		print(blue("*") + " Committing '" + commit + "'")
		raw_data = Popen("git commit --quiet --message '[" + revision + "] " + commit + "' --signoff", shell=True, stdout=PIPE).stdout.read().rstrip()

		for data in raw_data.splitlines():
			print(red("*") + " " + data)

		print(green("*") + " Pushing to '" + repository + "'")
		raw_data = Popen("git push --quiet " + repository, shell=True, stdout=PIPE).stdout.read().rstrip()

		for data in raw_data.splitlines():
			print(red("*") + " " + data)
	else:
		print(green("*") + " No update needed.")

except Exception,e:
	print(red("*") + " " + str(e))
	exit(0)
except KeyboardInterrupt,e:
	print("")
	print(red("*") + " Ctrl + C")
	exit(0)

exit(0)

import os
import login

username = login.username
password = login.password
host = login.host

output_folder = "./data"

log_file = "log.txt"


classes = [
	"O",
	"LINK",
	"CLI_NAME",
	"MAIL_ADDR",
	"PKG_TYPE",
	"WEIGHT",
	"VOLUME",
	"MERCH_TYPE",
	"DEPT_FROM",
	"DEPT_TO",
	"HAYON",
	"RDV_FIXE",
	"CHG_PALETTE"
]

d = [
		"saved",
		"validated",
		"rejected"
	]


def makedir(path):
	if not os.path.isdir(path):
		os.mkdir(path)

def log(msg):
	with open(log_file, "a", encoding="utf8") as log:
		log.write(msg)

makedir(output_folder)

for directory in d:
	makedir(os.path.join(output_folder, directory))
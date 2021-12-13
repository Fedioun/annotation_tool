import os
from login import username, password, host

output_folder = "./data"

log_file = "log.txt"

OFFSET = 180

classes = [
	"O",
	"CLI_NAME",
	"MAIL_ADDR",
	"PKG_TYPE",
	"MULT_FACTOR",
	"WEIGHT",
	"WEIGHT_UNIT",
	"VOLUME",
	"DIMENSIONS",
	"DEPT_FROM",
	"DEPT_TO",
	"MERCH_TYPE",
	"HAYON",
	"DANGEROUS",
	"STACKABLE",
	"RDV_FIXE",
	"CHG_PALETTE",
	"NB_COTATION"
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
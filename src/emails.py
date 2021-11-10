import imaplib
import email
from time import sleep
import os
import re
from email.header import decode_header
from datetime import datetime
import config
from bs4 import BeautifulSoup
from src.filtering import filter, tokenize


# Get N Emails
def get_emails(password, username):
	#'smtp.office365.com
	server = imaplib.IMAP4_SSL("outlook.office365.com")
	server.login(username, password)	
	status, messages = server.select("INBOX")
	messages = int(messages[0])
	msgs = []

	for i in range(messages-30, 0, -1):
		res, msg = server.fetch(str(i), "(RFC822)")
		for response in msg:
			if isinstance(response, tuple):
				# parse a bytes email into a message object
				msg = email.message_from_bytes(response[1])
				

 


				# decode the email subject
				subject, encoding = decode_header(msg["Subject"])[0]
				if isinstance(subject, bytes):
					subject = subject.decode(encoding)
				# decode email sender
				From, encoding = decode_header(msg.get("From"))[0]
				if isinstance(From, bytes):
					From = From.decode(encoding)
				emailaddr = From.split(" ")[-1][1:-1]

				try:
					config.log("Date : " + msg["Date"] + "\n")
					time = datetime.strptime(" ".join(msg["Date"].split(" ")[:-1]), "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d-%H:%M:%S")

				except:
					try:
						time = datetime.strptime(" ".join(msg["Date"].split(" ")[:-2]), "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d-%H:%M:%S")
					except:

						config.log("Cannot parse date for email :" + subject + "\n")
						time = "2000-01-01-00:00:00"

				emailId = time + "-" + emailaddr

				#status, tokens = load_old_mail(emailId)
				status = 0
				if status != -1 and False:
					if status > 0 :
						break
					out = {
						"id" : emailId,
						"subject" : subject,
						"from" : From,
						"tokens" : tokens
					}

				else:
					#print("\nSubject:", subject)
					# if the email message is multipart
					config.log("Extracting + " + subject + "\n")

					out = {
						"id" : emailId,
						"subject" : subject,
						"from" : From,
						"body" : extract_mail_body(msg)
					}


					########### Not filter history for clavel
					#if not "normandie@clavel-georges.fr" in out["from"]:
					#	out["body"] = filter_email_history(out["body"])


						
					out["text"] = out["from"] + " \n\n " + out["subject"]  + "\n\n" + out["body"]

					out["tokens"] = filter(tokenize(out["text"]))

					
					
					msgs.append(out)

				yield(out)



	# close the connection and logout
	server.close()
	server.logout()

	return msgs



def extract_mail_body(msg):
	content = ""
	for part in msg.walk():
		content_type = part.get_content_type()

		if content_type == "text/plain" and not part.is_multipart():
			try:
				content += part.get_payload(decode=True).decode()
			except:
				try:
					charset = re.findall('charset=".*?"', str(part))[0][9:-1]
					content += part.get_payload(decode=True).decode(charset)
				except:
					content += part.get_payload()

	if content == "" or content.startswith("<html"):
		content = ""
		config.log("Failed to extract body \n")
		for part in msg.walk():
			config.log(part.get_content_type() + "\n")
			if part.get_content_type() == "text/html":
				try:
					content += part.get_payload(decode=True).decode()
				except:
					charset = re.findall('charset=".*?"', str(part))[0][9:-1]
					content += part.get_payload(decode=True).decode(charset)

				soup = BeautifulSoup(content)
				content = soup.get_text()
	return content

'''
Status :
0 - saved
1 - validated
2 - rejected
''' 

def save(email, status):
	d = [
		"saved",
		"validated",
		"rejected"
	]
	path = os.path.join(config.output_folder, d[status], email["id"])
	
	with open(path, "w", encoding="utf8") as out:
		for token in email["tokens"]:
			if token["text"] != "":
				out.write(token["text"] + " " + config.classes[int(token["class"]/2)] + "\n")



def load_old_mail(mailid):
	d = [
		"saved",
		"validated",
		"rejected"
	]
	for k in d:
		directory = os.path.join(config.output_folder, k)
		mails = os.listdir(directory)
		if mailid in mails:
			config.log("Found mail " + mailid + " in local folders\n")
			return d.index(k), load(os.path.join(directory, mailid))["tokens"]
	return -1, None



def load(path):
	email = {
		"id" : path,
		"tokens" : []
	}

	with open(path, "r", encoding="utf8") as out:
		lines = out.readlines()
		for line in lines:
			if len(line.split(" "))>1:
				token = {
					"text" : line.split(" ")[0].strip(),
					"class" : config.classes.index(line.split(" ")[1].strip()) * 2
				}
				email["tokens"].append(token)
	return email




def get_saved_emails(path):
	files = os.listdir(path)
	for file in files:
		yield({
			"id" : file,
			"tokens" : filter(load(os.path.join(path, file))["tokens"])
		})

		









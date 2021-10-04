import imaplib
import email
from time import sleep
import os
import re
from email.header import decode_header
from datetime import datetime
import config
from bs4 import BeautifulSoup


def tokenize(text):
	return text.replace("\r\n",  " [n] ").replace("\n",  " [n] ").replace("\r",  " [n] ").split(" ")


# Get N Emails
def get_emails(password, username):


	#'smtp.office365.com
	server = imaplib.IMAP4_SSL("outlook.office365.com")
	server.login(username, password)
	#Adding a newline before the body text fixes the missing message body
	#mailserver.sendmail('user@company.co','user@company.co','\npython email')
	#mailserver.quit()

	status, messages = server.select("INBOX")

	# total number of emails
	messages = int(messages[0])

	msgs = []

	for i in range(messages-30, 0, -1):
		# fetch the email message by ID
		#print(i)
		res, msg = server.fetch(str(i), "(RFC822)")
		for response in msg:
			if isinstance(response, tuple):
				# parse a bytes email into a message object
				msg = email.message_from_bytes(response[1])


				time = datetime.strptime(" ".join(msg["Date"].split(" ")[:-1]), "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d-%H:%M:%S")

				# decode the email subject
				subject, encoding = decode_header(msg["Subject"])[0]
				if isinstance(subject, bytes):
					subject = subject.decode(encoding)
				# decode email sender
				From, encoding = decode_header(msg.get("From"))[0]
				if isinstance(From, bytes):
					From = From.decode(encoding)

				emailaddr = From.split(" ")[-1][1:-1]

				emailId = time + "-" + emailaddr

				status, tokens = load_old_mail(emailId)

				if status != -1:
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
					out["text"] = out["from"] + " \n\n " + out["subject"]  + "\n\n" + out["body"]
					out["rawtokens"] = tokenize(out["text"])
					
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
				charset = re.findall('charset=".*?"', str(part))[0][9:-1]
				content += part.get_payload(decode=True).decode(charset)

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


	content = filter_email_history(content)


	return content

def filter_email_history(content):
	lines = content.split("\n")
	filtered = ""
	k = 0
	while not ((lines[k].startswith("De") or lines[k].startswith("From") )and "@" in lines[k]):
		filtered += lines[k] + "\n"
		k+=1
		if k == len(lines):
			break


	return filtered

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
			out.write(token["text"] + " " + str(token["class"]) + "\n")



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
			token = {
				"text" : line.split(" ")[0],
				"class" : int(line.split(" ")[1])
			}
			email["tokens"].append(token)
	config.log(str(email["tokens"]))
	return email






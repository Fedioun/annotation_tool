import config
import re


def tokenize(raw_text):
	tokens = []
	raw_text = re.sub(' +',' ',raw_text)
	for token in raw_text.split(" "):
		tokens.append({
			"text" : token,
			"class" : 0
		})
	return tokens

def filter_new_line(tokens):
	filtered = []
	for token in tokens:
		parts = re.sub("(\n\r|\n)", " [n] ",token["text"]).split(" ")
		for part in parts:			
			if part != "":
				tmp = token.copy()
				tmp["text"] = part
				filtered.append(tmp)
	return filtered

def bound_new_lines(tokens):
	filtered = []
	c = 0
	for token in tokens:
		if token["text"] == "[n]":
			c+=1
			if c < 3:
				filtered.append(token)
		else:
			c=0
			filtered.append(token)
	return filtered


def filter_links(tokens):
	filtered = []
	for t in tokens:
		filtering = re.findall('\[.*?\]', t["text"])
		for f in filtering:
			if f!="[n]":
				#config.log(str(filtering) + "\n")
				t["text"] = t["text"].replace(f, "")
		filtering = re.findall('<http.*?>', t["text"])
		for f in filtering:
			t["text"] = t["text"].replace(f, "")
		if t["text"] != "":
			filtered.append(t)
	return filtered


#
def expand(tokens, regex):
	expanded = []
	for t in tokens:
		matches = re.finditer(regex, t["text"]) 
		end = 0
		for element in matches:
			if element.span()[0] > end:
				tmp = t.copy()
				tmp["text"] = t["text"][end:element.span()[0]]
				expanded.append(tmp)

			tmp = t.copy()
			tmp["text"] = t["text"][element.span()[0]: element.span()[1]]
			expanded.append(tmp)
			end = element.span()[1]
		if end < len(t["text"]):
			tmp = t.copy()
			tmp["text"] = t["text"][end:]
			expanded.append(tmp)
	return expanded

def filter_empty(tokens):
	filtered = []
	for token in tokens:
		token["text"] = re.sub("\s", "", token["text"])
		if token["text"] != "" or token["text"] == " ":
			filtered.append(token)
	return filtered

def filter_until(tokens, words):

	config.log("Filter until \n")
	filtered = []

	line_tokens = [[]]
	lines = [""]
	for token in tokens:
		t = token["text"]
		if t == "[n]":
			lines.append("")
			line_tokens.append([])
		else:
			lines[-1]+=t + ' '
			line_tokens[-1].append(token)

	filter = True
	word_index = 0
	num_line = 0

	for line in lines:
		if line.startswith(words[word_index]):
			if word_index == 0:
				config.log("yahoou")
				num_line = lines.index(line)
			word_index += 1
		else:
			word_index = 0
		if word_index == len(words):
			num_line = lines.index(line) +1
			filter = False
			break

	for k in range(num_line, len(lines)):
			filtered.extend(line_tokens[k])
			filtered.append({
				"text" : "[n]",
				"class" : 0
			})
	return filtered


def filter_email_history(tokens, words):

	filtered = []

	line_tokens = [[]]
	lines = [""]
	for token in tokens:
		t = token["text"]
		if t == "[n]":
			lines.append("")
			line_tokens.append([])
		else:
			lines[-1]+=t + ' '
			line_tokens[-1].append(token)

	filter = False
	word_index = 0
	num_line = 0

	for line in lines:
		if line.startswith(words[word_index]):
			if word_index == 0:
				num_line = lines.index(line)
			word_index += 1
		else:
			word_index = 0
		if word_index == len(words):
			filter = True
			break

	if not filter:
		return tokens
	else:
		for k in range(0, num_line):
			filtered.extend(line_tokens[k])
			filtered.append({
				"text" : "[n]",
				"class" : 0
			})
	return filtered

def filter_long(tokens, n):
	filtered = []
	buffer = []
	filter = False
	c = 0
	for token in tokens:
		
		if token["text"] != "[n]":
			c += len(token["text"])
			if c > n:
				break
		else:
			c = 0 
			filtered.extend(buffer)
			buffer = []
		buffer.append(token)
	return filtered



def filter(tokens):
	tokens = filter_new_line(tokens)
	tokens = filter_links(tokens)
	tokens = expand(tokens, "(\d+,\d+|\d+\.\d+|\d+)")
	tokens = expand(tokens, ":")
	tokens = expand(tokens, "/")
	tokens = expand(tokens, "\+")
	tokens = expand(tokens, "\(|\)|-+")
	tokens = filter_empty(tokens)
	tokens = bound_new_lines(tokens)
	tokens = filter_empty(tokens)


	if "clavel-georges.fr" in tokens[0]["text"]:
		tokens = filter_until(tokens, ["ATTENTION"])
	else:
		tokens = filter_email_history(tokens, ["De :", "Envoyé :", "À :"])
		tokens = filter_email_history(tokens, ["a écrit :"])


	tokens = filter_long(tokens, 150)

	#for t in tokens:
	#	config.log("Token : " + t["text"] + "\n")


	
	return tokens


def filter_email_histoy(content):
    lines = content.split("\n")
    filtered = ""
    k = 0
    while not filter_next(lines[k:]) or "normandie@clavel-georges.fr" in lines[0] or "s.duclos@clavel-georges.fr" in lines[0]:
        filtered += lines[k] + "\n"
        k+=1
        if k == len(lines):
            break
    return filtered


def filter_next(lines):
    if len(lines) < 4:
        return False
    else:
        ####
        if lines[0].startswith("From") and lines[1].startswith("Sent") and lines[2].startswith("To"):
            return True
        if lines[0].startswith("De") and lines[1].startswith("Envoyé") and lines[2].startswith("À"):
            return True
        if lines[0].startswith("De") and lines[2].startswith("Envoyé") and lines[3].startswith("À"):
            return True
        '''
        if lines[0].startswith("") and lines[1].startswith("") and lines[2].startswith(""):
            return True
        '''
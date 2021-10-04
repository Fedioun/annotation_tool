import curses
from curses import wrapper
from src.emails import get_emails, save, load

#import webbrowser
import os

import time
import config


open(config.log_file, "w").close()





def configure_scr(stdscr):
	curses.curs_set(0)
	stdscr.clear()
	curses.start_color()
	curses.use_default_colors()
	curses.init_pair(0, 15, curses.COLOR_BLACK)
	curses.init_pair(1, curses.COLOR_BLACK, 15)
	for i in range(1, curses.COLORS-1):
		curses.init_pair(i * 2    , i, 0)
		curses.init_pair(i * 2 + 1, 15, i)

	return stdscr


def write_text(stdscr, email):
	tokens = []
	x = 0
	y = 2
	for token in email["rawtokens"]:
		# Crop long lines
		if len(token) + x > curses.COLS :
			y += 1
			x = 0

		# Check carriage return 
		if token == "[n]":
			y += 1
			x = 0
			tokens.append({
				"text" : token,
				"x" : x,
				"y" : y,
				"class" : 0
			})
		else:
			if token != "":
				# Write token 
				try:
					stdscr.addstr(y, x, token)
				except :
					config.log("Fail to write token  " + token + " at postition y=" + str(y) + " x=" + str(x) + "\n")
					pass

				tokens.append({
					"text" : token,
					"x" : x,
					"y" : y,
					"class" : 0
				})

				x += len(token) + 1
	stdscr.refresh(0, 0, 5, 0, curses.LINES-1, curses.COLS-1)
	return tokens

def write_tokens(stdscr, email):
	x = 0
	y = 2
	for token in email["tokens"]:

		if len(token["text"]) + x > curses.COLS :
			y += 1
			x = 0

		# Check carriage return 
		if token["text"] == "[n]":
			y += 1
			x = 0
			token["x"] = x
			token["y"] = y
		else:
			if token["text"] != "":
				# Write token 
				try:
					stdscr.addstr(y, x, token["text"], curses.color_pair(token["class"]))
				except :
					config.log("Fail to write token  " + token["text"] + " at postition y=" + str(y) + " x=" + str(x) + "\n")
					pass

				token["x"] = x
				token["y"] = y

				x += len(token["text"]) + 1
	stdscr.refresh(0, 0, 5, 0, curses.LINES-1, curses.COLS-1)
	return email["tokens"]


def w_token(stdscr, token):
	stdscr.addstr(token["y"], token["x"], token["text"], curses.color_pair(token["class"]))

# Main loop
def navigation(stdscr, email):
	stdscr.clear()
	

	info_win = curses.newwin(5, curses.COLS-1, 0, 0)
	pad_pos = 0

	if "tokens" in email:
		tokens = write_tokens(stdscr, email)
	else:
		tokens = write_text(stdscr, email)
	ntx = 50000
	nty = 50000
	k = 0
	base_x = 0
	pen_down = True
	current_color = 0
	# Color var
	tmp_digit = 0

	display_nav_info(info_win, tokens[k], pen_down, current_color)
	while True:

		key = stdscr.getkey()

		'''
		# Scrolling
		if key == "+":
			pad_pos += 1
		if key == "-":
			if pad_pos > 0:
				pad_pos -= 1
		'''

		# Change email

		if key == "+":
			return 1, tokens
		if key == "-":
			
			return -1, tokens


		# Pen
		if key == "\n":
			pen_down = not pen_down

		# Suppr
		if key == "~":
			tokens[k]["class"] = 0


		###  NAVIGATION
		if key == "C" and k < len(tokens) -1:
			w_token(stdscr, tokens[k])
			k += 1
			while (tokens[k]["text"] == "" or tokens[k]["text"] == "[n]") and k < len(tokens) -1:
				k+=1
			base_x = tokens[k]["x"]

		if key == "D" and k > 0:
			w_token(stdscr, tokens[k])
			k -= 1
			while (tokens[k]["text"] == "" or tokens[k]["text"] == "[n]") :
				k-=1
			base_x = tokens[k]["x"]

		# Down key
		if key ==  "B" :
			nk = k
			miny = 10e9
			ntx = 10e9
			for i in range(len(tokens)):				
				if tokens[i]["y"] > tokens[k]["y"] and tokens[i]["text"] != "" and tokens[i]["text"] != "[n]"and tokens[i]["y"] < miny:
					miny = tokens[i]["y"]
				if (tokens[i]["x"] - base_x)**2 < ntx and tokens[i]["y"] == miny:
					nk = i
					ntx = (tokens[i]["x"] - base_x)**2

			w_token(stdscr, tokens[k])
			k = nk

		# Up key
		if key ==  "A" :
			nk = k
			maxy = -10e9
			ntx = 10e9
			for i in range(len(tokens)-1, 0, -1):				
				if tokens[i]["y"] < tokens[k]["y"] and tokens[i]["text"] != "" and tokens[i]["text"] != "[n]" and tokens[i]["y"] > maxy:
					maxy = tokens[i]["y"]
				if (tokens[i]["x"] - base_x)**2 < ntx and tokens[i]["y"] == maxy:
					nk = i
					ntx = (tokens[i]["x"] - base_x)**2


			w_token(stdscr, tokens[k])
			k = nk

		# Auto scrolling
		while tokens[k]["y"] > curses.LINES + pad_pos - 10 :
			pad_pos += 1

		while tokens[k]["y"] < pad_pos + 10 :
			pad_pos -= 1

		# Save
		if key == "s":
			stdscr.addstr(0, 5, "Voulez-vous vraiment valider ce document? (y/n)")
			stdscr.refresh(pad_pos, 0, 5, 0, curses.LINES-1, curses.COLS-1)
			while True:
			    char = stdscr.getkey()       
			    if char != curses.ERR:
			    	if char == "y":
			    		email["tokens"] = tokens
			    		save(email, True)
			    	stdscr.addstr(0, 5, " saved                                                    ")
			    	break


		# Change color
		if key.isdigit() :
			if tmp_digit > 0 :
				tmp_digit += int(key) * 2 + tmp_digit * 20
			else:
				tmp_digit = int(key) * 2

			current_color = tmp_digit

		if not key.isdigit() and tmp_digit != 0:
			tmp_digit = 0

		# Write color
		if pen_down:
			tokens[k]["class"] = current_color

		# Display
		try:
			stdscr.addstr(tokens[k]["y"], tokens[k]["x"], tokens[k]["text"], curses.color_pair(tokens[k]["class"] + 1))
		except:
			config.log("Failed to write token '" + tokens[k]["text"] + "' at y=" + str(tokens[k]["y"]) + " x=" + str(tokens[k]["x"]) + "\n")
		stdscr.refresh(pad_pos, 0, 5, 0, curses.LINES-1, curses.COLS-1)


		if key != curses.ERR:
			email["tokens"] = tokens
			save(email, False)


		display_nav_info(info_win, tokens[k], pen_down, current_color)
		
		stdscr.refresh(pad_pos, 0, 5, 0, curses.LINES-1, curses.COLS-1)

def display_nav_info(info_win, token, pen_down, current_color):
	info_win.addstr(0, 0, " " * 30)
	info_win.addstr(1, 0, " " * 30)
	info_win.addstr(0, 0, "Current token : " + config.classes[int(token["class"]/2)], curses.color_pair(token["class"]))
	info_win.addstr(1, 0, "Current tag : " + config.classes[int(current_color/2)], curses.color_pair(current_color))
	info_win.addstr(2, 0, "Pen down : " + str(pen_down))

	for k in range(len(config.classes)):
		info_win.addstr(k%5, 30 + 20 * int(k/5), str(k) + " : " + config.classes[k], curses.color_pair(2*k))
	info_win.refresh()


def main(stdscr):

	email = get_emails(config.password, config.username)
	stdscr = configure_scr(stdscr)

	pad = curses.newpad(1500, curses.COLS)
	pad_pos = 0
	pad.refresh(pad_pos, 0, 5, 0, curses.LINES-1, curses.COLS-1)

	emails = []
	k = -1


	nav = 1
	while True:
		k = max(k + nav, 0)			
		
		if k == len(emails):
			pad.clear()
			pad.addstr(int(curses.LINES/2)-3, int(curses.COLS/2)-10, "Loading next email...")
			pad.refresh(0, 0, 5, 0, curses.LINES-1, curses.COLS-1)
			emails.append(next(email))


		nav, tokens = navigation(pad, emails[k])
		emails[k]["tokens"] = tokens





	save(emails)

	#config.log(emails)

# DEBUG
#emails = get_emails(3, config.password, config.username)
wrapper(main)
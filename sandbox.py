import praw

import time

import urllib2
from antigate_key import *
from antigate import AntiGate

import re

import cPickle as pickle

# must use unique user-agent or bot gets rate-limited
user_agent = "praw:io.m4r5.travelbot:v0.0 (by /u/marsman12019)"

r = praw.Reddit(user_agent=user_agent, site_name="travelbot")
r.login()

try:
	last_dest = pickle.load(open("last_dest.pk", "rb"))
	num_destinations = pickle.load(open("num_destinations.pk", "rb"))
	post_id = pickle.load(open("post_id.pk", "rb"))
except:
	last_dest = ("", "")
	num_destinations = 1
	post_id = ""

print last_dest, num_destinations, post_id

def post_message(subreddit):

	title = "I am /u/travel_bot, and I need your help."

	if last_dest == ("", ""):
		msg = "Good day, fellow traveler! I am /u/travelbot, and I'm on a journey across reddit.\n\nThis is the first stop on my adventure!! Where should I go to next?\n\n^^comment ^^with ^^a ^^subreddit ^^in ^^the ^^form ^^of: ^^/r/subredditname"
	else:
		last_suggestion_url = "http://www.reddit.com/r/" + str(r.get_submission(submission_id=last_dest[0]).subreddit) + "/comments/" + str(last_dest[0]) + "/i_am_utravel_bot_and_i_need_your_help/" + str(last_dest[1])

		msg = "Good day, fellow traveler! I am /u/travelbot, and I'm on a journey across reddit.\n\nMy adventure has taken me to " + str(num_destinations) + " places so far, most recently [/r/" + str(r.get_submission(submission_id=last_dest[0]).subreddit) + "](" + last_suggestion_url + "). Where should I go to next?\n\n^^comment ^^with ^^a ^^subreddit ^^in ^^the ^^form ^^of: ^^/r/subredditname"

	captcha = {}

	# keep looping until CAPTCHA works, then break
	while True:

		try:

			if len(captcha.keys()) == 0:
				print "Trying to post..."
				submission = r.submit(subreddit, title=title, text=msg, raise_captcha_exception=True)
			else:
				print "Trying to post again..."
				submission = r.submit(subreddit, title=title, text=msg, raise_captcha_exception=True, captcha=captcha)

		except praw.errors.InvalidCaptcha as error:

			print "Posting requires CAPTCHA."

			captcha['iden'] = error.response['captcha']

			print "Downloading CAPTCHA..."
			captcha_url = "https://www.reddit.com/captcha/" + error.response['captcha'] + ".png"
			request = urllib2.Request(captcha_url, headers={'User-Agent' : user_agent})
			captcha_img = urllib2.urlopen(request).read()
			with open('captcha.png', 'w') as f:
				f.write(captcha_img)

			print "Sending CAPTCHA to AntiGate..."
			captcha['captcha'] = str(AntiGate(ANTIGATE_KEY, 'captcha.png')).upper()
			print "Response received:", captcha['captcha']

			continue

		except praw.errors.ExceptionList as error:
			print error
			print "ERROR. You're probably trying to post too often. Trying again in 60 seconds..."
			print "T-minus:",
			for t in xrange(12):
				print 60 - t * 5,
				time.sleep(5)
			continue

		except praw.errors.APIException as error:
			print error
			print "ERROR. You probably hit your posting quota. Trying again in one hour..."
			print "T-minus:",
			for t in xrange(60):
				print 60 - t,
				time.sleep(60)
			continue

		break

	print "Post successful:", submission.id
	return submission.id

def listen(submission_id):

	print "Listening for destinations..."
	already_checked = []
	destination = ""
	while destination == "":
		submission = r.get_submission(submission_id=submission_id)
		# submission = r.get_submission(submission_id='2xovhr')
		for comment in submission.comments:
			if comment.id not in already_checked:
				# print comment.body
				already_checked.append(comment.id)

				if '/r/' in comment.body:
					subreddit_name = re.findall(r"/r/([^\s/]+)", comment.body)[0]
					try:
						subreddit = r.get_subreddit(subreddit_name, fetch=True)
						print "Subreddit exists:", subreddit_name
						comment.reply("/r/" + subreddit_name + " it is, then! So long, and thanks for all the fish!")
						last_dest = (comment.submission.id, comment.id)
						pickle.dump(last_dest, open("last_dest.pk", 'wb'))
						destination = subreddit_name
					except:
						print "Subreddit does not exist:", subreddit_name
		time.sleep(60)
	print "heading over to", destination
	return destination

next_dest = "botwatch"

if (post_id == ""):
	post_id = post_message(next_dest)
	pickle.dump(post_id, open("post_id.pk", 'wb'))

while True:

	next_dest = listen(post_id)
	post_id = post_message(next_dest)
	pickle.dump(post_id, open("post_id.pk", 'wb'))
	num_destinations += 1
	pickle.dump(num_destinations, open("num_destinations.pk", 'wb'))

import praw


# user_agent = "<platform>:<app ID>:<version string> (by /u/<reddit username>)"
user_agent = "python:io.m4r5.karmaBreakdown:v0.1 (by /u/marsman12019)"

r = praw.Reddit(user_agent=user_agent)

user_name = "marsman12019"
user = r.get_redditor(user_name)

submitted = user.get_submitted(limit=None)

karma_by_subreddit = {}
for submit in submitted:
	subreddit = submit.subreddit.display_name
	karma_by_subreddit[subreddit] = (karma_by_subreddit.get(subreddit, 0) + submit.score)

import pprint
pprint.pprint(karma_by_subreddit)

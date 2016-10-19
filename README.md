# Python Flask application for demonstrating how to capture and store Access Token and Secret for other accounts in order to execute three-legged-oauth calls, such as those in the  [Audience API](http://support.gnip.com/apis/audience_api/) and [Engagement API](http://support.gnip.com/apis/engagement_api/).

###Note: Requires: [tweepy](http://www.tweepy.org) and [python-insights](https://github.com/GnipDz/Python-Insights) libraries.

To install: 
`pip install flask`
`pip install tweepy`

(download and copy gnip_insights.py into the same directory as AudienceCallback.py)

Requires a public IP address to allow for a call from Twitter.com into this application.

##Configure / AudienceCallback.py
Flask app that acts as a Flask server.
Set port to a port number that will be accessible through a firewall
Set the application's Consumer Key and Secret for the application being authorized.

start Flask server by executing:
`python AudienceCallback.py`


##Configure the application
At apps.twitter.com, log in and select the application associated with the Consumer Key above.  On the settings tab, set the Callback URL to the http://[Public IP]:[Port]/callback (where [Public IP] are the public IP address and port number used for the flask application.  As an example:  http://192.168.10.10:8000/callback

If dependancies are met, a URL/port will be show that can be used (or an external IP address that maps to this internal IP address).

Navigating to the 'root' of this page will generate an authorization request, which will redirect the user to Twitter.com to log in and authorize the app (associated to the Consumer Key set above).  If the web page browser (user) authorizes the app, a call is made from Twitter with an oauth token and verifier.  These two tokens can then be exchanged for the Access Token and Token Secret for that account.  This process only needs to be done once for each account.  The Access Token/Secret can be stored (securely) and used perpetually until the authorizing account revokes access.

---
###Feedback
Please send help requests / comments / complaints / chocolate to [@SteveDz](stevedz@twitter.com)

Note that this code is provide "As Is".  You should review and understand Python code, and be able to debug this code _on your own_ if used in a production environment.  See the License file for more legal limitations.

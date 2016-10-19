from flask import Flask, render_template, request, redirect, session
import tweepy
import os
import json
import gnip_insights as insights

app=Flask(__name__)

#Settings
PORT=8000
HOST_FILTER='0.0.0.0'
DEBUG=False
RECEIVED_FILE="Received-Tokens.json"
CONSUMER_KEY="CONSUMER_KEY_HERE"
CONSUMER_SECRET="CONSUMER_SECRET_HERE"

# Configure Flask app uniqueness
app.secret_key = os.urandom(24)

# Global dictionary to store request tokens in.
request_tokens={}

# Default / "Home page"
@app.route('/', methods=['GET'])
def root():
    return render_template('index.html', port=PORT)


# Process request to authorize application.  From index.html, clicking the button will call this endpoint.
@app.route('/authorize', methods=['GET'])
def authorize():
	try:
		# create Twitter API object
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

		# Generate authorization URL for requestor		
		url=auth.get_authorization_url()
		
		# capture request_token (made up of a request specific oauth token, oauth token secret, and confirmation that a callback url is configured.
		requestToken = auth.request_token

		if DEBUG:
			print "Authorize Request Token:", requestToken
		
		# Store request token to global dictionary.  In production, this should be stored to a database for scale.
		# The 'oauth_token' comes across via the callback, so we can use that as the key to retrieve the other info.
		request_tokens[requestToken['oauth_token']]=requestToken
		
		if DEBUG:
			print "Redirect URL:", url
	except Exception as ex:
		return render_template('index.html', error=ex)
	return redirect(url)

@app.route('/callback', methods=['GET'])
def oauth_data_collect():
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	
	if DEBUG:
		print "In Callback"
	if "denied" in request.args:
		if DEBUG:
			print "Denied! - Token = ", request.args.get('denied')
		return render_template('index.html', port=PORT, message="Authorization Denied!")
		
	else:
		try:
			if DEBUG:
				print "Getting args"

			oauth_token = request.args.get('oauth_token', '')
			oauth_verifier = request.args.get('oauth_verifier', '')
			access_data ="not set"
			access_token = "not set"
			access_secret = "not set"

			if DEBUG:
				print "oauth_token:",oauth_token
				print "oauth_verifier:", oauth_verifier
				print "setting request token"

			requestToken = request_tokens[oauth_token]
			auth.request_token = requestToken # requestToken # oauth_token

			if DEBUG:
				print "retrieving access data"

			access_data = auth.get_access_token(oauth_verifier)

			if DEBUG:
				print "access_data:", access_data
		except Exception as ex:
			if DEBUG:
				print "Error in get_access_token:",  str(ex)
			return render_template('index.html', port=PORT, error=ex)
	
		if access_data is not "not set":
			access_token = access_data[0]
			access_secret = access_data[1]
	
		if access_token is not "not set":
		
			# access_secret = auth.get_access_secret(oauth_verifier)
			engage=insights.Engagement(CONSUMER_KEY, CONSUMER_SECRET, access_token, access_secret)

		
			try:
				# Now that we have the token and secret, we can generate an authorization on Twitter "as" that user.
				auth.set_access_token(access_token, access_secret)
				api = tweepy.API(auth)

				#Get data for the user that authorized the app.
				authorized_user = api.me()
				if DEBUG:
					print "user info - ID:", authorized_user.id_str, ", handle:", authorized_user.screen_name

				# Build Authorization Record object (to store a JSON row to file)
				auth_record={}
				auth_record["id_str"] = authorized_user.id_str
				auth_record["screen_name"] = authorized_user.screen_name
				auth_record["oauth_token"] = oauth_token
				auth_record["oauth_verifier"] = oauth_verifier
				auth_record["access_token"] = access_token
				auth_record["access_secret"] = access_secret
								
				if DEBUG:
					print json.dumps(auth_record)
								
				# Store auth_record to file for later use.  Line Delimited JSON file
				with open(RECEIVED_FILE, "a") as myfile:
					myfile.write(json.dumps(auth_record) + "\n")

				# Get authorizing user's current timeline (20 most current Tweets)
				tweets = api.user_timeline()
	
				# create tweet ID array to pass to Engagement API
				tweet_ids=[]
				for tweet in tweets:
					tweet_ids.append(tweet.id_str)

				# Get Engagement data for timeline Tweets
				engagement_data = engage.get_historical(tweet_ids)
		
				# Build collection from scratch as the "tweets" data can't be modified directly, 
				# and we don't need to send all the data to the web page for rendering
				tweet_data=[]

				if engagement_data.status_code == 200:
					if DEBUG:
						print "Engagements = ", json.dumps(engagement_data.json(), indent=3)
		
					for tweet in tweets:
						new_tweet={}
						new_tweet['id'] = tweet.id
						new_tweet['user'] = tweet.user
						new_tweet['engagements'] = engagement_data.json()['by-tweet-id'][tweet.id_str]
						if DEBUG:
							print "Engagements for ", tweet.id_str, ": ", engagement_data.json()['by-tweet-id'][tweet.id_str]
						tweet_data.append(new_tweet)
					
					# Render Tweets and engagement data
					return render_template('callback.html', tweets=tweet_data)    
			except Exception as ex:
				if DEBUG:
					print "Error in get_access_token:",  str(ex)
				return render_template('index.html', port=PORT, error=ex)
	   
@app.errorhandler(404)
def not_found(error):
    return redirect("http://www.nullisland.com")

if __name__ =='__main__':
    app.run(debug=DEBUG, host=HOST_FILTER, port=PORT)

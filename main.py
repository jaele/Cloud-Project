# Author: James Le
# Assignment: Oauth 2.0 implementation
# Due date: 5/7/2017
# CSS Layout from : http://maxdesign.com.au/css-layouts/
# Reference: https://cloud.google.com/appengine/docs/standard/python/issue-requests
#            http://jinja.pocoo.org/docs/2.9/api/

import logging
import webapp2
import json
import os
import jinja2
import uuid
import requests
from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

CLIENT_ID = '512742852375-0ah9b65vct66o0d13v82rd55bu9484v3.apps.googleusercontent.com'
CLIENT_SECRET = 'BQXty7SiGTJBa6GTxcaTwmJJ'
#REDIRECT_URI = 'https://8080-dot-2331216-dot-devshell.appspot.com/oauth'  # local development server
REDIRECT_URI = 'https://cs-496-163617.appspot.com/oauth'
STATE = str(uuid.uuid4())


JINJA_ENVIRONMENT = jinja2.Environment (
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

# default page for user to get started
class MainHandler(webapp2.RequestHandler):
    def get(self):
        # GET request for authorization code and state
        google_endpoint_url = "https://accounts.google.com/o/oauth2/v2/auth" + "?response_type=code&client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URI + "&scope=email&state=" + STATE
        # link on website that the end-user clicks on to get to google's endpoint
        ouath_link = {'endpoint_link': google_endpoint_url}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.out.write(template.render(ouath_link))

# page where user gets redirected to
class OuathHandler(webapp2.RequestHandler):
    def get(self):
        logging.debug('The contents of the GET request are:' + repr(self.request.GET))
        # save responses from GET request
        code = self.request.get('code')
        state = self.request.get('state')
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        # data to be sent to google's api
        data = {'code': code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'}
        
        # send data via POST request
        r_post = requests.post('https://www.googleapis.com/oauth2/v4/token', headers = headers, data = data)
        
        # save responses from POST request
        r_data = r_post.json()
        
        credentials = r_data['access_token']
        header = {'Authorization': 'Bearer ' + credentials}
        
        
        # exchange token for information via GET request
        r_token_exchange = requests.get('https://www.googleapis.com/plus/v1/people/me', headers = header)
        
        
        r_info = json.loads(r_token_exchange.content)
        
        r_names = r_info['name']
        
        # print user's information on webpage
        information = { 'family_name': r_names['familyName'],
                        'given_name': r_names['givenName'],
                        'url_link': r_info['url'],
                        'state': state }
        
        template = JINJA_ENVIRONMENT.get_template('oauth.html')
        self.response.out.write(template.render(information))

# extra filler tabs
class AboutHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('about.html')
        self.response.out.write(template.render())
  
        
class ContactHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('contact.html')
        self.response.out.write(template.render())
        
app = webapp2.WSGIApplication([
        ('/', MainHandler),
        ('/oauth', OuathHandler),
        ('/about', AboutHandler),
        ('/contact', ContactHandler)
], debug=True)
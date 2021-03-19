import os
from flask import Flask, session, redirect, request, url_for
from requests_oauthlib import OAuth2Session
import requests
import pandas as pd

app = Flask(__name__)

OURA_CLIENT_ID = 'ABMZCHV4LSSQUFZM'
OURA_CLIENT_SECRET = '27CWYIW4W5JIKZ6WBAQ6UEGBXCEOIX2O'

START_DATE = '2021-02-01'
END_DATE = '2021-02-07'
LOCAL_STORAGE_PATH = 'sleep_data_from{}_to{}.csv'.format(START_DATE, END_DATE)

OURA_AUTH_URL = 'https://cloud.ouraring.com/oauth/authorize'
OURA_TOKEN_URL = 'https://api.ouraring.com/oauth/token'

@app.route("/")
def home():
    return "Hello i am oura ring <h1>eeeeeeeeeeeeeeeeeee<h1>"

@app.route('/login')
def oura_login():
    oura_session = OAuth2Session(OURA_CLIENT_ID)
    authorization_url, state = oura_session.authorization_url(OURA_AUTH_URL)
    session['oauth_state'] = state

    return redirect(authorization_url)

@app.route('/callback')
def callback():
    """
    Callback page
    Get the access_token from response url from Oura.
    Redirect to the sleep data page.
    """
    oura_session = OAuth2Session(OURA_CLIENT_ID, state=session['oauth_state'])
    session['oauth'] = oura_session.fetch_token(
                        OURA_TOKEN_URL,
                        client_secret=OURA_CLIENT_SECRET,
                        authorization_response=request.url)
    return redirect(url_for('.sleep'))

    # redirect to the /sleep route when finished
    return redirect(url_for('.sleep'))

@app.route('/sleep')
def sleep():
    """
    Sleep data page
    Get sleep data from the OURA API
    transform sleep data to a pandas DataFrame
    store sleep data as a csv
    return description of the DataFrame
    """
    oauth_token = session['oauth']['access_token']

    sleep_data = requests.get('https://api.ouraring.com/v1/sleep?'
                              'start={}&end={}&access_token={}'
                              .format(START_DATE, END_DATE, oauth_token))
    json_sleep = sleep_data.json()
    df = pd.DataFrame(json_sleep['sleep'])
    df.to_csv(LOCAL_STORAGE_PATH)
    return '<p>Successfully stored sleep data</p><p>{}</p>'\
        .format(df.describe())


if __name__ == "__main__":

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = os.urandom(24)
    app.run(debug=False, host='127.0.0.1', port=8080)
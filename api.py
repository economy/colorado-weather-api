#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request
import logging
from logging import Formatter, FileHandler
import os
import pandas as pd
import pickle

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
#app.config.from_object('config')

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/get', methods=['GET', 'POST'])
def get():
	
	a = df.sort_values('celc', ascending=False).to_json(orient='records')	

	return a, 200

@app.route('/head')
def head():

	# optionally, specify how many records you want
	recs = request.args.get('records')
	if recs:
		recs = int(recs)
	else:
		recs = 10

	a = df.head(recs).to_json(orient='records')

	return a, 200


@app.route('/options')
def options():
    
    	return "/get, /put, /post, /head, /options", 200


# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    
    	return "Internal error encountered", 500


@app.errorhandler(404)
def not_found_error(error):
    	return "That route does not exist", 404

if not app.debug:
    	file_handler = FileHandler('error.log')
    	file_handler.setFormatter(
        	Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    	)
    	app.logger.setLevel(logging.INFO)
    	file_handler.setLevel(logging.INFO)
    	app.logger.addHandler(file_handler)
    	app.logger.info('errors')


# Utility Functions

def load_data(f='./weather_data.pkl', colorado_only=True):
	
	# load file, get dict unpacked into dataframe
	w = pickle.load(open('./weather_data.pkl', 'rb'))
	zipped = list(zip(w.keys(), w.values()))
	unpacked = [ [x[0][0], x[0][1], x[-1]] for x in zipped ]
	df = pd.DataFrame(unpacked, columns = ['lat', 'long', 'fahr'])

	# limit to only colorado (NB: longs are flipped because negative!)
	if colorado_only:
		df = df[
			(df['lat'] >= 37.090957) & (df['lat'] <= 40.967523)
			& (df['long'] >= -109.015605) & (df['long'] <= -102.145939)
		] 

	# convert fahrenheit to celsius	
	df['celc'] = df['fahr'].apply(lambda x: fahr_to_celc(x))
	
	# we only care about celsius, so ignore fahr column
	df = df.drop('fahr', axis=1)

	return df	

def fahr_to_celc(fahr):
	
	celc = (fahr - 32) * (5 / 9) 
	return celc
	
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == '__main__':

	# load dataframe on init
	df = load_data()

	port = int(os.environ.get('PORT', 5555))
	app.run(host='0.0.0.0', port=port)

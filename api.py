#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, abort, g
import logging
from logging import Formatter, FileHandler
import os
import pandas as pd
import pickle
from datetime import datetime
import sqlite3

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
DATABASE = './tmp_db.db'

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/weather', methods=['GET', 'POST'])
def get():

	conn = get_db()	
	df = read_df(conn)
 
	if request.method == 'GET':
		if request.args.get('lat') and request.args.get('long'):
			lat = request.args.get('lat')
			long = request.args.get('long')
		else: 
			return "`lat` and `long` parameters required for this method", 500
	elif request.method == 'POST':
		if all([ x in request.get_json().keys() for x in ['lat', 'long'] ]):
			lat = request.get_json()['lat']
			long = request.get_json()['long']
		else:
			return "`lat` and `long` parameters required for this method", 500

	result = df[
		(df['lat'] == lat)
		& (df['long'] == long)
	]
	if result.empty:
		return "Record not found.", 404
		
	response = result.to_json(orient='records')

	return response, 200


@app.route('/weather/all', methods=['GET'])
def get_all():
	conn = get_db()
	df = read_df(conn)

	# optionally, specify how many records you want
	recs = request.args.get('records')
	if recs:
		recs = int(recs)
		response = df.head(recs).to_json(orient='records')
	else:
		response = df.sort_values('added', ascending=False).to_json(orient='records')	

	return response, 200


@app.route('/weather/add', methods = ['GET', 'POST'])
def add():
	conn = get_db()
	df = read_df(conn)

	if request.method == 'GET':
		if request.args.get('lat') and request.args.get('long') and request.args.get('temp'):
			lat = request.args.get('lat')
			long = request.args.get('long')
		else: 
			return "`lat`, `long`, and `temp` parameters required for this method", 500
	elif request.method == 'POST':
		if all([ x in request.get_json().keys() for x in ['lat', 'long', 'temp'] ]):
			lat = request.get_json()['lat']
			long = request.get_json()['long']
		else:
			return "`lat`, `long`, and `temp` parameters required for this method", 500
	
	cursor = conn.cursor()
	cursor.execute('''
		INSERT INTO temps (lat, long, celc, added)
		VALUES (?, ?, ?, ?)
	''', (lat, long, temp, str(datetime.now())))
	conn.commit()

	updated_df = read_df(conn)

	response = "Record added. {:,} records now in weather DB.".format(updated_df.shape[0])		
	
	return response, 200
	

@app.route('/weather/update', methods = ['GET', 'POST'])
def update():
	conn = get_db()
	df = read_df(conn)

	if request.method == 'GET':
		if request.args.get('lat') and request.args.get('long') and request.args.get('temp'):
			lat = request.args.get('lat')
			long = request.args.get('long')
		else: 
			return "`lat`, `long`, and `temp` parameters required for this method", 500
	elif request.method == 'POST':
		if all([ x in request.get_json().keys() for x in ['lat', 'long', 'temp'] ]):
			lat = request.get_json()['lat']
			long = request.get_json()['long']
		else:
			return "`lat`, `long`, and `temp` parameters required for this method", 500

	result = df[
		(df['lat'] == lat)
		& (df['long'] == long)
	]

	if result.empty:
		return "Record not found, nothing was updated", 404
	else:
		cursor = conn.cursor()
		cursor.execute('''
			UPDATE temps SET celc = ?, added = ?
			WHERE lat = ? AND long = ?
		''', (temp, str(datetime.now()), lat, long))
		conn.commit()

	updated_df = read_df(conn)

	new_result = updated_df[
		(updated_df['lat'] == lat)
		& (updated_df['long'] == long)
	]

	response = new_result.to_json(orient='records')

	return "Record updated: {}".format(response), 200


@app.route('/weather/remove', methods = ['GET', 'POST'])
def remove():
	conn = get_db()
	df = read_df(conn)

	if request.method == 'GET':
		if request.args.get('lat') and request.args.get('long'):
			lat = request.args.get('lat')
			long = request.args.get('long')
		else: 
			return "`lat` and `long` parameters required for this method", 500
	elif request.method == 'POST':
		if all([ x in request.get_json().keys() for x in ['lat', 'long'] ]):
			lat = request.get_json()['lat']
			long = request.get_json()['long']
		else:
			return "`lat` and `long` parameters required for this method", 500
	
	result = df[
		(df['lat'] == lat)
		& (df['long'] == long)
	]

	if result.empty:
		return "Record not found, nothing was updated", 404
	else:
		cursor = conn.cursor()
		cursor.execute('''
			DELETE FROM temps
			WHERE lat = ? AND long = ?
		''', (temp, str(datetime.now()), lat, long))
		conn.commit()

	updated_df = read_df(conn)
	response = "Record deleted. {:,} records now in weather DB".format(updated_df.shape[0])

	return response, 200


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

	# add a datetime field to keep track of recent record additions
	df['added'] = str(datetime.now())

	return df	

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
	return db

def read_df(conn):
	df = pd.read_sql_query('select * from temps', conn)
	return df

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

def db_load(conn, df):

	cursor = conn.cursor()

	# drop old if exists
	cursor.execute(
		'''
		DROP TABLE IF EXISTS temps
		'''
	)
	conn.commit()

	# create table in memory
	cursor.execute(
		'''
		CREATE TABLE temps(lat REAL, long REAL, celc REAL, added TEXT)
		'''
	)
	conn.commit()

	# load df into table
	cursor.executemany(
		'''
		INSERT INTO temps(lat, long, celc, added) VALUES(?,?,?,?)
		''', df.to_records(index=False)
	)
	conn.commit()

def fahr_to_celc(fahr):
	
	celc = (fahr - 32) * (5 / 9) 
	return celc
	
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == '__main__':

	# load dataframe on init to sqlite3
	df = load_data()

	# place data in temp db
	with app.app_context():
		conn = get_db()
		db_load(conn, df)

	port = int(os.environ.get('PORT', 5555))
	app.run(host='0.0.0.0', port=port)

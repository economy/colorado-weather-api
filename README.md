# Colorado Weather API

Test Flask API for returning temperature in Colorado in degrees Celsius, given a dictionary of global temperatures by latitude and longitude.

### Description
The API loads a provided pickle file with a dictionary of weather data by latitude and longitude. On startup, the app will reduce this data to a rectangle approximately representing Colorado:

- Northwest corner of Colorado state lat: 40.967523, lng: -109.015605
- Southeast corner of Colorado state lat: 37.090957, lng: -102.145939

The app loads this data into a sqlite3 database, along with the datetime string when it was added. Records can be queried by latitude / longitude directly,
added, updated, or removed. An additional endpoint is available for returning all records, or, optionally, a subset of the records.

### API Endpoints 
- `/weather`: provided a `lat` and a `long`, return the record that contains the degrees Celsius and date added
- `/weather/all`: returns all records in the dataset, including records updated or added. Optionally, provide a `records` parameter (int) to specify how many records to return (sorted by date added)
- `/weather/add`: add a weather record, given a `lat`, a `long`, and a `temp` (float, degrees Celsius)
- `/weather/update`: update an existing record, given a `lat`, a `long`, and a `temp` (float, degrees Celsius)
- `/weather/remove`: remove an existing record, given its `lat` and `long`

### Requirements
- Python >= 3.5, for compatibility and included packages (`pickle`, `sqlite3`, `logging`, etc.)
- `flask`: runs the API application, opens a port on localhost
- `pandas`: slices data, returns JSON records

### Run
`python api.py`

This will run the Flask API. `curl` requests can now be made on port 5555. Errors are logged to `error.log`

### Sample CURL (add a record to the weather DB)
`curl -d '{"lat": 38.655, "long": -108, "temp": 25}' -H "Content-Type: application/json" -X POST http://0.0.0.0:5555/weather/add`

# Colorado Weather API

Test Flask API for returning temperature in Colorado in degrees Celsius, given a dictionary of global temperatures by latitude and longitude

### Run
`python api.py`

This will run the Flask API. `curl` requests can now be made on port 5555. Errors are logged to `error.log`

### Sample CURL (add a record to the weather DB)
`curl -d '{"lat": 38.655, "long": -108, "temp": 25}' -H "Content-Type: application/json" -X POST http://0.0.0.0:5555/weather/add`

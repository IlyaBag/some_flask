grun:
	poetry run gunicorn -w 4 webtest.example:app

startflask:
	poetry run flask --app example --debug run --port 8000

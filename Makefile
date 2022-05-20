WORK_DIR := movie_collector

check:
	poetry install -n
	poetry run mypy --config-file mypy.ini $(WORK_DIR) tests
	poetry run flake8 --config=tox.ini $(WORK_DIR) tests
	APP_SETTINGS=testing poetry run pytest \
					--cov-report term-missing \
					--cov=$(WORK_DIR) \
					tests

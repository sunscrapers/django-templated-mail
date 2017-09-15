init:
	pipenv install --dev
	pipenv run pip install -e .

test:
	pipenv run py.test --ds=tests.settings --capture=no --cov-report term-missing --cov-report html --cov=templated_mail tests
	pipenv run flake8 .


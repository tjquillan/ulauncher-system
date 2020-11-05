lint:
	flake8 --exit-zero *.py
	mypy *.py

format:
	black *.py
	isort *.py

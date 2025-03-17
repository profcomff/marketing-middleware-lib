configure: venv
	source ./venv/bin/activate && pip install -r requirements.dev.txt

format:
	isort ./
	black ./
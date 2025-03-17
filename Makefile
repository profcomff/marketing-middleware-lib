configure: venv
	source ./venv/bin/activate && pip install -r requirements.dev.txt

format:
	autoflake -r --in-place --remove-all-unused-imports ./
	isort ./
	black ./
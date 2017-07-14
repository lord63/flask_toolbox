freeze:
	@pip-compile --output-file requirements/requirements.txt requirements/requirements.in

sync:
	@pip-sync requirements/requirements.txt

update:
	@pip-compile --upgrade requirements/requirements.in

clean:
	@find . -name "*.pyc" -exec rm -f {} \;
	@echo "Removed all the .pyc files"

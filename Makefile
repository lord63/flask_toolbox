freeze:
	@uv lock

sync:
	@uv sync

update:
	@uv lock --upgrade

clean:
	@find . -name "*.pyc" -exec rm -f {} \;
	@echo "Removed all the .pyc files"

.PHONY:
	install
	requirements

install:
	@echo Installing Python requirements...
	pip install -U pip setuptools pip-tools
	pip install -r requirements.dev.txt

requirements:
	@echo Compiling Python requirements...
	pip install -U pip setuptools pip-tools
	pip-compile -q requirements.dev.in
	pip-compile -q requirements.in

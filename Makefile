PYTHON_HOME = python3
VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
MAIN = src/main.py


# Setup minimum venv to run the Bot.
$(VENV)/bin/activate: requirements.txt
	$(PYTHON_HOME) -m venv $(VENV)
	$(PIP) install -r requirements.txt


# Run the Bot, optionally pass arguments.
.PHONY: run
run: ARGS?=
run: $(VENV)/bin/activate
	$(PYTHON) $(MAIN) $(ARGS)

.PHONY: help
help:
	@echo "\n---------------------------------------"
	@echo "Makefile Help:"
	@echo "---------------------------------------"
	@echo "make run \t\t\t<--- Start the Bot service with default settings."
	@echo "make run ARGS=\"\" \t\t<--- Pass more specific arguments to the Bot service."
		@echo "\te.g. ARGS=\"-n 'localhost' -p 5001 -t '12345BotToken!'\"\n"
	@echo "---------------------------------------"
	@echo "Script Args:"
	@echo "---------------------------------------"
	@$(MAKE) run ARGS?="-h"
	@echo "---------------------------------------\n"


# Install dev dependencies into the venv.
.PHONY: dev
dev: $(VENV)/bin/activate
	$(PIP) install -r requirements-dev.txt


RUFF = $(VENV)/bin/ruff
$(RUFF): $(VENV)/bin/activate
	$(MAKE) dev


# Linting and static analysis. Done before a push.
.PHONY:check
check: $(RUFF)
	$(RUFF) format src/
	$(RUFF) check src/ --fix


# Remove cache files and venv from the project directory.
.PHONY:clean
clean:
	rm -rf src/__pycache__ src/bot/__pycache__ .ruff_cache
	rm -rf $(VENV)

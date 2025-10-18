# configs/makefiles/v1.1.0
# See [7.2.1 General Conventions for Makefiles](https://www.gnu.org/prep/standards/html_node/Makefile-Basics.html)
SHELL := /bin/sh

init: project	## default (no-arg) target to initialise the project

# See [7.2.6 Standard Targets for Users > 'all'](https://www.gnu.org/prep/standards/html_node/Standard-Targets.html)
all: init	## primary target for creating all Project artifacts

.PHONY: init all
# ========================================
# Environment Variables
# ========================================
# [6.2.4 Conditional Variable Assignment](https://www.gnu.org/software/make/manual/html_node/Conditional-Assignment.html)
# [6.10 Variables from the Environment](https://www.gnu.org/software/make/manual/html_node/Environment.html)

## only used to create the virtual environment
PYTHON_HOME ?= python3
# ========================================
# Project Initialisation
# ========================================
MADE := ./.made
ENV := ./.env

project: $(MADE)/requirements $(ENV)	## alias for initialising the Project

project-dev: project $(MADE)/requirements-dev	## alias for initialising the development environment

$(MADE):	## setup directory for timestamps artifacts
	mkdir $(MADE)

$(ENV):
	@printf "\033[0;36mA template $(ENV) file was added. A real Discord bot token is required to run the Audio Service.\033[0m\n"
	echo "# Add a Discord Bot token, or create one at https://discord.com/developers/applications" >> "$(ENV)" ; \
	echo "DISCORD_BOT_TOKEN=<your_token_here>" >> "$(ENV)" ; \

VENV := ./.venv
PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python3

$(VENV) $(PIP) $(PYTHON):	## initialise the virtual environment
	$(PYTHON_HOME) -m venv $(VENV)

$(MADE)/requirements: $(MADE) $(PIP) requirements.txt	## install, or update Project dependencies
	$(PIP) install -r requirements.txt
	touch $(MADE)/requirements

RUFF := $(VENV)/bin/ruff

$(MADE)/requirements-dev: $(MADE) $(PIP) requirements-dev.txt	## install, or update development dependencies
	$(PIP) install -r requirements-dev.txt
	touch $(MADE)/requirements-dev

rm-project:	##> remove all Project initialisation artifacts
	rm -rf $(VENV) $(MADE)

.PHONY: project project-dev rm-project
# ========================================
# Python
# ========================================
start: $(MADE)/requirements	## run the Project
	$(PYTHON) "./src/main.py"

.PHONY: start
# ========================================
# Linting Rules
# ========================================
lint: lint-diff lint-untracked	## alias to run linting (lint-diff) (lint-untracked) rules
	git status -s

lint-diff: $(MADE)/requirements-dev	##> run linting on modified (git diff HEAD) source (./src/) files only
	git diff HEAD --diff-filter=ACM --name-only -z "./src/" | xargs -r -0 $(RUFF) check --fix

lint-untracked: $(MADE)/requirements-dev	##> run linting on untracked source (./src/) files only
	git ls-files --others --exclude-standard -z  "./src/" | xargs -r -0 $(RUFF) check --fix

lint-source: $(MADE)/requirements-dev	##> run linting on (./src/) files
	$(RUFF) check "./src/" --fix

.PHONY: lint lint-diff lint-untracked lint-source
# ========================================
# Formatting Rules
# ========================================
format: format-diff format-untracked	## alias to run formatting (format-diff) (format-untracked) rules
	git status -s

format-diff: $(MADE)/requirements-dev	##> run formatting on modified (git diff HEAD) source (./src/) files only
	git diff HEAD --diff-filter=ACM --name-only -z "./src/" | xargs -r -0 $(RUFF) format

format-untracked: $(MADE)/requirements-dev	##> run formatting on untracked source (./src/) files only
	git ls-files --others --exclude-standard -z  "./src/" | xargs -r -0 $(RUFF) format

format-source: $(MADE)/requirements-dev	##> run formatting on (./src/) files
	$(RUFF) format "./src/"

.PHONY: format format-diff format-untracked format-source
# ========================================
# Utilities
# ========================================
# See [7.2.6 Standard Targets for Users > 'clean'](https://www.gnu.org/prep/standards/html_node/Standard-Targets.html)
clean: rm-project	## alias for cleaning up all artifacts produced by this Project
	rm -rf .ruff_cache
	find "./src" -type d -name "__pycache__" -print0 | xargs -0 rm -rf

help:  ## show a summary of available targets
	@printf "%s\n" \
	"------------------" \
	" General Commands" \
	"------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; { \
			cmd = $$1; desc = $$2; \
			gsub(/\(([^)]*)\)/, "\033[34m&\033[0m", desc); \
			printf "  \033[36m%-21s\033[0m %s\n", cmd, desc \
		}'
	@printf "%s\n" \
	"------------------"

help-ext:  ## show all available targets
	@printf "%s\n" \
	"------------------" \
	"Available Commands" \
	"------------------"
	@grep -E '^[a-zA-Z0-9_-]+:.*?##>? ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?##>? "}; { \
			cmd = $$1; desc = $$2; \
			gsub(/\(([^)]*)\)/, "\033[34m&\033[0m", desc); \
			printf "  \033[36m%-21s\033[0m %s\n", cmd, desc \
		}'
	@printf "%s\n" \
	"------------------"

.PHONY: clean help help-ext
# ========================================
# ANSI Color Escape Codes
# ========================================
# YELLOW='\033[0;33m'
# RED='\033[0;31m'
# GREEN='\033[0;32m'
# CYAN='\033[0;36m'
# BLUE='\033[0;34m'
# NONE='\033[0m'
# ========================================

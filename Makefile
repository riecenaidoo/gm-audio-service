# =============================================================================
# configs:/makefiles/v1.3.1;/python/v1.0.0
# =============================================================================
# ANSI Color Escape Codes
# =============================================================================
YELLOW=\033[0;33m
RED=\033[0;31m
GREEN=\033[0;32m
CYAN=\033[0;36m
BLUE=\033[0;34m
NONE=\033[0m
# =============================================================================

# See [7.2.1 General Conventions for Makefiles](https://www.gnu.org/prep/standards/html_node/Makefile-Basics.html)
SHELL := /bin/sh

init: project git	## default (no-arg) target to initialise the Project and local repository

# See [7.2.6 Standard Targets for Users > 'all'](https://www.gnu.org/prep/standards/html_node/Standard-Targets.html)
all: init python	## primary target for creating all Project artifacts

start: serve	## start the Project (make stop)

stop: kill-serve	## stop the Project

log:	## show logs of the Project
	tail $(MADE)/serve
	@printf "$(CYAN)\n%s\n$(NONE)" "(Streaming Mode) tail -f $(MADE)/serve"

.PHONY: init all start stop log
# =============================================================================
# Environment Variables
# =============================================================================
# [6.2.4 Conditional Variable Assignment](https://www.gnu.org/software/make/manual/html_node/Conditional-Assignment.html)
# [6.10 Variables from the Environment](https://www.gnu.org/software/make/manual/html_node/Environment.html)

## only used to create the virtual environment
PYTHON_HOME ?= python3
# =============================================================================
# Script Macros
# =============================================================================
XARGS := xargs -0 --no-run-if-empty
PLAINTEXT_FILTER := $(XARGS) file --mime-type | awk -F: '/text\// { printf "%s\0", $$1 }'

STOP_PROCESS := ./.scripts/stop-process.sh

##> Given the PID file, stop the process
define stop_process	
@if [ -f "$(1)" ]; then \
	xargs --no-run-if-empty --arg-file "$(1)" "$(STOP_PROCESS)"; \
fi
endef
# =============================================================================
# Project
# =============================================================================
MADE := ./.made
ENV := ./.env

project: $(MADE) $(MADE)/stop-script $(ENV)	##> alias for initialising the Project

$(MADE):
	mkdir $(MADE)

# See [4.3 Types of Prerequisites](https://www.gnu.org/software/make/manual/html_node/Prerequisite-Types.html) > order-only-prerequisites
$(MADE)/stop-script: $(STOP_PROCESS) | $(MADE)	##> mark scripts executable
	chmod +x $(STOP_PROCESS)
	touch $(MADE)/stop-script

$(ENV):
	@printf "$(CYAN)\n%s\n$(NONE)" "A template $(ENV) file was added. A real Discord bot token is required to run the Audio Service."
	echo "# Add a Discord Bot token, or create one at https://discord.com/developers/applications" >> "$(ENV)" ; \
	echo "DISCORD_BOT_TOKEN=<your_token_here>" >> "$(ENV)" ; \

rm-project:	##> remove all Project initialisation artifacts
	rm -f $(MADE)/stop-script
	@if [ -d $(MADE) ]; then \
		rmdir --ignore-fail-on-non-empty $(MADE); \
	fi

.PHONY: project rm-project
# =============================================================================
# Git
# - [Git Hooks](https://git-scm.com/book/ms/v2/Customizing-Git-Git-Hooks)
# =============================================================================
DIFF_FILES := git diff HEAD --diff-filter=ACM --name-only --relative -z
UNTRACKED_FILES := git ls-files --others --exclude-standard --full-name -z

git: .git/hooks/pre-commit .git/hooks/pre-push	##> alias for initialising the local repository; creates Git artifacts

.git/hooks/pre-commit: ./.scripts/pre-commit.sh	| $(MADE)	## updates the pre-commit hook in the local repository
	@if [ -f .git/hooks/pre-commit ]; then \
		cat .git/hooks/pre-commit >> $(MADE)/pre-commit; \
	fi
	cat .scripts/pre-commit.sh > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit	# Ensure the script is executable.
	@printf '\n$(YELLOW)%s$(NONE)\n' "Pre-Commit Hook installed."
	@printf '\tHint:\t$(CYAN)%s$(NONE)\n' "rm .git/hooks/pre-commit" "make rm-git"

.git/hooks/pre-push: ./.scripts/pre-push.sh	| $(MADE)	## updates the pre-push hook in the local repository
	@if [ -f .git/hooks/pre-push ]; then \
		cat .git/hooks/pre-push >> $(MADE)/pre-push; \
	fi
	cat .scripts/pre-push.sh > .git/hooks/pre-push
	chmod +x .git/hooks/pre-push	# Ensure the script is executable.
	@printf '\n$(YELLOW)%s$(NONE)\n' "Pre-Push Hook installed."
	@printf '\tHint:\t$(CYAN)%s$(NONE)\n' "rm .git/hooks/pre-push" "make rm-git"

rm-git:	##> remove all Git artifacts produced by this script
	rm -f .git/hooks/pre-commit .git/hooks/pre-push
	@printf '\n$(YELLOW)%s$(NONE)\n' "Git Hook(s) removed."
	@printf '\tHint:\t$(CYAN)%s$(NONE) contains any overwritten existing Git hooks.\n' "$(MADE)"

.PHONY: git rm-git
# =============================================================================
# Docker
# =============================================================================
image: $(MADE)/image-dev	## build the (dev) image

$(MADE)/image-dev: $(find src/ -type f -name '*.py')
	docker build -t gm-discord:dev . -f ./Dockerfile
	touch $(MADE)/image-dev

latest: $(MADE)/image-dev	## tag the (dev) image as (latest)
	docker tag gm-discord:dev gm-discord:latest

rm-docker:	##> remove all Docker artifacts produced by this script
	rm -f $(MADE)/image-dev

.PHONY: image latest rm-docker
# =============================================================================
# PYTHON
# =============================================================================
python: $(MADE)/requirements	##> alias for creating all Python artifacts

VENV := ./.venv
PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python3

$(VENV) $(PIP) $(PYTHON):	## initialise the virtual environment
	$(PYTHON_HOME) -m venv $(VENV)

$(MADE)/requirements: $(PIP) requirements.txt | $(MADE)	## install, or update Project dependencies
	$(PIP) install -r requirements.txt
	touch $(MADE)/requirements

python-dev: python $(MADE)/requirements-dev	##> alias for creating all Python development artifacts

RUFF := $(VENV)/bin/ruff

$(RUFF) $(MADE)/requirements-dev: $(PIP) requirements-dev.txt | $(MADE)	## install, or update development dependencies
	$(PIP) install -r requirements-dev.txt
	touch $(MADE)/requirements-dev

rm-python: kill-serve	##> remove all Project initialisation artifacts
	rm -rf $(VENV) $(MADE)
	rm -rf .ruff_cache
	find "./src" -type d -name "__pycache__" -print0 | $(XARGS) rm -rf

serve:	$(MADE) $(PYTHON) python kill-serve	##> start the Python server
	$(PYTHON) "./src/main.py" > $(MADE)/serve 2>&1 & echo $$! > $(MADE)/serve.pid

kill-serve:	##> kill the Python server process
	$(call stop_process,$(MADE)/serve.pid)

PYTHON_FILTER := $(XARGS) awk -v RS='\0' '/\.py$$/'

.PHONY: python python-dev rm-python serve kill-serve
# =============================================================================
# Linting
# =============================================================================
LINT := $(PYTHON_FILTER) | $(XARGS) $(RUFF) check --fix
LINT_CHECK := $(PYTHON_FILTER) | $(XARGS) $(RUFF) check

lint: lint-diff lint-untracked	## alias to run linting (lint-diff) (lint-untracked) rules
	git status -s

lint-diff: python-dev	##> run linting on modified (git diff HEAD) files
	$(DIFF_FILES) | $(LINT)

lint-diff-check: python-dev	##> check linting on modified (git diff HEAD) files
	$(DIFF_FILES) | $(LINT_CHECK)

lint-untracked: python-dev	##> run linting on untracked files
	$(UNTRACKED_FILES) | $(LINT)

lint-all: python-dev	##> run linting on all files
	find src/ -type f -name '*.py' -print0 | $(LINT)

.PHONY: lint lint-diff lint-untracked lint-all
# =============================================================================
# Formatting
# =============================================================================
FORMAT := $(PYTHON_FILTER) | $(XARGS) $(RUFF) format
FORMAT_CHECK := $(PYTHON_FILTER) | $(XARGS) $(RUFF) format --check

TRIM_CHECK := $(PLAINTEXT_FILTER) | $(XARGS) grep -lZ '[[:blank:]]$$'
TRIM := $(TRIM_CHECK) | $(XARGS) sed -i 's/[ \t]*$$//'

format: format-diff format-untracked	## alias to run formatting (format-diff) (format-untracked) rules
	git status -s

format-diff: python-dev	##> run formatting on modified (git diff HEAD) files
	$(DIFF_FILES) | $(TRIM)
	$(DIFF_FILES) | $(FORMAT)

format-diff-check: python-dev	##> check formatting on modified (git diff HEAD) files
	$(DIFF_FILES) | $(FORMAT_CHECK)
	@TRAILING_WHITESPACE_FILES=$$($(DIFF_FILES) | $(TRIM_CHECK)); \
	if [ -n "$$TRAILING_WHITESPACE_FILES" ]; then \
		  printf '$(RED)%s$(NONE)' "Trailing Whitespaces!"; \
		  printf '\t- %s\n' "$$TRAILING_WHITESPACE_FILES"; \
		exit 1; \
	fi

format-untracked: python-dev	##> run formatting on untracked files
	$(UNTRACKED_FILES) | $(TRIM)
	$(UNTRACKED_FILES) | $(FORMAT)

format-all: python-dev	##> run formatting on all files
	find . -maxdepth 1 -type f -print0 | $(TRIM)
	find .scripts/ src/ -type f -print0 | $(TRIM)
	find src/ -type f -name '*.py' -print0 | $(FORMAT)

.PHONY: format format-diff format-untracked format-all
# =============================================================================
# Utilities
# =============================================================================
# See [7.2.6 Standard Targets for Users > 'clean'](https://www.gnu.org/prep/standards/html_node/Standard-Targets.html)
clean: rm-python rm-git rm-project	## alias for cleaning up all artifacts produced by this Project

help:  ## show a summary of available targets
	@printf "%s\n" \
	"===============================================================================" \
	" General Commands" \
	"==============================================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; { \
			cmd = $$1; desc = $$2; \
			gsub(/\(([^)]*)\)/, "$(CYAN)&$(NONE)", desc); \
			printf "  $(BLUE)%-21s$(NONE) %s\n", cmd, desc \
		}'
	@printf "%s\n" \
	"==============================================================================="

help-ext:  ## show all available targets
	@printf "%s\n" \
	"===============================================================================" \
	"Available Commands" \
	"==============================================================================="
	@grep -E '^[a-zA-Z0-9_-]+:.*?##>? ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?##>? "}; { \
			cmd = $$1; desc = $$2; \
			gsub(/\(([^)]*)\)/, "$(CYAN)&$(NONE)", desc); \
			printf "  $(BLUE)%-21s$(NONE) %s\n", cmd, desc \
		}'
	@printf "%s\n" \
	"==============================================================================="

.PHONY: clean help help-ext
# =============================================================================

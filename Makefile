PROJ := bot-prakasha-ke
LIB := prakasha
GITHUB_REPO := github.com:oubiwann/$(PROJ).git
#GOOGLE_REPO := code.google.com/p/$(PROJ)
LP_REPO := lp:$(PROJ)
PKG_NAME := $(PROJ)
BZR_MSG_FILE ?= BZR_MSG
GIT_MSG_FILE ?= GIT_MSG
TMP_FILE ?= /tmp/MSG
VIRT_DIR ?= .venv
VIRT_BUILD_DIR ?= test-build


keygen:
	@python -c "import prakasha.app;from carapace.sdk import scripts;scripts.KeyGen()"

run:
	twistd -n prakasha

daemon:
	twistd prakasha

shell:
	@python -c "import prakasha.app;from carapace.sdk import scripts;scripts.ConnectToShell()"

stop:
	@python -c "import prakasha.app;from carapace.sdk import scripts;scripts.StopDaemon()"

run-test:
	make daemon && make shell && make stop

generate-config: DIR ?= $(VIRT_DIR)/$(VIRT_BUILD_DIR)
generate-config:
	@. $(DIR)/bin/activate && python -c "from prakasha import app;from carapace.sdk import scripts;scripts.GenerateConfig();"

bzr-2-git:
	git init && bzr fast-export `pwd` | git fast-import && git reset HEAD
	git remote add origin git@$(GITHUB_REPO)
	git push -u origin master

import-bzr:
	rm -rf .bzr
	bzr branch $(LP_REPO) bzr-tmp
	mv bzr-tmp/.bzr .
	rm -rf bzr-tmp

add: FILES =
add:
	git add $(FILES)
	bzr add $(FILES)

remove: FILE =
remove:
	#cp $(file) $(file).bak
	git rm $(FILE)
	bzr rm $(FILE)

update: import-bzr
	git pull

log-concise:
	git log --oneline

log-verbose:
	git log --format=fuller

log-authors:
	git log --format='%aN %aE' --date=short

log-authors-date:
	git log --format='%ad %aN %aE' --date=short

log-changes:
	git log --format='%ad %n* %B %N%n' --date=short

clean:
	sudo rm -rfv dist/ build/ MANIFEST *.egg-info
	rm -rfv _trial_temp/ CHECK_THIS_BEFORE_UPLOAD.txt twistd.log
	find ./ -name "*~" -exec rm -v {} \;
	sudo find ./ -name "*.py[co]" -exec rm -v {} \;
	find . -name "*.sw[op]" -exec rm -v {} \;

msg:
	-@rm $(BZR_MSG_FILE) $(GIT_MSG_FILE)
	@echo '!!! REMOVE THIS LINE !!!' >> $(GIT_MSG_FILE)
	@git diff ChangeLog |egrep -v '^\+\+\+'|egrep '^\+.*'|sed -e 's/^+//' >> $(GIT_MSG_FILE)
	@bzr diff ChangeLog |egrep -v '^\+\+\+'|egrep '^\+.*'|sed -e 's/^+//' >> $(BZR_MSG_FILE)
.PHONY: msg

commit: msg
	bzr commit --show-diff --file=$(BZR_MSG_FILE)
	git commit -a -v -t $(GIT_MSG_FILE)
	@mv $(BZR_MSG_FILE) $(BZR_MSG_FILE).backup
	@mv $(GIT_MSG_FILE) $(GIT_MSG_FILE).backup
	@touch $(BZR_MSG_FILE) $(GIT_MSG_FILE)

push:
	bzr push $(LP_REPO)
	git push --all git@$(GITHUB_REPO)
#	git push --all https://$(GOOGLE_REPO)

push-tags:
	git push --tags git@$(GITHUB_REPO)
#	git push --tags https://$(GOOGLE_REPO)

push-all: push push-tags
.PHONY: push-all

commit-push: commit push-all
.PHONY: commit-push

stat: msg
	@echo
	@echo "### Changes ###"
	@echo
	-@cat $(BZR_MSG_FILE)
	@echo
	@echo "### Bzr status ###"
	@echo
	@bzr stat
	@echo
	@echo "### Git working branch status ###"
	@echo
	@git status -s
	@echo
	@echo "### Git branches ###"
	@echo
	@git branch
	@echo 

status: stat
.PHONY: status

todo:
	git grep -n -i -2 XXX
	git grep -n -i -2 TODO
.PHONY: todo

build:
	python setup.py build
	python setup.py sdist

build-docs:
	cd docs/sphinx; make html

check-docs: files = "README.rst"
check-docs:
	@echo "noop"

check-examples: files = "examples/*.py"
check-examples:
	@echo "noop"

check-dist:
	@echo "Need to fill this in ..."

check: build check-docs check-examples
	trial $(LIB)

check-integration:
# placeholder for integration tests
.PHONY: check-integration

version:
	@echo $(VERSION)

virtual-deps:
	sudo pip install virtualenv

virtual-build: DIR ?= $(VIRT_DIR)/$(VIRT_BUILD_DIR)
virtual-build: clean build virtual-deps
	mkdir -p $(VIRT_DIR)
	-test -d $(DIR) || virtualenv $(DIR)
	@. $(DIR)/bin/activate
	-test -e $(DIR)/bin/twistd || $(DIR)/bin/pip install twisted
	-test -e $(DIR)/bin/rst2html.py || $(DIR)/bin/pip install docutils
	. $(DIR)/bin/activate && pip install ./dist/$(PACKAGE_NAME)*
#	$(DIR)/bin/pip uninstall -vy $(PKG_NAME)

clean-virt: clean
	rm -rf $(VIRT_DIR)

virtual-build-clean: clean-virt build virtual-build
.PHONY: virtual-build-clean

register:
	python setup.py register

upload: check
	python setup.py sdist upload --show-response

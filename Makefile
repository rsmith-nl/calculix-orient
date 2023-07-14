# file: Makefile
# vim:fileencoding=utf-8:fdm=marker:ft=make
#
# NOTE: This Makefile is only intended for developers.
#       It is only meant for UNIX-like operating systems.
#       Most of the commands require extra software.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2018-01-21 22:44:51 +0100
# Last modified: 2023-07-14T18:41:48+0200
.PHONY: clean check format test zip

.if make(zip)
TAGCOMMIT!=git rev-list --tags --max-count=1
TAG!=git describe --tags ${TAGCOMMIT}
.endif

all::
	@echo 'you can use the following commands:'
	@echo '* clean: remove all generated files.'
	@echo '* check: check all python files. (requires pylama)'
	@echo '* format: format the source. (requires black)'
	@echo '* test: run the built-in tests. (requires py.test)'
	@echo '* zip: create a zipfile of the latest tagged version.'

clean::
	rm -f backup-*.tar* calculix-orient-*.zip
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

# The targets below are mostly for the maintainer.
check:: .IGNORE
	pylama auto-orient.py test/*.py

test::
	py.test -v

zip:: clean
	git checkout ${TAG}
	cd .. && zip -r calculix-orient-${TAG}.zip calculix-orient/ \
		-x 'calculix-orient/.git/*' '*/.pytest_cache/*' '*/__pycache__/*' '*/.cache/*'
	git checkout main
	mv ../calculix-orient-${TAG}.zip .

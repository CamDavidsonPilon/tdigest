
PROJ=tdigest
PYTHON=python
TEST_TIMEOUT=600


default:
	@echo "Try one of:"
	@echo "    env - build a dev env in env/"
	@echo "    test - run all the tests"
	@echo "    test1 - run tests until one fails"
	@echo "    package - build a .whl for potential deployment"
	@echo "    release - build the .whl on the current machine with a new version number, tag and push the source"
	@echo "    deploy - (requires sudo) build and install the .whl on the current machine"
	@echo "    clean - nuke all generated output"

env:
	virtualenv --python=`which $(PYTHON)` env
	@if [ -d vendor ]; then \
    	    ./env/bin/pip install -e .[tests] --find-links vendor/ ;\
	else \
    	    ./env/bin/pip install -e .[tests] ;\
	fi

test: env
	./env/bin/py.test tests --timeout=$(TEST_TIMEOUT)

test1: env
	./env/bin/py.test -x --ff tests --timeout=$(TEST_TIMEOUT)

shippabletest: env
	mkdir -p shippable/testresults shippable/codecoverage
	./env/bin/py.test \
	     --cov-report xml \
	     --cov=$(PROJ) \
	     --junitxml=shippable/testresults/pytest.xml tests
	mv coverage.xml shippable/codecoverage/

travistest: env
	./env/bin/py.test -v \
	     --cov-report xml \
	     --cov-report term \
	     --cov-report html \
	     --cov=$(PROJ) \
	     --junitxml=testresults.xml tests

clean:
	rm -rf env build dist *.egg *.egg-info 

package:
	$(PYTHON) setup.py bdist_wheel

deploy: package
	sudo pip install --upgrade `ls ./dist/*.whl | tail -1`

release:
	@if git tag | grep -q v`$(PYTHON) setup.py -V` ; then\
		echo "Already released this version.";\
		echo "Update the version number and try again.";\
		exit 1;\
	fi
	@if [ `git status --short | wc -l` != 0 ]; then\
		echo "Uncommited code. Aborting." ;\
		exit 1;\
	fi
	$(PYTHON) setup.py bdist_wheel
	git tag v`$(PYTHON) setup.py -V`
	git push
	git push --tags

.PHONY: default package deploy release clean 

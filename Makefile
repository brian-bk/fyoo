.PHONY: help clean dev docs package lint type-check test security-check

help:
	@echo "This project assumes that an active Python virtualenv is present."
	@echo "The following make targets are available:"
	@echo "	 dev 	install all deps for dev env"
	@echo "  docs	create pydocs for all relveant modules"
	@echo "	 test	run all tests with coverage"

clean:
	python setup.py clean --all

dev:
	if [ ! -d "venv" ]; then \
		echo "Making virtualenv at venv" ; \
		virtualenv -p python3 venv ; \
	fi
	./venv/bin/pip install -e .[all]
	echo "Activate with . venv/bin/activate"

docs:
	$(MAKE) -C docs html

package:
	python setup.py sdist
	python setup.py bdist_wheel

lint:
	pylint fyoo

test:
	coverage run -m pytest
	coverage html

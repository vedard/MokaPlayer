run:
	python3 mokaplayer.py --debug

release:
	python3 setup.py sdist

publish:
	python setup.py sdist upload -r pypi

format:
	autopep8 mokaplayer --recursive --in-place --pep8-passes 2000
	autoflake mokaplayer -i -r

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type f -name "*.ui~" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -wholename "*.egg-info/*" -delete
	find . -type d -name "*.egg-info" -delete

test:
	python3 -m unittest discover test "*_test.py"

report-pep8:
	mkdir -p reports/pep8
	pep8 mokaplayer | pepper8 > reports/pep8/index.html
	xdg-open reports/pep8/index.html

report-coverage:
	mkdir -p reports/coverage
	coverage run --source . -m unittest discover test "*_test.py"
	coverage html -d reports/coverage
	xdg-open reports/coverage/index.html

init:
	pip3 install -r requirements.txt -U
	pip3 install -r requirements-dev.txt -U

help:
	@echo ""
	@echo "init"
	@echo "    Download requirements"
	@echo "test"
	@echo "    Run all test"
	@echo "format"
	@echo "    Format all code with autopep8"
	@echo "report-coverage"
	@echo "    Generate a report (test coverage) with coverage"
	@echo "report-pep8"
	@echo "    Generate a report (syntax) with pep8 and pepper8"
	@echo "run"
	@echo "    Run the program"
	@echo "clean"
	@echo "    Remove python artifacts."

.PHONY: init test clean run help

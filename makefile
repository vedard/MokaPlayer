run:
	python3 application.py --debug

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type f -name "*.ui~" -delete
	find . -type d -name "__pycache__" -delete

test:
	python3 -m unittest discover test "*_test.py"

report-pep8:
	mkdir -p reports/pep8
	pep8 musicplayer | pepper8 > reports/pep8/index.html
	xdg-open reports/pep8/index.html

report-coverage:
	mkdir -p reports/coverage
	coverage run --source . -m unittest discover test "*_test.py"
	coverage html -d reports/coverage
	xdg-open reports/coverage/index.html

init:
	pip3 install -r requirements.txt
	pip3 install -r requirements-dev.txt

help:
	@echo ""
	@echo "init"
	@echo "    Download requirements"
	@echo "test"
	@echo "    Run all test"
	@echo "run"
	@echo "    Run the program"
	@echo "clean"
	@echo "    Remove python artifacts."

.PHONY: init test clean run help

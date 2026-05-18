CSV ?= $(HOME)/Downloads/testmo-export-run-2154.csv
REPO ?= $(HOME)/automation_web_2.0

.PHONY: generate clean open

generate: testmo_tests.json automated_tests.json mapping.json
	@echo "✅ Report ready! Open index.html in browser"

testmo_tests.json: parse_testmo_csv.py $(CSV)
	python3 parse_testmo_csv.py "$(CSV)"

automated_tests.json: extract_tests.py
	python3 extract_tests.py "$(REPO)"

mapping.json: build_mapping.py testmo_tests.json automated_tests.json
	python3 build_mapping.py

clean:
	rm -f testmo_tests.json automated_tests.json mapping.json

open: generate
	open index.html

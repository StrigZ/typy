.PHONY: run dev pot lint format

run:
	python3 usr/lib/uncom/typy/typy.py -g

dev:
	find usr/lib/uncom/typy -name "*.py" -o -name "*.css" | entr -r python3 usr/lib/uncom/typy/typy.py -g

pot:
	pygettext3 -d base -o po/base.pot usr/lib/uncom/typy/*.py
	msgmerge --update po/ru.po po/base.pot

lint:
	ruff check .

format:
	ruff format .
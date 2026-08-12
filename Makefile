.PHONY: run dev pot mo lint format

pot:
	pygettext3 -d base -o po/base.pot usr/lib/uncom/typy/*.py
	msgmerge --update po/ru.po po/base.pot

mo:
	mkdir -p usr/share/locale/ru/LC_MESSAGES
	msgfmt po/ru.po -o usr/share/locale/ru/LC_MESSAGES/typy.mo

dev: mo
	find usr/lib/uncom/typy -name "*.py" -o -name "*.css" | entr -r python3 usr/lib/uncom/typy/typy.py
run:
	python3 usr/lib/uncom/typy/typy.py

dev:
	find usr/lib/uncom/typy -name "*.py" -o -name "*.css" | entr -r python3 usr/lib/uncom/typy/typy.py

build:
	debuild -b -uc -us

install:
	sudo dpkg -r typy || true
	sudo dpkg -i ../typy_*.deb

reinstall: build install
	typy

words:
	python3 tools/convert_words.py

lint:
	ruff check .

format:
	ruff format .
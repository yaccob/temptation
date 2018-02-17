PACKAGE=temptation

VERSION=`python -c "import $(PACKAGE); print($(PACKAGE).__version__)"`

%PHONY: all clean test upload tag commit merge

all: test

README.rst: README.md
	pandoc -t rst $< -o $@

test:
	-pip uninstall -y $(PACKAGE)
	python -m unittest discover -v
	python -m doctest README.md
	scripts/temptation -t samples/helloworld1/helloworld.tpt samples/helloworld1/helloworld.yaml
	scripts/temptation -t samples/helloworld2/helloworld.tpt samples/helloworld2/helloworld.yaml
	@echo "TODO: implement and call tests"

install: test dist_source dist_binary
	python -m wheel install --force dist/$(PACKAGE)-$(VERSION)-py2-none-any.whl

dist_source: $(wildcard $(PACKAGE)/*.py) README.rst setup.py requirements.txt MANIFEST.in
	python setup.py sdist

dist_binary: $(wildcard $(PACKAGE)/*.py) README.rst setup.py requirements.txt MANIFEST.in
	python setup.py bdist_wheel

commit:
	-git commit -a -m "Committing for Version $(VERSION)"
	-git push

merge: commit
	git checkout master
	git merge development
	git checkout development

tag: commit
	git tag -a $(PACKAGE)-"v$(VERSION)" -m "$(PACKAGE) Version $(VERSION)"
	git push origin $(PACKAGE)-"v$(VERSION)"

upload: clean test dist_binary tag merge
	twine upload dist/*
	pip install --upgrade $(PACKAGE)

clean:
	for pattern in `cat .gitignore`; do find . -name "$$pattern" -exec rm -r {} +; done

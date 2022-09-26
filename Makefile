format:
	@isort nimphel
	@black nimphel

docs:
	mkdocs serve

docs_push:
	@mkdocs gh-deploy

.PHONY: format docs docs_push

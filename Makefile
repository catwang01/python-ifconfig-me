.PHONY: help test build publish

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Build the package
	rm -rf dist/
	poetry build

publish: ## Publish the package to PyPI with twine
	python3 -m twine upload --repository pypi dist/* --v

test: ## Run tests and linters
	poetry run tox -e
	poetry run tox -e coverage
	poetry run tox -e lint,type
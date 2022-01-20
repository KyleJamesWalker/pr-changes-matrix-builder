clean:
	@rm -rf reports/
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete

build:
	docker-compose build app test

test:
	docker-compose run --rm test

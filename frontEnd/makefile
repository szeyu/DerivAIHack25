commit:
	make pull
	@git add .
	@git commit -m "$(message)"
	@git push origin "$(branch)"

docker-build:
	docker build -t frontendtest -f frontEnd/Dockerfile .

docker-run-test:
	docker run -it frontendtest /bin/sh

docker-run:
	docker run frontendtest /bin/sh
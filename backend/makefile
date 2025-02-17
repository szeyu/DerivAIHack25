commit:
	make pull
	@git add .
	@git commit -m "$(message)"
	@git push origin "$(branch)"

pull:
	@git pull origin backend

docker-build:
	docker build -t backendtest -f backend/Dockerfile .

docker-run-test:
	docker run -it backendtest /bin/sh

docker-run:
	docker run backendtest /bin/sh
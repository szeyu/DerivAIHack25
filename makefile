commit:
	make pull
	@git add .
	@git commit -m "$(message)"
	@git push origin "$(branch)"

pull:
	@git pull origin backend

docker-build:
	docker compose up --build

docker-down:
	docker compose down

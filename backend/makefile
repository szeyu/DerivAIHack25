setup-windows:
	@python -m venv venv
	@.\venv\Scripts\activate
	@pip install -r requirements.txt
	@cp .env.example .env

setup-mac:
	@python3 -m venv venv
	@source venv/bin/activate
	@pip install -r requirements.txt
	@cp .env.example .env 

commit:
	@git add .
	@git commit -m "$(message)"
	@git push origin "$(branch)"
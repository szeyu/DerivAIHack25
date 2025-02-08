commit-jack-branch: 
	@git add .
	@git commit -m "$(message)"
	@git push origin jack-branch

update-main:
	@git pull origin main

first-commit:
	@git add .
	@git commit -m "$(message)"
	@git push --set-upstream origin "$(branch)"
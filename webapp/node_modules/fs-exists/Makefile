build:
	mkdir -p lib
	node_modules/.bin/coffee --compile -m --output lib/ src/

watch:
	node_modules/.bin/coffee --watch --compile --output lib/ src/
	
test:
	node_modules/.bin/mocha

jumpstart:
	curl -u 'meryn' https://api.github.com/user/repos -d '{"name":"fs-exists", "description":"Wraps fs.exists so callback is called with (err, result) instead of just (result).","private":false}'
	touch src/fs-exists.coffee
	git init
	git remote add origin git@github.com:meryn/fs-exists
	git add *
	git commit -m "jumpstart commit."
	git push -u origin master
	
.PHONY: test
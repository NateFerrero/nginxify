install:
	groupadd -f nginxify

	rm -rf /usr/bin/nginxify
	cp nginxify.py /usr/bin/nginxify
	chown root:nginxify /usr/bin/nginxify
	chmod g+x /usr/bin/nginxify

	@echo "Successfully installed! Try: nginxify"

uninstall:
	rm -rf /usr/bin/nginxify

	@echo "Successfully uninstalled!"

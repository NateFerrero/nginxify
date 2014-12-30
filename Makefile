install:
	groupadd -f nginxify
	make _install

install-mac-os-x:
	rm -rf /bin/nginxify
	cp nginxify.py /bin/nginxify
	mkdir -p /var/log/nginx
	@echo "Installed! Use: sudo python /bin/nginxify"

_install:
	rm -rf /bin/nginxify
	cp nginxify.py /bin/nginxify
	chown root:nginxify /bin/nginxify
	chmod g+x /bin/nginxify
	chmod +x /bin/nginxify

	rm -rf /usr/bin/nginxify
	cp usr.sh /usr/bin/nginxify
	chown root:nginxify /usr/bin/nginxify
	chmod g+x /usr/bin/nginxify
	chmod +x /usr/bin/nginxify

	mkdir -p /etc/nginx/sites-enabled

	@echo "Successfully installed! Try: nginxify"

uninstall:
	rm -rf /bin/nginxify
	rm -rf /usr/bin/nginxify

	@echo "Successfully uninstalled!"

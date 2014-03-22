#! /usr/bin/python2
# Author: Nate Ferrero
import os
import json
import glob

master = {}

all = ""

locblock = """
location {location} <<
  {type} {value};
>>"""

http_https = """
server <<
  listen 80;
  server_name {name};
  access_log  /var/log/nginx/{user}-{xname}-insecure-access.log;
  error_log   /var/log/nginx/{user}-{xname}-insecure-error.log;

  location / <<
    rewrite   ^ https://$http_host$request_uri? permanent;
  >>
>>"""

ssl_block = """
  ssl_certificate            {sslpath}{xname}.crt;
  ssl_certificate_key        {sslpath}{xname}.key;
  ssl_client_certificate     {sslpath}cacert.pem;
  ssl_verify_client          off;
  ssl_ciphers                EECDH+ECDSA+AESGCM:EECDH+aRSA+AESGCM:EECDH+ECDSA+SHA384:EECDH+ECDSA+SHA256:EECDH+aRSA+SHA384:EECDH+aRSA+SHA256:EECDH+aRSA+RC4:EECDH:EDH+aRSA:RC4:!aNULL:!eNULL:!LOW:!3DES:!MD5:!EXP:!PSK:!SRP:!DSS;
  ssl_prefer_server_ciphers  on;
  ssl_protocols              TLSv1 TLSv1.1 TLSv1.2;
  ssl_session_cache          shared:SSL:10m;
"""

block = """
server <<
  listen {listen};
  server_name {name};
  {ssl}

  client_max_body_size 1024M;
  index index.html;
  allow all;
  autoindex on;

  gzip               on;
  gzip_http_version  1.1;
  gzip_vary          on;
  gzip_comp_level    6;
  gzip_proxied       any;
  gzip_types         text/plain text/css application/json application/javascript application/x-javascript text/javascript text/xml application/xml application/rss+xml application/atom+xml application/rdf+xml;

  access_log         /var/log/nginx/{user}-{xname}-access.log;
  error_log          /var/log/nginx/{user}-{xname}-error.log;
  {locations}
>>"""

for path in glob.glob('/home/*/.nginx'):
  with open(path) as file:
    user = os.path.basename(os.path.dirname(path))
    print '[nginxify] Loading nginx config for user: {}'.format(user)
    print ' '

    domains = json.load(file)
    alnum = 'abcdefghijklmnopqrstuvwxyz0123456789-_'
    alnum += alnum.upper()

    for (name, conf) in domains.items():
      sub = {'name': name, 'user': user}
      sub['xname'] = ''.join([x if x in alnum else '-' for x in name])
      sub['sslpath'] = os.path.dirname(path) + '/.ssl/'

      # HTTPS: SSL is enabled
      if 'ssl' in conf:
        sub['listen'] = '443 ssl spdy'
        ssl = {
          'header': 'add_header  Alternate-Protocol 443:npn-spdy/3',
          'block': ssl_block.format(**sub)
        }
        sub['ssl'] = '  {header};\n{block}'.format(**ssl)

        sslcrt = '{sslpath}{xname}.crt'.format(**sub)
        sslkey = '{sslpath}{xname}.key'.format(**sub)
        sslpem = '{sslpath}cacert.pem'.format(**sub)

        failpath = None
	for sslf in [sslcrt, sslkey, sslpem]:
          if not os.path.exists(sslf):
            failpath = sslf
            break

        if failpath:
            print '[nginxify] SSL certificate must be present at ' + failpath
            print '           [FAIL] skipping ' + name
            print ' '
            continue

        all += http_https.format(**sub).replace('<<', '{').replace('>>', '}')

      # HTTP: No SSL
      else:
        sub['listen'] = '80'
        sub['ssl'] = ''

      # Handle locations
      sub['locations'] = ''
      for (location, value) in conf['paths'].items():
        loc = {
          'location': location,
        }

        # Static files
        if (isinstance(value, basestring)):
          loc['type'] = 'alias'
          loc['value'] = os.path.dirname(path) + '/' + value.replace('..', '.')
          if not loc['value'].endswith('/'):
            loc['value'] += '/'

        # Proxy to port
        elif (isinstance(value, integer)):
          loc['type'] = 'proxy_pass'
          loc['value'] = 'http://localhost:' + value

        # Invalid
        else:
          print '[error] invalid location format for: ' + location
          continue

        sub['locations'] += locblock.format(**loc)
        
      # Format block
      sub['locations'] = sub['locations'].replace('\n', '\n  ')
      all += '\n' + block.format(**sub).replace('<<', '{').replace('>>', '}')

      print '           ... done!'
      print ' '

print '[nginxify] Writing nginx configuration file'

with open('/etc/nginx/sites-enabled/nginxify.conf', 'w') as f:
  f.write(all)

print '           ... done!'
print ' '

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

  {config}
>>"""

error_block = """error_page {code} {value};
"""

generic_block = """{key} {value};
"""

proxy_upgrade_block = """
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "Upgrade";
"""

php_fpm_block = """
location ~ \.php$ <<
  try_files $uri =404;
  fastcgi_split_path_info ^(.+\.php)(/.+)$;
  # With php5-fpm:
  fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
  fastcgi_pass unix:/var/run/php5-fpm.sock;
  fastcgi_index index.php;
  include fastcgi_params;
>>"""

sphp_fpm_block = """
location ~ \.php$ <<
  try_files $uri =404;
  fastcgi_split_path_info ^(.+\.php)(/.+)$;
  # With php5-fpm:
  fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
  fastcgi_pass unix:/var/run/php5-fpm.sock;
  fastcgi_index index.php;
  include fastcgi_params;
  fastcgi_param  PHP_VALUE "auto_prepend_file=/usr/share/simplified-php/simplified.php \n auto_append_file=/usr/share/simplified-php/simplified.php";
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

if os.path.exists('/Users'):
  pattern = '/Users/*/.nginx'

elif os.path.exists('/home'):
  pattern = '/home/*/.nginx'

else:
  raise OSError('No suitable search path found')

for path in glob.glob(pattern):
  print path
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
          'config': ''
        }

        # Advanced configuration with {default: ..., 404: 'index.html'} etc.
        if isinstance(value, dict):
            setup = value
            value = setup['default']

            for key, val in setup.items():
               if key == 'default':
                   continue

               # Error pages
               try:
                   code = int(key)
                   if code > 200:
                       loc['config'] += error_block.format(code=code, value=val)
                   continue
               except:
                   pass

               # Try Files etc
               if isinstance(key, basestring):
                   loc['config'] += generic_block.format(key=key, value=val)

        # Static files
        if isinstance(value, basestring):
          loc['type'] = 'alias'
          loc['value'] = os.path.dirname(path) + '/' + value.replace('..', '.')
          if not loc['value'].endswith('/'):
            loc['value'] += '/'

        # Simple [type, value] configuration
        elif isinstance(value, list):
          if len(value) != 2:
            print '[error] List must contain 2 elements exactly'
            continue

          _type, root = value
          loc['type'] = _type
          loc['value'] = os.path.dirname(path) + '/' + root.replace('..', '.')
          if not loc['value'].endswith('/'):
            loc['value'] += '/'

          if loc['type'] == 'php':
            sub['locations'] += '\nroot {};'.format(loc['value'])
            sub['locations'] += '\nindex index.php index.html;'
            sub['locations'] += php_fpm_block

          elif loc['type'] == 'sphp':
            sub['locations'] += '\nroot {};'.format(loc['value'])
            sub['locations'] += '\nindex index.php index.html;'
            sub['locations'] += sphp_fpm_block

          else:
            print '[error] Invalid location type {}'.format(_type)

          continue

        # Proxy to port
        elif isinstance(value, int):
          loc['type'] = 'proxy_pass'
          loc['value'] = 'http://localhost:{}'.format(value)
          if location != '/':
             loc['config'] += generic_block.format(
               key="rewrite",
               value="^{}(.*)$ $1 break".format(location)
             )
          loc['config'] += proxy_upgrade_block

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

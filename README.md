nginxify
========

Nginxify parses JSON configurations of NGINX config files and creates the appropriate representations in configuration.

## Usage

#### Static

Static site path config has a string path relative to your home folder.

#### Proxy Pass

Proxy pass to a port with an integer port number as the path config.

#### PHP

PHP using [PHP-FPM](http://php-fpm.org/) is supported with the path config `["php", "path/to/project"]`.

#### SimplifiedPHP

[SimplifiedPHP](https://github.com/NateFerrero/simplified-php) using [PHP-FPM](http://php-fpm.org/) is supported with the path config `["sphp", "path/to/project"]`.

Create a file called `.nginx` in your home directory (/home/username), and populate according to the following JSON:

```js
{
  "my.domain.com": {
    "paths": {
      "/": "my_domain", // this is a directory relative to your home directory,
      "/testapp": 3000  // This will proxy all requests to a server running on port 3000
    }
  },
  "other.domain.com": {
    "paths": {
      "/foo": "another/folder/path"
    }
  },
  "another.domain.com": {
    "paths": {
      "/": ["sphp", "path/to/sphp-project"]
    }
  },
  "php.domain.com": {
    "paths": {
      "/": ["php", "path/to/php-project"]
    }
  }
}
```

Finally, when you have completed editing the configuration file, run the `nginxify` command! That's all.

## Installation - Mac OS X

```bash
git clone git@github.com:NateFerrero/nginxify.git
cd nginxify
sudo make install-mac-os-x
```

Then to run on Mac OS X, just execute the following command: `sudo python /bin/nginxify && sudo nginx -s reload`.

For PHP, be sure to fix permissions for /var/run socket.

## Installation - Linux

```bash
git clone git@github.com:NateFerrero/nginxify.git
cd nginxify
sudo make install
```

Then, add the following to /etc/sudoers using `visudo`:

```bash
# Nginxify
%nginxify ALL=NOPASSWD: /bin/nginxify, /etc/init.d/nginx reload
```


## Allowing Users to run `nginxify`

```bash
sudo usermod -a -G nginxify the_username
```

Keep in mind that the user will have to open a new shell to gain the new group permissions.

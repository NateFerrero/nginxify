nginxify
========

Nginxify parses JSON configurations of NGINX config files and creates the appropriate representations in configuration.

## Usage

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
  }
}
```

Finally, when you have completed editing the configuration file, run the `nginxify` command! That's all.

## Installation

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

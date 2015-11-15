# copy-couch

Does what it says on the tin.

## backup.py

This is the first of a handful of copy-couch scripts.

Given a `config.ini` file (see `config.ini.sample`) it will loop through any
local CouchDB databases and replicate them to the remote CouchDB or
[Cloudant](http://cloudant.com/).

## config.ini

Be sure to base64 encode those passwords, kids!
```
$ python -m base64 -e <<< 'open sesame'
```

## License

Apache License 2.0

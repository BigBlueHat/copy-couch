#!/usr/bin/env python

"""copy-couch makes copies of couches. no joke.

License: Apache 2.0 - http://opensource.org/licenses/Apache-2.0
"""

import argparse
import base64
import ConfigParser
import datetime
import json

import requests

argparser = argparse.ArgumentParser()
argparser.add_argument('config_file', type=file,
        help="Config INI file. See `config.sample.ini` for info.")
args = argparser.parse_args()

config = ConfigParser.RawConfigParser({
    'protocol': 143,
    'host': 'localhost:5984'
    })
config.readfp(args.config_file)

local_couch = config._sections['local']
local_couch['password'] = base64.b64decode(local_couch['password'])
local_url = local_couch['protocol'] + '://' + local_couch['host'] + '/'

remote_couch = config._sections['remote']
remote_couch['password'] = base64.b64decode(remote_couch['password'])
remote_url = remote_couch['protocol'] + '://' + remote_couch['host'] + '/'

# setup local db session
local_db = requests.Session()
local_db.auth = (local_couch['user'], local_couch['password'])

# setup remote db session
remote_db = requests.Session()
remote_db.auth = (remote_couch['user'], remote_couch['password'])

rv = local_db.get(local_url).json()
uuid = rv['uuid']

rv = local_db.get(local_url + '_all_dbs').json()
# TODO: make which DB's configurable
dbs = [db for db in rv if db[0] != '_']

# create & store one rep_doc per database
for db in dbs:
    # create _replicator docs for each DB on local; target remote
    rep_doc = {
        "_id": "backup~" + datetime.datetime.now().isoformat(),
        "source": local_url,
        "target": remote_couch['protocol'] + '://' \
            + remote_couch['user'] + ':' + remote_couch['password'] \
            + '@' + remote_couch['host'] + '/backup%2F' + uuid + '%2F',
        "create_target": True
    }

    rep_doc['source'] += db;
    rep_doc['target'] += db;

    # TODO: make the backup db name configurable / reusable
    print 'Copying ' + db
    print '  from: ' + local_url
    print '  to: ' + remote_url + 'backup%2F' + uuid + '%2F' + db

    rv = local_db.post(local_url + '_replicate', json=rep_doc, headers = {
        'Content-Type': 'application/json'})
    print rv.json()


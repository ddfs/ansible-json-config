# ansible-json-config
Json configuration using JsonPatch

# Requirements:
-- jsonpatch


```ansible
#
# No change
#
TASK [docker : debug] *********************************************************************************************************************************************************************************************
ok: [a.b.c.d] => {
    "msg": {
        "backup": true,
        "backup_file": null,
        "changed": false,
        "diff": "[]",
        "failed": false,
        "gid": 0,
        "group": "root",
        "mode": "0644",
        "msg": null,
        "owner": "root",
        "path": "/path/to/daemon.json",
        "size": 0,
        "state": "file",
        "uid": 0
    }
}


#
# On change
#
TASK [docker : debug] *********************************************************************************************************************************************************************************************
ok: [a.b.c.d] => {
    "msg": {
        "backup": true,
        "backup_file": "/path/to/daemon.json.bak",
        "changed": true,
        "diff": "[{\"path\": \"/foo\", \"value\": \"bar\", \"op\": \"add\"}, {\"path\": \"/baz\", \"value\": [42], \"op\": \"add\"}]",
        "failed": false,
        "gid": 0,
        "group": "root",
        "mode": "0644",
        "msg": null,
        "owner": "root",
        "path": "/path/to/daemon.json",
        "size": 54,
        "state": "file",
        "uid": 0
    }
}

```


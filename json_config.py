#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Fatih Piristine <fatihpiristine () gmail dot com>
# Apache Software License 2.0

import json
import os
import re
import jsonpointer
import jsonpatch
from shutil import copyfile

from ansible.module_utils.basic import AnsibleModule

def _doc_write(module, path, doc):
    changed = False
    try:
        fh = open(path, 'w')
        json.dump(doc, fh)
        fh.close()
        changed = True
    except Exception as e:
        module.fail_json(rc=257, msg=str(e))

    return changed


def _doc_read(module, path):
    doc = None
    try:
        fh = open(path, 'r')
        doc = json.load(fh)
        fh.close()
    except Exception as e:
        module.fail_json(rc=257, msg=str(e))
    return doc


def do_resolve_node(module, path, resolve):
    changed, message, node = None, False, None

    # ignore if not exists, exceptions
    if os.path.exists(path):
        try:
            doc = _doc_read(module, path)
            node, changed, message = jsonpointer.resolve_pointer(doc, resolve, None), True, 'Resolved.'
        except:
            pass

    return changed, message, node


def do_json_config(module, path, patch, backup=False, backup_file=None, create=True):
    config_doc, config_diff, changed, message = None, [], False, None

    if not os.path.exists(path):
        if not create:
            module.fail_json(rc=257, msg='File `%s` does not exist !' % path)

        # create file
        destpath = os.path.dirname(path)
        if not os.path.exists(destpath) and not module.check_mode:
            os.makedirs(destpath)
        changed, message = _doc_write(module, path, json.loads("{}")), 'JSON file created'

    # check file has content
    if os.stat(path).st_size == 0:
        changed, message = _doc_write(module, path, json.loads("{}")), 'JSON file initialized'

    config_doc = _doc_read(module, path)

    try:
        # make patch
        patch = jsonpatch.JsonPatch(patch)

        # apply patch
        config_new = patch.apply(config_doc)

        # make diff
        config_diff = jsonpatch.make_patch(config_doc, config_new)

        # no diff no changes
        if config_diff:
            if backup:
                backup_file = backup_file if backup_file else path + '.bak'
                copyfile(path, backup_file)

            changed = _doc_write(module,  path, config_new)
            message = 'JSON file updated'

        # convert diff to string
        config_diff = config_diff.to_string()

    # skip if test fails
    except jsonpatch.JsonPatchTestFailed:
        pass

    return changed, message, config_diff, backup_file


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True, aliases=['dest']),
            patch=dict(type='list'),
            resolve=dict(type='str'),
            backup=dict(type='bool', default=False),
            backup_file=dict(type='path', default=None),
            create=dict(type='bool', default=True)
        ),
        add_file_common_args=True,
        supports_check_mode=True,
    )

    path = module.params['path']
    patch = module.params['patch']
    resolve = module.params['resolve']
    create = module.params['create']
    backup = module.params['backup']
    backup_file = module.params['backup_file']
    changed, msg, diff, resolved = False, None, None, None

    if path and patch:
        changed, msg, diff, backup_file = do_json_config(module, path, patch,
                                                     backup=backup,
                                                     backup_file=backup_file,
                                                     create=create)
    elif path and resolve:
        changed, msg, resolved = do_resolve_node(module, path, resolve)

    if not module.check_mode and os.path.exists(path):
        file_args = module.load_file_common_arguments(module.params)
        changed = module.set_fs_attributes_if_different(file_args, changed)

    results = dict(
        changed=changed,
        msg=msg,
        path=path,
        backup=backup,
        backup_file=backup_file,
        diff=diff,
        resolve=resolved,
    )

    module.exit_json(**results)

if __name__ == '__main__':
    main()


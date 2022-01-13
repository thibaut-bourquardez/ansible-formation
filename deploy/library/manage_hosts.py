#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: manage_hosts

short_description: ajoutera les noms d'hôtes et adresses IP spécifiées pour la résolution de nom locale 
(fichiers /etc/hosts sous Linux et C:\Windows\System32\Drivers\etc\hosts sous Windows)

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''
import platform

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        entries=dict(type='list', default=[])
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    
    if len(module.params['entries']) == 0:
        result.message='No entries specified'
        module.exit_json(**result)

    if platform.system() == 'Windows':
        fileName = "C:\Windows\System32\Drivers\etc\hosts"
    else :
        fileName = "/etc/hosts"

    with open(fileName, "r") as filin:
        fileLines = filin.readlines()

    entries = list(module.params['entries'])
    finalFileLines = []
    changed=False
    for ligne in fileLines:
        innerChanged=False
        if ligne.startswith('#') == False :
            elements = ligne.split()
            if len(elements) > 0:
                ip = elements[0] 
                for entry in entries: 
                    if entry["ip"] == ip :
                        matchEntry = entry
                        break
                else :
                    matchEntry = None 
                if matchEntry != None :
                    entries.remove(matchEntry)
                    newLine = ligne.replace('\n', '')
                    for name in matchEntry["names"]: 
                        if newLine.find(name) == -1:
                            newLine = newLine + ' ' + name
                            innerChanged=True
                
        if innerChanged == True : 
            newLine = newLine + "\n"
            finalFileLines.append(newLine)
            changed=True
            result["message"] = result["message"] + '-Update Line ' + newLine
        else :
            finalFileLines.append(ligne)
    
    for entry in entries :
        newLine = entry['ip'] + " " + " ".join(entry["names"]) + "\n"
        finalFileLines.append(newLine)
        changed=True
        result["message"] = result["message"] + '-New Line ' + newLine

    result["changed"] = changed
        
    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    if changed == True : 
        with open(fileName, "w") as filout:
            for finalLine in finalFileLines : 
                filout.write(finalLine)

    
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
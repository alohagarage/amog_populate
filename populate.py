#! /usr/bin/env python

import sys, curses, os, requests, json

from curses_menu import cmenu

API_ENDPOINT = 'http://lriserver.com:6000'
ENTITY_TYPE = ''

def top():
    os.system("top")

def exit():
    sys.exit(1)

def get_things():

    query = {
        'urn:amog:property_type:ancestors': 'urn:amog:entity_type:thing'
    }

    r = requests.get(API_ENDPOINT + '/entity/search?q=' + json.dumps(query))

    response = json.loads(r.content)['response']
    
    return [r['props']['urn:amog:property_type:id'] for r in response]

def get_thing_properties():
    #print id
    pass

def menu(list):
    index = raw_input('\n'.join([(str(g[0]) + ' ' + g[1]) for g in enumerate(list)]) + '\n')
    return list[int(index)]

def main():
    all_things = get_things()

    thing = menu(all_things)

    print thing
    
    """
    all_things = get_things()

    try:
        c = cmenu([{id: get_thing_properties} for id in all_things])
        c.display()

    except SystemExit:
        pass

    else:
        c.cleanup()
    """


if __name__ == '__main__':
    main()

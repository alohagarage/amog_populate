#! /usr/bin/env python

import sys, curses, os, requests, json


from curses_menu import cmenu

API_ENDPOINT = 'http://lriserver.com:6000'
ENTITY_TYPE = ''


def get_things():

    query = { 'urn:amog:property_type:ancestors': 'urn:amog:entity_type:thing' }

    return get_ids(query)


def get_ids(query):

    r = requests.get(API_ENDPOINT + '/entity/search?q=' + json.dumps(query))

    response = json.loads(r.content)['response']
    
    return [r['props']['urn:amog:property_type:id'] for r in response]


def get_thing_properties(id):
    query = {
        'urn:amog:property_type:id': id
    }

    r = requests.get(API_ENDPOINT + '/entity/search?q=' + json.dumps(query))

    response = json.loads(r.content)['response']

    try:
        output = response[0]['props']['urn:amog:property_type:properties'] + response[0]['props']['urn:amog:property_type:specific_properties']
    except:
        output = response[0]['props']['urn:amog:property_type:properties']

    return output


def find_rels(type, string=None):
    query = {

        'urn:amog:property_type:types': 'urn:amog:entity_type:' + type

    }

    r = requests.get(API_ENDPOINT + '/entity/search?q=' + json.dumps(query))

    response = json.loads(r.content)['response']
    
    if string:
        output = [r['props']['urn:amog:property_type:id'] for r in response if string in r['props']['urn:amog:property_type:id']]
    else:
        output = [r['props']['urn:amog:property_type:id'] for r in response]

    return output


def menu(list):
    index = raw_input('\n'.join([(str(g[0]) + ' ' + g[1]) for g in enumerate(list)]) + '\n')
    try:
        return list[int(index)]
    except Exception:
        return ''


def main():
    query = {}

    all_things = get_things()

    thing = menu(all_things)

    uuid = raw_input("WHAT'S THE ID? ")

    query['urn:amog:property_type:types'] = thing

    query['urn:amog:property_type:id'] = uuid

    all_props = get_thing_properties(thing)

    while True:

        prop = menu(all_props)

        if prop:
            val = raw_input(prop + ' --> ')

            if '!!' in val:

                split_val = val.split(' ')

                if split_val[2]:

                    val = menu(find_rels(split_val[1], split_val[2]))

                else:

                    val = menu(find_rels(split_val[1]))


            query[prop] = val
            
        else:

            break

    print json.dumps(query)


if __name__ == '__main__':
    main()

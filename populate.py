#! /usr/bin/env python

import sys, curses, os, requests, json, curses, traceback, string


from curses_menu import cmenu

API_ENDPOINT = 'http://lriserver.com:6000'
ENTITY_TYPE = ''

hotkey_attr = curses.A_BOLD | curses.A_UNDERLINE
menu_attr = curses.A_NORMAL

#-- Define default conversion dictionary
query_dict = {'target': 'DEFAULT.HTML',
            'source': 'txt2html.txt',
            'type':   'INFER',
            'proxy':  'NONE' }


EXIT = 0
CONTINUE = 1

screen = None

def topbar_menu(menus):
    left = 2
    for menu in menus:
        menu_name = menu[0]
        menu_hotkey = menu_name[0]
        menu_no_hot = menu_name[1:]
        screen.addstr(1, left, menu_hotkey, hotkey_attr)
        screen.addstr(1, left + 1, menu_no_hot, menu_attr)
        left = left + len(menu_name) + 3

        topbar_key_handler((string.upper(menu_hotkey), menu[1]))
        topbar_key_handler((string.lower(menu_hotkey), menu[1]))

    screen.addstr(1, left - 1, "AMOG POPULATE", curses.A_STANDOUT)

    screen.refresh()

def topbar_key_handler(key_assign=None, key_dict={}):
    if key_assign:
        key_dict[ord(key_assign[0])] = key_assign[1]
    else:
        c = screen.getch()
        if c in (curses.KEY_END, ord('!')):
            return 0
        elif c not in key_dict.keys():
            curses.beep()
            return 1
        else:
            return eval(key_dict[c])

def help_func():
    help_lines = []
    offset = 0
    s = curses.newwin(19, 77, 3, 1)
    fh_help = open('amog_populate_help.txt')
    for line in fh_help.readlines():
        help_lines.append(string.rstrip(line))
    s.box()
    num_lines = len(help_lines)
    end = 0
    while not end:
        for i in range(1,18):
            if i+offset < num_lines:
                line = string.ljust(help_lines[i+offset],74)[:74]
            else:
                line = " "*74
                end = 1
            if i<3 and offset>0: s.addstr(i, 2, line, curses.A_BOLD)
            else: s.addstr(i, 2, line, curses.A_NORMAL)
        s.refresh()
        c = s.getch()
        offset = offset+15
    s.erase()
    return CONTINUE

def thing_func():
    help_lines = []
    offset = 0
    s = curses.newwin(19, 77, 3, 1)
    s.box()
    ckey = None
    while ckey != ord('q'):
        ckey = s.getch()
        s.refresh()

    s.erase()

    return CONTINUE


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


def menu(list_list):
    """
    index = raw_input('\n'.join([(str(g[0]) + ' ' + g[1]) for g in enumerate(list)]) + '\n')
    try:
        return list[int(index)]
    except Exception:
        return ''
    """
    c = cmenu([{l: l} for l in list_list])

    c.display()
    
    print c.pos

    print list_list
    
    index = c.pos

    del c

    return list_list[index]

def draw_dict():
    for i in range(len(query_dict.keys())):
        key = query_dict.keys()[i]
        whitespace = 27 - len(key)
        screen.addstr(5 + (i * 3),33, " "*43, curses.A_NORMAL)
        screen.addstr(5 + (i * 3), 4, " "*whitespace + key, curses.A_BOLD)
        screen.addstr(5 + (i * 3), 33, query_dict[key], curses.A_STANDOUT)
        #screen.addstr(17,33, str(counter), curses.A_STANDOUT)
    screen.refresh()

def main(stdscr):
    global screen
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE, 77)
    screen.refresh()

    # Define the topbar menus
    help_menu = ("Help", "help_func()")
    thing_menu = ("Type", "thing_func()")
    exit_menu = ("Exit", "EXIT")

    # Add the topbar menus to screen object
    topbar_menu((help_menu, thing_menu, exit_menu))

    # Draw the onscreen field titles
    """
    screen.addstr(5, 4, "           Source of Input:", curses.A_BOLD)
    screen.addstr(8, 4, "        Output Destination:", curses.A_BOLD)
    screen.addstr(11, 4,"           Conversion Type:", curses.A_BOLD)
    screen.addstr(14, 4,"                Proxy Mode:", curses.A_BOLD)
    screen.addstr(17, 4,"Conversions during Session:", curses.A_BOLD)
    """
    screen.addstr(1, 77, "", curses.A_STANDOUT)
    draw_dict()

    # Enter the topbar menu loop
    while topbar_key_handler():
        draw_dict()

    """
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
    """


if __name__ == '__main__':
    try:
        # Initialize curses
        stdscr=curses.initscr()
        #curses.start_color()
        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho() ; curses.cbreak()

        # In keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        stdscr.keypad(1)
        main(stdscr)                    # Enter the main loop
        # Set everything back to normal
        stdscr.keypad(0)
        curses.echo() ; curses.nocbreak()
        curses.endwin()                 # Terminate curses
    except:
        # In the event of an error, restore the terminal
        # to a sane state.
        stdscr.keypad(0)
        curses.echo() ; curses.nocbreak()
        curses.endwin()
        traceback.print_exc()           # Print the exception

    


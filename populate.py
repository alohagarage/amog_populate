#! /usr/bin/env python

import sys, curses, os, requests, json, curses, traceback, string, yaml

import time


from curses_menu import cmenu

API_ENDPOINT = 'http://lriserver.com:6000'
ENTITY_TYPE = ''

hotkey_attr = curses.A_BOLD | curses.A_UNDERLINE
menu_attr = curses.A_NORMAL

#-- Define default conversion dictionary
query_dict = {
        'urn:amog:property_type:types': '?',
        'urn:amog:property_type:id': '?'
    }


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

def simple_menu(screen, array, title, subtitle):

    #TODO Functionality to enter index directly


    screen.clear()

    screen.addstr(2, 2, title, curses.A_STANDOUT | curses.A_BOLD)
    #screen.addstr(4, 2, subtitle, curses.A_BOLD)

    pos = 0

    ckey = None
    
    while ckey != ord('\n'):
        for n in range(0, len(array)):

            option = array[n]

            try:
                if n != pos:
                    screen.addstr(3 + n, 4, "%d. %s" % (n, option), curses.A_NORMAL) 
                else:
                    screen.addstr(3 + n, 4, "%d. %s" % (n, option), curses.color_pair(1)) 
            except:
                pass

        screen.refresh()

        ckey = screen.getch()

        if ckey == ord('j'):
            if pos == (len(array) - 1):
                pos = 0
            else:
                pos += 1

        elif ckey == ord('k'):
            if pos <= 0:
                pos = len(array) - 1
            else:
                pos -= 1
        else:
            break

    return array[pos]

def relationship_menu():
    pass

def help_func():
    help_lines = []
    offset = 0
    s = curses.newwin(max_screen_size[0] - 4,  max_screen_size[1] - 32, 3, 1)
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

    title = "New Entry Type"

    subtitle = "What sort of thing are you adding here?"

    s = curses.newwin(max_screen_size[0] - 4,  max_screen_size[1] - 32, 3, 1)

    s.box()

    query_type = simple_menu(s, get_things(), title, subtitle)

    query_dict['urn:amog:property_type:types'] = query_type

    s.erase()

    return CONTINUE

def is_simple_property(property_type):

    query = {
        'urn:amog:property_type:id': property_type
    }

    r = requests.get(API_ENDPOINT + '/entity/search?q=' + json.dumps(query))

    response = json.loads(r.content)['response']

    try:
        return 'data_type' in response[0]['props']['urn:amog:property_type:ranges']
    except:
        return True

def property_func():

    title = "New Property on Entity"

    subtitle = "What properties does the entity have"

    s = curses.newwin(max_screen_size[0] - 4,  max_screen_size[1] - 32, 3, 1)

    s.box()

    property_type = simple_menu(s, get_thing_properties(query_dict['urn:amog:property_type:types']), title, subtitle)

    s.clear()

    s.box()

    s.refresh()

    if is_simple_property(property_type):

        curses.echo()

        s.addstr(5,4, property_type, curses.A_NORMAL)
        s.addstr(5,33, " "*43, curses.A_UNDERLINE)

        value = s.getstr(5,33)

        curses.noecho()

        s.erase()

    else:

        curses.echo()

        s.addstr(5,4, "What type of entity would you like to connect?", curses.A_NORMAL)
        s.addstr(6,33, " "*43, curses.A_UNDERLINE)

        type_to_connect = s.getstr(6,33)

        curses.noecho()

        value = simple_menu(s, find_rels(type_to_connect), "Which of these would you like to connect?", "")


        s.erase()

    query_dict[property_type] = value

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

    c = cmenu([{l: l} for l in list_list])

    c.display()
    
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

def load_to_amog(query):
    pass

def write_to_yaml(query, filename):
    #If filename exists, add
    # Else, start

    if filename in os.listdir('.'):
        f = open(filename, 'a')
    else:
        f = open(filename, 'w')

    query_container = {"action": "entity/create", "opts": { "access_token": "letmein" }, "q": query }
    full_query = {"STEP_" + str(time.time()): query_container}

    f.write(yaml.safe_dump(full_query, default_flow_style=False))


def main(stdscr):
    global screen
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    screen = stdscr.subwin(max_screen_size[0], max_screen_size[1] - 30, 0, 0)
    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE,  max_screen_size[1] - 32)
    screen.refresh()

    # Define the topbar menus
    help_menu = ("Help", "help_func()")
    thing_menu = ("Type", "thing_func()")
    property_menu = ("Property", "property_func()")
    exit_menu = ("Exit", "EXIT")

    # Add the topbar menus to screen object
    topbar_menu((help_menu, thing_menu, property_menu, exit_menu))

    screen.addstr(1, 77, "", curses.A_STANDOUT)
    draw_dict()

    # Enter the topbar menu loop
    while topbar_key_handler():
        draw_dict()

    print query_dict

    write_to_yaml( query_dict, 'test.yaml')



if __name__ == '__main__':
    try:
        # Initialize curses

        stdscr=curses.initscr()

        global max_screen_size

        max_screen_size = stdscr.getmaxyx()

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

    


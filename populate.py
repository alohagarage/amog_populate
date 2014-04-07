#! /usr/bin/env python

import sys, curses, os, requests, json
import curses, traceback, string, yaml
import copy

import time

import logging


from curses_menu import cmenu

API_ENDPOINT = 'http://lriserver.com:6000'
ENTITY_TYPE = ''

hotkey_attr = curses.A_BOLD | curses.A_UNDERLINE
menu_attr = curses.A_NORMAL

logging.basicConfig(filename='amog_populate.log',level=logging.DEBUG)

#-- Define default conversion dictionary




class AmogPopulate(object):

    def __init__(self, stdscr):
        self.screen = None

        self.EXIT = 0
        self.CONTINUE = 1

        self.DEFAULT_QUERY = {
                'urn:amog:property_type:types': '?',
                'urn:amog:property_type:id': '?'
            }

        self.query_dict = copy.copy(self.DEFAULT_QUERY)

        self.max_screen_size = stdscr.getmaxyx()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)

        self.screen = stdscr.subwin(self.max_screen_size[0], self.max_screen_size[1] - 30, 0, 0)
        self.screen.box()
        self.screen.hline(2, 1, curses.ACS_HLINE,  self.max_screen_size[1] - 32)
        self.screen.refresh()

        if len(sys.argv) > 1:

            self.yaml_destination = sys.argv[1]

        else:

            self.yaml_destination = "amog_populate" + time.strftime('%m%d%H%M') + ".yaml"

        # Define the topbar menus
        help_menu = ("Help", "self.help_func()")
        thing_menu = ("Type", "self.thing_func()")
        property_menu = ("Property", "self.property_func()")
        submit_menu = ("Submit", "self.load_to_amog()")
        exit_menu = ("Exit", "self.EXIT")

        # Add the topbar menus to screen object
        self.topbar_menu((help_menu, thing_menu, property_menu, submit_menu, exit_menu))

        self.screen.addstr(1, 77, "", curses.A_STANDOUT)

        self.draw_dict()

        # Enter the topbar menu loop
        while self.topbar_key_handler():
            self.draw_dict()


    def topbar_menu(self, menus):

        left = 2

        for menu in menus:
            menu_name = menu[0]
            menu_hotkey = menu_name[0]
            menu_no_hot = menu_name[1:]

            self.screen.addstr(1, left, menu_hotkey, hotkey_attr)
            self.screen.addstr(1, left + 1, menu_no_hot, menu_attr)

            left = left + len(menu_name) + 3

            self.topbar_key_handler((string.upper(menu_hotkey), menu[1]))
            self.topbar_key_handler((string.lower(menu_hotkey), menu[1]))

        self.screen.addstr(1, left - 1, "AMOG POPULATE", curses.A_STANDOUT)

        self.screen.refresh()


    def topbar_key_handler(self, key_assign=None, key_dict={}):
        if key_assign:
            key_dict[ord(key_assign[0])] = key_assign[1]
        else:
            c = self.screen.getch()
            if c in (curses.KEY_END, ord('!')):
                return 0
            elif c not in key_dict.keys():
                curses.beep()
                return 1
            else:
                return eval(key_dict[c])

    def simple_menu(self, array, title):

        #TODO Functionality to enter index directly

        s = curses.newwin(self.max_screen_size[0] - 4,  self.max_screen_size[1] - 32, 3, 1)

        s.box()


        s.addstr(2, 2, title, curses.A_STANDOUT | curses.A_BOLD)

        pos = 0

        ckey = None

        #array.sort(reverse=True)
        array.sort()
        
        while ckey != ord('\n'):
            for n in range(0, len(array)):

                option = array[n]

                try:
                    if n != pos:
                        s.addstr(3 + n, 4, "%d. %s" % (n, option), curses.A_NORMAL) 
                    else:
                        s.addstr(3 + n, 4, "%d. %s" % (n, option), curses.color_pair(1)) 
                except:
                    pass

            s.refresh()

            ckey = self.screen.getch()

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

        s.erase()

        return array[pos]


    def help_func(self):
        help_lines = []
        offset = 0
        s = curses.newwin(self.max_screen_size[0] - 4,  self.max_screen_size[1] - 32, 3, 1)
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
        return self.CONTINUE

    def thing_func(self):
        
        logging.info("STARTING THING FUNC")

        title = "New Entry Type"

        query_type = self.simple_menu(self.get_things(), title)

        self.query_dict['urn:amog:property_type:types'] = query_type

        return self.CONTINUE


    def is_property_rel(self,property_type):

        query = {
            'urn:amog:property_type:id': property_type
        }

        r = requests.get(API_ENDPOINT + '/entity/search?q=' + json.dumps(query))

        response = json.loads(r.content)['response']

        ranges = response[0]['props']['urn:amog:property_type:ranges']

        logging.debug("ranges")
        logging.debug(ranges)

        if 'data_type' in ranges:

            return None

        else:

            return ranges




    def property_func(self):

        title = "New Property on Entity"

        property_type = self.simple_menu(self.get_thing_properties(self.query_dict['urn:amog:property_type:types']), title)

        prop = self.is_property_rel(property_type)

        logging.info("RETURNED FROM RANGE CALL")

        logging.info(prop)

        if not prop:

            curses.echo()

            s = curses.newwin(self.max_screen_size[0] - 4,  self.max_screen_size[1] - 32, 3, 1)

            s.box()

            s.addstr(5,4, property_type, curses.A_NORMAL)
            s.addstr(5,33, " "*43, curses.A_UNDERLINE)

            value = s.getstr(5,33)

            curses.noecho()

            s.erase()

        else:

            value = self.simple_menu(self.find_rels(prop), "Which of these would you like to connect?")

        if not value.rstrip():
            del self.query_dict[property_type]

        else:
            self.query_dict[property_type] = value

        return self.CONTINUE


    def get_things(self):

        query = { 'urn:amog:property_type:ancestors': 'urn:amog:entity_type:thing' }

        return self.get_ids(query)


    def get_ids(self, query):

        r = requests.get(API_ENDPOINT + '/entity/search?q=' + json.dumps(query))

        response = json.loads(r.content)['response']
        
        return [r['props']['urn:amog:property_type:id'] for r in response]


    def get_thing_properties(self, id):
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


    def find_rels(self, type, string=None):
        query = {

            'urn:amog:property_type:types': type

        }

        r = requests.get(API_ENDPOINT + '/entity/search?q=' + json.dumps(query))

        response = json.loads(r.content)['response']
        
        if string:
            output = [r['props']['urn:amog:property_type:id'] for r in response if string in r['props']['urn:amog:property_type:id']]
        else:
            output = [r['props']['urn:amog:property_type:id'] for r in response]

        return output



    def draw_dict(self):

        for l in range((self.max_screen_size[0] - 10)):

            self.screen.addstr(( 5 + l) , 4, " " * (self.max_screen_size[1] - 44), curses.A_NORMAL)

        self.screen.refresh()

        for i in range(len(self.query_dict.keys())):

            key = self.query_dict.keys()[i]

            string = key + ' -- ' + self.query_dict[key]

            whitespace = " " * (self.max_screen_size[1] - len(string) - 44)

            self.screen.addstr(5 + (i * 3), 4, string + whitespace, curses.A_BOLD)

        self.screen.refresh()


    def load_to_amog(self):
        opts = {'access_token': 'letmein'}
        r = requests.get(API_ENDPOINT + '/entity/create?q=' + json.dumps(self.query_dict) + '&opts=' + json.dumps(opts))

        if r.status_code == 200:
            message = "SUCCESS!"
        else:
            message = "FAILURE\n" + json.dumps(self.query_dict) + "\nFAILED with error:\n" + r.content

        s = curses.newwin(self.max_screen_size[0] - 4,  self.max_screen_size[1] - 32, 3, 1)

        s.box()

        s.addstr(5, 5, message, curses.A_BOLD)

        ckey = None

        while ckey != ord('\n'):
            ckey = s.getch()

        self.write_to_yaml( self.query_dict, self.yaml_destination)

        self.query_dict = self.DEFAULT_QUERY

        return self.CONTINUE

    def write_to_yaml(self, query, filename):
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

    am = AmogPopulate(stdscr)


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

    


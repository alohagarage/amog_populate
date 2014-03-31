#! /usr/bin/env python

import sys, curses, os

from curses_menu import cmenu

def top():
    os.system("top")

def exit():
    sys.exit(1)

def main():

    try:
        c = cmenu([
            { "Top": top },
            { "Exit": exit },
            ])
        c.display()

    except SystemExit:
        pass
    else:
        c.cleanup()


if __name__ == '__main__':
    main()

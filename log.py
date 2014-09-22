#!/usr/bin/env python


def log(*args):
    msg = ''

    for arg in args:
        msg += str(arg)

    with open('giton.log', 'a') as file:
        file.write(msg + '\n')

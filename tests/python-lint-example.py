# -*- coding: utf-8 -*-

"""Example python code with deliberate quality issues

Used to test the flake8 gitlab-ci template
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

def my_function(a):
    return a ** 2


def complicated(a):
    if a > 4:
        if a > 10:
            return "too large"
        if a > 6:
            return "a bit too big"
        else:
            return a
    if a == 3:
        return False
    if a:
        return True
    else:
        return None


print(my_function( 4 ))

#!/usr/bin/env python
# encoding: utf-8
from user import *
from todo import *


def all():
    result = []
    models = [user, todo]

    for m in models:
        result += m.__all__

    return result

__all__ = all()

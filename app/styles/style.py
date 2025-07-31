#!/usr/bin/env python

from app.helper import HasID

class Style(HasID[str]):

    def __init__(self, name: str, prefix: str):
        HasID[str].__init__(self, name, prefix)

    @property
    def name(self) -> str:
        return self.id

class Greige(Style):

    def __init__(self, name: str):
        Style.__init__(self, name, 'GREIGE STYLE')
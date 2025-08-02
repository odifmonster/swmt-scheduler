#!/usr/bin/env python

from app.support import HasID

class Style(HasID[str]):

    def __init__(self, id, prefix):
        super().__init__(id, prefix)
    
    @property
    def name(self):
        return self.id
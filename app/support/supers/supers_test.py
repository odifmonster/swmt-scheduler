#!/usr/bin/env python

import unittest

from math import sqrt
from immutable import ArgTup, SuperImmut
from view import setter_like, SuperView

def subclass_immut(attrs: ArgTup = tuple(), priv_attrs: ArgTup = tuple(),
                   frozen: ArgTup | None = None) -> type[SuperImmut]:
    
    class SubImmut(SuperImmut, attrs=attrs, priv_attrs=priv_attrs, frozen=frozen):
        pass

    return SubImmut

class TestSuperImmut(unittest.TestCase):

    def test_public_frozen_check(self):
        raises_err = lambda: subclass_immut(attrs=('x','y'), frozen=('x','z'))
        self.assertRaises(ValueError, raises_err)
    
    def test_private_frozen_check(self):
        raises_err = lambda: subclass_immut(priv_attrs=('x','y'),
                                            frozen=('_SubImmut__x','_SubImmut__z'))
        self.assertRaises(ValueError, raises_err)

    def test_no_dynamic_attrs(self):
        NewImmut = subclass_immut(attrs=('name','x','y'), frozen=tuple())
        
        with self.assertRaises(AttributeError) as cm:
            var = NewImmut(name='var', x=10, y=15, z=3)
        
        err_msg = 'Type \'SubImmut\' has no public attribute \'z\'.'
        self.assertEqual(str(cm.exception), err_msg)

        with self.assertRaises(AttributeError) as cm:
            var = NewImmut(name='var', x=10, y=15)
            var.z = 3
        
        err_msg = 'Type \'SubImmut\' has no attribute \'z\'.'
        self.assertEqual(str(cm.exception), err_msg)
    
    def test_frozen_attrs(self):
        NewImmut = subclass_immut(attrs=('name','x','y'), frozen=('name',))

        with self.assertRaises(AttributeError) as cm:
            var = NewImmut(name='var', x=10, y=5)
            var.x /= 2
            var.y *= 3
            var.name = 'new_var'
        
        err_msg = 'Attribute \'name\' of type \'SubImmut\' is immutable.'
        self.assertEqual(str(cm.exception), err_msg)
    
    def test_private_vars(self):

        class HasPrivate(SuperImmut, priv_attrs=('id','prefix')):
            __id: int
            __prefix: str

            def __eq__(self, value: 'HasPrivate'):
                return self.__id == value.__id and self.__prefix == value.__prefix
        
        var1 = HasPrivate(priv={'id': 10, 'prefix': 'var'})
        var2 = HasPrivate(priv={'id': 10, 'prefix': 'var'})
        var3 = HasPrivate(priv={'id': 11, 'prefix': 'var'})

        self.assertEqual(var1, var2)
        self.assertNotEqual(var1, var3)
    
    def test_with_props(self):

        class Data(SuperImmut, attrs=('label','coords'), priv_attrs=('x','y'), frozen=tuple()):

            def __init__(self, x: int, y: int):
                super().__init__(priv={'x': x, 'y': y})
            
            @property
            def label(self):
                return 'Data'
            
            @property
            def coords(self):
                return (self.__x, self.__y)
            @coords.setter
            def coords(self, new: tuple[int, int]):
                self.__x = new[0]
                self.__y = new[1]

        var = Data(5, 6)

        with self.assertRaises(AttributeError) as cm:
            var.label = 'Data2'
        
        self.assertNotEqual(var.label, 'Data2')
        fullname = var.__class__.__qualname__
        self.assertEqual(str(cm.exception), f'property \'label\' of \'{fullname}\' object has no setter')
        self.assertEqual(var.coords, (5,6))
        var.coords = (1, 2)
        self.assertEqual(var.coords, (1,2))

class Data:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __eq__(self, other: 'Data'):
        return self.x == other.x and self.y == other.y
    
    def added(self):
        return self.x + self.y
    
    def norm(self):
        return sqrt(self.x**2 + self.y**2)
    
    @setter_like
    def make_square(self, newnorm: float):
        self.x = sqrt((newnorm**2)/2)
        self.y = self.y

_dat = {
    'funcs': ['added','norm','make_square'],
    'dunders': ['eq'],
    'attrs': ['x','y']
}

class DataView(SuperView[Data], funcs=_dat['funcs'], dunders=_dat['dunders'],
               attrs=_dat['attrs'], vfuncs=['size'], vdunds=['len'],
               vattrs=['length']):
    
    def __init__(self, link: Data, length: int):
        super().__init__(link)
        self.length = length
    
    def __len__(self):
        return self.length
    
    def size(self):
        return self.length
    
class TestSuperView(unittest.TestCase):

    def setUp(self):
        self.data1 = Data(1, 2)
        self.data2 = Data(2, 3)
        self.dview1 = DataView(self.data1, 3)
        self.dview2 = DataView(self.data2, 5)

    def test_setlike_call(self):
        with self.assertRaises(TypeError) as cm:
            self.dview1.make_square(2)
        
        self.assertEqual(str(cm.exception), 'Objects of type \'DataView\' cannot call methods that mutate the objects they view.')
    
    def test_view_set(self):
        with self.assertRaises(AttributeError) as cm:
            self.dview1.length = 7
            self.dview1.x = 7
        
        self.assertEqual(self.dview1.length, 7)
        self.assertNotEqual(self.data1.x, 7)
        self.assertEqual(str(cm.exception), '\'x\' is a viewed attribute on another object.')

        with self.assertRaises(AttributeError) as cm:
            self.dview1.z = -1
        
        self.assertEqual(str(cm.exception), 'Type \'DataView\' has no attribute \'z\'.')
    
    def test_method_set(self):
        with self.assertRaises(AttributeError) as cm:
            self.dview1.added = lambda: 0
        
        self.assertEqual(str(cm.exception), '\'added\' is bound to a method and cannot be reassigned.')
    
    def test_viewed_attrs(self):
        self.data1.x = 6
        self.data1.y = 10
        self.data2.x = 3
        self.data2.y = 3

        self.assertEqual(self.dview1.x, 6)
        self.assertEqual(self.dview1.y, 10)
        self.assertEqual(self.dview2.x, 3)
        self.assertEqual(self.dview2.y, 3)
    
    def test_viewed_methods(self):
        self.assertEqual(self.data1, self.dview1)
        self.assertEqual(self.dview1.added(), 3)
        self.data1.x = 3
        self.data1.y = 4
        self.assertEqual(self.dview1.added(), 7)

if __name__ == '__main__':
    unittest.main()
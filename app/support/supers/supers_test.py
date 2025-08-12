#!/usr/bin/env python

import unittest

from immutable import ArgTup, SuperImmut

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

if __name__ == '__main__':
    unittest.main()
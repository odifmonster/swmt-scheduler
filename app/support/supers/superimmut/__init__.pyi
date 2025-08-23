class SuperImmut:
    """
    A super class for creating types with "immutable" attributes. Subclassing from SuperImmut
    allows you to declare certain attributes as "frozen", and these cannot be re-assigned after
    initialization.
    """
    def __init_subclass__(cls, attrs: tuple[str, ...] = tuple(),
                          priv_attrs: tuple[str, ...] = tuple(),
                          frozen: tuple[str, ...] = tuple()) -> None:
        """
        Initialize a new subclass of SuperImmut.

            attrs:
              The non-mangled attributes of the class.
            priv_attrs:
              The attributes whose names should be mangled to act as "private" variables.
            frozen:
              The attributes to freeze. Private attributes can be marked with a preceding '*', and the
              following string will be mangled. A ValueError is raised if 'frozen' contains names not
              declared in 'attrs' or 'priv_attrs'.
        """
        ...
    def __init__(self, priv: dict[str] = {}, **kwargs) -> None:
        """
        Initialize a new SuperImmut object.

            priv: (default {})
              A mapping from un-mangled private variable names to their values.
            **kwargs:
              Every keyword should be an attribute provided to the subclass initializer. The values are
              the corresponding values of those attributes.
        
        Raises an error if any names in 'priv' or any keywords do not correspond to attributes declared
        via the subclass initializer.
        """
        ...
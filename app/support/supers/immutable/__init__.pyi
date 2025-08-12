from typing import Any, Unpack

type ArgTup = tuple[str, ...]

class SuperImmut:
    """
    A class for partly immutable types. Subclassing from SuperImmut prevents you from dynamically
    adding class or instance attributes and allows you to "freeze" certain attributes after
    initializing new instances.
    """
    def __init_subclass__(cls, attrs: ArgTup = tuple(), priv_attrs: ArgTup = tuple(),
                          frozen: ArgTup | None = None) -> None:
        """
        Create a new partly immutable type. No new attributes can be added outside of what is
        defined in 'attrs' and 'priv_attrs'.

            attrs:
              The publicly-accessible attributes of this type.
            priv_attrs:
              The privately-accessible attributes of this type. The names are mangled for you,
              and will be accessible within the class body as self.__<name>.
            frozen (opt):
              The attributes to freeze after initializing. If no argument is given, it will
              freeze all attributes.
        """
        ...
    def __init__(self, priv: dict[str, Any] = {}, **kwargs: Unpack[dict[str, Any]]) -> None:
        """
        Initialize a new partly immutable object.

            priv:
              A dictionary mapping unmangled private names to their values.
            **kwargs:
              A series of attr=val assignments for publicly accessible attributes.
        """
        ...
    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set the attributes of this object. Any 'name' which was defined as frozen or which was not
        provided in the subclass definition will result in an AttributeError.
        """
        ...
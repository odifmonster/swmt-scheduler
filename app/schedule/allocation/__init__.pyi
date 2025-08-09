from app.support import HasID

class Allocation(HasID[int]):
    """
    A class for Allocation objects. The unique id is automatically incremented upon
    initialization. Allows allocation of one roll to multiple dye lots. Immutable
    after initialization.
    """
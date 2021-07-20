class FinalMeta(type):
    """
    Overview:
        A meta class for making one class be final (unable to be extended by other classes)
    """

    def __new__(mcs, name, bases, attrs):
        """
        Overview:
            Creation process of new finalized class.

        Arguments:
            - name (:obj:`str`): Name of the new created class
            - bases (:obj:`Tuple[type]`): Base classes of the new created class
            - attrs (:obj: `Dict[str, Any]`): Attached attributes (such as method and fields) of the new created class

        Example:

            >>> class FinalClass(metaclass=FinalMeta):  # this is a final class
            >>>     pass
            >>>
            >>> class TryToExtendFinalClass(FinalMeta):  # TypeError will be raised in compile time
            >>>     pass
            >>>
        """
        for b in bases:
            if isinstance(b, FinalMeta):
                raise TypeError("Type {name} is a final class, which is not an acceptable common type."
                                .format(name=repr(b.__name__)))
        return type.__new__(mcs, name, bases, attrs)

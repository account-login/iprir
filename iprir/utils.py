

_logger = None


def set_logger(logger):
    global _logger
    _logger = logger


def get_logger():
    return _logger


class cached_property:
    """
    Descriptor (non-data) for building an attribute on-demand on first use.

    ref: http://stackoverflow.com/a/4037979/3886899
    """
    __slots__ = ('_factory',)

    def __init__(self, factory):
        """
        <factory> is called such: factory(instance) to build the attribute.
        """
        self._factory = factory

    def __get__(self, instance, owner):
        # Build the attribute.
        attr = self._factory(instance)
        # Cache the value; hide ourselves.
        setattr(instance, self._factory.__name__, attr)
        return attr

import six
import inspect


def get_not_implemented(cls_name, cls, method):
    return NotImplementedError('{0} (a subclass of {1}) must override method {1}.{2}'.format(
        cls_name,
        cls.__name__,
        method
    ))


class InterfaceMeta(type):
    def __new__(cls, name, parents, dct):
        parent_interface = next((i for i in parents if hasattr(i, '__interface__')), None)

        if not parent_interface:
            dct['__interface__'] = True
        else:
            for key, value in inspect.getmembers(parent_interface, inspect.isfunction):
                if key not in dct:
                    raise get_not_implemented(name, parent_interface, key)

        return super(InterfaceMeta, cls).__new__(cls, name, parents, dct)


class Interface(six.with_metaclass(InterfaceMeta)):
    pass

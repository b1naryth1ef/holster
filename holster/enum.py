class BaseEnum(object):
    pass

class EnumAttr(object):
    def __init__(self, parent, content, index):
        self.parent = parent
        self.content = content
        self.index = index

    def __eq__(self, other):
        if isinstance(other, EnumAttr):
            (self.index == other.index) or (self.content == other.content)

        if isinstance(other, int):
            if self.index == other:
                return True

        return self.content == other

    def __cmp__(self, other):
        if isinstance(other, EnumAttr):
            return self.index - other.index

        if isinstance(other, int):
            return self.index - other

        return self.index - self.parent.ORDER.index(other)

    def __repr__(self):
        return '<EnumAttr {}>'.format(self.content)

    def __str__(self):
        return self.content

    def __int__(self):
        return self.index

class BaseEnumMeta(type):
    def __getattr__(self, attr):
        if attr.lower() in self.attrs:
            return self.attrs[attr.lower()]
        raise AttributeError

    def __getitem__(self, item):
        if isinstance(item, str):
            return getattr(self, item)
        else:
            return self.attrs[self.order[item]]

def Enum(*args):
    class _T(BaseEnum):
        __metaclass__ = BaseEnumMeta

    _T.order = args
    _T.attrs = {}

    for index, entry in enumerate(args):
        _T.attrs[entry] = EnumAttr(_T, entry, index)
        # setattr(_T, entry, EnumAttr(_T, entry, index))
        # setattr(_T, entry.upper(), getattr(_T, entry))

    return _T


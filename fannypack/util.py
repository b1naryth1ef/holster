from flask import flash

def flashy(msg, etype="danger", path="/"):
    """
    Flashes a message and redirects a user. Returns a flask Response that can
    be returned to the user.
    """
    flash(msg, etype)
    return redirect(path)

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
        return self.content

    def __str__(self):
        return self.content

def create_enum(*args):
    class _T(BaseEnum):
        ORDER = args

    for index, entry in enumerate(args):
        setattr(_T, entry, EnumAttr(_T, entry, index))

    return _T


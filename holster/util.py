
def flashy(msg, etype="danger", path="/"):
    """
    Flashes a message and redirects a user. Returns a flask Response that can
    be returned to the user.
    """
    from flask import flash, redirect
    flash(msg, etype)
    return redirect(path)


class SimpleObject(object):
    def __init__(self, data=None):
        self.__dict__.update(data or {})

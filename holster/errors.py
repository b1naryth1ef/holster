from flask import jsonify

from .util import flashy


class ResponseException(Exception):
    """
    Represents an exception that can be cleanly handled and displayed to the
    user. This exception does not imply an error has occured, but rather can
    be used as an easy way to break execution and return responses inside
    complicated view handlers.
    """
    def to_response(self):
        """
        Subclasses must implement this method. Returns a flask Response object.
        """
        raise NotImplementedError("Must define to_response on `%s`" % self.__class__.__name__)


class UserError(ResponseException):
    """
    Flashes a message and redirects a user.
    """
    def __init__(self, msg, etype="danger", path="/"):
        self.msg = msg
        self.etype = etype
        self.path = path

    def to_response(self):
        return flashy(self.msg, self.etype, self.path)


class APIError(ResponseException):
    def __init__(self, msg, status_code=200):
        self.msg = msg
        self.status_code = status_code

    def to_response(self):
        resp = jsonify({
            "message": self.msg,
            "success": False
        })
        resp.status_code = self.status_code
        return resp

    @classmethod
    def ensure(condition, message):
        if not condition:
            raise APIError(message)

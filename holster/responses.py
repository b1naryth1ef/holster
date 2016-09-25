import json

from flask import Response, request


class APIResponse(Response):
    def __init__(self, obj={}):
        Response.__init__(self)

        if 'success' not in obj:
            obj['success'] = True

        if request.values.get("pretty") == '1':
            self.data = json.dumps(obj,
                sort_keys=True,
                indent=2,
                separators=(',', ': '))
        else:
            self.data = json.dumps(obj)

        self.mimetype = "application/json"

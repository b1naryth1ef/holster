import json


def to_json_filter(data):
    return json.dumps(data, separators=(',', ':'))


def to_pjson_filter(data):
    return json.dumps(data)


def register_filters(app):
    app.add_template_filter(to_json_filter, "to_json")
    app.add_template_filter(to_pjson_filter, "to_pjson")


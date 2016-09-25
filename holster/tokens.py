import itsdangerous

_unsafe_deserializer = itsdangerous.URLSafeTimedSerializer('')


class SecureEntity(object):
    def get_token_secret_key(self):
        raise NotImplementedError('{} must override SecureEntity.get_token_secret_key'.format(self.__class__.__name__))


def create_token(entity, contents=None, field=None, salt=b'itsdangerous'):
    assert isinstance(entity, SecureEntity)

    if callable(contents):
        contents = contents(entity)

    if not contents and field:
        contents = getattr(entity, field)

    return itsdangerous.URLSafeTimedSerializer(secret_key=entity.get_token_secret_key(), salt=salt).dumps(contents)


def peak_token_data(token):
    """
    Peaks at a tokens data without any validation/verification of the signature.
    :param token: The token to peak at.
    :rtype: Any valid JSON data
    """
    try:
        payload = itsdangerous.want_bytes(token).rsplit('.', 2)[0]
        return _unsafe_deserializer.load_payload(payload)
    except (itsdangerous.BadPayload, IndexError):
        return None


def verify_token(token, entity_getter, salt=b'itsdangerous', max_age=None):
    data = peak_token_data(token)
    if not data:
        return None, None

    entity = entity_getter(data)
    if not entity:
        return None, data

    try:
        itsdangerous.URLSafeTimedSerializer(entity.get_token_secret_key(), salt).loads(token, max_age=max_age)
    except (itsdangerous.BadSignature, itsdangerous.SignatureExpired):
        return None, None

    return entity, data

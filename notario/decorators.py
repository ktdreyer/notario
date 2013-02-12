from notario.utils import is_callable, safe_repr


class instance_of(object):
    """
    When trying to make sure the value is coming from any number of valid
    objects, you will want to use this decorator as it will make sure that
    before executing the validator it will comply being of any of the
    ``valid_types``.

    For example, if the input for a given validator can be either a dictionary
    or a list, this validator could be used like::

        @instance_of((list, dict))
        def my_validator(value):
            assert len(value) > 0

    This decorator **needs** to be called as it has a default for valid types,
    which is: ``(list, dict, str)``. A working implementation would look like
    this with the default types::

        @instance_of()
        def my_validator(value):
            assert len(value) > 0

    When it fails, as almost all of Notario's exceptions, it will return
    a meaningful error, this is how passing a boolean to a validator that
    accepts the defaults would raise said error:

    .. doctest:: instance_of

        >>> from notario.decorators import instance_of
        >>> @instance_of()
        ... def my_validator(value):
        ...     assert len(value) == 2
        ...
        >>> my_validator(True)
        Traceback (most recent call last):
        ...
        AssertionError: not of any valid types: ['list', 'dict', 'str']
    """

    def __init__(self, valid_types=None):
        self.valid_types = valid_types or (list, dict, str)

    def __call__(self, func):
        fail_msg = "not of any valid types: %s" % self.valid_names()

        def decorated(value):
            assert isinstance(value, self.valid_types), fail_msg
            func(value)
        return decorated

    def valid_names(self):
        return [safe_repr(obj)
                for obj in self.valid_types]


def not_empty(_object):
    """
    Validates the given input (has to be a valid data structure) is empty.
    Input *has* to be one of: `list`, `dict`, or `string`.

    It is specially useful when most of the validators being created are
    dealing with data structures that should not be empty.
    """
    if is_callable(_object):
        _validator = _object

        @instance_of()
        def decorated(value):
            assert value, "%s is empty" % safe_repr(value)
            return _validator(value)
        return decorated
    try:
        assert len(_object), "%s is empty" % safe_repr(_object)
    except TypeError:
        raise AssertionError("not of any valid types: [list, dict, str]")


def optional(_object):
    """
    This decorator has a double functionality, it can wrap validators and make
    them optional or it can wrap keys and make that entry optional.

    **Optional Validator:**
    Allows to have validators work only when there is a value that contains
    some data, otherwise it will just not pass the information to the actual
    validator and will not fail as a result.

    As any normal decorator, it can be used corectly with the decorator
    syntax or in the actual schema.

    This is how it would look in a schema::

        ('key', optional(my_validator))

    Where ``my_validator`` can be any validator that accepts a single
    argument.

    In case a class based validator is being used (like the ``recursive`` or
    ``iterables`` then it would look like::

        ('key', optional(class_validator(('key', 'value'))))

    Of course, the schema should vary depending on your needs, it is just the
    way of constructing the validator call that should be important.

    **Optional Keys:**
    Sometimes a given data structure may present optional entries. For example
    this data::

        data = {'required': 1, 'optional': 2}

    To represent this, you will need to declare the `optional` key in the
    schema but by wrapping the key with this decorator you will basically tell
    the validation engine that if that key is present it should be validated,
    otherwise, it should be skipped. This is how the schema would look::

        schema = (('required', 1), (optional('optional'), 1))

    The above schema would allow data that is missing the ``optional`` key. The
    data below would pass validation without any issues::

        data = {'required': 1}
    """
    if is_callable(_object):
        validator = _object

        def decorated(value):
            if value:
                return validator(value)
            return

        return decorated
    else:
        def wrapped(*args):
            return _object
        wrapped.is_optional = True
        wrapped._object = _object
        return wrapped

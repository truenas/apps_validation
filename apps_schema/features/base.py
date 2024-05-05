from apps_validation.exceptions import ValidationErrors

from .utils import FEATURES


class FeatureMeta(type):

    def __new__(cls, name, bases, dct):
        klass = type.__new__(cls, name, bases, dct)
        if getattr(klass, 'NAME', NotImplementedError) is NotImplementedError:
            raise ValueError(f'Feature {name!r} must have a NAME attribute')

        FEATURES[klass.NAME] = klass
        return klass


class BaseFeature(metaclass=FeatureMeta):

    NAME = NotImplementedError
    VALID_SCHEMAS = []

    def __str__(self):
        return self.NAME

    def validate(self, schema_obj, schema_str):
        verrors = ValidationErrors()
        if not isinstance(schema_obj, tuple(self.VALID_SCHEMAS)):
            verrors.add(
                f'{schema_str}.type',
                f'Schema must be one of {", ".join(str(v) for v in self.VALID_SCHEMAS)} schema types'
            )

        if not verrors:
            self._validate(verrors, schema_obj, schema_str)
        verrors.check()

    def _validate(self, verrors, schema_obj, schema_str):
        pass

    def __eq__(self, other):
        return self.NAME == (other if isinstance(other, str) else other.NAME)

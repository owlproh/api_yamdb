from enum import Enum


class UserRoles(Enum):
    """Выбор пользовательских ролей."""
    admin = 'admin'
    moderator = 'moderator'
    user = 'user'

    @classmethod
    def choices(cls):
        """Формирует соответствие констант и значений."""
        return tuple((attribute.name, attribute.value) for attribute in cls)

    @classmethod
    def max_length_choices(cls):
        """Вычисляет максимальную длину названия роли."""
        return max((len(attribute.value) for attribute in cls))

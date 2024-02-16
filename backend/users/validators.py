from rest_framework import serializers


def required_username(value: str) -> None:
    """Проверка на создание пользователя с именем `me`."""
    if value.lower() == 'me':
        raise serializers.ValidationError('Использование имени "me"'
                                          'запрещено.')

from rest_framework import permissions


# class IsOwnerAdminModerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
#     """
#     Пользовательская проверка аутентификации для определения,
#     имеет ли текущий пользователь
#     право на добавление/изменение/удаление объекта.
#     """

#     def has_object_permission(self, request, view, obj):
#         return (request.method in permissions.SAFE_METHODS
#                 or request.user.has_admin_role()
#                 or request.user.has_moderator_role()
#                 or obj.author == request.user)

# class IsAdminOrReadOnly(permissions.BasePermission):
#     """
#     Пользовательская проверка аутентификации для определения,
#     имеет ли текущий пользователь
#     право на добавление/изменение/удаление объекта.
#     """

#     def has_permission(self, request, view):
#         return (request.method in permissions.SAFE_METHODS
#                 or request.user.is_authenticated
#                 and request.user.has_admin_role())

class IsOwnerOrIsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Пользователь может выполнять действия только с собственным объектом.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)

from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)


class AuthorStaffOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Разрешение на изменение только для служебного персонала и автора.
    Остальным только чтение объекта.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (request.user == obj.author)
            or request.user.is_staff
        )


class OwnerOrAdminOrReadOnly(BasePermission):
    """ Разрешение на изменение только для админа и автора.
    Остальным только чтение объекта.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.user.is_superuser:
            return True
        return request.user == obj.author

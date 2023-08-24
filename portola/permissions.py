from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    def has_object_permission(self, request, view, object):
        return request.user.is_superuser

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to restrict write permissions to admins only
    """

    def has_object_permission(self, request, view, object):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, object):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            return request.user.is_superuser or getattr(object, view.user_lookup_kwarg) == request.user
        except:
            pass

        return request.user.is_superuser
        # Write permissions are only allowed to the owner of the snippet.
        # try:
        #     return object.owner == request.user
        # # KLUGE
        # except:
        #     return False

class IsOwner(permissions.BasePermission):
    """
    simple permission, is the current user the owner of the document?
    """
    def has_object_permission(self, request, view, object):
        return object.owner == request.user

class IsAdminOrSelf(permissions.BasePermission):
    """
    User permission, is the current user a superuser or editing their own record?
    """
    def has_object_permission(self, request, view, object):
        return request.user.is_superuser or object == request.user

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, object):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return object.owner == request.user

class IsStaffAndReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff members to have read access.
    """

    def has_object_permission(self, request, view, object):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return object.owner == request.user


        # Write permissions are only allowed to the owner of the snippet.

class IsProjectApprover(permissions.BasePermission):

    def has_object_permission(self, request, view, object):
        return (request.user == object.project.document_approver)


class IsAvailableOrAgreed(permissions.BasePermission):
    """
    Custom permission to only allow users to see Generally available Documents
    or those that have an agreement. Need to know if the agreement is between
    entities or Users.

    3 sets of rules: Global, list, and download.
        Global: Doc owner and admins always have permission
        List: if GENERAL, REQUEST, or entity is approved
        Download: if GENERAL or entity approved

    """

    def has_object_permission(self, request, view, object):
        # Anything using this permission requires Authentication
        if permissions.IsAuthenticated:
            # read permissions are granted to logged in users for
            # GNEREAL documents
            if object.disclosure == 'GENERAL':
                return True
            # Document entity is same entity as request user:
            if object.entity == request.user.profile.entity:
                return True

            if object.disclosure == 'BY REQUEST':
                if "download" in request.path:
                    # raise NameError(object.disclosure)
                    # Need to check if there is an agreement on this document for this
                    # User or their Entity
                    if request.user.profile.entity in object.permitted_entities.all():
                        return True
                    else:
                        return request.user.is_staff
                # if "docrequest" in request.path:
                else:
                    return True

        # Admin users have access
        return request.user.is_staff

class IsStaff(permissions.BasePermission):
    """
    simple permission, is the current user staff?
    """
    def has_object_permission(self, request, view, object):
        return request.user.is_staff

'''
a document is only downloadable by a user if:
1. the user belongs to the same legal entity as the document OR
2. the document is generally available for download OR
3. the user is a PVEL admin OR
4. the document is "by request" AND  there is an agreement between the requesting user entity and the owner entity (edited)
￼￼￼￼￼
5:13 PM
a document is only visible to a user if:
1. the user belongs to the same legal entity as the document OR
2. the document is generally available for download OR
3. the user is a PVEL admin OR
4. the document is "by request"
'''

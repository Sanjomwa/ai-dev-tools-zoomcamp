import functools

from django.shortcuts import redirect

from .models import Member


def require_identity(view_func):
    """Session-identity guard (issue #4).

    Wrap any view that needs to know "who am I". If the session has no
    ``member_id``, or it points at a ``Member`` that no longer exists (e.g.
    deleted via admin after being picked), redirect to the identity-pick page
    instead of rendering or erroring.

    Apply this to every view with that need rather than repeating the check
    inline. Do NOT apply it to ``identity_pick`` itself — guarding the picker
    page would make picking a name loop forever. Exemption is simply "don't
    decorate it".
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        member_id = request.session.get("member_id")
        if member_id is None or not Member.objects.filter(pk=member_id).exists():
            return redirect("identity_pick")
        return view_func(request, *args, **kwargs)

    return wrapper

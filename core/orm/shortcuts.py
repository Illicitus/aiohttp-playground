from tortoise.exceptions import DoesNotExist
from core.responses.json import NotFound


async def _get_object_or_404(queryset, *args, **kwargs):
    """
    Use get() to return an object, or raise a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """

    return await queryset.get(*args, **kwargs)


async def get_object_or_404(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.
    """
    try:
        return await _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError, DoesNotExist):
        raise NotFound

from django import template

register = template.Library()


@register.filter
def glyphicon_tags(value):
    """
    Get icons by fields name
    """
    tags = [
        ('username', 'user'),
    ]

    if 'password' in value:
        return 'lock'

    for search, replace in tags:
        value = value.replace(search, replace)

    return value


@register.filter
def status_icons(value):
    """
        Get icons from statuses.
    """
    tags = {
        1: 'glyphicon-repeat',
        2: 'glyphicon-ok',
        3: 'glyphicon-ban-circle',
        4: 'glyphicon-user',
        5: 'glyphicon-home',
        6: 'glyphicon-question-sign',
        7: 'glyphicon-remove',
        8: 'glyphicon-minus',
        9: 'glyphicon-king',
        10: 'glyphicon-resize-full',
        11: 'glyphicon-exclamation-sign',
    }

    return tags[value]


@register.filter
def messages_alert_tags(value):
    """
        Get alerts class from alerts type
    """
    tags = [
        ('error', 'danger'),
        ('info', 'info'),
        ('success', 'success'),
        ('warning', 'warning')
    ]

    for search, replace in tags:
        value = value.replace(search, replace)

    return value

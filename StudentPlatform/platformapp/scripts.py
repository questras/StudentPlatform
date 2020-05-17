from .models import Group, Tab, Element




def create_group(name, description, user):
    """Create group."""

    group = Group.objects.create(
        name=name,
        description=description,
        creator=user,
    )
    group.save()
    group.users.add(user)
    group.save()

    return group


def create_tab(name, user, group):
    """Create Tab."""

    tab = Tab.objects.create(
        name=name,
        creator=user,
        group=group,
    )
    tab.save()

    return tab


def create_element(name, text, user, tab):
    """Create element."""

    element = Element.objects.create(
        name=name,
        text=text,
        creator=user,
        tab=tab,
    )
    element.save()

    return element

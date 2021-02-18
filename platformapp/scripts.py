from django.contrib.auth import get_user_model
from django.db import IntegrityError
from typing import List
import random
import requests
import json

from .models import Group, Tab, Element, Comment

User = get_user_model()


def get_random_words() -> List[str]:
    """Return list of random english words."""

    url = 'https://raw.githubusercontent.com/sindresorhus/mnemonic-words/master/words.json'
    r = requests.get(url)
    r.raise_for_status()

    words = json.loads(r.text)
    return words


def create_random_data(users: int, groups: int, tabs: int,
                       elements: int, comments: int):
    """Add randomly generated data to database. Create users, groups,
    tabs and elements in number specified in parameters.

    :param users:       number of users to add, positive number,
    :param groups:      number of groups to add, positive number,
    :param tabs:        number of tabs to add, positive number,
    :param elements:    number of elements to add, positive number,
    :param comments:    number of comments to add, positive number.
    """

    if users <= 0 or groups <= 0 or tabs <= 0 or elements <= 0 or comments <= 0:
        raise ValueError

    words = get_random_words()
    users_list = []
    groups_list = []
    tabs_list = []
    elements_list = []

    # Create users.
    for i in range(users):
        user = create_random_user(words)
        users_list.append(user)

    # Create groups.
    for i in range(groups):
        group = create_random_group(words, users_list)
        groups_list.append(group)

    # Add random amount of created users to each group.
    for group in groups_list:
        for user in users_list:
            if random.choice([True, False]):
                group.users.add(user)

    # Create tabs.
    for i in range(tabs):
        tab = create_random_tab(words, groups_list)
        tabs_list.append(tab)

    # Create elements.
    for i in range(elements):
        element = create_random_element(words, tabs_list)
        elements_list.append(element)

    # Create comments.
    for i in range(comments):
        comment = create_random_comment(words, elements_list)


def create_random_comment(words: List[str], elements: List[Element]) -> Comment:
    """Create comment with text set as random
    english word from words. Comment's element is
    chosen from elements list and creator is chosen from
    element's group users.
    """

    text = random.choice(words)
    element = random.choice(elements)
    user = random.choice(element.tab.group.users.all())

    return create_comment(text, user, element)


def create_random_element(words: List[str], tabs: List[Tab]) -> Element:
    """Create element with name and text set as random
    english word from words. Element's tab is chosen from
    tabs list and creator is chosen from tab's group users.
    """

    name = random.choice(words)
    text = random.choice(words)
    tab = random.choice(tabs)
    user = random.choice(tab.group.users.all())

    return create_element(name, text, user, tab)


def create_random_tab(words: List[str], groups: List[Group]) -> Tab:
    """Create tab with name set as random english word from words.
    Tab's group is chosen from groups list and creator is
    chosen from group's users.
    """

    name = random.choice(words)
    group = random.choice(groups)
    user = random.choice(group.users.all())

    return create_tab(name, user, group)


def create_random_group(words: List[str], creators: List[User]) -> Group:
    """Create group with name and description set as
    random english word from words. Group's creator is randomly
    chosen from creators.
    """

    name = random.choice(words)
    description = random.choice(words)
    creator = random.choice(creators)

    return create_group(name, description, creator)


def create_random_user(words: List[str]) -> User:
    """Create user with username and password set as
    random english word from words.
    Function runs until new user is created."""

    username = random.choice(words)
    password = random.choice(words)

    try:
        user = create_user(username, password)
        return user
    except IntegrityError:
        return create_random_user(words)


def create_user(username: str, password: str) -> User:
    user = User.objects.create_user(username=username, password=password)
    return user


def create_group(name: str, description: str, user: User) -> Group:
    group = Group.objects.create(
        name=name,
        description=description,
        creator=user,
    )
    group.save()
    group.users.add(user)
    group.save()

    return group


def create_tab(name: str, user: User, group: Group) -> Tab:
    tab = Tab.objects.create(
        name=name,
        creator=user,
        group=group,
    )
    tab.save()

    return tab


def create_element(name: str, text: str, user: User, tab: Tab) -> Element:
    element = Element.objects.create(
        name=name,
        text=text,
        creator=user,
        tab=tab,
    )
    element.save()

    return element


def create_comment(text: str, user: User, element: Element) -> Comment:
    comment = Comment.objects.create(
        text=text,
        creator=user,
        element=element,
    )
    comment.save()

    return comment


def get_all_tabs_from_groups(groups: List[Group]) -> List[Tab]:
    """Return list of all tabs in groups."""

    tabs = []
    for group in groups:
        tabs += list(group.tab_set.all())

    return tabs


def get_all_elements_from_tabs(tabs: List[Tab]) -> List[Element]:
    """Return list of all elements in tabs."""

    elements = []
    for tab in tabs:
        elements += list(tab.element_set.all())

    return elements


def get_all_comments_from_elements(elements: List[Element]) -> List[Comment]:
    """Return list of all comments in elements."""

    comments = []
    for element in elements:
        comments += list(element.comment_set.all())

    return comments

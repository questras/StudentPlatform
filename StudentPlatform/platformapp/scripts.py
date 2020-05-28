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

    for i in range(users):
        user = create_random_user(words)
        print(f'Created: {user}')
        users_list.append(user)

    for i in range(groups):
        group = create_random_group(words, users_list)
        print(f'Created: {group}')
        groups_list.append(group)

    for i in range(tabs):
        tab = create_random_tab(words, groups_list, users_list)
        print(f'Created: {tab}')
        tabs_list.append(tab)

    for i in range(elements):
        element = create_random_element(words, tabs_list, users_list)
        print(f'Created: {element}')
        elements_list.append(element)

    for i in range(comments):
        comment = create_random_comment(words, elements_list, users_list)
        print(f'Created: {comment}')


def create_random_comment(words: List[str], elements: List[Element],
                          creators: List[User]) -> Comment:
    """Create comment with text set as random
    english word from words. Comment's element and user are
    chosen from elements and creators.
    """

    text = random.choice(words)
    user = random.choice(creators)
    element = random.choice(elements)

    return create_comment(text, user, element)


def create_random_element(words: List[str], tabs: List[Tab],
                          creators: List[User]) -> Element:
    """Create element with name and text set as random
    english word from words. Element's tab and user are
    chosen from tabs and creators.
    """

    name = random.choice(words)
    text = random.choice(words)
    user = random.choice(creators)
    tab = random.choice(tabs)

    return create_element(name, text, user, tab)


def create_random_tab(words: List[str], groups: List[Group],
                      creators: List[User]) -> Tab:
    """Create tab with name set as random english word from words.
    Tab's group and user are chosen from groups and creators.
    """

    name = random.choice(words)
    user = random.choice(creators)
    group = random.choice(groups)

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

import logging

from typing import Dict, Tuple, List, Any, Union, Callable


# requirements = List[str] #list of ids of the packages required for the current package
# conflicts = List[str] #list of ids of packages incompatible with the current one
# before = List[str] #list of ids of packages that must be installed before the current package
# after = List[str] #list of ids of packages that must be installed after the current package
# dependencies = Tuple[requirements, conflicts, before, after]



class Component:
    """

    """

    def __init__(self, componentid: str, componentname: str, subcomponents: List["Component"]):
        self.id = componentid
        self.name = componentname
        self.subcomponents = subcomponents


class Dependencies:
    """

    """

    def __init(self, requirements: List[str] = None, conflicts: List[str] = None, before: List[str] = None,
               after: List[str] = None):
        self.requirements = requirements if requirements else []
        self.conflicts = conflicts if conflicts else []
        self.before = before if before else []
        self.after = after if after else []

class Package:
    """

    """

    def __init__(self, packageid: str, name: str, depends: List[Tuple[Dependencies, List[str]]],
                 components: List[Component]):
        """
        This initialises a package with an id and a name. The id will be used as a unique identifier. The name will be displayed to the user.
        components must describe the components of the package.
        depends is a list of tuples. Each tuple must have dependencies as a first element and a list of the component ids they apply to as second element.
        :param id: Unique identifier of the package
        :param name: Name of the package
        :param depends: dependencies of the package
        :param components: components of the package
        """
        self.id = packageid
        self.name = name
        self.depends = depends
        self.components = components


class InstallAction:
    """

    """

    def __init__(self, installmethod: Callable, prev: List["InstallAction"], name: str):
        self.execute = installmethod
        self.prev = prev
        self.name = name


class IncompatibleActionsException(Exception):
    pass


def sortInstallActionList(actions: List[InstallAction]) -> List[InstallAction]:
    log = logging.getLogger(__name__)
    # depth first search into topologic sort
    sortedList = []

    def depthFirstSort(action):

        # Open node
        if action.state == 1:
            log.error(
                'There is a loop in the action list, the action {} is within its predecessors'.format(action.name))
            raise IncompatibleActionsException('There is a loop in the ')

        # Closed node
        if action.state == 2:
            log.debug('Action {} is closed, nothing new here'.format(action.name))
            return

        # New node
        log.debug('Opening {}'.format(action.name))
        action.state = 1
        for prevAction in action.prev:
            log.debug('Looking at child {}'.format(action.name))
            depthFirstSort(prevAction)
        log.debug('Closing {}'.format(action.name))
        action.state = 2
        sortedList.append(action)

    for action in actions:
        action.state = 0

    for action in actions:
        log.debug('Initialising search on action {}'.format(action.name))
        # noinspection PyTypeChecker
        depthFirstSort(action)

    for action in actions:
        del action.state

    return sortedList

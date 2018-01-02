from typing import Dict, Tuple, List, Any, Union, Callable

import logging
import json

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

    def to_dict(self) -> Dict[str, Any]:
        return {'id': self.id,
                'name': self.name,
                'subcomponents': [comp.to_dict() for comp in self.subcomponents]}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Component":
        return cls(d['id'],
                   d['name'],
                   [cls.from_dict(subcomp) for subcomp in d['subcomponents']])


class Dependencies:
    """

    """

    def __init__(self, requirements: List[str] = None, conflicts: List[str] = None, before: List[str] = None,
                 after: List[str] = None):
        self.requirements = requirements if requirements else []
        self.conflicts = conflicts if conflicts else []
        self.before = before if before else []
        self.after = after if after else []

    def to_dict(self) -> Dict[str, Any]:
        return {'requirements': self.requirements.copy(),
                'conflicts': self.conflicts.copy(),
                'before': self.before.copy(),
                'after': self.after.copy()}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Dependencies":
        return cls(requirements=d['requirements'],
                   conflicts=d['conflicts'],
                   before=d['before'],
                   after=d['after'])

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

    def to_dict(self) -> Dict[str, Any]:
        return {'id': self.id,
                'name': self.name,
                'dependencies': [{'involvedcomps': dep[1],
                                  'dependency': dep[0].to_dict()} for dep in self.depends],
                'components': [comp.to_dict() for comp in self.components]}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Package":
        return cls(packageid=d['id'],
                   name=d['name'],
                   depends=[(Dependencies.from_dict(dep['dependency']), dep['involvedcomps']) for dep in
                            d['dependencies']],
                   components=[Component.from_dict(comp) for comp in d['components']])

    @classmethod
    def save_to_json(cls, pkgdict: Dict[str, "Package"], filename: str):
        log = logging.getLogger(__name__)
        log.info('Starting dict creation')
        d = {}
        for pkg in pkgdict.values():
            log.debug('Saving mod {}'.format(pkg.id))
            d[pkg.id] = pkg.to_dict()

        log.info('Starting json dump to {}'.format(filename))
        with open(file=filename, mode='w', encoding='utf-8') as f:
            json.dump(d, f, indent=4)

        return True

    @classmethod
    def load_from_json(cls, filename: str) -> Dict[str, "Package"]:
        log = logging.getLogger(__name__)
        log.info('Getting dict object')
        with open(file=filename, mode='r', encoding='utf-8') as f:
            d = json.load(f)

        log.info('Creating objects')
        pkgdict = {}
        for pkgid, pkg in d.items():
            pkgdict[pkgid] = cls.from_dict(pkg)

        return pkgdict

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

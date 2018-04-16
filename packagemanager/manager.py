import json
import logging
import itertools as it

from typing import Callable, List, Any, Dict, Tuple, Union, Set, Iterable


class NonUniqueParentException(Exception): pass


class NonUniqueIDException(Exception): pass


class UnexistingComponentException(Exception): pass


class Dependencies:
    """

    """

    def __init__(self, requirements: Iterable[str] = None, conflicts: Iterable[str] = None,
                 before: Iterable[str] = None,
                 after: Iterable[str] = None):
        self.requirements = set(requirements) if requirements else set()
        self.conflicts = set(conflicts) if conflicts else set()
        self.before = set(before) if before else set()
        self.after = set(after) if after else set()

    def union(self, other: "Dependencies"):
        d = Dependencies(self.requirements, self.conflicts, self.before, self.after)
        d.requirements |= other.requirements
        d.conflicts |= other.conflicts
        d.before |= other.before
        d.after |= other.after

        return d

    def to_dict(self) -> Dict[str, Any]:
        return {'requirements': list(self.requirements),
                'conflicts': list(self.conflicts),
                'before': list(self.before),
                'after': list(self.after)}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Dependencies":
        return cls(requirements=d['requirements'],
                   conflicts=d['conflicts'],
                   before=d['before'],
                   after=d['after'])


class Component:
    def __init__(self, componentid: str, name: str,
                 subcomponents: List["SubComponent"] = None, depends: Dependencies = None):
        """
        This initialises a component with an id and a name. The id will be used as a unique identifier. The name will be displayed to the user.
        subcomponents must be a list of component to be subcomponents of the new one.
        depends is a dependency that will be added to the ancestor's dependencies if there are any.
        :param id: Unique identifier of the package
        :param name: Name of the package
        :param depends: dependencies of the package
        :param components: components of the package
        """
        self.id = componentid
        self.name = name
        self.parent = None

        self.subcomponents = []
        self._subcompdict = {}
        if subcomponents:
            for c in subcomponents:
                self._add_subcomponent(c)

        self.depends = depends if depends else Dependencies()

    def _add_subcomponent(self, comp: "SubComponent"):
        '''
        Raises NonUniqueIDException if there is already a subcomponent with the same id.
        Raises NonUniqueParentException if the component already has a parent.
        Adds the component to the subcomponents and sets itself as parent of the component
        :param comp:
        :return:
        '''
        log = logging.getLogger(__name__)
        if comp.id in (c.id for c in self.subcomponents):
            log.error('Non Unique ID encountered, component {} already exists in {}'.format(comp.id, self.id))
            raise NonUniqueIDException
        if comp.parent is not None:
            log.error('Non Unique Parent encountered, component {} already has {} as a parent before {}'.format(comp.id,
                                                                                                                comp.parent.id,
                                                                                                                self.id))
            raise NonUniqueParentException

        self.subcomponents.append(comp)
        self._subcompdict[comp.id] = comp
        comp.parent = self

    def get_comp(self, id_) -> "Component":
        if id_ in self._subcompdict:
            return self._subcompdict[id_]
        raise UnexistingComponentException

    def get_dependencies(self) -> Dependencies:
        if self.parent:
            return self.depends.union(self.parent.get_dependencies())
        return self.depends

    def get_full_id(self) -> str:
        if self.parent:
            return '.'.join([self.parent.get_full_id(), self.id])
        return self.id

    def get_ancestors(self) -> List["Component"]:
        '''
        Returns the list of all the ancestors of the component in descending order of closeness(the first element always has no ancestor)
        :return:
        '''
        if self.parent is None:
            return []
        res = self.parent.get_ancestors()
        res.append(self.parent)
        return res

    def get_childrens(self) -> Iterable["Component"]:
        '''
        Returns an iterator over the children of the component
        :return:
        '''
        return it.chain((c for c in self.subcomponents), *(c.get_childrens() for c in self.subcomponents))

    def to_dict(self):
        '''
        Returns a dict compatible with json format representing the object.
        The same dict can be used to create the same component using the 'from_dict' method
        :return:
        '''
        return {'id': self.id,
                'name': self.name,
                'subcomponents': [comp.to_dict() for comp in self.subcomponents],
                'dependencies': self.depends.to_dict()}

    @classmethod
    def from_dict(cls, dict_):
        return cls(componentid=dict_['id'],
                   name=dict_['name'],
                   depends=Dependencies.from_dict(dict_['dependencies']),
                   subcomponents=(cls.from_dict(d) for d in dict_['subcomponents']))


class SubComponent(Component):
    """

    """

    def __init__(self, componentid: str, name: str,
                 subcomponents: List["SubComponent"] = None, depends: Dependencies = None):
        super().__init__(componentid=componentid, name=name, subcomponents=subcomponents, depends=depends)


class Package(Component):
    """

    """

    def __init__(self, packageid: str, name: str,
                 depends: Dependencies,
                 components: List[SubComponent] = None):
        """
        This initialises a package with an id and a name. The id will be used as a unique identifier. The name will be displayed to the user.
        components must describe the components of the package.
        depends is a list of tuples. Each tuple must have dependencies as a first element and a list of the component ids they apply to as second element.
        :param id: Unique identifier of the package
        :param name: Name of the package
        :param depends: dependencies of the package
        :param components: components of the package
        """
        super().__init__(componentid=packageid, name=name, subcomponents=components, depends=depends)

    def generate_install_actions(self, installed_components: List[SubComponent]) -> List["InstallAction"]:
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        return {'id': self.id,
                'name': self.name,
                'components': [comp.to_dict() for comp in self.subcomponents],
                'dependencies': self.depends.to_dict()}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Package":
        return cls(packageid=d['id'],
                   name=d['name'],
                   depends=Dependencies.from_dict(d['dependencies']),
                   components=[SubComponent.from_dict(comp) for comp in d['components']])

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

    def __init__(self, installmethod: Callable, args: List[Any], id: str, prev: List["InstallAction"]):
        self.method = installmethod
        self.args = args
        self.prev = prev
        self.id = id

    def execute(self):
        self.method(*self.args)


class IncompatibleActionsException(Exception): pass


class ImpossibleComponentException(Exception): pass


class Selection:
    def __init__(self, pkg: Package, components: List[SubComponent] = None):
        self.pkg = pkg
        self.components: List[SubComponent] = []

        if components:
            for c in components:
                self.select_component(c)

    def select_component(self, comp: Component) -> None:
        if comp.get_ancestors()[0] != self.pkg:
            raise ImpossibleComponentException
        self.components.append(comp)

    def unselect_component(self, comp: Component) -> None:
        self.components.remove(comp)

    def get_components_id(self) -> List[str]:
        log = logging.getLogger(__name__)
        log.info('Getting components ids')
        res = []
        for comp in self.components:
            log.debug('Getting ancestors id for {}'.format(comp.id))
            res.append(comp.get_full_id())
        return res

    def get_dependencies(self) -> Dependencies:
        r = Dependencies()
        for c in self.components:
            r = r.union(c.get_dependencies())
        return r


def sortInstallActionList(actions: List[InstallAction]) -> List[InstallAction]:
    log = logging.getLogger(__name__)
    # depth first search into topologic sort
    sortedList = []

    def depthFirstSort(action):

        # Open node
        if action.state == 1:
            log.error(
                'There is a loop in the action list, the action {} is within its predecessors'.format(action.id))
            raise IncompatibleActionsException('There is a loop in the ')

        # Closed node
        if action.state == 2:
            log.debug('Action {} is closed, nothing new here'.format(action.id))
            return

        # New node
        log.debug('Opening {}'.format(action.id))
        action.state = 1
        for prevAction in action.prev:
            log.debug('Looking at child {}'.format(action.id))
            depthFirstSort(prevAction)
        log.debug('Closing {}'.format(action.id))
        action.state = 2
        sortedList.append(action)

    for action in actions:
        action.state = 0

    for action in actions:
        log.debug('Initialising search on action {}'.format(action.id))
        # noinspection PyTypeChecker
        depthFirstSort(action)

    for action in actions:
        del action.state

    return sortedList


class UnavailablePackageException(Exception): pass


class PackageHasConflictException(Exception): pass


class NotInitialisedPackageException(Exception): pass


class NotSelectedPackageException(Exception): pass


class Manager:
    def __init__(self):
        self.availablepkg: Dict[str, Package] = {}
        self.selectedpkg: Dict[str, Selection] = {}

    def add_pkg(self, pkg: Package):
        '''
        Will raise NonUniqueIDException if a package with an identical id already exists in the manager.
        Adds the package to the list of available package
        :param pkg:
        :return:
        '''
        log = logging.getLogger(__name__)
        log.info('Adding Package {} to the Manager'.format(pkg.id))

        if pkg.id in self.availablepkg:
            log.error('The package id already exists in the manager')
            raise NonUniqueIDException
        else:
            self.availablepkg[pkg.id] = pkg
            log.debug('Initialising conflict counter')
            pkg.nb_conflicts = 0
            for c in pkg.get_childrens():
                c.nb_conflicts = 0

    def select_pkg(self, pkg: Package, components: List[Component], raiseconflicts=True):
        '''

        :param raiseconflicts:
        :param components:
        :param pkg:
        :return:
        '''
        log = logging.getLogger(__name__)
        log.info('Selecting Package {}'.format(pkg.id))

        if pkg.id not in self.availablepkg:
            raise UnavailablePackageException

        if pkg.id not in self.selectedpkg:
            self.selectedpkg[pkg.id] = s = Selection(pkg)
        else:
            s = self.selectedpkg[pkg.id]

        if not hasattr(pkg, 'nb_conflicts'):
            raise NotInitialisedPackageException(pkg.id)

        if raiseconflicts:
            if pkg.nb_conflicts > 0:
                raise PackageHasConflictException(pkg.id)
            incompatible_comp = []
            for comp in components:
                if comp.nb_conflicts > 0:
                    incompatible_comp.append(comp.get_full_id())
            if incompatible_comp:
                raise PackageHasConflictException(incompatible_comp)

        for comp in components:
            if comp not in s.components:
                for conflict in comp.get_dependencies().conflicts:
                    self.getcomp(conflict).nb_conflicts += 1
                s.select_component(comp)

    def unselect_package(self, pkg: Package, components: List[Component]):

        log = logging.getLogger(__name__)
        log.info('Unselecting components from Package {}'.format(pkg.id))

        if pkg.id not in self.availablepkg:
            raise UnavailablePackageException

        if pkg.id not in self.selectedpkg:
            raise NotSelectedPackageException

        s = self.selectedpkg[pkg.id]

        for comp in components:
            if comp in s.components:
                for conflict in comp.get_dependencies().conflicts:
                    self.getcomp(conflict).nb_conflicts -= 1
                s.unselect_component(comp)

        if not s.components:
            self.selectedpkg.pop(pkg.id)

    def getcomp(self, compid: str):
        ids = '.'.split(compid)
        c = self.availablepkg[ids[0]]
        for id_ in ids[1:]:
            c = c.get_comp(id_)
        return c

    def generate_action_list(self):
        self.installActions: List[InstallAction] = []
        for selection in self.selectedpkg.values():
            self.installActions.extend(selection.pkg.generate_install_actions(selection.components))
        return self.installActions

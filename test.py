import json
import logging.config
import unittest

log = logging.getLogger(__name__)
logging.config.dictConfig(json.load(open('logging_config.json', 'r')))

from packagemanager import manager as mngr


class TestDependencies(unittest.TestCase):
    def testUnion(self):
        d1 = mngr.Dependencies(requirements=['p01.c01'], conflicts=['p02.c02'], before=[], after=['p01.c01'])
        d2 = mngr.Dependencies(requirements=['p02.c01'], conflicts=['p02.c02'], before=['p02.c01'], after=[])
        d3 = d1.union(d2)
        self.assertEqual((d3.requirements, d3.conflicts, d3.before, d3.after),
                         ({'p01.c01', 'p02.c01'}, {'p02.c02'}, {'p02.c01'}, {'p01.c01'}))


class TestComponents(unittest.TestCase):
    def test_to_dict_simple(self):
        c1 = mngr.SubComponent(componentid='cid01', name='name01', subcomponents=[], depends=None)
        expected = {'id': 'cid01',
                    'name': 'name01',
                    'subcomponents': [],
                    'dependencies': {'requirements': [],
                                     'conflicts': [],
                                     'before': [],
                                     'after': []}}
        self.assertEqual(c1.to_dict(), expected)

    def test_to_dict_complex(self):
        c2 = mngr.SubComponent(componentid='cid02', name='name02')
        c3 = mngr.SubComponent(componentid='cid03', name='name03')
        c4 = mngr.SubComponent(componentid='cid04', name='name04', subcomponents=[c2, c3])
        c5 = mngr.SubComponent(componentid='cid05', name='name05')
        c6 = mngr.SubComponent(componentid='cid06', name='name06', subcomponents=[c5])
        c7 = mngr.SubComponent(componentid='cid07', name='name07', subcomponents=[c4, c6])

        expected = {'id': "cid07",
                    'name': "name07",
                    'subcomponents': [
                        {'id': 'cid04',
                         'name': 'name04',
                         'subcomponents': [
                             {'id': 'cid02',
                              'name': 'name02',
                              'subcomponents': [],
                              'dependencies': {'requirements': [],
                                               'conflicts': [],
                                               'before': [],
                                               'after': []}},
                             {'id': 'cid03',
                              'name': 'name03',
                              'subcomponents': [],
                              'dependencies': {'requirements': [],
                                               'conflicts': [],
                                               'before': [],
                                               'after': []}}],
                         'dependencies': {'requirements': [],
                                          'conflicts': [],
                                          'before': [],
                                          'after': []}},
                        {'id': 'cid06',
                         'name': 'name06',
                         'subcomponents': [
                             {'id': 'cid05',
                              'name': 'name05',
                              'subcomponents': [],
                              'dependencies': {'requirements': [],
                                               'conflicts': [],
                                               'before': [],
                                               'after': []}}],
                         'dependencies': {'requirements': [],
                                          'conflicts': [],
                                          'before': [],
                                          'after': []}}],
                    'dependencies': {'requirements': [],
                                     'conflicts': [],
                                     'before': [],
                                     'after': []}}
        self.assertEqual(c7.to_dict(), expected)

    def test_non_unique_id(self):
        c1 = mngr.SubComponent(componentid='cid01', name='name01', subcomponents=[])
        c2 = mngr.SubComponent(componentid='cid01', name='name02', subcomponents=[])
        with self.assertRaises(mngr.NonUniqueIDException):
            c3 = mngr.SubComponent(componentid='cid02', name='name03', subcomponents=[c1, c2])

    def test_non_unique_parent(self):
        c1 = mngr.SubComponent(componentid='cid01', name='name01', subcomponents=[])
        c2 = mngr.SubComponent(componentid='cid02', name='name02', subcomponents=[c1])
        with self.assertRaises(mngr.NonUniqueParentException):
            c3 = mngr.SubComponent(componentid='cid03', name='name03', subcomponents=[c1])

    def test_get_parents(self):
        c1 = mngr.SubComponent(componentid='cid01', name='name01')
        c2 = mngr.SubComponent(componentid='cid02', name='name02', subcomponents=[c1])
        c3 = mngr.SubComponent(componentid='cid03', name='name03', subcomponents=[c2])
        self.assertEqual(c1.get_ancestors(), [c3, c2])
        self.assertEqual(c2.get_ancestors(), [c3])
        self.assertEqual(c3.get_ancestors(), [])

    def test_full_id(self):
        c1 = mngr.SubComponent(componentid='cid01', name='name01')
        c2 = mngr.SubComponent(componentid='cid02', name='name02', subcomponents=[c1])
        c3 = mngr.SubComponent(componentid='cid03', name='name03', subcomponents=[c2])
        self.assertEqual(c3.get_full_id(), 'cid03')
        self.assertEqual(c2.get_full_id(), 'cid03.cid02')
        self.assertEqual(c1.get_full_id(), 'cid03.cid02.cid01')

    def test_get_childrens(self):
        c1 = mngr.SubComponent(componentid='cid01', name='name01')
        c2 = mngr.SubComponent(componentid='cid02', name='name02', subcomponents=[c1])
        c3 = mngr.SubComponent(componentid='cid03', name='name03', subcomponents=[c2])
        self.assertEqual(set(c1.get_childrens()), set())
        self.assertEqual(set(c2.get_childrens()), {c1})
        self.assertEqual(set(c3.get_childrens()), {c1, c2})

    @unittest.skip
    def test_recursion_limit(self):
        clist = [mngr.SubComponent(componentid='cid00', name='name00')]
        for i in range(900):
            clist.append(
                mngr.SubComponent(componentid='cid0{}'.format(i), name='name0{}'.format(i), subcomponents=[clist[-1]]))
        print(*clist[-1].get_childrens())


class TestPackage(unittest.TestCase):
    def test_import_export(self):
        c1 = mngr.SubComponent(componentid='cid01', name='namec01')
        p1 = mngr.Package(packageid='pid01', name='namep01', depends=mngr.Dependencies(), components=[c1])

        c2 = mngr.SubComponent(componentid='cid02', name='namec02')
        c3 = mngr.SubComponent(componentid='cid03', name='namec03')
        c4 = mngr.SubComponent(componentid='cid04', name='namec04', subcomponents=[c2, c3])
        c5 = mngr.SubComponent(componentid='cid05', name='namec05')
        c6 = mngr.SubComponent(componentid='cid06', name='namec06', subcomponents=[c5])

        p2 = mngr.Package(packageid="pid02", name="namep02", depends=mngr.Dependencies(),
                          components=[c4, c6])

        pkgdict = {p1.id: p1, p2.id: p2}
        mngr.Package.save_to_json({p1.id: p1, p2.id: p2}, 'test.json')
        pkgdictexp = mngr.Package.load_from_json('test.json')
        self.assertEqual({pkg.id: pkg.to_dict() for pkg in pkgdict.values()},
                         {pkg.id: pkg.to_dict() for pkg in pkgdictexp.values()})


class TestSelection(unittest.TestCase):
    def setUp(self):
        self.c1 = mngr.SubComponent(componentid="cid01", name='namec01')
        self.c2 = mngr.SubComponent(componentid="cid02", name='namec02')

        self.p1 = mngr.Package(packageid='pid01', name='namep01', depends=mngr.Dependencies(), components=[self.c1])
        self.p2 = mngr.Package(packageid='pid02', name='namep02', depends=mngr.Dependencies(), components=[self.c2])

        self.c3 = mngr.SubComponent(componentid='cid03', name='namec03')
        self.c4 = mngr.SubComponent(componentid='cid04', name='namec04', subcomponents=[self.c3])
        self.c5 = mngr.SubComponent(componentid='cid05', name='namec05', subcomponents=[self.c4])

        self.p3 = mngr.Package(packageid='pid03', name='namep03', depends=mngr.Dependencies(), components=[self.c5])

    def test_creation(self):
        s1 = mngr.Selection(self.p1)
        self.assertEqual(s1.pkg, self.p1)

        s2 = mngr.Selection(self.p2)
        self.assertEqual(s2.pkg, self.p2)

        s3 = mngr.Selection(self.p3)
        self.assertEqual(s3.pkg, self.p3)

    def test_selection_comp(self):
        s1 = mngr.Selection(self.p1)
        s1.select_component(self.c1)
        self.assertEqual(s1.components, [self.c1])

        s3 = mngr.Selection(self.p3)
        s3.select_component(self.c4)
        self.assertEqual(s3.components, [self.c4])
        s3.select_component(self.c5)
        self.assertEqual(s3.components, [self.c4, self.c5])

    def test_impossible_comp(self):
        s1 = mngr.Selection(self.p1)
        with self.assertRaises(mngr.ImpossibleComponentException):
            s1.select_component(self.c2)

    def test_component_ids(self):
        s1 = mngr.Selection(self.p1)
        s1.select_component(self.c1)
        self.assertEqual(s1.get_components_id(), ['pid01.cid01'])
        s3 = mngr.Selection(self.p3)
        s3.select_component(self.c3)
        s3.select_component(self.c5)
        self.assertEqual(s3.get_components_id(), ['pid03.cid05.cid04.cid03', 'pid03.cid05'])


class TestManager(unittest.TestCase):
    def setUp(self):
        self.c1 = mngr.SubComponent(componentid="cid01", name='namec01')
        self.c2 = mngr.SubComponent(componentid="cid02", name='namec02')

        self.p1 = mngr.Package(packageid='pid01', name='namep01', depends=mngr.Dependencies(), components=[self.c1])
        self.p2 = mngr.Package(packageid='pid02', name='namep02', depends=mngr.Dependencies(), components=[self.c2])

        self.c3 = mngr.SubComponent(componentid='cid03', name='namec03')
        self.c4 = mngr.SubComponent(componentid='cid04', name='namec04', subcomponents=[self.c3])
        self.c5 = mngr.SubComponent(componentid='cid05', name='namec05', subcomponents=[self.c4])

        self.p3 = mngr.Package(packageid='pid03', name='namep03', depends=mngr.Dependencies(), components=[self.c5])

    def test_ajout_package(self):
        m = mngr.Manager()
        m.add_pkg(self.p1)
        self.assertIn(self.p1.id, m.availablepkg)
        m.add_pkg(self.p2)
        self.assertIn(self.p2.id, m.availablepkg)
        m.add_pkg(self.p3)
        self.assertIn(self.p3.id, m.availablepkg)

    def test_non_unique_id(self):
        m = mngr.Manager()
        m.add_pkg(self.p1)
        c = mngr.SubComponent(componentid="cid", name="namec")
        p = mngr.Package(packageid='pid01', name='namep', depends=mngr.Dependencies(), components=[c])
        with self.assertRaises(mngr.NonUniqueIDException):
            m.add_pkg(p)

    def test_select_package(self):
        m = mngr.Manager()
        m.add_pkg(self.p1)
        m.add_pkg(self.p3)
        m.select_pkg(self.p1, list(self.p1.get_childrens()))
        self.assertEqual(m.selectedpkg[self.p1.id].pkg, self.p1)
        self.assertEqual(set(m.selectedpkg[self.p1.id].components), set(self.p1.get_childrens()))

        m.select_pkg(self.p3, [self.c3, self.c5])
        self.assertEqual(m.selectedpkg[self.p3.id].pkg, self.p3)
        self.assertEqual(set(m.selectedpkg[self.p3.id].components), {self.c3, self.c5})

        m.select_pkg(self.p3, [self.c4, self.c5])
        self.assertEqual(m.selectedpkg[self.p3.id].pkg, self.p3)
        self.assertEqual(set(m.selectedpkg[self.p3.id].components), {self.c3, self.c4, self.c5})

    def test_unavailable_package(self):
        m = mngr.Manager()
        m.add_pkg(self.p1)
        m.add_pkg(self.p3)

        with self.assertRaises(mngr.UnavailablePackageException):
            m.select_pkg(self.p2, list(self.p2.get_childrens()))




class TestActionSort(unittest.TestCase):
    def setUp(self):
        def dummy_installmethod():
            pass

        self.down = mngr.InstallAction(installmethod=dummy_installmethod, args=[], id='Download', prev=[])
        self.ext = mngr.InstallAction(installmethod=dummy_installmethod, args=[], id='Extraction', prev=[self.down])

        self.m11 = mngr.InstallAction(installmethod=dummy_installmethod, args=[], id='m11', prev=[])
        self.m12 = mngr.InstallAction(installmethod=dummy_installmethod, args=[], id='m12', prev=[self.m11, self.down])
        self.m13 = mngr.InstallAction(installmethod=dummy_installmethod, args=[], id='m13', prev=[self.m12, self.ext])
        self.m21 = mngr.InstallAction(installmethod=dummy_installmethod, args=[], id='m21', prev=[])
        self.m22 = mngr.InstallAction(installmethod=dummy_installmethod, args=[], id='m22', prev=[self.m21, self.down])
        self.m23 = mngr.InstallAction(installmethod=dummy_installmethod, args=[], id='m23',
                                      prev=[self.m13, self.m22, self.ext])

        self.down.prev.extend([self.m11, self.m21])
        self.ext.prev.extend([self.m12, self.m22])

        self.actions = [self.down, self.ext, self.m23, self.m22, self.m21, self.m13, self.m12, self.m11]

    def test_sort(self):
        sortedActions = mngr.sortInstallActionList(self.actions)

        for action in self.actions:
            for prevaction in action.prev:
                with self.subTest(i=(action, prevaction)):
                    self.assertGreater(sortedActions.index(action), sortedActions.index(prevaction))

    def test_loop_detection(self):
        self.m22.prev.append(self.m23)

        with self.assertRaises(mngr.IncompatibleActionsException):
            mngr.sortInstallActionList(self.actions)

if __name__ == '__main__':
    log.info('Starting tests')
    unittest.main()

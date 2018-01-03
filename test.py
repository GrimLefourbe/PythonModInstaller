import logging.config
import json

import unittest

log = logging.getLogger(__name__)
logging.config.dictConfig(json.load(open('logging_config.json', 'r')))

import packagemanager as pm


class TestComponents(unittest.TestCase):
    def setUp(self):
        self.c1 = pm.Component(componentid='cid01', componentname='name01', subcomponents=[])
        self.c2 = pm.Component(componentid='cid02', componentname='name02', subcomponents=[])
        self.c3 = pm.Component(componentid='cid03', componentname='name03', subcomponents=[])
        self.c4 = pm.Component(componentid='cid04', componentname='name04', subcomponents=[self.c2, self.c3])
        self.c5 = pm.Component(componentid='cid05', componentname='name05', subcomponents=[])
        self.c6 = pm.Component(componentid='cid06', componentname='name06', subcomponents=[self.c5])
        self.c7 = pm.Component(componentid='cid07', componentname='name07', subcomponents=[self.c4, self.c6])

    def test_to_dict_simple(self):
        expected = {'id': 'cid01',
                    'name': 'name01',
                    'subcomponents': []}
        self.assertEqual(self.c1.to_dict(), expected)

    def test_to_dict_complex(self):
        expected = {'id': "cid07",
                    'name': "name07",
                    'subcomponents': [
                        {'id': 'cid04',
                         'name': 'name04',
                         'subcomponents': [
                             {'id': 'cid02',
                              'name': 'name02',
                              'subcomponents': []},
                             {'id': 'cid03',
                              'name': 'name03',
                              'subcomponents': []}]},
                        {'id': 'cid06',
                         'name': 'name06',
                         'subcomponents': [
                             {'id': 'cid05',
                              'name': 'name05',
                              'subcomponents': []}]}]}
        self.assertEqual(self.c7.to_dict(), expected)


class TestPackage(unittest.TestCase):
    def setUp(self):
        self.c1 = pm.Component(componentid='cid01', componentname='namec01', subcomponents=[])
        self.p1 = pm.Package(packageid='pid01', name='namep01', depends=[(pm.Dependencies(), ['all'])],
                             components=[self.c1])

        self.c2 = pm.Component(componentid='cid02', componentname='namec02', subcomponents=[])
        self.c3 = pm.Component(componentid='cid03', componentname='namec03', subcomponents=[])
        self.c4 = pm.Component(componentid='cid04', componentname='namec04', subcomponents=[self.c2, self.c3])
        self.c5 = pm.Component(componentid='cid05', componentname='namec05', subcomponents=[])
        self.c6 = pm.Component(componentid='cid06', componentname='namec06', subcomponents=[self.c5])

        self.p2 = pm.Package(packageid="pid02", name="namep02", depends=[(pm.Dependencies(), ["all"])],
                             components=[self.c4, self.c6])

    def test_to_dict_simple(self):
        expected = {'id': 'pid01',
                    'name': 'namep01',
                    'dependencies': [
                        {'involvedcomps': ['all'],
                         'dependency': {'requirements': [],
                                        'conflicts': [],
                                        'before': [],
                                        'after': []}}],
                    'components': [{'id': "cid01",
                                    'name': 'namec01',
                                    'subcomponents': []}]}
        self.assertEqual(self.p1.to_dict(), expected)

    def test_to_dict_complex(self):
        expected = {'id': 'pid02',
                    'name': 'namep02',
                    'dependencies': [
                        {'involvedcomps': ['all'],
                         'dependency': {'requirements': [],
                                        'conflicts': [],
                                        'before': [],
                                        'after': []}}],
                    'components': [{'id': 'cid04',
                                    'name': 'namec04',
                                    'subcomponents': [{'id': 'cid02',
                                                       'name': 'namec02',
                                                       'subcomponents': []},
                                                      {'id': 'cid03',
                                                       'name': 'namec03',
                                                       'subcomponents': []}]},
                                   {'id': 'cid06',
                                    'name': 'namec06',
                                    'subcomponents': [{'id': 'cid05',
                                                       'name': 'namec05',
                                                       'subcomponents': []}]}]}
        self.assertEqual(self.p2.to_dict(), expected)

    def test_import_export(self):
        pkgdict = {self.p1.id: self.p1, self.p2.id: self.p2}
        pm.Package.save_to_json({self.p1.id: self.p1, self.p2.id: self.p2}, 'test.json')
        pkgdictexp = pm.Package.load_from_json('test.json')
        self.assertEqual({pkg.id: pkg.to_dict() for pkg in pkgdict.values()},
                         {pkg.id: pkg.to_dict() for pkg in pkgdictexp.values()})


class TestActionSort(unittest.TestCase):
    def setUp(self):
        def dummy_installmethod():
            pass

        self.down = pm.InstallAction(installmethod=dummy_installmethod, prev=[], name='Download')
        self.ext = pm.InstallAction(installmethod=dummy_installmethod, prev=[self.down], name='Extraction')

        self.m11 = pm.InstallAction(installmethod=dummy_installmethod, prev=[], name='m11')
        self.m12 = pm.InstallAction(installmethod=dummy_installmethod, prev=[self.m11, self.down], name='m12')
        self.m13 = pm.InstallAction(installmethod=dummy_installmethod, prev=[self.m12, self.ext], name='m13')
        self.m21 = pm.InstallAction(installmethod=dummy_installmethod, prev=[], name='m21')
        self.m22 = pm.InstallAction(installmethod=dummy_installmethod, prev=[self.m21, self.down], name='m22')
        self.m23 = pm.InstallAction(installmethod=dummy_installmethod, prev=[self.m13, self.m22, self.ext], name='m23')

        self.down.prev.extend([self.m11, self.m21])
        self.ext.prev.extend([self.m12, self.m22])

        self.actions = [self.down, self.ext, self.m23, self.m22, self.m21, self.m13, self.m12, self.m11]

    def test_sort(self):
        sortedActions = pm.sortInstallActionList(self.actions)

        for action in self.actions:
            for prevaction in action.prev:
                with self.subTest(i=(action, prevaction)):
                    self.assertGreater(sortedActions.index(action), sortedActions.index(prevaction))

    def test_loop_detection(self):
        self.m22.prev.append(self.m23)
        self.assertRaises(pm.IncompatibleActionsException)

if __name__ == '__main__':
    log.info('Starting tests')
    unittest.main()

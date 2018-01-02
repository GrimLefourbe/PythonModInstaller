import logging.config
import json

import unittest

log = logging.getLogger(__name__)
logging.config.dictConfig(json.load(open('logging_config.json', 'r')))

import packagemanager as pm


def test_components():
    log.info('Starting component test')
    c1 = pm.Component(componentid='cid01', componentname="name01", subcomponents=[])
    log.debug('c1 created')
    log.info('Simple component creation tested')
    c1dict = c1.to_dict()
    try:
        assert c1dict == {'id': "cid01", 'name': 'name01', 'subcomponents': []}
        log.debug('c1 dict is as expected')
    except AssertionError:
        log.error('c1 dict is not as expected. c1dict : {}'.format(c1dict))
    log.info('Simple component export tested')
    log.info('Simple component tested')
    c11 = pm.Component(componentid="cid01", componentname="name01", subcomponents=[])
    log.debug('c11 created')
    c12 = pm.Component(componentid="cid02", componentname="name02", subcomponents=[])
    log.debug('c12 created')
    c13 = pm.Component(componentid="cid03", componentname="name03", subcomponents=[c11, c12])
    log.debug('c13 created')
    c14 = pm.Component(componentid="cid04", componentname="name04", subcomponents=[])
    log.debug('c14 created')
    c15 = pm.Component(componentid="cid05", componentname="name05", subcomponents=[c14])
    log.debug('c15 created')
    c16 = pm.Component(componentid="cid06", componentname="name06", subcomponents=[c13, c15])
    log.debug('c16 created')

    log.info('Complex component creation tested')

    c16dict = c16.to_dict()
    try:
        assert c16dict == {'id': "cid06",
                           'name': "name06",
                           'subcomponents': [
                               {'id': 'cid03',
                                'name': 'name03',
                                'subcomponents': [
                                    {'id': 'cid01',
                                     'name': 'name01',
                                     'subcomponents': []},
                                    {'id': 'cid02',
                                     'name': 'name02',
                                     'subcomponents': []}]},
                               {'id': 'cid05',
                                'name': 'name05',
                                'subcomponents': [
                                    {'id': 'cid04',
                                     'name': 'name04',
                                     'subcomponents': []}]}]}
        log.debug('c16 is as expected')
    except AssertionError:
        log.error('c16 dict is not as expected. c16dict : {}'.format(c16dict))
    log.info('Complex component export tested')
    log.info('Complex component tested')
    log.info('Done testing components')


def test_package():
    log.info('Starting package test')
    c1 = pm.Component(componentid="cid01", componentname="name01", subcomponents=[])
    log.debug('c1 created')
    p1 = pm.Package(packageid="pid01", name="name02", depends=[(pm.Dependencies(), ["all"])], components=[c1])
    log.debug('p1 created')
    log.info('Simple package creation tested')
    p1dict = p1.to_dict()
    try:
        assert p1dict == {'id': 'pid01',
                          'name': 'name02',
                          'dependencies': [
                              {'components': ['all'],
                               'dep': {'requirements': [],
                                       'conflicts': [],
                                       'before': [],
                                       'after': []}}],
                          'components': [{'id': "cid01",
                                          'name': 'name01',
                                          'subcomponents': []}]}
        log.debug('p1dict is as expected')
    except AssertionError:
        log.error('p1dict is not as expected. p1dict : {}'.format(p1dict))
    log.debug('testing export to json')
    pm.Package.save_to_json({'pid01': p1}, 'test.json')
    log.info('Simple package export tested')
    p1reconst = pm.Package.load_from_json('test.json')

    try:
        assert p1reconst['pid01'].to_dict() == p1.to_dict()
        log.debug('p1reconst is equal to p1')
    except AssertionError:
        log.error('p1reconst is not equal to p1')
    log.info('simple package import tested')
    log.info('Simple package tested')

    c11 = pm.Component(componentid="cid02", componentname="name02", subcomponents=[])
    log.debug('c11 created')
    c12 = pm.Component(componentid="cid03", componentname="name03", subcomponents=[])
    log.debug('c12 created')
    c13 = pm.Component(componentid="cid04", componentname="name04", subcomponents=[c11, c12])
    log.debug('c13 created')
    c14 = pm.Component(componentid="cid05", componentname="name05", subcomponents=[])
    log.debug('c14 created')
    c15 = pm.Component(componentid="cid06", componentname="name06", subcomponents=[c14])
    log.debug('c15 created')

    p2 = pm.Package(packageid="pid02", name="name07", depends=[(pm.Dependencies(), ["all"])], components=[c13, c15])
    log.debug('p2 created')

    log.info('Complex package creation tested')

    p2dict = p2.to_dict()
    try:
        assert p2dict == {'id': 'pid02',
                          'name': 'name07',
                          'dependencies': [
                              {'components': ['all'],
                               'dep': {'requirements': [],
                                       'conflicts': [],
                                       'before': [],
                                       'after': []}}],
                          'components': [{'id': 'cid04',
                                          'name': 'name04',
                                          'subcomponents': [{'id': 'cid02',
                                                             'name': 'name02',
                                                             'subcomponents': []},
                                                            {'id': 'cid03',
                                                             'name': 'name03',
                                                             'subcomponents': []}]},
                                         {'id': 'cid06',
                                          'name': 'name06',
                                          'subcomponents': [{'id': 'cid05',
                                                             'name': 'name05',
                                                             'subcomponents': []}]}]}
        log.debug('p2 dict is as expected')
    except AssertionError:
        log.error('p2 dict is not as expected. p2dict : {}'.format(p2dict))
    log.debug('testing export to json')
    p2.save_to_json({'pid01': p1, 'pid02': p2}, 'test.json')
    log.info('Complex package export tested')
    log.info('Complex package tested')
    log.info('Done testing package')



def test_action_sort():
    log.info('Starting action sort test')

    def dummy_installmethod():
        pass

    down = pm.InstallAction(installmethod=dummy_installmethod, prev=[], name='Download')
    ext = pm.InstallAction(installmethod=dummy_installmethod, prev=[down], name='Extraction')

    m11 = pm.InstallAction(installmethod=dummy_installmethod, prev=[], name='m11')
    log.debug('m11 created')
    m12 = pm.InstallAction(installmethod=dummy_installmethod, prev=[m11, down], name='m12')
    log.debug('m12 created')
    m13 = pm.InstallAction(installmethod=dummy_installmethod, prev=[m12, ext], name='m13')
    log.debug('m13 created')
    m21 = pm.InstallAction(installmethod=dummy_installmethod, prev=[], name='m21')
    log.debug('m21 created')
    m22 = pm.InstallAction(installmethod=dummy_installmethod, prev=[m21, down], name='m22')
    log.debug('m22 created')
    m23 = pm.InstallAction(installmethod=dummy_installmethod, prev=[m13, m22, ext], name='m23')
    log.debug('m23 created')

    down.prev.extend([m11, m21])
    ext.prev.extend([m12, m22])

    actions = [down, ext, m23, m22, m21, m13, m12, m11]

    sortedActions = pm.sortInstallActionList(actions)

    log.debug('sorted actions : {}'.format([a.name for a in sortedActions]))

    m22.prev.append(m23)

    try:
        log.error("Incompatible actions aren't detected".format(pm.sortInstallActionList(actions)))
    except pm.IncompatibleActionsException:
        log.info('Incompatible actions detection successful')
    log.info('Done testing action sort')

if __name__ == '__main__':
    log.info('Starting tests')
    try:
        test_components()
        test_package()
        test_action_sort()
    except Exception:
        log.exception('Unkown Error')

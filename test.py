import logging.config
import json

log = logging.getLogger(__name__)
logging.config.dictConfig(json.load(open('logging_config.json', 'r')))

import packagemanager as pm


def test_package():
    log.info('Starting package test')
    c1 = pm.Component(componentid="cid01", componentname="name01", subcomponents=[])
    log.debug('c1 created')
    p1 = pm.Package(packageid="pid01", name="name02", depends=[(pm.Dependencies(), ["all"])], components=[c1])
    log.debug('p1 created')
    log.info('Simple package creation tested')

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
    test_package()
    test_action_sort()

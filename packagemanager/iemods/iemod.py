import logging
from typing import List, Dict, Any, Tuple

from packagemanager.manager import Package, Dependencies, Component, SubComponent

from packagemanager import tools
from packagemanager.manager import InstallAction


class IEMod(Package):
    def __init__(self, packageid: str, name: str, depends: Dependencies, components: List[SubComponent],
                 versionno: str, downloadurl: str, readmeurl: str = None, desc: str = None):
        super().__init__(packageid, name, depends, components)

        log = logging.getLogger(__name__)
        log.debug('Parsing versionno {}'.format(versionno))
        self.version = tools.parse(versionno)
        self.downloadurl = downloadurl
        self.readmeurl = readmeurl
        self.desc = desc

    def to_dict(self):
        d = super().to_dict()
        d['version'] = str(self.version)
        d['downloadurl'] = self.downloadurl
        d['readmeurl'] = self.readmeurl
        d['desc'] = self.desc

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "IEMod":
        return cls(packageid=d['id'],
                   name=d['name'],
                   depends=Dependencies.from_dict(d['dependencies']),
                   components=[Component.from_dict(comp) for comp in d['components']],
                   versionno=d['version'],
                   downloadurl=d['downloadurl'],
                   readmeurl=d['readmeurl'],
                   desc=d['desc'])

    def generate_install_actions(self, comp: List[SubComponent]) -> List[InstallAction]:
        actions = []
        dlAction = InstallAction(installmethod=tools.download.DownloadFile,
                                 args=[self.downloadurl, "_".join([self.id, str(self.version)])],
                                 id='Download {}'.format(self.name),
                                 prev=[])
        actions.append(dlAction)
        return actions

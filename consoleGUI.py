import logging.config
import json

from packagemanager import manager as mngr, iemods

log = logging.getLogger(__name__)
logging.config.dictConfig(json.load(open('logging_config.json', 'r')))


class BWSconsoleGUI:
    def __init__(self):
        self.mngr = mngr.Manager()

    def load_mods(self, filename):
        mods = iemods.IEMod.load_from_json(filename)
        for mod in mods.values():
            self.mngr.add_pkg(mod)

    def display_available_mods(self):
        print('Available mods')
        for mod in list(self.mngr.availablepkg.values()):
            self.display_mod(mod)
            print('\n')

    def display_mod(self, mod: iemods.IEMod, indent=0):
        indentstr = ' ' * indent
        print(indentstr + mod.name + ' : ' + mod.id)
        print(indentstr + mod.desc)
        print(indentstr + str(mod.version))
        print(indentstr + 'Components :')
        for c in mod.subcomponents:
            self.display_component(c, indent + 4)
        print(indentstr + mod.downloadurl)
        print(indentstr + mod.readmeurl)

    def display_component(self, comp: mngr.Component, indent=0):
        indentstr = ' ' * indent
        print(indentstr + comp.name)
        for c in comp.subcomponents:
            self.display_component(c, indent + 4)

    def display_selected_mods(self):
        for selection in self.mngr.selectedpkg.values():
            print(selection.pkg.name)
            for c in selection.components:
                print(' ' * 4 + c.name)

    def pick_mod(self):
        choice = input('Write the Mod ID:')

        if choice not in self.mngr.availablepkg:
            return
        mod = self.mngr.availablepkg[choice]
        comps = list(mod.get_childrens())
        for i, comp in enumerate(comps):
            print('{}: '.format(i + 1) + comp.name)
        selection = []
        while True:
            compchoice = int(input('Give number of component to pick (-1 to stop)'))
            if compchoice == -1:
                break
            if compchoice < 1 or compchoice > len(comps):
                break
            selection.append(comps[compchoice])
        self.mngr.select_pkg(mod, selection)

    def install_current(self):
        self.mngr.generate_action_list()
        for action in self.mngr.installActions:
            action.execute()

    def main_menu(self):
        while True:
            choice = int(input('1. Display Mods\n'
                               '2. Display currently selected mods\n'
                               '3. Pick Mod\n'
                               '4. Install Current Selection\n'
                               '5. Exit\n'))
            if choice < 1 or choice > 5:
                continue
            if choice == 1:
                self.display_available_mods()
            elif choice == 2:
                self.display_selected_mods()
            elif choice == 3:
                self.pick_mod()
            elif choice == 4:
                self.install_current()
            elif choice == 5:
                break


if __name__ == '__main__':
    log.info('Starting console-based GUI')
    gui = BWSconsoleGUI()
    gui.load_mods('Config/mods.json')
    gui.main_menu()


"""
yorick.py

Entry package for remapping biped motion to bone motion.
You should start reading from here.

Usage
 - In MaxScript Editor,
   python.ExecuteFile "{PATH_TO_HERE}\yorick.py"

Dependencies
 - Intended to be used in 3dsMax. Please read yorick_service.py
 - PyQt4
 - Expect to maintain ./uidef/Biped2Bone.ui file

TODO:
 - package requirements(requirement)


author: minu jeong
date: Nov. 2016

All Copyrights Reserved, (C) Maverick Games, 2017
"""

# python built-ins
import os
import sys
import inspect
from functools import partial

# paths
package_dir = os.path.dirname(__file__)
sys.path.append(package_dir)

# PySide
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMainWindow
from PySide2.QtCore import Qt

from uidef import biped2bone

# package
import uisetup
import yorick_service

reload(biped2bone)
reload(uisetup)
reload(yorick_service)


class UISetup:
    """ manage connections of signals and slots of ui components.
        just add a new class of component name in uisetup.py, and \
        add method of signal name to add connection. """

    app = None
    handlers = {}

    def setup(self, app):
        """ Initialize here.
            called from Biped2Bone class. """

        self.app = app

        # hand in cached ui handlers
        uisetup.uisetup = self

        for class_name in dir(uisetup):
            if not self.isvalidcomponentdef(class_name):
                continue

            self.connect(class_name)

    def connect(self, componentname):
        """ connect using reflection of uisetup package """

        component = getattr(self.app, componentname)
        componentdef = getattr(uisetup, componentname)

        if (not componentdef) or (not component):
            return

        if componentdef not in self.handlers:
            self.handlers[componentdef] = componentdef(component)
        componentdef_instance = self.handlers[componentdef]

        def slot_gen(slotmethod, componentname, sender):
            """ a closure for generate qt slot method.
                executed when signal emits """

            method = getattr(componentdef_instance, slotmethod)
            if not inspect.ismethod(method):
                return
            method()

        for method in dir(componentdef_instance):

            if method.startswith("__"):
                continue

            if not hasattr(component, method) or \
               not hasattr(componentdef_instance, method):
                continue

            signal = getattr(component, method)
            signal.connect(partial(slot_gen, method, componentname))

    def isvalidcomponentdef(self, componentname):
        """ escape connecting if conditions not satisfied """

        if not self.app:
            return False

        if componentname.startswith("__"):
            return False

        componentdef = getattr(uisetup, componentname)
        if not inspect.isclass(componentdef):
            return False

        if not hasattr(self.app, componentname):
            return False

        return True

    def getui(self, uitype):
        if uitype not in self.handlers:
            return None
        return self.handlers[uitype]


class Biped2Bone(biped2bone.Ui_MainWindow):
    """ Application entry class using QT widgets. """

    instance = None
    uisetup = None

    def __init__(self, mainwin):

        yorick_service.Service.mainwindow = self
        Biped2Bone.instance = self

        flags = mainwin.windowFlags()
        mainwin.setWindowFlags(flags | Qt.WindowStaysOnTopHint)

        # load qt ui
        self.setupUi(mainwin)

        # setup ui
        self.uisetup = UISetup()
        self.uisetup.setup(self)


def entry():
    print("Running yorick.py..")

    # This block will remove intermittent crash
    # Please refer to 3dsMax documentation
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication([])
    qmainwin = QMainWindow()

    try:
        global tool
    except:
        pass

    # initialize
    try:
        tool = Biped2Bone(qmainwin)
        qmainwin.show()
        print("Tool initialized")
    except Exception as e:
        print(e)

    qapp.exec_()

# entry point here
if __name__ == "__main__":
    entry()

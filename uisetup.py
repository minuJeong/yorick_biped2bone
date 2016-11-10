
"""
uisetup.py

this package defines how ui components should be initialized.
class names should be matching with object names of QT ui definition file,
and method names should be matching with slots of signals.
Please consider read PyQt4 documentation for further information.

QTDesigner generated file: ./uidef/Biped2Bone.ui


author: minu jeong
date: Nov. 2016

All Copyrights Reserved, (C) Maverick Games, 2016
"""

import sys
from functools import partial

from PyQt4.QtGui import QTreeWidgetItem

# packages
import yorick_service
reload(yorick_service)


# set from yorick package
uisetup = None


def getui(uiname):
    if not uisetup:
        print("uisetup is not set")
        return None

    thismodule = sys.modules[__name__]
    if not hasattr(thismodule, uiname):
        return None

    return uisetup.getui(
        getattr(thismodule, uiname)
    )


class __uicompbase(object):
    widget = None

    def __init__(self):
        raise Exception("Consider this class as abstract")


class JointListView(__uicompbase):

    datacontainer = None
    item_to_node = {}

    def __init__(self, widget, DataControl):
        """ biped list control """
        self.widget = widget
        self._reload(DataControl)

    def _unload(self):
        self.datacontainer = None
        self.widget.clear()

    def _reload(self, DataControl):
        self._unload()
        self._load(DataControl)
        self.expandall()

    def _load(self, DataControl):
        """ consider as protected member.
            instead of calling it directly from outside,
            add 'reload' method to call this.

            read 'l_BipedList' class for example. """

        self._unload()

        self.datacontainer = DataControl()

        # get node mapping data from service
        rootnode = self.datacontainer.gather()
        if not rootnode:
            return

        self._map_treeitems(rootnode)

    def _map_treeitems(self, rootnode):
        """ rootnode: yorick_service.Nodes.Node """

        # PyQt4 is designed to add top level item alone
        rootitem = QTreeWidgetItem(self.widget)
        rootitem.setText(0, rootnode.node_name)
        self.widget.addTopLevelItem(rootitem)

        # add children widget items recursively
        def gen_child(parent, node):
            child = QTreeWidgetItem(parent)
            child.setText(0, node.node_name)

            self.item_to_node[child] = node
            node.listitem = child

            # partial to generate gen_child recurse
            map(partial(gen_child, child), node.children)
            return child

        rootitem.addChildren(
            list(map(partial(gen_child, rootitem), rootnode.children))
        )

    def expandall(self):
        self.widget.expandAll()

    def collapseall(self):
        self.widget.collapseAll()

    def get_selectednode(self):
        selections = self.widget.selectedItems()
        if not selections:
            return None

        selected = selections[0]
        if not selected:
            return None

        return self.item_to_node[selected]


class l_BipedList(JointListView):
    """ Biped List Handler
        handles listing scene assets and let user select biped root. """

    # reference cache
    selection_required_buttons = None

    def __init__(self, widget):
        super(l_BipedList, self).__init__(
            widget,
            yorick_service.BipedData
        )

        self.widget.selectionChanged = self.on_changeselect

        self.selection_required_buttons = [
            getui("b_GenBones"),
            getui("b_CopyMotions")
        ]

    def on_changeselect(self, selected, deselected):

        # disable all buttons
        map(lambda x: x.disable(),
            self.selection_required_buttons)

        selections = self.widget.selectedItems()
        if not selections:
            return

        selected = selections[0]
        if not selected:
            return

        # enable all buttons
        map(lambda x: x.enable(),
            self.selection_required_buttons)

    def reload(self):
        self._reload(yorick_service.BipedData)

    def unload(self):
        self._unload()


class l_BoneList(JointListView):
    """ Bone List Handler
        handles listing and editting generated bone nodes. """

    rename_rule = None

    def __init__(self, widget):
        super(l_BoneList, self).__init__(
            widget,
            yorick_service.BoneData
        )

    def reload(self):
        self._reload(yorick_service.BoneData)

    def unload(self):
        self._unload()

    def map_node(self, rootnode):
        self._unload()
        self._map_treeitems(rootnode)


class __DisableableButton(object):
    """ consider as abstract class
        handles enable/disable button """

    enabletext = "ENABLED"
    disabletext = "DISABLED"

    def disable(self):
        self.widget.setText(self.disabletext)
        self.widget.setEnabled(False)

    def enable(self):
        self.widget.setText(self.enabletext)
        self.widget.setEnabled(True)


class b_GenBones(__DisableableButton):

    def __init__(self, widget):
        self.widget = widget

        self.enabletext = "Generate Bones"
        self.disabletext = "Select Biped.."

        self.disable()

    def clicked(self):
        bipedlist_comp = getui("l_BipedList")
        bonelist_comp = getui("l_BoneList")

        # read rename rule
        bonelist_comp.rename_rule = \
            yorick_service.Biped2BoneRenameRule(
                getui("le_rename_from"),
                getui("le_rename_to")
            )

        # start generate (high overhead)
        newroot = bonelist_comp.datacontainer.generate(
            bipedlist_comp.get_selectednode(),
            bonelist_comp.rename_rule
        )

        # add items to treeview
        bonelist_comp.map_node(newroot)
        bonelist_comp.expandall()


class b_CopyMotions(__DisableableButton):

    def __init__(self, widget):
        self.widget = widget

        self.enabletext = "Copy Motions"
        self.disabletext = "Select Biped.."

        self.disable()

    def clicked(self):
        print("Copy motion!")


class b_Reload:

    def __init__(self, widget):
        self.widget = widget

    def clicked(self):
        print("Reloading scene..")
        getui("l_BipedList").reload()


class b_Unload:

    def __init__(self, widget):
        self.widget = widget

    def clicked(self):
        print("Unloading scene..")
        getui("l_BipedList").unload()


class b_Expand:

    def __init__(self, widget):
        self.widget = widget

    def clicked(self):
        getui("l_BipedList").expandall()
        getui("l_BoneList").expandall()


class b_Collapse:

    def __init__(self, widget):
        self.widget = widget

    def clicked(self):
        getui("l_BipedList").collapseall()
        getui("l_BoneList").collapseall()


class le_rename_from:

    def __init__(self, widget):
        self.widget = widget


class le_rename_to:

    def __init__(self, widget):
        self.widget = widget

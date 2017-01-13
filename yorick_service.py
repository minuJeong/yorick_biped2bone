
"""
this package defines the terminal actions of this application.
Intention of splitting this package is, to enable reuse of other codes \
for other platforms, like Maya.
So, every code depending on 3dsMax should be placed here.


author: minu jeong
date: Nov. 2016

All Copyrights Reserved, (C) Maverick Games, 2016
"""

from functools import partial

# 3dsMax
import MaxPlus


class ServiceBase:
    """ base class for sub-services
         - for future convenience """
    pass


class Service(ServiceBase):
    """ Service reference container. consider as static class """

    # public:
    mainwindow = None

    # private:
    _services = {}

    def __init__(self):
        raise Exception("consider Service as static class")

    @staticmethod
    def Application():
        if Application not in Service._services:
            Service._services[Application] = Application(
                Service.mainwindow
            )
        return Service._services[Application]


# [DEPRECATED] maybe can be removed
class Application(ServiceBase):
    """ sub-service for handles application wide actions """

    mainwindow = None

    def __init__(self, mainwindow):
        self.mainwindow = mainwindow


class Nodes:
    """ data model for node gatherer
        gather nodes from 3dsMax scene """

    class Node(object):
        children = []
        parent = None

        node_in_max = None

        def __init__(self, parent=None):
            self.override_parent(parent)

        def override_parent(self, parent):
            self.parent = parent
            if parent:
                if not parent.children:
                    parent.children = []
                parent.children.append(self)

        def map_node(self, maxnode):
            """ maxnode is MaxPlus INode,
                children are abstract nodes """

            self.node_in_max = maxnode
            self.children = []

            maxnode_num_children = maxnode.GetNumChildren()
            for maxnode_child_index in range(maxnode_num_children):
                childnode = Nodes.Node(self)
                childnode.map_node(
                    maxnode.GetChild(maxnode_child_index)
                )

        @property
        def node_name(self):
            if not self.node_in_max:
                return "UNNAMED_NODE"
            return self.node_in_max.GetName()

        @property
        def worldpos(self):
            return self.node_in_max.GetWorldPosition()

        @worldpos.setter
        def worldpos(self, value):
            self.node_in_max.SetWorldPosition(value)

        def clone(self, parent=None):
            return Nodes.Node(parent)

        def __repr__(self):
            return self.node_name

    rootnode = None

    def gather(self):
        self.rootnode = None
        return self._gather()

    def mapallscene(self):
        """ read all scene nodes, and returns as structured nodes """

        self.rootnode = Nodes.Node()
        rootnode_max = MaxPlus.Core.GetRootNode()

        # recursively add all children nodes here
        if rootnode_max:
            self.rootnode.map_node(
                rootnode_max
            )

        return self.rootnode

    def _gather(self):
        """ override this """
        pass


class BipedData(Nodes):

    def _gather(self):
        return self.mapallscene()


class BoneData(Nodes):

    def _gather(self):
        """ bone data does not need to gather anything """
        return None

    def generate(self, biped_node, renamerule):
        """ recursively clone nodes and create bones """

        def assign_node_in_max(old_child, new_child):
            newname = renamerule.rename(old_child.node_name)
            new_child.node_in_max = MaxScript.CreateBone(
                                        old_child,
                                        new_child.parent,
                                        newname
                                    )
            return new_child

        def recurse_copychild(old_parent, new_parent):
            for old_child in old_parent.children:
                new_child = old_child.clone(new_parent)
                new_bone_node = assign_node_in_max(old_child, new_child)

                # connect max-hierarchy
                new_bone_node.node_in_max.SetParent(new_parent.node_in_max)

                # recurse
                recurse_copychild(old_child, new_child)

        new_root = biped_node.clone()
        new_root.override_parent(None)
        assign_node_in_max(biped_node, new_root)
        recurse_copychild(biped_node, new_root)

        return new_root


class Biped2BoneRenameRule(ServiceBase):
    """ connection from user line edit top service,
        held by l_BoneList widget """

    lineedit_fromstring = None
    lineedit_tostring = None

    def __init__(self,
                 lineedit_fromstring,
                 lineedit_tostring):
        self.lineedit_fromstring = lineedit_fromstring
        self.lineedit_tostring = lineedit_tostring

    @property
    def fromstring(self):
        if not self.lineedit_fromstring:
            return ""
        return str(self.lineedit_fromstring.widget.text())

    @property
    def tostring(self):
        if not self.lineedit_tostring:
            return ""
        return str(self.lineedit_tostring.widget.text())

    def rename(self, org_name):
        """ from user input, read rename rule """

        return org_name.replace(
            self.fromstring, self.tostring
        )


class MaxScript(ServiceBase):

    @staticmethod
    def CreateBone(old_node, parent_node=None, newname=None):
        def maxify_point3(point):
            return "[{}, {}, {}]".format(
                point.GetX(), point.GetY(), point.GetZ()
            )

        pos_1 = maxify_point3(old_node.worldpos)
        pos_2 = pos_1
        zaxis = "[0, 0, 1]"

        if old_node.children:
            pos_2 = maxify_point3(old_node.children[0].worldpos)

        if old_node.node_in_max:
            axis_type = old_node.node_in_max.GetBoneAxis()
            if axis_type == 0:
                zaxis = maxify_point3(MaxPlus.Point3(0, 0, 1))
            else:
                raise Exception("Not implemented!")

        # generate maxscript
        gen_script = \
            "BoneSys.createBone {} {} {}".format(pos_1, pos_2, zaxis)

        # try to create bone, escape on fail
        fbnode = MaxPlus.Core.EvalMAXScript(gen_script)
        if not fbnode:
            return None

        maxnode = fbnode.GetNode()
        maxnode.SetName(newname or old_node.node_name)
        return maxnode

    @staticmethod
    def CopyMotions(from_rootnode, to_rootnode):
        if not from_rootnode or not to_rootnode:
           print("Please select root nodes above.")
           return

        def copymotion_recurse_children(from_node, to_node):
            if not from_node.node_in_max or \
               not to_node.node_in_max:
                return

            to_node.node_in_max.Transform = from_node.node_in_max.Transform

            # recurse children zipped
            if from_node.children:
                list(map(
                    lambda x: copymotion_recurse_children(*x),
                    zip(
                        from_node.children,
                        to_node.children
                    )
                ))

        animation_range = MaxPlus.Animation.GetAnimRange()
        starttime = animation_range.Start() / 160
        endtime = animation_range.End() / 160

        MaxSceneControl.GoToAndStop(0)
        MaxPlus.Animation.SetAnimateButtonState(True)
        for frame in range(starttime, endtime + 1):
            MaxSceneControl.GoToAndStop(frame)
            copymotion_recurse_children(from_rootnode, to_rootnode)

        MaxSceneControl.GoToAndStop(0)
        MaxPlus.Animation.SetAnimateButtonState(False)


class MaxSceneControl(ServiceBase):

    TICKS = 160

    @staticmethod
    def SelectInScene(node):
        if not node:
            return

        if node.node_in_max:
            MaxPlus.SelectionManager_SelectNode(node.node_in_max)

    @staticmethod
    def GoToAndStop(key):
        anim = MaxPlus.Animation
        anim.SetTime(key * MaxSceneControl.TICKS)

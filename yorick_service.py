
"""
this package defines the terminal actions of this application.
Intention of splitting this package is, to enable reuse of other codes \
for other platforms, like Maya.
So, every code depending on 3dsMax should be placed here.


author: minu jeong
date: Nov. 2016

All Copyrights Reserved, (C) Maverick Games, 2016
"""


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

    class Node:
        children = []
        parent = None

        node_in_max = None
        listitem = None

        def __init__(self, parent=None):
            self.parent = parent

        def map_node(self, node_max):
            """ node in argument is 3dsMax node,
                children are abstract nodes """

            self.node_in_max = node_max
            self.children = []

            for i in range(node_max.GetNumChildren()):
                childnode = Nodes.Node(self)
                childnode.map_node(node_max.GetChild(i))
                self.children.append(childnode)

        @property
        def node_name(self):
            return self.node_in_max.GetName()

        @property
        def worldpos(self):
            return self.node_in_max.GetWorldPosition()

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

    def generate(self, rootnode, renamerule):
        """ recursively clone nodes and create bones """

        def clone_node(old_bipednode, parent=None):
            """ node_in_max is copied, but will be replaced while recurse """

            new_bonenode = Nodes.Node(parent)
            new_bonenode.children = old_bipednode.children
            new_bonenode.node_in_max = old_bipednode.node_in_max

            return new_bonenode

        def recurse(parentnode):
            """ will be called recursively.
                parentnode should be cloned before here """

            # try create bone
            newname = renamerule.rename(parentnode.node_name)
            created_bone = MaxScript.CreateBone(parentnode, newname)
            if not created_bone:
                return

            # reassign max node
            parentnode.node_in_max = created_bone
            if not parentnode.children:
                return

            oldchildren = parentnode.children[:]
            parentnode.children = []
            # recurse children
            for node in oldchildren:
                newchild = clone_node(node, parentnode)
                parentnode.children.append(newchild)
                recurse(newchild)

        # clone children, and start recursive
        newroot = clone_node(rootnode)
        recurse(newroot)

        return newroot


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
    def CreateBone(basenode, newname=None):
        def maxify_point3(point):
            return "[{}, {}, {}]".format(
                point.GetX(), point.GetY(), point.GetZ()
            )

        pos_1 = maxify_point3(basenode.worldpos)
        pos_2 = "[0, 0, 0]"

        if basenode.parent and basenode.parent.worldpos:
            pos_2 = maxify_point3(basenode.parent.worldpos)

        gen_script = "BoneSys.createBone {} {} [0, 0, 1]".format(pos_1, pos_2)

        # try to create bone, escape on fail
        fbnode = MaxPlus.Core.EvalMAXScript(gen_script)
        if not fbnode:
            return None

        node = fbnode.GetNode()
        node.SetName(newname or basenode.node_name)

        # connect parenting information
        if basenode.parent and basenode.parent.node_in_max:
            node.SetParent(basenode.parent.node_in_max)

        return node

    @staticmethod
    def CopyMotion(from_rootnode, to_rootnode):
        print(from_rootnode, to_rootnode)

class MaxSceneControl(ServiceBase):

    TICKS = 160

    @staticmethod
    def SelectInScene(node):
        if not node:
            return

        MaxPlus.SelectionManager_SelectNode(node.node_in_max)

    @staticmethod
    def GoToAndStop(key):
        anim = MaxPlus.Animation
        anim.SetTime(key * MaxSceneControl.TICKS)

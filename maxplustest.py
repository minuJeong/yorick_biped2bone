
import MaxPlus


script = """
BoneSys.createBone [0, 0, 0] [1, 1, 1] [0, 0, 0]
"""

fpv = MaxPlus.Core.EvalMAXScript(script)
print(fpv.GetNode())


def get_classname_by_classid(self, classid):
    classes = MaxPlus.PluginManager.GetClassList().Classes
    for classinfo in classes:
        thisid = classinfo.GetClassId()
        if str(thisid) == str(classid):
            return classinfo.GetName()
    return None


def get_classsid_by_classname(self, classname):
    classes = MaxPlus.PluginManager.GetClassList().Classes
    for classinfo in classes:
        thisname = classinfo.GetName()
        if str(thisname) == str(classname):
            return classinfo.GetSuperClassId(), classinfo.GetClassId()
    return None, None

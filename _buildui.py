
import os

from pyside2uic import compileUiDir
from pyside2uic import compileUi


dirname = os.path.dirname(__file__)
with open("{}/uidef/biped2bone.py".format(dirname), 'w') as fp:
    compileUi("{}/uidef/Biped2Bone.ui".format(dirname), fp)
# compileUiDir("{}/uidef".format(os.path.dirname(__file__)))

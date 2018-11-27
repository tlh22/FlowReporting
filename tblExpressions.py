#from qgis.utils import qgsfunction

import qgis

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
import math
from geomGen import genGeom

import sys


""" ****************************** """


@qgsfunction(args='auto', group='tblLabel', usesgeometry=True, register=True)
def tblDisplay(feature, parent):
    try:
        res = genGeom.displayTable(feature)
    except:
        QgsMessageLog.logMessage('generate_display_geometry error in expression function: {}'.format(sys.exc_info()[0]), tag="TOMs panel")

    return res

functions = [
    tblDisplay
]

def registerFunctions():

    tbl_list = QgsExpression.Functions()

    for func in functions:
        QgsMessageLog.logMessage("Considering function {}".format(func.name()), tag="TOMs panel")
        try:
            if func in tbl_list:
                QgsExpression.unregisterFunction(func.name())
                #del toms_list[func.name()]
        except AttributeError:
            #qgis.toms_functions = dict()
            pass

        if QgsExpression.registerFunction(func):
            QgsMessageLog.logMessage("Registered expression function {}".format(func.name()), tag="TOMs panel")
            #qgis.toms_functions[func.name()] = func

    """for title in qgis.toms_functions:
        QgsMessageLog.logMessage("toms_functions function {}".format(title), tag="TOMs panel")

    for title2 in toms_list:
        QgsMessageLog.logMessage("toms_list function {}".format(title2.name()), tag="TOMs panel")"""

def unregisterFunctions():
    # Unload all the functions that we created.
    for func in functions:
        QgsExpression.unregisterFunction(func.name())
        QgsMessageLog.logMessage("Unregistered expression function {}".format(func.name()), tag="TOMs panel")
        #del qgis.toms_functions[func.name()]

    QgsExpression.cleanRegisteredFunctions()

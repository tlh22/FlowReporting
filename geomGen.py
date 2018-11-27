#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------
# Tim Hancock 2017

from PyQt4.QtGui import (
    QMessageBox
)

from qgis.core import (
    QgsExpressionContextUtils,
    QgsMapLayerRegistry,
    QgsMessageLog,
    QgsFeature,
    QgsGeometry,
    QgsFeatureRequest,
    QgsPoint,
    QgsRectangle,
    QgsVectorLayer
    # QgsWkbTypes
)

from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

import math
from cmath import rect, phase
from formOpen_Table import formOpen_Table

class genGeom:

    @staticmethod
    def displayTable(feature):
        formOpen_Table.formOpen_Table(feature)

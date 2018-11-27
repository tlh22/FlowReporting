# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tblLabel_TH
                                 A QGIS plugin
 vv
                             -------------------
        begin                : 2018-11-13
        copyright            : (C) 2018 by TH
        email                : th
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load tblLabel_TH class from file tblLabel_TH.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .tblLabel_TH import tblLabel_TH
    return tblLabel_TH(iface)

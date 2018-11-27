# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------
# Tim Hancock 2018
"""
Adapted from http://nathanw.net/2011/09/05/qgis-tips-custom-feature-forms-with-python-logic/

and also ...


https://medspx.fr/blog/Qgis/better_qgis_forms_part_three/

"""

# DEBUGMODE = True

from PyQt4.QtGui import (
    QMessageBox,
    QPixmap,
    QDialog,
    QLabel,
    QTableWidget
)

from qgis.core import (
    QgsMessageLog,
    QgsExpressionContextUtils
)

import os


@staticmethod
def formOpen_Table(feature):
    """
    Code that runs when the form is opened.
    """

    if not feature.isValid():
        return

    DIALOG = dialog
    TABLE = DIALOG.findChild(QTableWidget, "tbl_Peds")

    QgsMessageLog.logMessage("In formOpen_Table: ", tag="TOMs panel")

    # self.shownField = "NrPeds"

    # Somehow get the site number from the feature ...
    siteNr = 1

    if QgsMapLayerRegistry.instance().mapLayersByName("PedValues"):
        VALUES = QgsMapLayerRegistry.instance().mapLayersByName("PedValues")[0]
    else:
        QMessageBox.information(self.iface.mainWindow(), "ERROR", ("Table PedValues is not present"))
        found = False

    '''Fill the QTableWidget with values'''
    # Delete everything
    TABLE.clear()

    # can we read all the row headers for the table?
    nrRows = TABLE.rowCount()
    QgsMessageLog.logMessage("In formOpen_Table: nr Rows = " + str(nrRows), tag="TOMs panel")
    # verticalHeaderItem (self, int row)

    # set Headers columns

    fieldname = "SiteNr"
    txtFilter = siteNr
    dataColumn = "NrPeds"
    startTimeColumn = "StartTime"
    idxDataColumn = VALUES.fieldNameIndex(dataColumn)
    idxStartTime = VALUES.fieldNameIndex(startTimeColumn)

    # We need a request
    request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
    if txtFilter is not None:
        # fields = self.layer.dataProvider().fields()
        # fieldname = fields[self.shownField].name()

        request.setFilterExpression(u"\"{0}\" = '{1}'".format(fieldname, txtFilter))

    # Grab the results from the layer
    features = VALUES.getFeatures(request)

    timePeriods = [[7, "07:00-08:00", 0],
                   [8, "08:00-09:00", 0],
                   [9, "09:00-10:00", 0],
                   [10, "10:00-11:00", 0],
                   [11, "11:00-12:00", 0],
                   [12, "12:00-13:00", 0],
                   [13, "13:00-14:00", 0],
                   [14, "14:00-15:00", 0],
                   [15, "15:00-16:00", 0],
                   [16, "16:00-17:00", 0],
                   [17, "17:00-18:00", 0],
                   [18, "18:00-19:00", 0]]

    currTimePeriodPosition = 0

    timePeriodIndex = 0
    timePeriodTextIndex = 1
    valueIndex = 2

    currTimePeriodRow = timePeriods[currTimePeriodPosition]
    # currTimePeriodDetails.pop()

    currTimePeriod = timePeriods[currTimePeriodPosition][timePeriodIndex]
    QgsMessageLog.logMessage("In formOpen_Table: currTimePeriod " + str(currTimePeriod), tag="TOMs panel")

    # Set up table

    TABLE.setColumnCount(1)
    TABLE.setRowCount(len(timePeriods))
    TABLE.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem(dataColumn))

    totalPeds = 0
    QgsMessageLog.logMessage("In formOpen_Table: periodIndex1: " + str(currTimePeriodPosition), tag="TOMs panel")

    for feature in sorted(features, key=lambda f: f[0]):
        attr = feature.attributes()
        timePeriodStart = attr[idxStartTime].hour()
        value = attr[idxDataColumn]

        QgsMessageLog.logMessage("In formOpen_Table: " + str(timePeriodStart) + " : " + str(value), tag="TOMs panel")

        if timePeriodStart == currTimePeriod:
            totalPeds = totalPeds + value
        else:
            # Now update count
            QgsMessageLog.logMessage("In formOpen_Table: periodIndex2: " + str(currTimePeriodPosition),
                                     tag="TOMs panel")
            QgsMessageLog.logMessage(
                "In formOpen_Table: " + str(timePeriods[currTimePeriodPosition][timePeriodTextIndex]) + " : " + str(
                    totalPeds), tag="TOMs panel")

            timePeriods[currTimePeriodPosition][valueIndex] = totalPeds

            if currTimePeriodPosition < len(timePeriods) - 1:
                currTimePeriodPosition = currTimePeriodPosition + 1
                currTimePeriod = timePeriodStart
                totalPeds = value

            else:
                break


                # QgsMessageLog.logMessage("In formOpen_Table: " + str(timePeriodStart) + " : " + str(value), tag="TOMs panel")
                # element = QTableWidgetItem(value)
                # element.setData(Qt.UserRole, attr[self.IdField])

                # addValuesToTableSet


                # self.TABLE.addItem(element)

    # Deal with final row
    # Now update count
    QgsMessageLog.logMessage("In formOpen_Table: periodIndex2: " + str(currTimePeriodPosition), tag="TOMs panel")
    QgsMessageLog.logMessage(
        "In formOpen_Table: " + str(timePeriods[currTimePeriodPosition][timePeriodTextIndex]) + " : " + str(totalPeds),
        tag="TOMs panel")

    timePeriods[currTimePeriodPosition][valueIndex] = totalPeds

    QgsMessageLog.logMessage("In formOpen_Table: results " + str(timePeriods), tag="TOMs panel")

    for row in timePeriods:
        val = str(timePeriods[currTimePeriodPosition][timePeriodTextIndex])
        TABLE.setVerticalHeaderItem(row, QtGui.QTableWidgetItem(val))
        TABLE.setItem(row, 0, QtGui.QTableWidgetItem(str(timePeriods[currTimePeriodPosition][valueIndex])))
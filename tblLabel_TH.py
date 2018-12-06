# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tblLabel_TH
                                 A QGIS plugin
 vv
                              -------------------
        begin                : 2018-11-13
        git sha              : $Format:%H$
        copyright            : (C) 2018 by TH
        email                : th
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *


from qgis.core import *
from qgis.gui import *

import math
from datetime import datetime

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from tblLabel_TH_dialog import tblLabel_THDialog
import os.path

#from .tblExpressions import registerFunctions, unregisterFunctions

class signalTest(QObject):
    pointClicked = pyqtSignal(QgsPoint, QgsFeature)
    """Signal will be emitted, when click is made"""

class FlowReporting:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FlowReporting_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        #self.menu = self.tr(u'&tblLabel_TH')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'FlowReporting')
        self.toolbar.setObjectName(u'FlowReporting')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('FlowReporting', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = tblLabel_THDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        """if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)"""

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        #registerFunctions()  # Register the Expression functions that we need
        self.AnnotationsToolbar = self.iface.addToolBar("Annotations Toolbar")
        self.actionAnnotations = QAction(QIcon(":/plugins/FlowReporting/icons/LetterA.png"),
                                            QCoreApplication.translate("MyPlugin", "Start Annotations"),
                                            self.iface.mainWindow())
        self.actionAnnotations.setCheckable(True)

        self.AnnotationsToolbar.addAction(self.actionAnnotations)

        self.actionAnnotations.triggered.connect(self.onStartAnnotations)

        """icon_path = ':/plugins/FlowReporting/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'FlowReporting'),
            callback=self.run,
            parent=self.iface.mainWindow())"""

    def onStartAnnotations(self):
        """Filter main layer based on date and state options"""

        QgsMessageLog.logMessage("In onStartAnnotations", tag="TOMs panel")

        # print "** STARTING ProposalPanel"

        # dockwidget may not exist if:
        #    first run of plugin
        #    removed on close (see self.onClosePlugin method)

        #self.proposalsManager.TOMsStartupFailure.connect(self.setCloseTOMsFlag)
        # self.RestrictionTypeUtilsMixin.tableNames.TOMsStartupFailure.connect(self.closeTOMsTools)

        self.mapTool = None

        if self.actionAnnotations.isChecked():

            QgsMessageLog.logMessage("In onStartAnnotations. Activating ...", tag="TOMs panel")

            self.doAnnotations()

        else:

            QgsMessageLog.logMessage("In onStartAnnotations. Deactivating ...", tag="TOMs panel")
            # unset map tool
            self.actionAnnotations.setChecked(False)

            if self.mapTool <> None:

                #self.iface.mapCanvas().unsetMapTool(self.mapTool)
                self.mapTool = None


    def doAnnotations(self):

        #QMessageBox.information(self.iface.mainWindow(), "ERROR", ("Table Proposals is not present"))

        # TODO: Pick up details (time periods, headings, etc) from config area

        # check that we have the correct layer
        currLayer = self.iface.activeLayer()

        if QgsMapLayerRegistry.instance().mapLayersByName("TestGeometry"):
            self.geomLayer = QgsMapLayerRegistry.instance().mapLayersByName("TestGeometry")[0]
        else:
            QMessageBox.information(self.iface.mainWindow(), "ERROR", ("Table geomLayer is not present"))
            found = False

        if currLayer <> self.geomLayer:
            QMessageBox.information(self.iface.mainWindow(), "ERROR", ("Not using correct layer ..."))
            return

        # Now start creating

        # get the click position

        notSure = signalTest()

        self.mapTool = createAnnotation(self.iface, self.geomLayer, notSure)
        self.canvas.setMapTool(self.mapTool)

        self.nextAnnotation = QgsHtmlAnnotationItem(self.canvas, self.geomLayer)
        #self.nextAnnotation2 = QgsHtmlAnnotationItem(self.canvas, self.geomLayer)

        notSure.pointClicked.connect(self.makeAnnotation)

        #pointTool = QgsMapToolEmitPoint(self.canvas)
        #pointTool.connect(self.createAnnotation)
        #self.canvas.setMapTool(pointTool)

        #canvas_clicked = getClickedPoint(self.iface)
        #self.canvas.setMapTool(canvas_clicked)
        #canvas_clicked.pointClicked.connect(self.createAnnotation)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&tblLabel_TH'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def makeAnnotation(self, mapPt, closestFeature):

        """newAnnotation = self.nextAnnotation

        if newAnnotation.htmlPage():
            newAnnotation = self.nextAnnotation2"""

        if self.nextAnnotation.htmlPage():
            self.canvas.scene().addItem(self.nextAnnotation)
            anotherAnnotation = QgsHtmlAnnotationItem(self.canvas, self.geomLayer)

            self.nextAnnotation = anotherAnnotation

        newAnnotation = self.nextAnnotation

        # Can we get a new Annotation from the calling function at this point ****

        # unset map tool when signal is raised
        #QMessageBox.information(self.iface.mainWindow(), "ERROR", ("connected  ..." + str(mapPt.x()) + "; " + str(mapPt.y())))

        # self.iface.mapCanvas().unsetMapTool(self.mapTool)
        # self.iface.mainWindow().findChild(QAction, 'mActionHtmlAnnotation').trigger()

        #newAnnotation = QgsHtmlAnnotationItem(self.canvas, self.geomLayer)
        # newAnnotation = QgsHtmlAnnotationItem(self.canvas, self.geomLayer, True, closestFeature.id())

        # newAnnotation = QgsHtmlAnnotationItem(self.canvas)
        #self.newAnnotation = QgsTextAnnotationItem (self.canvas)
        # newAnnotation = QgsFormAnnotationItem (self.canvas, self.geomLayer)
        # newAnnotation.setFrameSize(QSizeF(100, 200))

        newAnnotation.setMapPosition(mapPt)
        """X, Y = float(3), float(45)
        point = QgsPoint(X, Y)
        newAnnotation.setMapPosition(point)"""

        fileName = self.buildHTMLFile(closestFeature)
        # fileName = self.buildSimpleHTMLFile()
        newAnnotation.setHTMLPage(fileName)


        newAnnotation.setFrameSize(QSizeF(170, 350))
        newAnnotation.minimumFrameSize
        newAnnotation.setFrameBorderWidth(2.0)
        newAnnotation.setFrameColor(self.featureColour)
        newAnnotation.setFrameBackgroundColor(QColor(128, 128, 128))

        markerSymbol = QgsMarkerSymbolV2()
        markerSymbol.setSize(0.0)
        newAnnotation.setMarkerSymbol(markerSymbol)
        #newAnnotation.setMarkerSymbol(markerSymbol).setSize(0.0)
        #newAnnotation.setMarkerSymbol(markerSymbol).setColour(0.0)

        #setMarkerSymbol(QgsMarkerSymbolV2 * symbol) # Set symbol that is drawn on map position
        # boundingRect
        # minimumFrameSize
        # setRect (QgsRectange)

        # self.iface.actionZoomIn().trigger()

        currPt = newAnnotation.mapPosition()

        QgsMessageLog.logMessage("In createAnnotation. fileName to used is ..." + str(newAnnotation.htmlPage()),
                                 tag="TOMs panel")
        QgsMessageLog.logMessage("In createAnnotation. frameSize to used is ..." + str(newAnnotation.frameSize()),
                                 tag="TOMs panel")
        QgsMessageLog.logMessage(
            "In createAnnotation. mapPost to used is ..." + str(currPt.x()) + "; " + str(currPt.y()),
            tag="TOMs panel")

        QgsMessageLog.logMessage(
            "In createAnnotation. layer to used is ..." + str(newAnnotation.vectorLayer().name()),
            tag="TOMs panel")

        # newAnnotation.setDesignerForm('C:\Users\marie_000\.qgis2\python\plugins\tblLabel_TH\tblLabel_TH_dialog_base.ui')
        # self.iface.mainWindow().findChild(QAction, 'mActionHtmlAnnotation').trigger()
        """annoPainter = QPainter()

        styleOptions = QStyleOptionGraphicsItem()

        newAnnotation.paint(annoPainter, styleOptions, None)"""


        #reply = QMessageBox.information(None, "Information", "check point.", QMessageBox.Ok)
        newAnnotation.update()
        #currPt = newAnnotation1.mapPosition()  - just to stop plugin for checking
        #self.canvas.refresh()

        # currMapTool = self.iface.mapCanvas().mapTool()
        # currMapTool.deactivate()
        # self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())

        # newAnnotation.setSourceFile(fileName)

    def transformCoordinates(self, screenPt):
        """ Convert a screen coordinate to map and layer coordinates.

            returns a (mapPt,layerPt) tuple.
        """
        return (self.toMapCoordinates(screenPt))

    def getFeatureColour(self, layer, feature):

        renderer = layer.rendererV2()

        """
        QGIS pyQGIS developer handbook
        You can query and set attribute name which is used for classification: use classAttribute() and setClassAttribute() methods.
        Where value() is the value used for discrimination between categories, label() is a text used for category description and symbol() method returns assigned symbol.

        The renderer usually stores also original symbol and color ramp which were used for the classification: sourceColorRamp() and sourceSymbol() methods.
        """
        QgsMessageLog.logMessage(
            "In getFeatureColour. Site Nr: " + str(self.siteNr),
            tag="TOMs panel")

        for cat in renderer.categories():
            colour = cat.symbol().color()
            QgsMessageLog.logMessage("In getFeatureColour. " + str(cat.value()) + ":" + str(cat.label()) + ":" + str(cat.symbol()) + ";" + str(colour.name()),
                                     tag="TOMs panel")
            if str(self.siteNr)+'_PCL' == str(cat.value()):
                return colour
            #print "%s: %s :: %s" % (cat.value().toString(), cat.label(), str(cat.symbol()))

        return None

    def buildSimpleHTMLFile(self):

        filePath = "Z:\Tim\TSS18-05 Sankey analysis\Mapping\htmlFiles"
        fileName = "Test" + ".html"
        fullFileName = os.path.join(filePath, fileName)

        #htmlFile = open(fullFileName, 'wt')

        QgsMessageLog.logMessage("In buildHTMLFile. file opened ..." + str(fullFileName),
                                 tag="TOMs panel")

        html_content = """<!DOCTYPE html>
        <html>
        <head>
          <title></title>
        </head>
        <body>
        <p>Pellentesque habitant morbi tristique senectus et netus et malesuada fames
         ac turpis egestas. Vestibulum tortor quam, feugiat vitae, ultricies eget,
         tempor sit amet, ante. Donec eu libero sit amet quam egestas semper.
         Aenean ultricies mi vitae est. Mauris placerat eleifend leo. Quisque sit amet
         est et sapien ullamcorper pharetra. Vestibulum erat wisi, condimentum sed,
         commodo vitae, ornare sit amet, wisi. Aenean fermentum, elit eget tincidunt
         condimentum, eros ipsum rutrum orci, sagittis tempus lacus enim ac dui. Donec
         non enim in turpis pulvinar facilisis. Ut felis. Praesent dapibus, neque id
         cursus faucibus, tortor neque egestas augue, eu vulputate magna eros eu erat.
         Aliquam erat volutpat. Nam dui mi, tincidunt quis, accumsan porttitor,
         facilisis luctus, metus
        </p>
        </body>
        </html>
        """

        with open(fullFileName, 'wb') as f:
            f.write(html_content)

        return fullFileName

    def buildHTMLFile(self, feature):

        self.getTitleDetails(feature, "Nr PCLs")

        self.featureColour = self.getFeatureColour(self.geomLayer, feature)

        if self.featureColour == None:
            self.featureColour = QColor(0, 0, 0)

        # Open file
        filePath = QgsExpressionContextUtils.projectScope().variable('FilePath')
        if filePath == None:
            reply = QMessageBox.information(None, "Information", "Please set value for FilePath.", QMessageBox.Ok)
            return
        else:
            QgsMessageLog.logMessage(
                "In buildHTMLFile. file path: " + filePath,
                tag="TOMs panel")

        #filePath = "Z:\Tim\TSS18-05 Sankey analysis\Mapping\htmlFiles"
        fileName = str(self.area) + "_" + str(self.siteNr) + ".html"
        fullFileName = os.path.join(filePath, fileName)

        htmlFile = open(fullFileName, 'wt')

        QgsMessageLog.logMessage("In buildHTMLFile. file opened ..." + str(fullFileName) + "; " + filePath + fileName,
                                 tag="TOMs panel")

        # set up css

        htmlFile.write('<!doctype html>\n'.format())
        htmlFile.write('<style type="text/css">\n'.format())
        htmlFile.write('.tg  {{border-collapse:collapse;border-spacing:0;}}\n'.format())
        htmlFile.write('.tg td{{font-family:Arial, sans-serif;font-size:9px;padding:2px 2px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}}\n'.format())
        htmlFile.write('.tg th{{font-family:Arial, sans-serif;font-size:9px;font-weight:normal;padding:2px 2px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}}\n'.format())
        htmlFile.write('.tg .normal{{text-align:center;vertical-align:top}}\n'.format())
        htmlFile.write('.tg .blank{{text-align:centre}}\n'.format())
        htmlFile.write('.tg .highlightHighestData{{background-color:#34ff34;text-align:center;vertical-align:top}}\n'.format())
        htmlFile.write('h1{{font-family:Arial, sans-serif;font-size:11px;font-weight:bold;}}\n'.format())
        htmlFile.write('</style>\n'.format())
        htmlFile.write('<body>\n'.format())
        htmlFile.write('<head>\n'.format())
        htmlFile.write('<title></title>\n'.format())
        htmlFile.write('</head>\n'.format())

        htmlFile.write('<h1 class="normal"><span style="background-color: {flowColour}">\
                      {title}</span></h1>\n'. format(flowColour=self.featureColour.name(), title=self.siteDetails))

        # Try to add halo effect ...
        """htmlFile.write('<h1 class="normal"><span style="background-color: {flowColour}; text-shadow: 1px -1px 0 white, 1px -1px 0 white, -1px 1px 0 white, 1px 1px 0 white; -webkit - font - smoothing: antialiased">\
                      {title}</span></h1>\n'. format(flowColour=self.featureColour.name(), title=self.siteDetails))"""

        # now write the table details

        """htmlFile.write('<table class="tg">\n'.format())
        htmlFile.write('  <tr>\n'.format())
        htmlFile.write('    <th class="blank"></th>\n'.format())
        htmlFile.write('    <th colspan="2" class="normal">{colHeader}</th>\n'.format (colHeader="Nr Peds"))
        htmlFile.write('  </tr>\n'.format())"""


        flowFieldName = "FlowNr"
        areaFieldName = "Area"
        dayFieldName = "Date"
        dataFieldName = "NrPCLs"
        startTimeFieldName = "StartTime"

        # get the different days for the flow.
        daysSet = self.getDaysForFlow(flowFieldName, self.siteNr, areaFieldName, self.area, dayFieldName)
        outputDetails = []

        """
        Logic is:
        
        For each surveyDay
            
        """
        for surveyDay in daysSet:

            QgsMessageLog.logMessage("In buildHTMLFile: collecting data for " + str(self.area) + ": " + str(self.siteNr) + "; " + str(surveyDay[2]),
                                     tag="TOMs panel")
            timePeriods, highestValueRow, overallTotal = self.fetchSurveyDetails(flowFieldName, self.siteNr, areaFieldName, self.area, dayFieldName, surveyDay[0], dataFieldName, startTimeFieldName)
            # Create (another) set with details - DayNumber, DayAbbreviation, data (timePeriods), highestValueRow, overallTotal

            surveyDate = surveyDay[0]
            surveyDayNr = surveyDay[1]
            surveyDayAbbrev = surveyDay[2]

            dayDetails = (surveyDate, surveyDayNr, surveyDayAbbrev, timePeriods, highestValueRow, overallTotal)

            QgsMessageLog.logMessage("In buildHTMLFile: highest value row " + str(highestValueRow) + ": overall Total " + str(overallTotal),
                                     tag="TOMs panel")

            outputDetails.append(dayDetails)

        idxtimePeriods = 3

        # TODO: set up headers
        # now write the table details

        htmlFile.write('<table class="tg">\n'.format())
        htmlFile.write('  <tr>\n'.format())
        htmlFile.write('    <th class="blank"></th>\n'.format())

        for dayDetails in sorted(outputDetails, key=lambda f: f[1]):
            currSurveyDayAbbrev = dayDetails[2]
            htmlFile.write('    <th class="normal">{colHeader}</th>\n'.format (colHeader=currSurveyDayAbbrev))
        htmlFile.write('  </tr>\n'.format())

        currRow = 0
        for row in timePeriods:

            #rowString = NULL
            rowValues = False

            timeString = str(timePeriods[currRow][self.timePeriodTextIndex])

            QgsMessageLog.logMessage("In buildHTMLFile: currTimePeriod " + str(timeString),
                                     tag="TOMs panel")

            rowString = ('  <tr>\n'.format())
            rowString = rowString + ('    <th class="normal">{timePeriod}</th>\n'.format(timePeriod=timeString))
            #htmlFile.write('  <tr>\n'.format())
            #htmlFile.write('    <th class="normal">{timePeriod}</th>\n'.format(timePeriod=timeString))

            for dayDetails in sorted(outputDetails, key=lambda f: f[1]):

                currTimePeriods = dayDetails[idxtimePeriods]
                highestValueRow = dayDetails[4]

                #for typeOutput in dayDetails:

                #currTimePeriods = typeOutput[idxtimePeriods]
                value = currTimePeriods[currRow][self.valueIndex]
                if value <> None:
                    value = str(currTimePeriods[currRow][self.valueIndex])
                    rowValues = True

                QgsMessageLog.logMessage("In buildHTMLFile: value " + str(value),
                                         tag="TOMs panel")

                rowType = "normal"
                if currRow == highestValueRow:
                    rowType = "highlightHighestData"

                rowString = rowString + ('    <td class="{rowTypePlace}">{rowValue}</td>\n'.format(rowTypePlace=rowType, rowValue=value))
                #htmlFile.write('    <td class="{rowTypePlace}">{rowValue}</td>\n'.format(rowTypePlace=rowType, rowValue=value))

            rowString = rowString + ('  </tr>\n'.format())
            #htmlFile.write('  </tr>\n'.format())
            if rowValues == True:
                htmlFile.write(rowString)

            currRow = currRow + 1

        # Now add the totals
        htmlFile.write('  <tr>\n'.format())
        htmlFile.write('    <th class="normal"><span style="font-weight:bold">TOTAL</span></th>\n'.format())

        for dayDetails in sorted(outputDetails, key=lambda f: f[1]):
            currOverallTotal = dayDetails[5]
            htmlFile.write('    <td class="normal"><span style="font-weight:bold;font-style:italic">{rowValue}</span></td>\n'.format(rowValue=currOverallTotal))
        htmlFile.write('  </tr>\n'.format())

        # close the table
        htmlFile.write('</table>\n'.format())
        htmlFile.write('</body>\n'.format())
        htmlFile.write('</html>\n'.format())
        # Close file

        htmlFile.close()

        return fullFileName

    def getTitleDetails(self, feature, dataReported):

        self.siteNr = feature[feature.fieldNameIndex("SiteNr")]
        self.area = feature[feature.fieldNameIndex("Area")]
        self.description = feature[feature.fieldNameIndex("SiteDescription")]
        self.siteDetails = str(self.area) + " - Flow " + str(self.siteNr) + " (" + str(dataReported) + ")"

        QgsMessageLog.logMessage("In getTitleDetails: " + str(self.area) + "(" + str(self.siteNr) + ") - " + str(self.description), tag="TOMs panel")


        # self.shownField = "NrPeds"

    def getHeaderDetails(self):
        pass

    def getDaysForFlow(self, flowFieldName, flowNr, areaFieldName, area, dayFieldName):

        if QgsMapLayerRegistry.instance().mapLayersByName("FlowValues"):
            VALUES = QgsMapLayerRegistry.instance().mapLayersByName("FlowValues")[0]
        else:
            QMessageBox.information(self.iface.mainWindow(), "ERROR", ("Table FlowValues is not present"))
            found = False

        idxDayColumn = VALUES.fieldNameIndex(dayFieldName)
        #idxStartTime = VALUES.fieldNameIndex(startTimeFieldName)

        daysSet = set()
        # We need a request
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
        if flowNr is not None:
            # fields = self.layer.dataProvider().fields()
            # fieldname = fields[self.shownField].name()

            request.setFilterExpression(
                u"\"{0}\" = '{1}' AND \"{2}\" = '{3}'".format(flowFieldName, flowNr, areaFieldName, area))

        # Grab the results from the layer
        features = VALUES.getFeatures(request)

        for feature in sorted(features, key=lambda f: f[2]):   # 6 = Date
            attr = feature.attributes()

            surveyDay = attr[idxDayColumn]
            day, date = (x for x in (surveyDay.split(',')))

            date_time_obj = datetime.strptime(attr[idxDayColumn], '%A, %d %B %Y')
            #hours, minutes = map(int, attr[idxStartTime].split(':'))
            #QTime.fromString(attr[idxStartTime], 'HH:MM')
            weekdayNr = date_time_obj.weekday()
            weekdayAbbrev = date_time_obj.strftime('%a')

            QgsMessageLog.logMessage("In getDaysForFlow: date " + str(surveyDay) + "; DayNr: " + str(weekdayNr) + " DayAbbrev: " + str(weekdayAbbrev), tag="TOMs panel")
            daysSet.add((surveyDay, weekdayNr, weekdayAbbrev))

        return daysSet

    def fetchSurveyDetails(self, flowFieldName, flowNr, areaFieldName, area, dayFieldName, day, dataFieldName, startTimeFieldName):

        if QgsMapLayerRegistry.instance().mapLayersByName("FlowValues"):
            VALUES = QgsMapLayerRegistry.instance().mapLayersByName("FlowValues")[0]
        else:
            QMessageBox.information(self.iface.mainWindow(), "ERROR", ("Table FlowValues is not present"))
            found = False

        #fieldname = "SiteNr"
        #txtFilter = siteNr
        #dataColumn = "NrPeds"
        #startTimeColumn = "StartTime"
        idxDataColumn = VALUES.fieldNameIndex(dataFieldName)
        idxStartTime = VALUES.fieldNameIndex(startTimeFieldName)

        # We need a request
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
        if flowNr is not None:
            # fields = self.layer.dataProvider().fields()
            # fieldname = fields[self.shownField].name()

            request.setFilterExpression(u"\"{0}\" = '{1}' AND \"{2}\" = '{3}' AND \"{4}\" = '{5}'".format \
                                            (flowFieldName, flowNr, areaFieldName, area, dayFieldName, day))

            QgsMessageLog.logMessage("In fetchSurveyDetails: expression " + str(request.filterExpression().expression()), tag="TOMs panel")

        # Grab the results from the layer
        features = VALUES.getFeatures(request)

        timePeriods = [[0, "00:00-01:00", None],
                       [1, "01:00-02:00", None],
                       [2, "02:00-03:00", None],
                       [3, "03:00-04:00", None],
                       [4, "04:00-05:00", None],
                       [5, "05:00-06:00", None],
                       [6, "06:00-07:00", None],
                       [7, "07:00-08:00", None],
                       [8, "08:00-09:00", None],
                       [9, "09:00-10:00", None],
                       [10, "10:00-11:00", None],
                       [11, "11:00-12:00", None],
                       [12, "12:00-13:00", None],
                       [13, "13:00-14:00", None],
                       [14, "14:00-15:00", None],
                       [15, "15:00-16:00", None],
                       [16, "16:00-17:00", None],
                       [17, "17:00-18:00", None],
                       [18, "18:00-19:00", None],
                       [19, "19:00-20:00", None],
                       [20, "20:00-21:00", None],
                       [21, "21:00-22:00", None],
                       [22, "22:00-23:00", None],
                       [23, "23:00-00:00", None]]

        currTimePeriodPosition = 0

        self.timePeriodIndex = 0
        self.timePeriodTextIndex = 1
        self.valueIndex = 2

        currTimePeriodRow = timePeriods[currTimePeriodPosition]
        # currTimePeriodDetails.pop()

        currTimePeriod = timePeriods[currTimePeriodPosition][self.timePeriodIndex]
        QgsMessageLog.logMessage("In fetchSurveyDetails: currTimePeriod " + str(currTimePeriod), tag="TOMs panel")

        overallTotal = 0
        totalPeds = 0
        highestValueRow = 0
        highestPedValue = 0
        firstPass = True

        # https://medspx.fr/blog/Qgis/better_qgis_forms_part_three/
        QgsMessageLog.logMessage("In fetchSurveyDetails: periodIndex1: " + str(currTimePeriodPosition),
                                 tag="TOMs panel")

        for feature in sorted(features, key=lambda f: f[7]):   # 6 = StartTime
            attr = feature.attributes()
            hours, minutes = map(int, attr[idxStartTime].split(':'))
            timePeriodStart = hours
            #struct_time = datetime.strptime(attr[idxStartTime], '%H:%M')
            #timePeriodStart = datetime.strptime(attr[idxStartTime], '%H:%M')
            #timePeriodStart = QTime.fromString(attr[idxStartTime], 'HH:MM').hour()
            value = attr[idxDataColumn]
            QgsMessageLog.logMessage("In fetchSurveyDetails attr: " + str(attr),
                                     tag="TOMs panel")
            QgsMessageLog.logMessage("In fetchSurveyDetails: " + str(timePeriodStart) + " : " + str(value),
                                     tag="TOMs panel")

            if firstPass == True:
                firstPass = False
                if timePeriodStart > currTimePeriod:
                    currTimePeriod = timePeriodStart
                    currTimePeriodPosition = timePeriodStart
                    QgsMessageLog.logMessage("In fetchSurveyDetails. Curr time period set to " + str(currTimePeriod),
                                             tag="TOMs panel")

            if timePeriodStart == currTimePeriod:
                totalPeds = totalPeds + value
            else:
                # Change of time periods ...
                # Now update count
                QgsMessageLog.logMessage("In fetchSurveyDetails: periodIndex2: " + str(currTimePeriodPosition),
                                         tag="TOMs panel")
                QgsMessageLog.logMessage(
                    "In fetchSurveyDetails - writing: " + str(
                        timePeriods[currTimePeriodPosition][self.timePeriodIndex]) + " : " + str(
                        totalPeds), tag="TOMs panel")

                timePeriods[currTimePeriodPosition][self.valueIndex] = totalPeds
                # Check for highestValueRow
                if totalPeds > highestPedValue:
                    highestValueRow = currTimePeriodPosition
                    highestPedValue = totalPeds

                overallTotal = overallTotal + totalPeds

                if currTimePeriodPosition < len(timePeriods) - 1:

                    if (currTimePeriod + 1) == timePeriodStart:
                        currTimePeriodPosition = currTimePeriodPosition + 1
                        currTimePeriod = timePeriodStart
                        totalPeds = value
                    else:
                        break

                else:
                    break

                    # element = QTableWidgetItem(value)

        # Deal with final row
        # Now update count
        """QgsMessageLog.logMessage("In fetchSurveyDetails: periodIndex2: " + str(currTimePeriodPosition),
                                 tag="TOMs panel")
        QgsMessageLog.logMessage(
            "In fetchSurveyDetails: " + str(timePeriods[currTimePeriodPosition][timePeriodTextIndex]) + " : " + str(
                totalPeds),
            tag="TOMs panel")"""

        timePeriods[currTimePeriodPosition][self.valueIndex] = totalPeds
        overallTotal = overallTotal + totalPeds
        if totalPeds > highestPedValue:
            highestValueRow = currTimePeriodPosition

        # TODO: Now add a final row with the overall TOTAL

        #timePeriods.append([19, "Total", overallTotal])
        
        QgsMessageLog.logMessage("In fetchSurveyDetails: results " + str(timePeriods), tag="TOMs panel")
        
        return timePeriods, highestValueRow, overallTotal

        """def  createAnnotation(self, mapPt):
        QgsMessageLog.logMessage("In createAnnotation ...", tag="TOMs panel")"""

class createAnnotation(QgsMapToolIdentify):
    # https://gis.stackexchange.com/questions/253733/how-to-get-co-ordinates-of-points-on-mouse-click-in-pyqgis
    def __init__(self, iface, geomLayer, notSure):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.geomLayer = geomLayer

        self.notSure = notSure

        QgsMapToolIdentify.__init__(self, self.canvas)


    def canvasPressEvent( self, e ):
        self.point = self.toMapCoordinates(self.canvas.mouseLastXY())
        #print '({:.4f}, {:.4f})'.format(point[0], point[1])

    def canvasReleaseEvent(self, event):

        #def createAnnotation(self):
        pos = event.pos()
        self.mapPt = self.transformCoordinates(pos)
        self.closestFeature, self.snappedVertex = self.findNearestFeatureAt(event.pos())

        if self.snappedVertex == None:
            QgsMessageLog.logMessage("In createAnnotation. point not snapped", tag="TOMs panel")
            self.snappedVertex = self.mapPt

        if self.closestFeature <> None:
            QgsMessageLog.logMessage("In createAnnotation. found close feature ..." + str(self.closestFeature.id()), tag="TOMs panel")

            self.notSure.pointClicked.emit(self.snappedVertex, self.closestFeature)

            #self.makeAnnotation()"""

    def transformCoordinates(self, screenPt):
        """ Convert a screen coordinate to map and layer coordinates.

            returns a (mapPt,layerPt) tuple.
        """
        return (self.toMapCoordinates(screenPt))


    def findNearestFeatureAt(self, pos):
        #  def findFeatureAt(self, pos, excludeFeature=None):
        # http://www.lutraconsulting.co.uk/blog/2014/10/17/getting-started-writing-qgis-python-plugins/ - generates "closest feature" function

        """ Find the feature close to the given position.

            'pos' is the position to check, in canvas coordinates.

            if 'excludeFeature' is specified, we ignore this feature when
            finding the clicked-on feature.

            If no feature is close to the given coordinate, we return None.
        """
        QgsMessageLog.logMessage("In findNearestFeatureAt...", tag="TOMs panel")

        mapPt = self.transformCoordinates(pos)
        QgsMessageLog.logMessage("In findNearestFeatureAt... x:" + str(mapPt.x()) + "; y:" + str(mapPt.y()), tag="TOMs panel")
        #tolerance = self.calcTolerance(pos)
        tolerance = 0.5
        searchRect = QgsRectangle(mapPt.x() - tolerance,
                                  mapPt.y() - tolerance,
                                  mapPt.x() + tolerance,
                                  mapPt.y() + tolerance)

        request = QgsFeatureRequest()
        request.setFilterRect(searchRect)
        request.setFlags(QgsFeatureRequest.ExactIntersect)

        for feature in self.geomLayer.getFeatures(request):
            QgsMessageLog.logMessage("In findNearestFeatureAt... feature FOUND", tag="TOMs panel")
            snappedPt = self.findVertexAt(feature, mapPt)

            return feature, snappedPt

        return None, None

    def findVertexAt(self, feature, layerPt):
        """ Find the vertex of the given feature close to the given position.

            'feature' is the QgsFeature to check, and 'pos' is the position to
            check, in canvas coordinates.

            We return the vertex number for the closest vertex, or None if no
            vertex is close enough to the given click position.
        """
        #mapPt,layerPt = self.transformCoordinates(pos)
        tolerance     = 2.0

        vertexCoord,vertex,prevVertex,nextVertex,distSquared = \
            feature.geometry().closestVertex(layerPt)

        distance = math.sqrt(distSquared)
        if distance > tolerance:
            return None
        else:
            return vertexCoord




# -*- coding: utf-8 -*-
"""
/***************************************************************************
 config_fmask
                                 A QGIS plugin
 QGIS plugin for testing Fmask cloud masking configuration settings
                              -------------------
        begin                : 2014-05-14
        copyright            : (C) 2014 by Chris Holden
        email                : ceholden@bu.edu
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
import os

# Import the PyQt and QGIS libraries
from PyQt4 import QtCore
from PyQt4 import QtGui

from qgis.core import *

# Initialize Qt resources from file resources.py
import resources_rc

# Import the code for the dialog
from fmask_dialog import FmaskDialog

class config_fmask:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n',
            'config_fmask_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = FmaskDialog()

    def init_toolbar(self):
        """ Create toolbar item for plugin """
        # Dialog button
        self.show_dialog = QtCore.QAction(QtGui.QIcon(
            ':/plugins/config_fmask/icon.png', self.iface.mainWindow()))
        self.show_dialog.triggered.connect(self.show_fmask_dialog)
        self.iface.addToolBarIcon(self.show_dialog)

    def unload(self):
        """ Shutdown by removing icons and disconnecting signals """
        # Remove toolbar icons
        self.iface.removeToolBarIcon(self.show_dialog)

        # Disconnect signals
        self.show_dialog.disconnect()

    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass

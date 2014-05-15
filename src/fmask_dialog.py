# -*- coding: utf-8 -*-
"""
/***************************************************************************
 config_fmaskDialog
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
from functools import partial
import os

from PyQt4 import QtCore
from PyQt4 import QtGui

from osgeo import gdal

from ui_config_fmask import Ui_config_fmask

from py_fmask import mtl2dict

###TODO
from fmask_cloud_masking import plcloud

class FmaskDialog(QtGui.QDialog, Ui_config_fmask):

    symbology = {
        'land'    :    (0, 255, 0, 255),
        'water'   :    (0, 0, 255, 255),
        'shadow'  :    (125, 125, 125, 255),
        'snow'    :    (255, 66, 0, 255),
        'cloud'   :    (255, 0, 248, 255)
    }

    enable_symbology = [False, False, True, True, True]
    mtl_file = ''
    mtl = {}

    def __init__(self):

        QtGui.QDialog.__init__(self)

        # Setup GUI (required by Qt)
        self.setupUi(self)

        # Create pairing of QCheckBox with QPushButton
        self.symbology_pairing = {
            'land'    :    (self.cbox_land,    self.button_sym_land),
            'water'   :    (self.cbox_water,   self.button_sym_water),
            'shadow'  :    (self.cbox_shadow,  self.button_sym_shadow),
            'snow'    :    (self.cbox_snow,    self.button_sym_snow),
            'cloud'   :    (self.cbox_cloud,   self.button_sym_cloud)
        }

        self.setup_gui()

    def setup_gui(self):
        ### Setup MTL input
        # Init text as current directory
        self.edit_MTL.setText(os.getcwd())
        self.button_MTL.clicked.connect(self.find_MTL)

        ### Setup output capacity
        # Find available GDAL drivers
        self.get_available_drivers()
        # Populate QComboBox with available drivers
        self.cbox_formats.addItems(self.drivers)

        ### Configure cloud probability slider and label
        self.lab_cloud_prob_val.setText("{0:.2f}%".format(
            self.slider_cloud_prob.value() / 10.0))
        self.slider_cloud_prob.valueChanged.connect(self.update_cloud_prob)

        ### Enable / disable color picking options
        self.symbology_on_off()
        # Add signals
        self.cbox_land.stateChanged.connect(self.symbology_on_off)
        self.cbox_water.stateChanged.connect(self.symbology_on_off)
        self.cbox_shadow.stateChanged.connect(self.symbology_on_off)
        self.cbox_snow.stateChanged.connect(self.symbology_on_off)
        self.cbox_cloud.stateChanged.connect(self.symbology_on_off)

        ### Set colors
        for fmask in self.symbology.keys():
            self.update_symbology_color(fmask)

        ### Connect signals for mask color symbology
        self.button_sym_land.clicked.connect(
            partial(self.select_color, 'land'))
        self.button_sym_water.clicked.connect(
            partial(self.select_color, 'water'))
        self.button_sym_shadow.clicked.connect(
            partial(self.select_color, 'shadow'))
        self.button_sym_snow.clicked.connect(
            partial(self.select_color, 'snow'))
        self.button_sym_cloud.clicked.connect(
            partial(self.select_color, 'cloud'))

        ### Override close event for saving of files
        # Disconnect accept so "Save" doesn't close dialog
        self.button_box.accepted.disconnect()
        # Connect clicked signal to custom slot
        self.button_box.clicked.connect(self.button_box_clicked)

    @QtCore.pyqtSlot()
    def find_MTL(self):
        """ Open QFileDialog to find a MTL file """
        # Save current path
        current_path = str(self.edit_MTL.text())
        # Open QFileDialog
        self.mtl_file = QtGui.QFileDialog.getOpenFileName(self,
            'Locate MTL file',
            os.path.dirname(current_path),
            '*MTL.txt')

        try:
            self.mtl = mtl2dict(filename)
        except:
            # TODO - QGIS message bar error
            print 'Error - cannot parse MTL file'
            raise

        self.update_table_MTL()

    @QtCore.pyqtSlot(int)
    def update_cloud_prob(self, value):
        """ Update slider's associated label with each value update """
        print 'Updated to value {v}'.format(v=value)
        self.lab_cloud_prob_val.setText("{0:.2f}%".format(
            self.slider_cloud_prob.value() / 10.0))

    @QtCore.pyqtSlot()
    def symbology_on_off(self):
        """ Updates on/off status of Fmask classes for symbology """
        # Loop through QCheckBox and QPushButton pairings
        for i, (cbox, button) in enumerate(self.symbology_pairing.itervalues()):
            # On state
            if cbox.isChecked():
                if not button.isEnabled():
                    button.setEnabled(True)
                self.enable_symbology[i] = True
            # Off state
            else:
                if button.isEnabled():
                    button.setEnabled(False)
                self.enable_symbology[i] = False

    @QtCore.pyqtSlot(QtGui.QPushButton)
    def button_box_clicked(self, button):
        """ Override for QDialogButttonBox slots

        Catches:
            AcceptRole       "Accept" button
            ApplyRole        "Apply" button
            HelpRole         "Help" button
            ResetRole        "Restore Defaults" button
        """
        button_role = self.button_box.buttonRole(button)
        print button_role

        if button_role == QtGui.QDialogButtonBox.AcceptRole:
            print 'Accept'
        elif button_role == QtGui.QDialogButtonBox.ApplyRole:
            print 'Apply'
        elif button_role == QtGui.QDialogButtonBox.HelpRole:
            print 'TODO - Help information'
        elif button_role == QtGui.QDialogButtonBox.ResetRole:
            print 'TODO - Reset to defaults'

    @QtCore.pyqtSlot(str)
    def select_color(self, fmask):
        """ Brings up QColorDialog to choose color for fmask image """
        # Look up current color
        c = self.symbology[fmask]
        current_c = QtGui.QColor(c[0], c[1], c[2], c[3])

        # Create QColorDialog
        color_dialog = QtGui.QColorDialog()

        # Get selected color
        new_c = color_dialog.getColor(current_c, self,
            'Pick color for {f}'.format(f=fmask),
            QtGui.QColorDialog.ShowAlphaChannel)

        # Update symbology colors
        self.symbology[fmask] = (
            new_c.red(),
            new_c.green(),
            new_c.blue(),
            new_c.alpha()
        )

        # Update label colors
        self.update_symbology_color(fmask)

    def update_symbology_color(self, fmask):
        """ Updates Fmask symbology QCheckBox label with appropriate color """
        # Retrieve color (r, g, b, a)
        c = self.symbology[fmask]
        # Create color string as rgb
        c_str = 'rgb({r}, {g}, {b})'.format(r=c[0], g=c[1], b=c[2])
        # Create style string
        style = 'color: {c}'.format(c=c_str)

        # Update style sheet
        self.symbology_pairing[fmask][1].setStyleSheet(style)

    def update_table_MTL(self):
        """ Updates MTL metadata table with information from MTL file """
        # Clear table before proceeding
        self.table_MTL.clear()

        self.table_MTL.setHorizontalHeaderLabels(
            ['Metadata Key', 'Value']
        )

        # Reset length
        self.table_MTL.setRowCount(len(self.mtl))
        for row, (key, value) in enumerate(self.mtl.iteritems()):
            _key = QtGui.QTableWidgetItem(key)
            _key.setTextAlignment(QtCore.Qt.AlignHCenter)
            _key.setTextAlignment(QtCore.Qt.AlignVCenter)

            _value = QtGui.QTableWidgetItem(str(value))
            _value.setTextAlignment(QtCore.Qt.AlignHCenter)
            _value.setTextAlignment(QtCore.Qt.AlignVCenter)

            self.table_MTL.setItem(row, 0, _key)
            self.table_MTL.setItem(row, 1, _value)


    def get_available_drivers(self):
        """ Creates list of GDAL's available drivers with creation capacity """
        self.drivers = ['GTiff', 'ENVI']

### DCAP_CREATE doesn't tell us if we can actually write data to the format
###    (e.g., VRT comes back as writeable)
#        for i in xrange(gdal.GetDriverCount()):
#            _driver = gdal.GetDriver(i)
#            if _driver.GetMetadata().get('DCAP_CREATE') == 'YES':
#                self.drivers.append(_driver.GetDescription())


# main for testing
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = FmaskDialog()
    window.show()
    sys.exit(app.exec_())

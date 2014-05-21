# -*- coding: utf-8 -*-

import os
import tempfile

from PyQt4 import QtCore
from PyQt4 import QtGui
import qgis.core

import numpy as np
from osgeo import gdal
from osgeo import gdal_array

def mtl2dict(filename, to_float=True):
    """ Reads in filename and returns a dict with MTL metadata """
    assert os.path.isfile(filename), '{f} is not a file'.format(f=filename)

    mtl = {}

    # Open filename with context manager
    with open(filename, 'rb') as f:
        # Read all lines in file
        for line in f.readlines():
            # Split KEY = VALUE entries
            key_value = line.strip().split(' = ')

            # Ignore END lines
            if len(key_value) != 2:
                continue

            key = key_value[0].strip()
            value = key_value[1].strip('"')

            # Try to convert to float
            if to_float is True:
                try:
                    value = float(value)
                except:
                    pass

            # Trim and add to dict
            mtl[key] = value

    return mtl

def temp_raster(raster, geo_transform, projection):
    """ Creates a temporary file raster dataset (GTiff) """
    # Get temporary filename
    filename = tempfile.mktemp('.gtif')

    # Parameterize raster
    if raster.ndim == 2:
        nband = 1
        nrow, ncol = raster.shape
    else:
        nrow, ncol, nband = raster.shape

    # Get driver
    driver = gdal.GetDriverByName('GTiff')
    # Create dataset
    ds = driver.Create(filename, ncol, nrow, nband,
                     gdal_array.NumericTypeCodeToGDALTypeCode(
                     raster.dtype.type))
    
    # Write file
    if nband == 1:
        ds.GetRasterBand(1).WriteArray(raster)
    else:
        for b in range(nband):
            ds.GetRasterBand(b + 1).WriteArray(raster)

    # Write projection / geo-transform
    ds.SetGeoTransform(geo_transform)
    ds.SetProjection(projection)

    return filename

def apply_symbology(rlayer, symbology):
    # See: QgsRasterRenderer* QgsSingleBandPseudoColorRendererWidget::renderer()
    # https://github.com/qgis/QGIS/blob/master/src/gui/raster/qgssinglebandpseudocolorrendererwidget.cpp

    # Get raster shader
    raster_shader = qgis.core.QgsRasterShader()
    # Color ramp shader
    color_ramp_shader = qgis.core.QgsColorRampShader()
    # Loop over Fmask values and add to color item list
    color_ramp_item_list = []
    for name, value in zip(['land', 'water', 'shadow', 'snow', 'cloud'],
                           [0, 1, 2, 3, 4]):
        color = symbology[name]
        # Color ramp item - color, label, value
        color_ramp_item = qgis.core.QgsColorRampShader.ColorRampItem(
            value,
            QtGui.QColor(color[0], color[1], color[2], color[3]),
            name
        )
        color_ramp_item_list.append(color_ramp_item)
    # After getting list of color ramp items
    color_ramp_shader.setColorRampItemList(color_ramp_item_list)
    # Exact color ramp
    color_ramp_shader.setColorRampType('EXACT')
    # Add color ramp shader to raster shader
    raster_shader.setRasterShaderFunction(color_ramp_shader)
    # Create color renderer for raster layer
    renderer = qgis.core.QgsSingleBandPseudoColorRenderer(
        rlayer.dataProvider(),
        1,
        raster_shader)
    # Set renderer for raster layer
    rlayer.setRenderer(renderer)
    # Repaint
    rlayer.triggerRepaint()

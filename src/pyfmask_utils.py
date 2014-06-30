# -*- coding: utf-8 -*-
import logging
import os
import tempfile
import time

from PyQt4 import QtGui
import qgis.core

import numpy as np
from osgeo import gdal
from osgeo import gdal_array

from fmask_cloud_masking_edit import nd2toarbt, plcloud, plcloud_warm

gdal.UseExceptions()

logger = logging.getLogger(__name__)

class FmaskResult(object):
    """ Object for running and storing some results from Fmask """

    def __init__(self, mtl, cache_toa_bt=False):
        # MTL filename
        self.mtl = mtl

        # Should TOA and BT data be cached?
        self._cache_toa_bt = cache_toa_bt
        # If so, have we cached it?
        self._cached_toa_bt = False

        # Cloud probability mask
        self.plcloud_mask = None
        self.geoT = None
        self.prj = None

    @property
    def cache_toa_bt(self):
        return self._cache_toa_bt

    @cache_toa_bt.setter
    def cache_toa_bt(self, value):
        """ Setter for caching of TOA/BT """
        logger.info('Changed caching TOA and BT data preference to {b}'.
            format(b=value))
        # Switching off the caching - delete cached data
        if self._cache_toa_bt and value is False:
            self.toa_bt = None

        self._cache_toa_bt = value

    def get_plcloud(self, cldprob=22.5, shadow_prob=False):
        """ Runs plcloud function according to cache_toa_bt policy """
        start = time.time()
        # Load TOA and BT information if needed
        if not self._cached_toa_bt:
#            (self.Temp, self.data,
#                self.dim, self.ul, self.zen, self.azi, self.zc,
#                self.satu_B1, self.satu_B2, self.satu_B3,
#                self.resolu, self.geoT, self.prj) = nd2toarbt(self.mtl)
            # Just save results as list since we only just pass it
            self.toa_bt = nd2toarbt(self.mtl)
            self._cached_toa_bt = True
            logger.info('Cached TOA and BT data')

        # Run plcloud
        if self._cache_toa_bt:
            # Used cached output from nd2toarbt
#            (zen,azi,ptm,
#                Temp,t_templ,t_temph,
#                WT,Snow,Cloud,Shadow,
#                dim,ul,resolu,zc,geoT,prj) = \
#            plcloud_warm(self.toa_bt, shadow_prob=shadow_prob)
            self.plcloud_result = plcloud_warm(self.toa_bt,
                                               cldprob=cldprob,
                                               shadow_prob=shadow_prob)
        else:
#            (zen,azi,ptm,
#                Temp,t_templ,t_temph,
#                WT,Snow,Cloud,Shadow,
#                dim,ul,resolu,zc,geoT,prj) = \
#            plcloud(cldprob, shadow_prob=shadow_prob)
            self.plcloud_result = plcloud(self.mtl,
                                          cldprob=cldprob,
                                          shadow_prob=shadow_prob)

        # Make reference to cloud probability mask
        self.plcloud_mask = self.plcloud_result[8]
        # Also include gdal info
        self.geoT = self.plcloud_result[14]
        self.prj = self.plcloud_result[15]

        processing_time = time.time() - start
        logger.info('Took {s}s to run plcloud'.format(s=processing_time))

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


def temp_raster(raster, geo_transform, projection,
                prefix='pyfmask_', directory=None):
    """ Creates a temporary file raster dataset (GTiff)
    Arguments:
    'raster'            numpy.ndarray image
    'geo_transform'     tuple of raster geotransform
    'projection'        str of raster's projection
    'prefix'            prefix of temporary filename
    'directory'         directory for temporary file (default: pwd)

    Returns:
    (filename of temporary raster image, temporary file object)
    """
    # Setup directory - default to os.getcwd()
    if directory is None:
        directory = os.getcwd()
    # Create temporary file that Python will delete on exit
    #   seems a little wonk to write over it with GDAL?
    #   but it will ensure it deletes the file...
    _tempfile = tempfile.NamedTemporaryFile(suffix='.gtif', prefix=prefix,
                                            delete=True, dir=directory)
    filename = _tempfile.name

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

    return (filename, _tempfile)


def apply_symbology(rlayer, symbology, symbology_enabled, transparent=255):
    """ Apply classification symbology to raster layer """
    # See: QgsRasterRenderer* QgsSingleBandPseudoColorRendererWidget::renderer()
    # https://github.com/qgis/QGIS/blob/master/src/gui/raster/qgssinglebandpseudocolorrendererwidget.cpp
    # Get raster shader
    raster_shader = qgis.core.QgsRasterShader()
    # Color ramp shader
    color_ramp_shader = qgis.core.QgsColorRampShader()
    # Loop over Fmask values and add to color item list
    color_ramp_item_list = []
    for name, value, enable in zip(['land', 'water', 'shadow', 'snow', 'cloud'],
                                   [0, 1, 2, 3, 4],
                                   symbology_enabled):
        if enable is False:
            continue
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

    # Set NoData transparency
    if not isinstance(transparent, list):
        transparent = [transparent]
    nodata = [qgis.core.QgsRasterRange(t, t) for t in transparent]
    rlayer.dataProvider().setUserNoDataValue(1, nodata)

    # Repaint
    if hasattr(rlayer, 'setCacheImage'):
        rlayer.setCacheImage(None)
    rlayer.triggerRepaint()

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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load config_fmask class from file config_fmask
    from config_fmask import config_fmask
    return config_fmask(iface)

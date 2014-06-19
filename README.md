config_fmask
============

QGIS plugin for testing Fmask cloud masking configuration settings

## Goals
This plugin aims to help guide the decision of which parameters should be used for any given image when creating Fmask cloud mask images.

1. Quickly visualize effect of changing cloud probability threshold after first cloud probability mask has been generated
2. Visualize effect of cloud, shadow, and snow mask dilation parameters
3. Ability to save generated Fmask cloud mask in variety of GDAL supported formats with option to include color table

## Example
Here is an example which displays two different cloud probability masks using the default parameter (22.5) and one more less likely to omit clouds but more likely to commit non-cloud objects (12.5).

![Example](https://raw.githubusercontent.com/ceholden/config_fmask/master/media/example/config_fmask_example.png)

## TODO
- Interrupt the plcloud function right before the cloud probability parameter is used in calculations to facilitate future "warm starts" to calculating the probability mask
- Connect cloud probability mask image to cloud object matching code
- Export options
- Check to ensure Landsat images referenced in MTL file exist (e.g., show error in QgsMessageBar if they need to be extracted)
- Move print messages and other information to QgsMessageBar
- Many miscellaneous usability / UI tweaks
- Documentation

## Install requirements - #TODO

- QGIS 2.0.1 or above
- Python 2.7 or above (tested on 2.7.5)
- Python numerical libraries
    - NumPy
    - numexpr
    - ...

and more...


## Citation
Fmask cloud and cloud shadow masking for Landsat data has been published [here](http://www.sciencedirect.com/science/article/pii/S0034425711003853) by Zhe Zhu.

Fmask software and more information from the author is available on his [Google Code page](https://code.google.com/p/fmask/).

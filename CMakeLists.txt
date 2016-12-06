cmake_minimum_required(VERSION 2.8.9)

project(BrainTissuesExtension)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/BrainTissuesExtension")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_DEPENDS AnomalousFiltersExtension ROBEXBrainExtraction)
set(EXTENSION_CONTRIBUTORS "Antonio Carlos da S. Senra Filho (University of Sao Paulo), Luiz Otavio Murta Junior (University of Sao Paulo)")
set(EXTENSION_DESCRIPTION "This extension aims to offer a series of brain tissues segmentation methods for strucutral MRI images, namely T1, T2 and PD weighted MRI images.")
set(EXTENSION_ICONURL "https://www.slicer.org/w/images/0/03/BrainTissuesExtension-logo.png")
set(EXTENSION_SCREENSHOTURLS "https://www.slicer.org/w/images/8/83/T1_fullBrain.png https://www.slicer.org/w/images/d/d6/T1_tissues.png https://www.slicer.org/w/images/9/97/WM_3DReconstruction.png https://www.slicer.org/w/images/9/98/GM_3DReconstruction.png https://www.slicer.org/w/images/a/a3/WM_GM_3DReconstruction.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BasicBrainTissues)
add_subdirectory(BrainStructuresSegmenter)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})

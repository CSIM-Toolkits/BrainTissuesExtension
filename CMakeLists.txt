cmake_minimum_required(VERSION 2.8.9)

project(BrainTissuesExtension)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/BrainTissuesExtension")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "John Doe (AnyWare Corp.)")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/BrainTissuesExtension.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/BrainTissuesExtension/Screenshots/1.png")

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

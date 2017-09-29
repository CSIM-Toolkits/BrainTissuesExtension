import os
import unittest
import vtk, qt, ctk, slicer
from numpy.lib.type_check import imag
from slicer.ScriptedLoadableModule import *
import logging

#
# BrainStructuresSegmenter
#

class BrainStructuresSegmenter(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
#TODO Verificar toda a documentacao da extensao: wikipage, modules...
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Brain Structures Segmenter"
    self.parent.categories = ["Segmentation"]
    self.parent.dependencies = []
    self.parent.contributors = ["Antonio Carlos da S. Senra Filho (University of Sao Paulo), Luiz Otavio Murta Junior (University of Sao Paulo)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This module offers a set of algorithms to brain tissue segmentation task in structural MRI images, namely T1, T2 and PD. This module is the main function to several brian segmentation methods, being at moment
     the K-Means and BLS segmentation methods available. More details are found in the wikipage: https://www.slicer.org/wiki/Documentation/Nightly/Modules/BrainStructuresSegmenter
    """
    self.parent.acknowledgementText = """
    This work was partially funded by CNPq grant 201871/2015-7/SWE and CAPES.
""" # replace with organization, grant and thanks.

#
# BrainStructuresSegmenterWidget
#

class BrainStructuresSegmenterWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "I/O Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersIOLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = True
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm. This should be an MRI strutural images with a type listed in the Image Modality option." )
    parametersIOLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # Image Modality
    #
    self.setImageModalityBooleanWidget = ctk.ctkComboBox()
    self.setImageModalityBooleanWidget.addItem("T1")
    self.setImageModalityBooleanWidget.addItem("T2")
    self.setImageModalityBooleanWidget.addItem("PD")
    self.setImageModalityBooleanWidget.setToolTip(
      "MRI strutural image inserted as a input volume.")
    parametersIOLayout.addRow("Image Modality ", self.setImageModalityBooleanWidget)

    #
    # Is brain extracted?
    #
    self.setIsBETWidget = ctk.ctkCheckBox()
    self.setIsBETWidget.setChecked(True)
    self.setIsBETWidget.setToolTip(
      "Is the input data already brain extracted? If not, the ROBEX brain extraction method is used.")
    parametersIOLayout.addRow("Is Brain Extracted?", self.setIsBETWidget)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.renameEnabled = True
    self.outputSelector.noneEnabled = False
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersIOLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # Parameters Area
    #
    parametersTissueCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersTissueCollapsibleButton.text = "Segmentation Parameters"
    self.layout.addWidget(parametersTissueCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersTissueLayout = qt.QFormLayout(parametersTissueCollapsibleButton)

    #
    # Separate one tissue?
    #
    self.setSeparateTissueBooleanWidget = ctk.ctkCheckBox()
    self.setSeparateTissueBooleanWidget.setChecked(False)
    self.setSeparateTissueBooleanWidget.setToolTip(
      "Select one tissue type desired to be passed as the output. If checked, the tissue type in Tissue Type option is used.")
    parametersTissueLayout.addRow("Separate One Tissue?", self.setSeparateTissueBooleanWidget)

    #
    # Tissue Type
    #
    self.setTissueTypeWidget = ctk.ctkComboBox()
    self.setTissueTypeWidget.addItem("White Matter")
    self.setTissueTypeWidget.addItem("Gray Matter")
    self.setTissueTypeWidget.addItem("CSF")
    self.setTissueTypeWidget.setToolTip(
      "Tissue type that will be resulted from the brain segmentation.")
    parametersTissueLayout.addRow("Tissue Type ", self.setTissueTypeWidget)


    #
    # Apply AAD filtering
    #
    self.setApplyAADBooleanWidget = ctk.ctkCheckBox()
    self.setApplyAADBooleanWidget.setChecked(True)
    self.setApplyAADBooleanWidget.setToolTip(
      "Apply the AAD filter on the input data. This is recommended since the image noise level may affect the segmentation performance.")
    parametersTissueLayout.addRow("Apply AAD filter", self.setApplyAADBooleanWidget)


    #
    # Apply Bias Correction
    #
    self.setApplyBiasCorrectionBooleanWidget = ctk.ctkCheckBox()
    self.setApplyBiasCorrectionBooleanWidget.setChecked(True)
    self.setApplyBiasCorrectionBooleanWidget.setToolTip(
      "Apply a bias field correction in the input data. This is recommended since the global signal fluctuation provided by magnetic fiel inhomogeneity may affect the segmentation performance.")
    parametersTissueLayout.addRow("Apply Bias Field Correction", self.setApplyBiasCorrectionBooleanWidget)

    #
    # Apply Label Smoothing
    #
    self.setApplyLabelSmoothingBooleanWidget = ctk.ctkCheckBox()
    self.setApplyLabelSmoothingBooleanWidget.setChecked(True)
    self.setApplyLabelSmoothingBooleanWidget.setToolTip(
      "Apply a post processing procedure to reduce the label variability. Here the label smoothing method based on morphological convolution is applied.")
    parametersTissueLayout.addRow("Apply Label Smoothing", self.setApplyLabelSmoothingBooleanWidget)

    #
    # Parameters Area
    #
    parametersSegmentationCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersSegmentationCollapsibleButton.text = "Expert Segmentation Parameters"
    parametersSegmentationCollapsibleButton.collapsed = True
    self.layout.addWidget(parametersSegmentationCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersSegmentationLayout = qt.QFormLayout(parametersSegmentationCollapsibleButton)

    #
    # Segmentation modality
    #
    self.groupBoxRadioButtons = qt.QGroupBox("Segmentation Method")
    RadioButtonLayout = qt.QFormLayout()
    self.groupBoxRadioButtons.setLayout(RadioButtonLayout)
    self.setRadioKMeans = qt.QRadioButton('K-Means')
    self.setRadioKMeans.setToolTip("K-Means algorithm used in the Basic Brain Segmentation module.")
    self.setRadioBLS = qt.QRadioButton('BLS')
    self.setRadioBLS.setChecked(True)
    self.setRadioBLS.setToolTip("Brain Logistic Segmentation (BLS) method.")
    RadioButtonLayout.addRow(self.setRadioKMeans)
    RadioButtonLayout.addRow(self.setRadioBLS)

    parametersSegmentationLayout.addRow(self.groupBoxRadioButtons)

    # #
    # # Tissue Threshold
    # #
    self.setTissueThresholdWidget = ctk.ctkSliderWidget()
    self.setTissueThresholdWidget.singleStep = 0.01
    self.setTissueThresholdWidget.minimum = 0.01
    self.setTissueThresholdWidget.maximum = 0.99
    self.setTissueThresholdWidget.value = 0.50
    self.setTissueThresholdWidget.setToolTip(
      "Regulates the local logistic classification to each brian tissue. The ideal value is 0.50 which does not offer label overlay, however, if you need a rough estimate of partial tissue volume (PTV), one can set it to other threshold (t<0.5 offer a numbered label estimate to PTV and t>0.5 offer a zero mask to PTV). This parameter is only used when BLS segmentation method is called."
      " Example: t=0.50 means that ...")
    parametersSegmentationLayout.addRow("Tissue Threshold", self.setTissueThresholdWidget)

    #
    # Use manual number of bins?
    #
    self.setManualBinsBooleanWidget = ctk.ctkCheckBox()
    self.setManualBinsBooleanWidget.setChecked(False)
    self.setManualBinsBooleanWidget.setToolTip(
      "Set this if you want to regulate the number of bins manually. This parameter is only used when BLS segmentation method is called.")
    parametersSegmentationLayout.addRow("Use Manual Bins", self.setManualBinsBooleanWidget)

    #
    # Number of Bins: manual setting
    #
    self.setNumberOfBinsWidget = ctk.ctkSliderWidget()
    self.setNumberOfBinsWidget.maximum = 255
    self.setNumberOfBinsWidget.minimum = 12
    self.setNumberOfBinsWidget.value = 32
    self.setNumberOfBinsWidget.singleStep = 1
    self.setNumberOfBinsWidget.setToolTip("Select the number of bins that should be used for the image histogram analysis. This parameter is only used when BLS segmentation method is called")
    parametersSegmentationLayout.addRow("Number Of Bins ", self.setNumberOfBinsWidget)


    #
    # Noise Attenuation Parameters Area
    #
    parametersNoiseAttenuationCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersNoiseAttenuationCollapsibleButton.text = "Noise Attenuation Parameters"
    parametersNoiseAttenuationCollapsibleButton.collapsed = True
    self.layout.addWidget(parametersNoiseAttenuationCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersNoiseAttenuationFormLayout = qt.QFormLayout(parametersNoiseAttenuationCollapsibleButton)

    #
    # Filtering Parameters: Condutance
    #
    self.setFilteringCondutanceWidget = ctk.ctkSliderWidget()
    self.setFilteringCondutanceWidget.maximum = 50
    self.setFilteringCondutanceWidget.minimum = 0
    self.setFilteringCondutanceWidget.value = 10
    self.setFilteringCondutanceWidget.singleStep = 1
    self.setFilteringCondutanceWidget.setToolTip("Condutance parameter.")
    parametersNoiseAttenuationFormLayout.addRow("Condutance ", self.setFilteringCondutanceWidget)

    #
    # Filtering Parameters: Number of iterations
    #
    self.setFilteringNumberOfIterationWidget = ctk.ctkSliderWidget()
    self.setFilteringNumberOfIterationWidget.maximum = 50
    self.setFilteringNumberOfIterationWidget.minimum = 1
    self.setFilteringNumberOfIterationWidget.value = 5
    self.setFilteringNumberOfIterationWidget.singleStep = 1
    self.setFilteringNumberOfIterationWidget.setToolTip("Number of iterations parameter.")
    parametersNoiseAttenuationFormLayout.addRow("Number Of Iterations ", self.setFilteringNumberOfIterationWidget)

    #
    # Filtering Parameters: Q value
    #
    self.setFilteringQWidget = ctk.ctkSliderWidget()
    self.setFilteringQWidget.singleStep = 0.01
    self.setFilteringQWidget.minimum = 0.01
    self.setFilteringQWidget.maximum = 1.99
    self.setFilteringQWidget.value = 1.2
    self.setFilteringQWidget.setToolTip("Q value parameter.")
    parametersNoiseAttenuationFormLayout.addRow("Q Value ", self.setFilteringQWidget)

    #
    # Label Refinement Area
    #
    parametersLabelRefinementCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersLabelRefinementCollapsibleButton.text = "Label Refinement Parameters"
    parametersLabelRefinementCollapsibleButton.collapsed = True
    self.layout.addWidget(parametersLabelRefinementCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersLabelRefinementLayout = qt.QFormLayout(parametersLabelRefinementCollapsibleButton)

    #
    # Gaussian Smooth Label Mask
    #
    self.setGaussianLabelQWidget = qt.QDoubleSpinBox()
    self.setGaussianLabelQWidget.setDecimals(3)
    self.setGaussianLabelQWidget.setMaximum(10)
    self.setGaussianLabelQWidget.setMinimum(0.1)
    self.setGaussianLabelQWidget.setSingleStep(0.1)
    self.setGaussianLabelQWidget.setValue(0.2)
    self.setGaussianLabelQWidget.setToolTip("Label smoothing by a gaussian distribution with variance sigma. The units here is given in mm.")
    parametersLabelRefinementLayout.addRow("Gaussian Sigma ", self.setGaussianLabelQWidget)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersIOLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = BrainStructuresSegmenterLogic()
    logic.run(self.inputSelector.currentNode()
              , self.outputSelector.currentNode()
              , self.setImageModalityBooleanWidget.currentText
              , self.setSeparateTissueBooleanWidget.isChecked()
              , self.setIsBETWidget.isChecked()
              , self.setRadioKMeans.isChecked()
              , self.setRadioBLS.isChecked()
              , self.setTissueTypeWidget.currentText
              , self.setApplyAADBooleanWidget.isChecked()
              , self.setApplyBiasCorrectionBooleanWidget.isChecked()
              , self.setApplyLabelSmoothingBooleanWidget.isChecked()
              , self.setTissueThresholdWidget.value
              , self.setManualBinsBooleanWidget.isChecked()
              , self.setNumberOfBinsWidget.value
              , self.setFilteringCondutanceWidget.value
              , self.setFilteringNumberOfIterationWidget.value
              , self.setFilteringQWidget.value
              , self.setGaussianLabelQWidget.value)

#
# BrainStructuresSegmenterLogic
#

class BrainStructuresSegmenterLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def run(self, inputVolume, outputVolume, imageModality, isSeparateTissue, applyBET, kMeansSegType, BLSSegType, tissueType, applyAAD, applyBiasCorrection, applyLabelSmoothing, tissueThr, useManualBins, numberOfBins, condutance, numIter, qValue, sigma):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False


    logging.info('Processing started')

    volumesLogic = slicer.modules.volumes.logic()
    tmpVolume = volumesLogic.CloneVolume(slicer.mrmlScene, inputVolume, "tmp-image")

    if not applyBET:
      slicer.util.showStatusMessage("Pre-processing: Brain extraction...")

      betParams = {}
      betParams["inputVolume"] = tmpVolume.GetID()
      betParams["outputVolume"] = tmpVolume.GetID()

      slicer.cli.run(slicer.modules.robexbrainextraction, None, betParams, wait_for_completion=True)


    if applyAAD:
      #################################################################################################################
      #                                              Noise Attenuation                                                #
      #################################################################################################################
      if isSeparateTissue:
        slicer.util.showStatusMessage("Step 1/4: Decreasing image noise level...")
      else:
        slicer.util.showStatusMessage("Step 1/3: Decreasing image noise level...")

      regParams = {}
      regParams["inputVolume"] = tmpVolume.GetID()
      regParams["outputVolume"] = tmpVolume.GetID()
      regParams["condutance"] = condutance
      regParams["iterations"] = numIter
      regParams["q"] = qValue

      slicer.cli.run(slicer.modules.aadimagefilter, None, regParams, wait_for_completion=True)


    if applyBiasCorrection:
      #################################################################################################################
      #                                             Bias Field Correction                                             #
      #################################################################################################################
      if isSeparateTissue:
        slicer.util.showStatusMessage("Step 2/4: Bias field correction...")
      else:
        slicer.util.showStatusMessage("Step 2/3: Bias field correction...")

      regParams = {}
      regParams["inputImageName"] = tmpVolume.GetID()
      regParams["outputImageName"] = tmpVolume.GetID()

      slicer.cli.run(slicer.modules.n4itkbiasfieldcorrection, None, regParams, wait_for_completion=True)

      #################################################################################################################
      #                                             Brain Tissue Segmentation                                         #
      #################################################################################################################
    if kMeansSegType:
      if isSeparateTissue:
        slicer.util.showStatusMessage("Step 3/4: Brain tissue segmentation...")
      else:
        slicer.util.showStatusMessage("Step 3/3: Brain tissue segmentation...")


      regParams = {}
      regParams["inputVolume"] = tmpVolume.GetID()
      regParams["outputLabel"] = outputVolume.GetID()
      regParams["imageModality"] = imageModality
      regParams["oneTissue"] = isSeparateTissue
      regParams["typeTissue"] = tissueType

      slicer.cli.run(slicer.modules.basicbraintissues, None, regParams, wait_for_completion=True)
    elif BLSSegType:
      if isSeparateTissue:
        slicer.util.showStatusMessage("Step 3/4: Brain tissue segmentation...")
      else:
        slicer.util.showStatusMessage("Step 3/3: Brain tissue segmentation...")

      regParams = {}
      regParams["inputVolume"] = tmpVolume.GetID()
      regParams["outputTissue"] = outputVolume.GetID()
      regParams["nTissues"] = 3  # Always 3 tissues...further improvements will be added
      regParams["doOneTissue"] = isSeparateTissue
      if imageModality == "T1":
        if tissueType == "White Matter":
          regParams["selectedTissueMask"] = 1
        elif tissueType == "Gray Matter":
          regParams["selectedTissueMask"] = 2
        elif tissueType == "CSF":
          regParams["selectedTissueMask"] = 3
      else:
        if tissueType == "White Matter":
          regParams["selectedTissueMask"] = 3
        elif tissueType == "Gray Matter":
          regParams["selectedTissueMask"] = 2
        elif tissueType == "CSF":
          regParams["selectedTissueMask"] = 1

      regParams["tissueThr"] = tissueThr
      regParams["useManualBins"] = useManualBins
      regParams["manualNumberOfBins"] = numberOfBins

      slicer.cli.run(slicer.modules.brainlogisticsegmentation, None, regParams, wait_for_completion=True)

    if applyLabelSmoothing:
      #################################################################################################################
      #                                                 Label Smoothing                                               #
      #################################################################################################################
      if isSeparateTissue:
        slicer.util.showStatusMessage("Step 4/4: Tissue mask refinement...")
        regParams = {}
        if kMeansSegType:
          if imageModality == "T1":
            if tissueType == "White Matter":
              regParams["labelToSmooth"] = 3
            elif tissueType == "Gray Matter":
              regParams["labelToSmooth"] = 2
            elif tissueType == "CSF":
              regParams["labelToSmooth"] = 1
          else:
            if tissueType == "White Matter":
              regParams["labelToSmooth"] = 1
            elif tissueType == "Gray Matter":
              regParams["labelToSmooth"] = 2
            elif tissueType == "CSF":
              regParams["labelToSmooth"] = 3
        elif BLSSegType:
          if imageModality == "T1":
            if tissueType == "White Matter":
              regParams["labelToSmooth"] = 1
            elif tissueType == "Gray Matter":
              regParams["labelToSmooth"] = 2
            elif tissueType == "CSF":
              regParams["labelToSmooth"] = 3
          else:
            if tissueType == "White Matter":
              regParams["labelToSmooth"] = 3
            elif tissueType == "Gray Matter":
              regParams["labelToSmooth"] = 2
            elif tissueType == "CSF":
              regParams["labelToSmooth"] = 1

        regParams["gaussianSigma"] = sigma
        regParams["inputVolume"] = outputVolume.GetID()
        regParams["outputVolume"] = outputVolume.GetID()

        slicer.cli.run(slicer.modules.labelmapsmoothing, None, regParams, wait_for_completion=True)


    #
    # Removing unnecessary nodes
    #
    slicer.mrmlScene.RemoveNode(tmpVolume)

    slicer.util.showStatusMessage("Processing completed")
    logging.info('Processing completed')

    return True


class BrainStructuresSegmenterTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_BrainStructuresSegmenter1()

  def test_BrainStructuresSegmenter1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = BrainStructuresSegmenterLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')

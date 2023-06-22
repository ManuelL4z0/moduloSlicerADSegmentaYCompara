import logging
import os

import vtk
import qt
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import numpy as np

#
# moduloGeneral
#

class moduloGeneral(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "moduloGeneral"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Manuel Lazo (US_MIBSD)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation

        self.parent.helpText = """
Este modulo ha sido desarrollado en el marco del MIBSD de la US. Tiene como objeto aglutinar efectos de Slicer para
facilitar la tarea de segmentacion y comparacion del cerebro principalmente.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """

"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # moduloGeneral1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='moduloGeneral',
        sampleName='moduloGeneral1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'moduloGeneral1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='moduloGeneral1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='moduloGeneral1'
    )

    # moduloGeneral2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='moduloGeneral',
        sampleName='moduloGeneral2',
        thumbnailFileName=os.path.join(iconsPath, 'moduloGeneral2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='moduloGeneral2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='moduloGeneral2'
    )


#
# moduloGeneralWidget
#

class moduloGeneralWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False
        self.radioDraw1 = 4,5
        self.radioDraw2 = 4,5
        self.segmentationNode = None
        self.segmentEditorNode = None
        self.segmentEditorWidget = None
        self.lastModifiedSegment = None
        self.segmentadoUmbrales = False



    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/moduloGeneral.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = moduloGeneralLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)",self.updateParameterNodeFromGUI)
        self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)",self.updateParameterNodeFromGUI)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).

        # CONTROL DEL ALGORITMO DE CRECIMIENTO DE SEMILLAS:
        ## BOTONES
        self.ui.pushButton_seedGrow_Draw1.clicked.connect(self.onButton_seedGrow_Draw1_Clicked)
        self.ui.pushButton_seedGrow_Draw2.clicked.connect(self.onButton_seedGrow_Draw2_Clicked)

        self.ui.pushButton_seedGrow_Preview.clicked.connect(self.onButton_seedGrow_Preview_Clicked)
        self.ui.pushButton_seedGrow_Apply.clicked.connect(self.onButton_seedGrow_Apply_Clicked)

        self.ui.pushButton_seedGrow_Erase1.clicked.connect(self.onButton_seedGrow_Erase1_Clicked)
        self.ui.pushButton_seedGrow_Erase2.clicked.connect(self.onButton_seedGrow_Erase2_Clicked)
        ## SLIDERS
        self.ui.SliderWidget_seedGrow_Draw1.valueChanged.connect(self.onSlider_seedGrow_Draw1_Changed)
        self.ui.SliderWidget_seedGrow_Draw2.valueChanged.connect(self.onSlider_seedGrow_Draw2_Changed)
        ## ATAJO BOTON 1 & 2 PARA CAMBIAR DE SEGMENTACION

        atajoDraw1 = qt.QShortcut(slicer.util.mainWindow())
        atajoDraw1.setKey(qt.QKeySequence("1"))
        atajoDraw1.connect("activated()",self.onButton_seedGrow_Draw1_Clicked)
        atajoDraw2 = qt.QShortcut(slicer.util.mainWindow())
        atajoDraw2.setKey(qt.QKeySequence("2"))
        atajoDraw2.connect("activated()",self.onButton_seedGrow_Draw2_Clicked)

        ## ATAJO ZOOM CON SHIFT

        self.lm = slicer.app.layoutManager()
        self.interactorInicial = self.lm.sliceWidget("Red").sliceView().interactorStyle().GetInteractor()
        self.interactor = self.interactorInicial
        self.interactor.AddObserver(vtk.vtkCommand.KeyPressEvent, self.onButton_seedGrow_KeyPressed)
        self.interactor.AddObserver(vtk.vtkCommand.KeyReleaseEvent, self.onButton_seedGrow_KeyReleased)
        #self.interactor.AddObserver(vtk.vtkCommand.MouseWheelForwardEvent, self.onButton_seedGrow_Incremento)
        #self.interactor.AddObserver(vtk.vtkCommand.MouseWheelBackwardEvent, self.onButton_seedGrow_Decremento)

        # SEGMENTACION EN 4 PASOS
        self.ui.RangeWidget_Threshold.valuesChanged.connect(self.onRangeWidget_Threshold_ValueChanged)
        self.ui.pushButton_a4p_Apply.clicked.connect(self.onButton_a4p_Apply_Clicked)

        # ESTADISTICAS DE LOS SEGMENTOS
        self.ui.pushButton_computeSegmentStatistics.clicked.connect(self.onButton_ComputeStatistics_Clicked)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if slicer.mrmlScene.GetFirstNodeByName("SegmentacionCerebro") is None:
            self.segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
            self.segmentationNode.CreateDefaultDisplayNodes()
            self.segmentationNode.SetName("SegmentacionCerebro")

            self.segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
            self.segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
            self.segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
            self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
            self.segmentEditorWidget.setSegmentationNode(self.segmentationNode)
        else:
            self.segmentationNode = slicer.mrmlScene.GetFirstNodeByName("SegmentacionCerebro")

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update node selectors and sliders
        self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
        self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
        #self.ui.invertedOutputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolumeInverse"))
        #self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
        #self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")

        # Update buttons states and tooltips
        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
        self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
        self._parameterNode.EndModify(wasModified)

    def onButton_seedGrow_Draw1_Clicked(self):
        # LLAMA AL WIDGET DE SEGMENT EDITOR Y ELIGE LA HERRAMIENTA DE DIBUJO
        # SELECCIONA UNA SEGMENTACIÓN EXISTENTE O CREA UNA NUEVA LLAMADA CEREBRO O BRAIN
        print("Sanity check del boton draw 1")
        if self._parameterNode.GetNodeReference("InputVolume") is not None and self.segmentEditorNode is not None and self.segmentEditorWidget is not None:
            if self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("Cerebro") != '':
                segmentID = self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("Cerebro")
                self.segmentEditorNode.SetSelectedSegmentID(segmentID)
                self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
                self.segmentEditorWidget.setMasterVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setActiveEffectByName("Paint")
                effect = self.segmentEditorWidget.activeEffect()
                effect.setParameter("BrushAbsoluteDiameter",self.radioDraw1)
                self.lastModifiedSegment = True
            else:
                segmentID = self.segmentationNode.GetSegmentation().AddEmptySegment("Cerebro")
                self.segmentEditorNode.SetSelectedSegmentID(segmentID)
                self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
                self.segmentEditorWidget.setMasterVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setActiveEffectByName("Paint")
                effect = self.segmentEditorWidget.activeEffect()
                effect.setParameter("BrushAbsoluteDiameter",self.radioDraw1)
                self.lastModifiedSegment = True

    def onButton_seedGrow_Draw2_Clicked(self):
        # LLAMA AL WIDGET DE SEGMENT EDITOR Y ELIGE LA HERRAMIENTA DE DIBUJO
        # SELECCIONA UNA SEGMENTACIÓN EXISTENTE O CREA UNA NUEVA LLAMADA NOCEREBRO O NOBRAIN
        print("Sanity check del boton draw 2")
        if self._parameterNode.GetNodeReference("InputVolume") is not None and self.segmentEditorNode is not None and self.segmentEditorWidget is not None:
            if self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("NoCerebro") != '':
                segmentID = self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("NoCerebro")
                self.segmentEditorNode.SetSelectedSegmentID(segmentID)
                self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
                self.segmentEditorWidget.setMasterVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setActiveEffectByName("Paint")
                effect = self.segmentEditorWidget.activeEffect()
                effect.setParameter("BrushAbsoluteDiameter",self.radioDraw2)
                self.lastModifiedSegment = False
            else:
                segmentID = self.segmentationNode.GetSegmentation().AddEmptySegment("NoCerebro")
                self.segmentEditorNode.SetSelectedSegmentID(segmentID)
                self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
                self.segmentEditorWidget.setMasterVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setActiveEffectByName("Paint")
                effect = self.segmentEditorWidget.activeEffect()
                effect.setParameter("BrushAbsoluteDiameter",self.radioDraw2)        
                self.lastModifiedSegment = False


    def onSlider_seedGrow_Draw1_Changed(self,value):
        self.radioDraw1 = value
        print("Tam, princel 1: ",self.radioDraw1)
        self.onButton_seedGrow_Draw1_Clicked()
        

    def onSlider_seedGrow_Draw2_Changed(self,value):
        self.radioDraw2 = value
        print("Tam, princel 1: ",self.radioDraw2)
        self.onButton_seedGrow_Draw2_Clicked()


    def onButton_seedGrow_Erase1_Clicked(self):
        print("Sanity check erase1")
        segmentID = self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("Cerebro")
        #segmento = self.segmentationNode.GetSegmentation().GetSegment(segmentID)
        #print(segmento)
        print(segmentID)
        if segmentID != '':
            self.segmentationNode.GetSegmentation().RemoveSegment(segmentID)

    def onButton_seedGrow_Erase2_Clicked(self):
        segmentID = self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("NoCerebro")
        if segmentID != '':
            self.segmentationNode.GetSegmentation().RemoveSegment(segmentID)

    def onButton_seedGrow_Preview_Clicked(self):
        print("Sanity check preview grow seeds")
        if self._parameterNode.GetNodeReference("InputVolume") is not None and self.segmentEditorNode is not None and self.segmentEditorWidget is not None:
            if self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("NoCerebro") != '' and self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("NoCerebro") != '':
                segmentID = self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("NoCerebro")
                self.segmentEditorNode.SetSelectedSegmentID(segmentID)
                self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
                self.segmentEditorWidget.setMasterVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setActiveEffectByName("Grow from seeds")
                effect = self.segmentEditorWidget.activeEffect()
                effect.self().onPreview()

            else:
                print("Error: Tried to start grow seeds but wass impossible")

    def onButton_seedGrow_Apply_Clicked(self):
        print("Sanity check apply grow seeds")
        if self._parameterNode.GetNodeReference("InputVolume") is not None and self.segmentEditorNode is not None and self.segmentEditorWidget is not None:
            if self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("NoCerebro") != '' and self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("NoCerebro") != '':
                segmentID = self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("NoCerebro")
                self.segmentEditorNode.SetSelectedSegmentID(segmentID)
                self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
                self.segmentEditorWidget.setMasterVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setActiveEffectByName("Grow from seeds")
                effect = self.segmentEditorWidget.activeEffect()
                effect.self().onApply()

            else:
                print("Error: Tried to start grow seeds but wass impossible")

    def onButton_seedGrow_KeyPressed(self,obj,event):
        print("Sanity check press draw grow seeds")
        key=self.interactor.GetKeySym()
        if key == 'Shift_L':
            self.interactor.AddObserver(vtk.vtkCommand.MouseWheelForwardEvent, self.onButton_seedGrow_Incremento,10)
            self.interactor.AddObserver(vtk.vtkCommand.MouseWheelBackwardEvent, self.onButton_seedGrow_Decremento,11)

    def onButton_seedGrow_KeyReleased(self,obj,event):
        print("Sanity check release draw grow seeds")
        key=self.interactor.GetKeySym()
        if key == 'Shift_L':
            self.interactor.RemoveObservers("MouseWheelForwardEvent",10)
            self.interactor.RemoveObservers("MouseWheelBackwardEvent",11)
        if key == '1':
            self.onButton_seedGrow_Draw1_Clicked()
        if key == '2':
            self.onButton_seedGrow_Draw2_Clicked()




    def onButton_seedGrow_Incremento(self,a,b):
        key=self.interactor.GetKeySym()
        #print(key)
        #if self.interactor.GetShiftKey():

        if self.interactor.GetShiftKey():
            print("INCREMENTO")
            if self.lastModifiedSegment:
                self.radioDraw1 += 1
                self.onButton_seedGrow_Draw1_Clicked()
            elif self.lastModifiedSegment ==False:
                self.radioDraw2 +=1
                self.onButton_seedGrow_Draw2_Clicked()


    def onButton_seedGrow_Decremento(self,a,b):
        key = self.interactor.GetKeySym()
        if self.interactor.GetShiftKey():
            print("DECREMENTO")
            if self.lastModifiedSegment:
                self.radioDraw1 -= 1
                self.onButton_seedGrow_Draw1_Clicked()
            elif self.lastModifiedSegment ==False:
                self.radioDraw2 -=1
                self.onButton_seedGrow_Draw2_Clicked()

    def onButton_ComputeStatistics_Clicked(self):
        #resultsTableNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableNode')

        import SegmentStatistics
        segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
        segStatLogic.getParameterNode().SetParameter("Segmentation", self.segmentationNode.GetID())
        segStatLogic.computeStatistics()
        stats = segStatLogic.getStatistics()

        # Display volume of each segment
        for segmentId in stats["SegmentIDs"]:
            volume_cm3 = stats[segmentId,"LabelmapSegmentStatisticsPlugin.volume_cm3"]
            segmentName = self.segmentationNode.GetSegmentation().GetSegment(segmentId).GetName()
            print(f"{segmentName} volume = {volume_cm3} cm3")        
        """
        segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
        segStatLogic.getParameterNode().SetParameter("Segmentation", self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName('Cerebro'))
        segStatLogic.getParameterNode().SetParameter("ScalarVolume", self._parameterNode.GetNodeReference("InputVolume").GetID())
        segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.enabled","False")
        segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.voxel_count.enabled","False")
        segStatLogic.computeStatistics()
        segStatLogic.exportToTable(resultsTableNode)
        resultsTableNode.AddEmptyRow()
        segStatLogic.getParameterNode().SetParameter("Segmentation", self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName('NoCerebro'))
        segStatLogic.computeStatistics()
        segStatLogic.exportToTable(resultsTableNode)        
        segStatLogic.showTable(resultsTableNode)
        """
        """
        segStatLogic.getParameterNode().SetParameter("ScalarVolume", self._parameterNode.GetNodeReference("InputVolume").GetID())
        segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.enabled","False")
        segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.voxel_count.enabled","False")
        """     

    def onRangeWidget_Threshold_ValueChanged(self,low,high):
        if self.segmentEditorNode is not None and self.segmentEditorWidget is not None:
            if self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("CerebroA4P") != '':
                segmentID = self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("CerebroA4P")
                self.segmentEditorNode.SetSelectedSegmentID(segmentID)
                self.segmentEditorNode.SetOverwriteMode(2)
                self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
                self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setMasterVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                self.segmentEditorWidget.setActiveEffectByName("Threshold")
                effect = self.segmentEditorWidget.activeEffect()
                effect.setParameter("MinimumThreshold",str(low))
                effect.setParameter("MaximumThreshold",str(high))
                effect.self().onApply()
                self.segmentadoUmbrales = True
                print("Sanity check de umbralizacion")
            else:
                segmentID = self.segmentationNode.GetSegmentation().AddEmptySegment("CerebroA4P")
                self.segmentEditorNode.SetSelectedSegmentID(segmentID)
                self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
                self.onRangeWidget_Threshold_ValueChanged(low,high)


    def onButton_a4p_Apply_Clicked(self):
        if self.segmentadoUmbrales:
            if self.segmentEditorNode is not None and self.segmentEditorWidget is not None:
                if self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("CerebroA4P") != '':
                    segmentID = self.segmentationNode.GetSegmentation().GetSegmentIdBySegmentName("CerebroA4P")
                    self.segmentEditorNode.SetSelectedSegmentID(segmentID)
                    self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
                    self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                    self.segmentEditorWidget.setMasterVolumeNode(self._parameterNode.GetNodeReference("InputVolume"))
                    
                    self.segmentEditorWidget.setActiveEffectByName("Margin")       
                    effect = self.segmentEditorWidget.activeEffect()
                    effect.setParameter("MarginSizeMm", -3)
                    effect.self().onApply()              

                    self.segmentEditorWidget.setActiveEffectByName("Islands")       
                    effect = self.segmentEditorWidget.activeEffect()
                    effect.setParameter("Minimumsize", 1000)
                    effect.setParameter("Operation","KEEP_LARGEST_ISLAND")
                    effect.self().onApply()              

                    self.segmentEditorWidget.setActiveEffectByName("Margin")       
                    effect = self.segmentEditorWidget.activeEffect()
                    effect.setParameter("MarginSizeMm", 3)
                    effect.self().onApply()              



class moduloGeneralLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("Threshold"):
            parameterNode.SetParameter("Threshold", "100.0")
        if not parameterNode.GetParameter("Invert"):
            parameterNode.SetParameter("Invert", "false")
    
    


#
# moduloGeneralTest
#

class moduloGeneralTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_moduloGeneral1()

    def test_moduloGeneral1(self):
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

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('moduloGeneral1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = moduloGeneralLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay('Test passed')

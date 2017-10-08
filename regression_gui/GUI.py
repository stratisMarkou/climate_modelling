from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from wx.lib.scrolledpanel import ScrolledPanel
from mpl_toolkits.basemap import Basemap
from matplotlib.figure import Figure
from training_script import *
from netCDF4 import *
import matplotlib
import custom_script
import numpy as np
import threading
import time
import wx
import os
import sys
import imp


class MainWindow():
    
    frame = None
    rootpath = None
    masterPanel = None
    
    def __init__(self, parent, title):
        self.rootpath = os.getcwd()
        self.frame = wx.Frame(parent, title=title, size=(760,480))
        self.statusbar = self.frame.CreateStatusBar()
        
        self.masterPanel = wx.Panel(self.frame)
        nb = wx.Notebook(self.masterPanel)

        filePage = FilePage(nb)
        trainingPage = TrainingPage(nb, self.rootpath)
        graphPage = GraphPage(nb, filePage, self.statusbar)

        nb.AddPage(filePage, "File settings")
        nb.AddPage(trainingPage, "Training")
        nb.AddPage(graphPage, "Graphs")

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        self.masterPanel.SetSizer(sizer)
        
        self.frame.Show(True)


class FilePage(wx.Panel):

    models = []
        
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.setContents()
        self.parent = parent

    def setContents(self):
        
        self.obsList = wx.ListCtrl(self, pos = (0, 0), size = (-1, 45), style = wx.LC_REPORT)
        self.obsList.InsertColumn(0, 'Target', width = 100) 
        self.obsList.InsertColumn(1, 'Filepath', wx.LIST_FORMAT_LEFT)
        self.obsList.InsertColumn(2, 'Filename', wx.LIST_FORMAT_LEFT)
        
        self.modelsList = wx.ListCtrl(self, pos = (0, 40), size = (-1, 150), style = wx.LC_REPORT)
        self.modelsList.InsertColumn(0, 'Models', width = 100) 
        self.modelsList.InsertColumn(1, 'Filepath', wx.LIST_FORMAT_LEFT)
        self.modelsList.InsertColumn(2, 'Filename', wx.LIST_FORMAT_LEFT)
        self.modelsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.removeModel)
                
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.obsList,0,wx.EXPAND)
        box.Add(self.modelsList,0,wx.EXPAND)
        
        settingsBox = wx.BoxSizer(wx.HORIZONTAL)
        
        panel_1 = wx.Panel(self, size = (-1, 180))
        wx.StaticText(panel_1, label = "Observational data")
        wx.StaticText(panel_1, label = "File location", pos = (0, 25))
        self.obsDirField = wx.TextCtrl(panel_1, -1, pos = (100, 25), size=(200,20))
        wx.StaticText(panel_1, label = "File name", pos = (0, 45))
        self.obsFilenameField = wx.TextCtrl(panel_1, -1, pos = (100, 45), size=(200,20))
        self.obsVarNamesList = wx.ListBox(panel_1, pos = (100, 65), size = (200, 100), choices = [], style = wx.LC_LIST)
        self.obsVarNamesList.Bind(wx.EVT_LISTBOX_DCLICK, self.setObservational)
        obsSearchButton = wx.Button(panel_1, -1, label = "...", pos = (310, 35), style = wx.BU_EXACTFIT)
        obsSearchButton.Bind(wx.EVT_BUTTON, self.searchObservational)
        
        settingsBox.Add(panel_1, 0, wx.ALL|wx.EXPAND, 10)

        panel_2 = wx.Panel(self, size = (-1, 180))
        wx.StaticText(panel_2, label = "Model data")
        wx.StaticText(panel_2, label = "File location", pos = (0, 25))
        self.modelDirField = wx.TextCtrl(panel_2, -1, pos = (100, 25), size=(200,20))
        wx.StaticText(panel_2, label = "File name", pos = (0, 45))
        self.modelFilenameField = wx.TextCtrl(panel_2, -1, pos = (100, 45), size=(200,20))
        wx.StaticText(panel_2, label = "Variable name", pos = (0, 65))
        self.modelDataVarname = wx.TextCtrl(panel_2, -1, pos = (100, 65), size=(100,20))
        self.modelVarNamesList = wx.ListBox(panel_2, pos = (100, 65), size = (200, 100), choices = [], style = wx.LC_LIST)
        self.modelVarNamesList.Bind(wx.EVT_LISTBOX_DCLICK, self.addModel)
        modelSearchButton = wx.Button(panel_2, -1, label = "...", pos = (310, 35), style = wx.BU_EXACTFIT)
        modelSearchButton.Bind(wx.EVT_BUTTON, self.searchModels)
        
        settingsBox.Add(panel_2, 0, wx.ALL|wx.EXPAND, 10)

        box.Add(settingsBox, 0, wx.EXPAND)
        
        self.SetSizer(box)

    def searchObservational(self, button):
        openFileDialog = wx.FileDialog(self, "Add", "", "", "NC files (*.nc)|*.nc", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        if not(openFileDialog.GetPath() == ""):
            self.setObservationalFields(openFileDialog.GetPath())
        
    def searchModels(self, button):
        openFileDialog = wx.FileDialog(self, "Add", "", "", "NC files (*.nc)|*.nc", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        if not(openFileDialog.GetPath() == ""):
            self.setModelFields(openFileDialog.GetPath())

    def setObservationalFields(self, filePath):
        
        path = ""
        self.obsFilenameField.SetValue(str(filePath).split("/")[-1])
        directory = str(filePath).split("/")[1:-1]
        for step in directory:
            path += "/" + step
        self.obsDirField.SetValue(path)

        os.chdir(path)
        dataset = Dataset(self.obsFilenameField.GetValue(), 'r', format = "NETCDF")
        variables = [name for name in dataset.variables]
        self.obsVarNamesList.Set(variables)

    def setModelFields(self, filePath):
        
        path = ""
        self.modelFilenameField.SetValue(str(filePath).split("/")[-1])
        directory = str(filePath).split("/")[1:-1]
        for step in directory:
            path += "/" + step
        self.modelDirField.SetValue(path)

        os.chdir(path)
        dataset = Dataset(self.modelFilenameField.GetValue(), 'r', format = "NETCDF")
        variables = [name for name in dataset.variables]
        self.modelVarNamesList.Set(variables)


    def setObservational(self, item):
        
        varName = item.GetString()
        self.obsList.DeleteAllItems()
        index = self.obsList.InsertStringItem(sys.maxsize, varName)
        self.obsList.SetStringItem(index, 1, self.obsDirField.GetValue())
        self.obsList.SetStringItem(index, 2, self.obsFilenameField.GetValue())
        
        
    def addModel(self, item):
        
        varName = item.GetString()
        if not(varName in self.getModels()):
            index = self.modelsList.InsertStringItem(sys.maxsize, varName)
            self.modelsList.SetStringItem(index, 1, self.modelDirField.GetValue())
            self.modelsList.SetStringItem(index, 2, self.modelFilenameField.GetValue())
            
            
    def removeModel(self, item):
        
        models = self.getModels()
        self.modelsList.DeleteItem(models.index(item.GetText()))
        
    def getModels(self):
        
        result = []
        for i in range(self.modelsList.GetItemCount()):
            result.append(self.modelsList.GetItem(itemIdx = i, col = 0).GetText())
            
        return result
            
        
class TrainingPage(wx.Panel):

    parent = None
    rootpath = None
    textEditor = None
    
    def __init__(self, parent, rootpath):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.rootpath = rootpath
        self.setEditor()

    def setEditor(self):
        
        boxSizer = wx.BoxSizer(wx.VERTICAL)
        
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.textEditor = wx.TextCtrl(self, -1, pos = (0, 0), size=(-1,-1), style = wx.TE_MULTILINE)
        self.textEditor.SetFont(font)
        try:
            self.textEditor.SetValue(self.getScript("custom_script.py"))
        except(FileNotFoundError):
            self.textEditor.SetValue(self.getScript("boilerplate_script.py"))
        panelSizer.Add(self.textEditor, 1, wx.EXPAND)

        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.Add((0,0), 1, wx.EXPAND)
        resetButton = wx.Button(self, -1, label = "Reset", style = wx.BU_EXACTFIT)
        resetButton.Bind(wx.EVT_BUTTON, self.resetEditor)
        bottomSizer.Add(resetButton, 0)
        saveButton = wx.Button(self, -1, label = "Load code", style = wx.BU_EXACTFIT)
        saveButton.Bind(wx.EVT_BUTTON, self.loadScript)
        bottomSizer.Add(saveButton, 0)
        
        boxSizer.Add(panelSizer, 1, wx.EXPAND|wx.BOTTOM, 5)
        boxSizer.Add(bottomSizer, 0, wx.EXPAND)
        self.SetSizer(boxSizer)

    def getScript(self, filename):
        script = ""
        file = open(filename, 'r')
        for line in file:
            script += line
        return script

    def resetEditor(self, event):
        self.textEditor.SetValue(self.getScript("boilerplate_script.py"))

    def loadScript(self, event):
        os.chdir(self.rootpath)
        file = open('custom_script.py', 'w')
        file.write(self.textEditor.GetValue())
        file.close()
        imp.reload(custom_script)
        
        
class GraphPage(ScrolledPanel):
    
    def __init__(self, parent, filePage, statusbar):
        ScrolledPanel.__init__(self, parent, style = wx.VSCROLL)
        self.EnableScrolling(False, True)
        self.filePage = filePage
        self.setContent()
        self.SetupScrolling()
        self.statusbar = statusbar
        self.thread = None

    def setContent(self, axes = None):

        masterSizer = wx.BoxSizer(wx.VERTICAL)

        self.resetTrainingPlots()
        
        self.canvas_1 = FigureCanvas(self, -1, self.trainingFigure)
        masterSizer.Add(self.canvas_1, 1, wx.EXPAND|wx.BOTTOM, 10)

        self.weightsFigure = Figure()
        self.canvas_2 = FigureCanvas(self, -1, self.weightsFigure)
        masterSizer.Add(self.canvas_2, 1, wx.EXPAND)
        self.canvas_2.Hide()

        self.modelPatchworkFigure = Figure()
        self.canvas_3 = FigureCanvas(self, -1, self.modelPatchworkFigure)
        masterSizer.Add(self.canvas_3, 1, wx.EXPAND)
        self.canvas_3.Hide()

        button = wx.Button(self, -1, label = "Train", pos = (0, 0), style = wx.BU_EXACTFIT)
        button.Bind(wx.EVT_BUTTON, self.trainAndUpdate)
        
        horizontalSizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontalSizer.Add((0,0), 1, wx.EXPAND)
        horizontalSizer.Add(button, 0, wx.ALL, 5)
        masterSizer.Add(horizontalSizer, 0, wx.EXPAND)
        
        self.SetSizerAndFit(masterSizer)
        self.SetupScrolling()

    def trainAndUpdate(self, event):
        
        obsList = self.filePage.obsList
        modelsList = self.filePage.modelsList

        if obsList.GetItemCount() == 0 or modelsList.GetItemCount() == 0:
            return
            
        obsPath = (obsList.GetItem(itemIdx = 0, col = 1).GetText(),
                    obsList.GetItem(itemIdx = 0, col = 2).GetText(),
                    obsList.GetItem(itemIdx = 0, col = 0).GetText())
                       
        modelPaths = [(modelsList.GetItem(itemIdx = i, col = 1).GetText(),
                        modelsList.GetItem(itemIdx = i, col = 2).GetText(),
                        modelsList.GetItem(itemIdx = i, col = 0).GetText())
                        for i in range(modelsList.GetItemCount())]
            
        obsDataset, modelDatasets, lng, lat = self.getDatasets(obsPath, modelPaths)
        modelDatasets = trim(modelDatasets)
        
        obsDataset = obsDataset[:modelDatasets.shape[1], :, :]
        mean = obsDataset.mean()
        obsDataset -= mean
        modelDatasets -= mean
        biasShape = modelDatasets[0, :, :, :].shape
        modelDatasets = np.concatenate((modelDatasets, np.ones(shape = (1,) + biasShape)))
        
        self.thread = threading.Thread(target=self.trainThread,
                                  args=(obsDataset, modelDatasets, lng, lat))
        self.thread.start()

    def trainThread(self, obsDataset, modelDatasets, lng, lat):
        self.statusbar.SetStatusText("Training...")
        selectionArray = custom_script.setSelectionArray()
        heldbackArray = custom_script.setHeldbackArray()
        weights, errors, heldbackErrors = getOptimizedWeights(
            obsDataset, modelDatasets, selectionArray,
            heldbackArray, custom_script.setTrainingParameters(),
            self.statusbar)
        self.statusbar.SetStatusText("Plotting...")
        self.resetTrainingPlots()
        self.resetPatchworkPlot()
        self.axes_training.plot(np.arange(len(errors)) + 1, errors)
        textstr = '$\sigma=%.2f$'%(errors[-1])
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.axes_training.text(0.65, 0.95, textstr, transform=self.axes_training.transAxes, fontsize=11, verticalalignment='top', bbox=props)
        
        self.axes_heldback.plot(np.arange(len(heldbackErrors)) + 1, heldbackErrors, color = "orange")
        textstr = '$\sigma=%.2f$'%(heldbackErrors[-1])
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.axes_heldback.text(0.65, 0.95, textstr, transform=self.axes_heldback.transAxes, fontsize=11, verticalalignment='top', bbox=props)

        weightsMatrix = weights.copy()
        maxW = weightsMatrix.max()
        minW = weightsMatrix.min()
        rows, cols = weightsMatrix.shape[2]//3 + 1, 3
        w = (1 - 0.09*(cols+1))/cols
        h = (1 - 0.07*(rows+1))/rows
        longs, lats = np.meshgrid(lng, lat)

        self.canvas_2.SetInitialSize(size=wx.Size(-1, rows*275))
        
        self.weightsFigure.clf()
        self.colorbarAxes = self.weightsFigure.add_axes([0.9, 0.3, 0.02, 0.4])
        for i in range(weightsMatrix.shape[0]):
            r, c = i//cols, i%cols
            axes = self.weightsFigure.add_axes([0.07 + (0.07+w)*c , 1-(h+0.07)*(r+1), w, h])
            shape = weightsMatrix.shape
            
            m = Basemap(projection='lcc',llcrnrlat=np.min(lat),urcrnrlat=np.max(lat),
                        llcrnrlon=np.min(lng),urcrnrlon=np.max(lng),resolution='c',
                        lat_0 = lat[:].mean(), lon_0 = lng[:].mean(), ax = axes)
            m.drawcoastlines()
            m.drawcountries()
            
            
            m.contourf(longs, lats, weightsMatrix[i, :,:], 15, linewidths=0.5,
                                latlon=True, vmin = minW, vmax =  maxW, color = 'plasma')

            parallels = np.arange(-90.,90,10.)
            m.drawparallels(parallels,labels=[1,0,0,0])
            meridians = np.arange(-180.,180.,10.)
            m.drawmeridians(meridians,labels=[0,0,0,1])
            
            norm = matplotlib.colors.Normalize(vmin = minW, vmax = maxW)
            matplotlib.colorbar.ColorbarBase(self.colorbarAxes, norm = norm, orientation = 'vertical')

        
        self.canvas_2.Show()
        
        bestModelPatchwork = evaluateBestModels(obsDataset, modelDatasets, selectionArray)

        m = Basemap(projection='lcc',llcrnrlat=np.min(lat),urcrnrlat=np.max(lat),
                        llcrnrlon=np.min(lng),urcrnrlon=np.max(lng),resolution='c',
                        lat_0 = lat[:].mean(), lon_0 = lng[:].mean(), ax = self.axes_patchwork)
        
        m.drawcoastlines()
        m.drawcountries()
        levels = np.unique(bestModelPatchwork)
        levels[-1] += 0.01
        m.imshow(bestModelPatchwork, interpolation = 'nearest')
        
        parallels = np.arange(-90.,90,10.)
        m.drawparallels(parallels,labels=[1,0,0,0])
        meridians = np.arange(-180.,180.,10.)
        m.drawmeridians(meridians,labels=[0,0,0,1])
        self.canvas_3.Show()
        
        self.Fit()
        self.statusbar.SetStatusText("Done.")

    def resetTrainingPlots(self):
        try:
            self.trainingFigure.clear()
        except(AttributeError):
            self.trainingFigure = Figure()
            
        left = 0.1
        bottom = 0.1
        width = 0.375
        height = 0.8
        self.axes_training = self.trainingFigure.add_axes([left, bottom, width, height])
        self.axes_training.set_yscale('log')
        self.axes_training.set_title("Training error")
        self.axes_training.set_xlabel("Training step")
        self.axes_training.set_ylabel("Error")

        left = 0.575
        bottom = 0.1
        width = 0.375
        height = 0.8
        self.axes_heldback = self.trainingFigure.add_axes([left, bottom, width, height])
        self.axes_heldback.set_yscale('log')
        self.axes_heldback.set_title("Heldback error")
        self.axes_heldback.set_xlabel("Training step")
        self.axes_heldback.set_ylabel("Error")
        
        self.Fit()

    def resetPatchworkPlot(self):
        try:
            self.modelPatchworkFigure.clear()
        except(AttributeError):
            self.modelPatchworkFigure = Figure()
        left = 0.1
        bottom = 0.1
        width = 0.8
        height = 0.8
        self.axes_patchwork = self.modelPatchworkFigure.add_axes([left, bottom, width, height])
        self.axes_patchwork.set_title("Best model patchwork")
    
    def getDatasets(self, obsPath, modelPaths):
        os.chdir(obsPath[0])
        obsDataset = Dataset(obsPath[1], 'r', format = "NETCDF4").variables[obsPath[2]]
        
        lng = Dataset(obsPath[1], 'r', format = "NETCDF4").variables['longitude'][:]
        lat = Dataset(obsPath[1], 'r', format = "NETCDF4").variables['latitude'][:]
        
        modelDatasets = []
        for i in range(len(modelPaths)):
            os.chdir(modelPaths[i][0])
            modelDatasets.append(Dataset(modelPaths[i][1], 'r', format = "NETCDF4")
                                 .variables[modelPaths[i][2]])
        
        return obsDataset, modelDatasets, lng, lat
    

app = wx.App(False)
MainWindow(None, "Linear trainer")
app.MainLoop()

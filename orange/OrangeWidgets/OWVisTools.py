from OWBaseWidget import *
from qt import *
from qwt import *
import sys
import cPickle
import os

class OptimizationDialog(OWBaseWidget):
    settingsList = ["resultListLen", "percentDataUsed"]
    resultsListLenList = ['10', '20', '50', '100', '150', '200', '250', '300', '400', '500', '700', '1000', '2000']
    resultsListLenNums = [ 10 ,  20 ,  50 ,  100 ,  150 ,  200 ,  250 ,  300 ,  400 ,  500 ,  700 ,  1000 ,  2000 ]
    percentDataList = ['5', '10', '15', '20', '30', '40', '50', '60', '70', '80', '90', '100']
    percentDataNums = [ 5 ,  10 ,  15 ,  20 ,  30 ,  40 ,  50 ,  60 ,  70 ,  80 ,  90 ,  100 ]

    def __init__(self,parent=None):
        #QWidget.__init__(self, parent)
        OWBaseWidget.__init__(self, parent, "Optimization Dialog", "optimize visualization impression and manage result", TRUE, FALSE, FALSE)

        self.setCaption("Qt Optimization Dialog")
        self.topLayout = QVBoxLayout( self, 10 ) 
        self.grid=QGridLayout(3,2)
        self.topLayout.addLayout( self.grid, 10 )

        self.kValue = 1
        self.resultListLen = 100
        self.percentDataUsed = 100
        self.widgetDir = sys.prefix + "/lib/site-packages/Orange/OrangeWidgets/"
        self.parentName = "Projection"
        #self.domainName = "Unknown"
        
        self.optimizedListFull = []
        self.optimizedListFiltered = []
        self.attrLenDict = {}

        self.loadSettings()
        
        self.optimizeButtonBox =QVGroupBox(self, "Optimize toolbox")
        self.optimizeButtonBox.setTitle("Optimize toolbox")
        
        self.manageResultsBox = QVGroupBox (self, "Manage results")
        self.manageResultsBox.setTitle("Manage results")

        self.infoBox =QVGroupBox(self, "Selected projection information")
        self.infoBox.setTitle("Information")
        
        self.resultsBox = QVGroupBox (self, "Results")
        self.resultsBox.setTitle("Results")

        self.grid.addWidget(self.optimizeButtonBox,0,0)
        self.grid.addWidget(self.manageResultsBox,1,0)
        self.grid.addWidget(self.infoBox, 2,0)
        self.grid.addMultiCellWidget (self.resultsBox,0,2, 1, 1)
        self.grid.setColStretch(0, 0)
        self.grid.setColStretch(1, 100)
        self.grid.setRowStretch(0, 0)
        self.grid.setRowStretch(1, 100)
        self.grid.setRowStretch(2, 0)
                
        self.interestingList = QListBox(self.resultsBox)
        #self.interestingList.setSelectionMode(QListBox.Extended)   # this would be nice if could be enabled, but it has a bug - currentItem doesn't return the correct value if this is on
        self.interestingList.setMinimumSize(200,200)

        self.hbox1 = QHBox(self.optimizeButtonBox)
        self.attrOrdLabel = QLabel('Number of neighbours (k): ', self.hbox1)
        self.attrKNeighbour = QComboBox(self.hbox1)

        self.hbox2 = QHBox(self.optimizeButtonBox)
        self.resultListLabel = QLabel('Length of results list: ', self.hbox2)
        self.resultListCombo = QComboBox(self.hbox2)
        for item in self.resultsListLenList: self.resultListCombo.insertItem(item)
        self.resultListCombo.setCurrentItem(self.resultsListLenNums.index(self.resultListLen))
        self.hbox5 = QHBox(self.optimizeButtonBox)
        self.minTableLenLabel = QLabel('Minimum examples in example table: ', self.hbox5)
        self.minTableLenEdit = QLineEdit(self.hbox5)
        self.minTableLenEdit.setText('0')
        self.hbox6 = QHBox (self.optimizeButtonBox)
        self.percentDataUsedLabel = QLabel('Percent of data used in evaluation: ', self.hbox6)
        self.percentDataUsedCombo = QComboBox(self.hbox6)
        for val in self.percentDataList: self.percentDataUsedCombo.insertItem(val)
        self.percentDataUsedCombo.setCurrentItem(self.percentDataNums.index(self.percentDataUsed))

        self.numberOfAttrBox = QVGroupBox (self.optimizeButtonBox, "Number of attributes")
        self.numberOfAttrBox.setTitle("Number of attributes")
    
        self.hbox3 = QHBox(self.numberOfAttrBox)
        self.optimizeSeparationButton = QPushButton('Optimize for exactly', self.hbox3)
        self.exactlyLenCombo = QComboBox(self.hbox3)    # maximum number of attributes in subset
        self.exactlyAttrLabel = QLabel('attr', self.hbox3)
        
        self.hbox4 = QHBox(self.numberOfAttrBox)
        self.optimizeAllSubsetSeparationButton = QPushButton('Optimize for max', self.hbox4)
        self.maxLenCombo = QComboBox(self.hbox4)    # maximum number of attributes in subset
        self.exactlyAttrLabel2 = QLabel('attr', self.hbox4)
        
        self.exactlyLenCombo.insertItem("ALL")
        self.maxLenCombo.insertItem("ALL")
        
        for i in range(3, 15):
            self.exactlyLenCombo.insertItem(str(i))
            self.maxLenCombo.insertItem(str(i))
        self.maxLenCombo.setCurrentItem(0)
        self.exactlyLenCombo.setCurrentItem(0)
        
        #self.resize(200, 500)
        self.attrLenCaption = QLabel('Select attribute count', self.manageResultsBox)
        self.attrLenList = QListBox(self.manageResultsBox)
        self.attrLenList.setSelectionMode(QListBox.Multi)
        self.attrLenList.setMinimumSize(60,60)

        self.reevaluateResults = QPushButton("Reevaluate results with different k values", self.manageResultsBox)
        self.filterButton = QPushButton("Remove attribute", self.manageResultsBox)
        self.removeSelectedButton = QPushButton("Remove selected projections", self.manageResultsBox)
        self.saveButton = QPushButton("Save", self.manageResultsBox)
        self.loadButton = QPushButton("Load", self.manageResultsBox)
        self.clearButton = QPushButton("Clear results", self.manageResultsBox)
        self.closeButton = QPushButton("Close", self.manageResultsBox)
        
        self.connect(self.resultListCombo, SIGNAL("activated(int)"), self.setResultListLen)
        self.connect(self.percentDataUsedCombo, SIGNAL("activated(int)"), self.setPercentDataUsed)
        self.connect(self.attrLenList, SIGNAL("selectionChanged()"), self.attrLenListChanged)
        self.connect(self.filterButton, SIGNAL("clicked()"), self.filter)
        self.connect(self.removeSelectedButton, SIGNAL("clicked()"), self.removeSelected)
        self.connect(self.saveButton, SIGNAL("clicked()"), self.save)
        self.connect(self.loadButton, SIGNAL("clicked()"), self.load)
        self.connect(self.clearButton, SIGNAL("clicked()"), self.clear)
        self.connect(self.closeButton, SIGNAL("clicked()"), self.hide)

        #self.optimizeButtonBox.setMinimumSize(180,150)
        #self.manageResultsBox.setMinimumSize(180,150)


    # result list can contain projections with different number of attributes
    # user clicked in the listbox that shows possible number of attributes of result list
    # result list must be updated accordingly
    def attrLenListChanged(self):
        self.interestingList.clear()
        self.optimizedListFiltered = []

        # check which attribute lengths do we want to show
        self.attrLenDict = {}
        for i in range(self.attrLenList.count()):
            intVal = int(str(self.attrLenList.text(i)))
            selected = self.attrLenList.isSelected(i)
            self.attrLenDict[intVal] = selected

        # show in results list only those results, that are the correct length        
        for i in range(len(self.optimizedListFull)):
            (accuracy, itemCount, list, strList) = self.optimizedListFull[i]
            if self.attrLenDict[len(list)] == 1:
                self.interestingList.insertItem("(%.2f, %d) - %s"%(accuracy, itemCount, strList))
                self.optimizedListFiltered.append((accuracy, itemCount, list, strList))
        self.interestingList.setCurrentItem(0)        

    # insert new result - give parameters: accuracy of projection, number of examples in projection and list of attributes.
    # parameter strList can be a pre-formated string containing attribute list (used by polyviz)
    def insertItem(self, accuracy, tableLen, list, strList = None):
        if strList == None:
            strList = list[0]
            for item in list[1:]:
                strList = strList + ", " + item

        for i in range(len(self.optimizedListFull)):
            (accuracy2, tableLen2, list2, strList2) = self.optimizedListFull[i]
            if accuracy2 == accuracy and tableLen2 == tableLen and list2 == list and strList2 == strList:
                return
            elif accuracy2 < accuracy:
                self.optimizedListFull.insert(i, (accuracy, tableLen, list, strList))
                return
        
        self.optimizedListFull.append((accuracy, tableLen, list, strList))

    # check result list and update list with number of attributes
    # + select the first result in the list
    def updateNewResults(self):
        # update list of attribute lengths
        self.attrLenList.clear()
        self.attrLenDict = {}
        found = []
        for i in range(len(self.optimizedListFull)):
            (acc, tableLen, list, strList) = self.optimizedListFull[i]
            if len(list) not in found:
                found.append(len(list))
        found.sort()
        for val in found:
            self.attrLenList.insertItem(str(val))
            self.attrLenDict[val] = 1
        self.attrLenList.selectAll(1)
        self.interestingList.setCurrentItem(0)

    # set the length of the list of best projections
    def setResultListLen(self, n):
        self.resultListLen = self.resultsListLenNums[n]
        self.saveSettings()

    # we may not want to use all the data when performing projection evaluation.
    def setPercentDataUsed(self, n):
        self.percentDataUsed = self.percentDataNums[n]
        self.saveSettings()

    def clear(self):
        self.optimizedListFull = []
        self.optimizedListFiltered = []
        self.attrLenDict = {}        
        self.interestingList.clear()
        self.attrLenList.clear()

    # we can remove projections that have a specific attribute
    def filter(self):
        (Qstring,ok) = QInputDialog.getText("Remove attribute", "Remove projections with attribute:")
        if ok:
            attributeName = str(Qstring)
            for i in range(len(self.optimizedListFiltered)-1, -1, -1):
                (accuracy, itemCount, list, strList) = self.optimizedListFiltered[i]
                found = 0
                for val in list:
                    if val == attributeName: found = 1
                if found:
                    # remove from  listbox and original list of results
                    self.interestingList.removeItem(i)
                    self.optimizedListFull.remove((accuracy, itemCount, list, strList))
        self.updateNewResults()

    # remove projections that are selected
    def removeSelected(self):
        for i in range(self.interestingList.count()-1, -1, -1):
            if self.interestingList.isSelected(i):
                # remove from listbox and original list of results
                self.interestingList.removeItem(i)
                (accuracy, itemCount, list, strList) = self.optimizedListFiltered[i]
                self.optimizedListFiltered.remove((accuracy, itemCount, list, strList))
                self.optimizedListFull.remove((accuracy, itemCount, list, strList))

    # save the list into a file - filename can be set if you want to call this function without showing the dialog
    def save(self, filename = None):
        if filename == None:
            # get file name
            filename = "%s (k - %2d)" % (self.parentName, self.kValue )
            qname = QFileDialog.getSaveFileName( os.getcwd() + "/" + filename, "Interesting projections (*.proj)", self, "", "Save Projections")
            if qname.isEmpty():
                return
            name = str(qname)
        else:
            name = filename
        if name[-5] != ".":
                name = name + ".proj"

        # open, write and save file
        file = open(name, "wt")
        cPickle.dump(self.optimizedListFiltered, file)
        file.flush()
        file.close()

    # load projections from a file
    def load(self):
        self.clear()
                
        name = QFileDialog.getOpenFileName( os.getcwd(), "Interesting projections (*.proj)", self, "", "Open Projections")
        if name.isEmpty():
            return

        file = open(str(name), "rt")
        self.optimizedListFull = cPickle.load(file)
        file.close()

        self.updateNewResults()

#test widget appearance
if __name__=="__main__":
    a=QApplication(sys.argv)
    ow=OptimizationDialog()
    a.setMainWidget(ow)
    ow.show()
    a.exec_loop()        
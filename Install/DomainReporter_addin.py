import arcpy, os, pythonaddins
from Tkinter import Tk

class CustomSubtype:
    def __init__(self,subtype):
        self.subtype = subtype
    def __repr__(self):
        if self.subtype['Default']:
            return "{0} (Default)".format(self.subtype["Name"])
        else:
            return self.subtype["Name"]
    def __str__(self):
        if self.subtype['Default']:
            return "{0} (Default)".format(self.subtype["Name"])
        else:
            return self.subtype["Name"]

    def __len__(self):
        return len(str(self))

    def GetFieldsWithDomains(self):
        fields = self.subtype["FieldValues"]
        fieldsWithDomains = []
        for k,v in fields.iteritems():
            defaultValue,domain = v
            fieldName = k
            if domain != None and domain.domainType == 'CodedValue':
                fieldsWithDomains.append(CustomSubtypeField(fieldName,domain))
        return fieldsWithDomains

class CustomSubtypeField:
    def __init__(self,name,domain):
        self.name = name
        self.domain = domain
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name
    
    def __len__(self):
        return len(str(self))

    def GetDomainValues(self):
        codedValueList = []
        for val, desc in self.domain.codedValues.iteritems():
                    codedValueList.append('{0} : {1}'.format(val, desc))
        return codedValueList

class CustomFeatureLayer:
    def __init__(self,featureLayer):
        self.featureLayer = featureLayer
        #self.fields = self.GetFieldsWithDomains()
        self.subtypes = map(lambda s: CustomSubtype(s), arcpy.da.ListSubtypes(featureLayer).values())
    def __repr__(self):
        return self.featureLayer.name

    def __str__(self):
        return self.featureLayer.name
    def __len__(self):
        return len(str(self))

class btnShowDomains(object):
    """Implementation for DomainReporter_addin.button (Button)"""
    def __init__(self):
        self.enabled = False
        self.checked = False
        self.domainValues = []
        btnShowDomains._hook = self

    def onClick(self):

        if len(self.domainValues) < 15:
            domainString = "\n".join(self.domainValues)
        else:
            truncatedList = self.domainValues[:15]
            truncatedList.append("<Truncated, but full list would be copied to clipboard>")
            domainString = "\n".join(truncatedList)
        layerName = cboLayers._hook.value
        subtypeName = cboSubtypes._hook.value
        fieldName = cboFieldsWithDomains._hook.value
        response = pythonaddins.MessageBox("Layer: {0}\nSubtype: {1}\nField: {2}\n\nCoded Values: \n\n{3}\n\nPress Yes to copy to clipboard and close this window. \nPress No to close without copying to clipboard.".format(layerName,subtypeName,fieldName,domainString),"Domain Values",4)    
        if response == "Yes":
            self.CopyToClipboard()

    def CopyToClipboard(self):
        domainString = "Code\tValue\n"+"\n".join(map(lambda x: x.replace(" : ","\t"),self.domainValues))
        r = Tk(baseName='') #fixes python 2.7 issue
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(domainString)
        r.update() 
        r.destroy()
    def SetButton(self,enabled=False,domainValues=[]):
        self.enabled = enabled
        self.domainValues = domainValues

class cboSubtypes(object):
    """Implementation for DomainReporter_addin.combobox_2 (ComboBox)"""
    def __init__(self):
        self.items = []
        self.editable = True
        self.enabled = False
        self.dropdownWidth = 'WWWWWWWWWWWWWW' 
        self.width = 'WWWWWWWWWWWWWW'
        self.selectedSubtype = None
        cboSubtypes._hook = self

    def onSelChange(self, selection):
        self.selectedSubtype = selection
        if self.selectedSubtype not in (None,""):
            fieldsWithDomains = self.selectedSubtype.GetFieldsWithDomains()
            if len(fieldsWithDomains):
                cboFieldsWithDomains._hook.SetComboBox(fieldsWithDomains,True,True,"")
            else:
                cboFieldsWithDomains._hook.SetComboBox(value="No fields w/ domains")
                

        else:
            cboFieldsWithDomains._hook.SetComboBox()

        
    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass
    def SetComboBox(self,items=[],editable=True,enabled=False,value=""):
        self.items = items
        self.editable = editable
        self.enabled = enabled
        self.value = value
        self.refresh()
    

class cboLayers(object):
    """Implementation for DomainReporter_addin.combobox (ComboBox)"""
    def __init__(self):
        self.items = []
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWWWWW' 
        self.width = 'WWWWWWWWWWWWWW'
        self.selectedLayer = None
        cboLayers._hook = self
        
 
    def onSelChange(self, selection):
        self.selectedLayer = selection
        btnShowDomains._hook.SetButton()
        if cboLayers._hook.selectedLayer not in (None,""):
            foundSubtypes = self.selectedLayer.subtypes
            if len(foundSubtypes):
                cboSubtypes._hook.SetComboBox(items=foundSubtypes,enabled=True)
            else:
                cboSubtypes._hook.SetComboBox()
            cboFieldsWithDomains._hook.SetComboBox()

        else:
            cboSubtypes._hook.SetComboBox()
            cboFieldsWithDomains._hook.SetComboBox()
        
    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass
    def SetComboBox(self,items=[],editable=True,enabled=False,value=""):
        self.items = items
        self.editable = editable
        self.enabled = enabled
        self.value = value
        self.refresh()


class cboFieldsWithDomains(object):
    """Implementation for DomainReporter_addin.combobox_1 (ComboBox)"""
    def __init__(self):
        self.items = []
        self.editable = True
        self.enabled = False
        self.dropdownWidth = 'WWWWWWWWWWWWWW' 
        self.width = 'WWWWWWWWWWWWWW'
        cboFieldsWithDomains._hook = self

    def onSelChange(self, selection):
        selectedField = selection
        if selectedField not in (None,""):
            domainValues = selectedField.GetDomainValues()
            if len(domainValues):
                btnShowDomains._hook.SetButton(True,domainValues)
            else:
                btnShowDomains._hook.SetButton()
                
        else:
            btnShowDomains._hook.SetButton()
            

    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass
    def SetComboBox(self,items=[],editable=True,enabled=False,value=""):
        self.items = items
        self.editable = editable
        self.enabled = enabled
        self.value = value
        self.refresh()





class extDomainReporter(object):
    """Implementation for DomainReporter_addin.extension (Extension)"""
    def __init__(self):
        # For performance considerations, please remove all unused methods in this class.
        self.enabled = True
        extDomainReporter._hook = self

    #def startup(self):
    #    pass
    def newDocument(self):
        #layerList = []
        self.CleanToolbar()
    def openDocument(self):
        self.GetMapFeatureLayers()
        
    def beforeCloseDocument(self):
        self.CleanToolbar()
    def itemAdded(self, new_item):
        self.GetMapFeatureLayers()

    def itemDeleted(self, deleted_item):
        self.GetMapFeatureLayers()
    def GetMapFeatureLayers(self):
        cboFieldsWithDomains._hook.SetComboBox()
        cboSubtypes._hook.SetComboBox()
        comboLayers = []
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = mxd.activeDataFrame
        layers = arcpy.mapping.ListLayers(mxd,data_frame=df)
        for layer in layers:
            if layer.isFeatureLayer and not layer.isBroken:
                customLayer = CustomFeatureLayer(layer)
                if len(customLayer.subtypes):
                    comboLayers.append(customLayer)
        #comboLayers = [CustomFeatureLayer(layer) for layer in layers if layer.isFeatureLayer and not layer.isBroken]
        if len(comboLayers):
            cboLayers._hook.SetComboBox(comboLayers,True,True)
        else:
            cboLayers._hook.SetComboBox()
    
    def CleanToolbar(self):
        cboLayers._hook.SetComboBox()
        cboFieldsWithDomains._hook.SetComboBox()
        cboSubtypes._hook.SetComboBox()
        btnShowDomains._hook.SetButton()
        

"""
All view classes that make up the boTools gui.
"""

__version__ = '0.2.0'

import logging
import boViewGui
from pymel.core import *

logger = logging.getLogger('Views')
logger.setLevel(logging.DEBUG)

class Main(boViewGui.View):
    """The main view of the GUI.
    Contains several large buttons for accessing other
    feature sections.
    
    Currently sections is hard-coded. Should replace
    with a global list and use a loop to generate the buttons.
    """
    
    def getPath(self):
        return [('Main', 'Main')]
    
    def content(self):
        self.frame.setMarginWidth(20)
        self.frame.setMarginHeight(20)
        
        with columnLayout(adj=True, rs=10):
            self.viewItem( l='Basic', view='BasicMain')
            self.viewItem( l='Advanced', view='AdvancedMain')
            self.viewItem( l='Special', view='SpecialMain')
            button(l='Reload boRigs...', c=self.run_reload)
    
    def run_reload(self, *args):
        import boRigs
        import boRigs.special
        import boRigs.special.bookPage
        reload(boRigs)
        reload(boRigs.gui)
        reload(boRigs.gui.gui)
        reload(boRigs.gui.views)
        reload(boRigs.special)
        reload(boRigs.special.bookPage)
        boRigs.GUI()


class BasicMain(boViewGui.View):
    
    def getPath(self):
        return [('Main', 'Main'), ('Basic', 'BasicMain')]
    
    def content(self):
        with columnLayout(adj=True, rs=2) as col1:
            self.viewItem(l='Joint Tools', view='JointTools', ann='Tools for rigging pre-existing joint chains')
            self.viewItem(l='Attribute Tools', view='AttrTools', ann='Tools for creating helpful attributes')

class JointTools(boViewGui.View):
    
    def getPath(self):
        return [('Main', 'Main'), ('Basic', 'BasicMain'), ('Joint Tools', 'JointTools')]
    
    def content(self):
        with columnLayout(adj=True, rs=2):
            self.frameItem('Orient Controls', Callback(self.orientCtls), 'Orient any control object to a joint\nSelect a control then the joint to orient to.\nControl/Joint selection pairs are allowed.')
            self.frameItem('Drive Controls', Callback(self.driveCtls), 'Cause a control object to follow it\'s parent\njoint, creating a hierarchy of controls.\nSelect a control then the joint to drive it.')
    
    def orientCtls(self):
        pairs = self.getPairs()
        for ctl, jnt in pairs:
            self.orientCtl(ctl, jnt)
    
    def driveCtls(self):
        pairs = self.getPairs()
        for ctl, jnt in pairs:
            self.driveCtl(ctl, jnt)
    
    def getPairs(self):
        pairs = []
        selList = ls(sl=True)
        if len(selList) % 2 == 0:
            i = len(selList) / 2
            pairs = zip(selList[:i], selList[i:])
        return pairs
    
    def orientCtl(self, ctl, jnt):
        #grp control
        orient = group(ctl, n='%s_orient' % ctl)
        xform(orient, os=True, piv=[0, 0, 0])
        #orient 'orient' to the joint
        pc = parentConstraint(jnt, orient, mo=False)
        delete(pc)
        #zero transforms on ctl
        xform(ctl, os=True, t=[0, 0, 0], ro=[0, 0, 0])
        #parent and scale constrain jnt to ctl
        parentConstraint(ctl, jnt, mo=False)
        scaleConstraint(ctl, jnt, mo=False)
        #freeze transforms of ctl
        makeIdentity(ctl, apply=True)
    
    def driveCtl(self, ctl, jnt):
        #parent constrain ctl's orient to jnt
        orient = ctl.getParent()
        parentConstraint(jnt, orient, mo=True)

class AttrTools(boViewGui.View):
    
    def getPath(self):
        return [('Main', 'Main'), ('Basic', 'BasicMain'), ('Attribute Tools', 'AttrTools')]
    
    def content(self):
        self.frameItemWidth = 120
        with columnLayout(adj=True, rs=2) as col1:
            self.frameItem('Create Geo Selectable Attr', Callback(self.createGeoSelectableAttrSelected), 'Create a \'geoSelectable\' attr for toggling\nthe reference state of geometry.\nSelect a control then the geometry.')
            
    def createGeoSelectableAttrSelected(self):
        ctl = ls(sl=True)[0]
        geoList = ls(sl=True)[1:]
        self.createGeoSelectableAttr(ctl, geoList)
    
    def createGeoSelectableAttr(self, ctl, geoList):
        #add attr
        addAttr(ctl, ln='geoSelectable', at='long', min=0, max=1)
        setAttr('%s.geoSelectable' % ctl, k=False, cb=True)
        #setup condition
        cond = shadingNode('condition', asUtility=True)
        cond.secondTerm.set(1)
        cond.colorIfFalseG.set(2)
        ctl.geoSelectable >> cond.firstTerm
        for geo in geoList:
            cond.outColorR >> geo.overrideEnabled
            cond.outColorG >> geo.overrideDisplayType

class AdvancedMain(boViewGui.View):
    
    def getPath(self):
        return [('Main', 'Main'), ('Advanced', 'AdvancedMain')]
    
    def content(self):
        with columnLayout(adj=True, rs=2) as col1:
            self.frameItem('Shapes', lambda x:x, 'Move, instance, and re-parent shape nodes')
            self.frameItem('Spaces', lambda x:x, 'Create space switches for any object')


class SpecialMain(boViewGui.View):
    """A view containing shortcuts for special rig types."""
    
    def getPath(self):
        return [('Main', 'Main'), ('Special', 'SpecialMain')]
    
    def content(self):
        with columnLayout(adj=True, rs=15) as col1:
            self.viewItem(l='Special Rigs', view='SpecialRigs', ann='Special type rigs designed for specific\nsituations from books to rubiks cubes.')
            with frameLayout(lv=False, mw=4, mh=4, bs='etchedIn'):
                button(l='Triggers', c=Callback(mel.eval, 'source boTriggers; boTriggers;'), ann='Advanced tool designed for simplifying\nrig control selection.')
                button(l='TSM Tools', c=Callback(mel.eval, 'source boTSMTools; boTSMTools;'), ann='Set of modifications for the TSM2 rig.')
                button(l='Rig Walk', c=Callback(mel.eval, 'source boRigWalk; boRigWalk;'), ann='Tool designed to allow selection\nof adjacent rig controls via the arrow keys.')
                button(l='Sliders', c=Callback(mel.eval, 'source boSliders; boSliders;'), ann='Facial rigging tool for setting\nup a Jasin Osipa style facial rig interface.')
                button(l='Resetter', c=Callback(mel.eval, 'python("import boResetter\\nboResetter.GUI()")'), ann='Facial rigging tool for setting\nup a Jasin Osipa style facial rig interface.')


class SpecialRigs(boViewGui.View):
    def getPath(self):
        return [('Main', 'Main'), ('Special', 'SpecialMain'), ('Rigs', 'SpecialRigs')]
    
    def content(self):
        with columnLayout(adj=True, rs=2) as col1:
            with frameLayout(lv=False, mw=4, mh=4, bs='etchedIn'):
                button(l='Ball', c=lambda x:x, ann='Rig a sphere for use as a ball.\nIncludes roll, tilt, squash and stretch.')
                button(l='Book Page', c=self.run_bookPage, ann='Rig a single page for use in a book\nSelect any number of page geometries')
                button(l='Book Binding', c=lambda x:x, ann='Rig a book binding\nSelect a book binding geometry')
                button(l='Rubiks Cube', c=lambda x:x, ann='Rig a rubiks cube for full animation.\nCreate a grid of 26 cubes then select them.')
    
    def run_bookPage(self, *args):
        import boRigs.special.bookPage as bookPage
        rigger = bookPage.BookPage()
        rigger.geo = ls(sl=True)
        rigger.run()

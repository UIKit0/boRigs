


from pymel.core import *
import boTweaks
from boTweaks import views
import boViewGui.gui


LOG = boTweaks.getLogger('Gui')


VIEWS = views.VIEWS
WIN_NAME = 'boTweaksWin'

def Gui():
    g = boViewGui.gui.Gui()
    g.title = 'Tweaks {0}'.format(boTweaks.__version__)
    g.winName = WIN_NAME
    g.defaultView = views.DEFAULT_VIEW
    g.views = VIEWS
    g.create()
    del g


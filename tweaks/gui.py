


from pymel.core import *
import boTweaks
from boTweaks import views
import boViewGui.gui


LOG = boTweaks.getLogger('Gui')


VIEWS = views.VIEWS
WIN_NAME = 'boTweaksWin'

def Gui():
    title = 'Tweaks {0}'.format(boTweaks.__version__)
    g = boViewGui.Gui(title, WIN_NAME, VIEWS, views.DEFAULT_VIEW)
    g.create()


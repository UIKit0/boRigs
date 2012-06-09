


from pymel.core import *
import boTweaks
from boTweaks import views
import viewGui.gui


LOG = boTweaks.getLogger('Gui')


VIEWS = views.VIEWS
WIN_NAME = 'boTweaksWin'

def Gui():
    title = 'Tweaks {0}'.format(boTweaks.__version__)
    g = viewGui.Gui(title, WIN_NAME, VIEWS, views.DEFAULT_VIEW)
    g.create()


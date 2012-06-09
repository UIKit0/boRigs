


from pymel.core import *
import boTweaks
from boTweaks import core
import boViewGui

LOG = boTweaks.getLogger('Views')

DEFAULT_VIEW = 'MainView'


class MainView(boViewGui.View):
    displayName='Main'
    def buildBody(self):
        with columnLayout(adj=True, rs=2):
            with frameLayout(l='Setup', mw=4, mh=4, bs='out'):
                button(l='Tweak Selected', c=Callback(core.createTweaks))



VIEWS = [
    MainView,
]


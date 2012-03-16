


from pymel.core import *
import boTweaks
from boTweaks import core
from boViewGui import view

LOG = boTweaks.getLogger('Views')

DEFAULT_VIEW = 'MainView'


class MainView(view.View):
    _displayName='Main'
    def bodyContent(self):
        with columnLayout(adj=True, rs=2):
            with frameLayout(l='Setup', mw=4, mh=4, bs='out'):
                button(l='Tweak Selected', c=Callback(core.createTweaks))



VIEWS = [
    MainView,
]


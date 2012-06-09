"""
    Tweaks
    1.1
    
    Bohdon Sayre and Michael Sauls 
    www.bohdon.com
    www.michaelsauls.com
    
    A tool for applying final adjustments to
    chracters when animation cannot yield the desired results.
    
    Idea and workflow developed by Mikey Sauls.
    
    Usage:
        >>> import boTweaks
        >>> boTweaks.Gui()
    
    Dependencies:
        boTools
        viewGui
        boSliders.mel
"""




import os, logging
__version__ = '0.1.0'
__author__ = 'Bohdon Sayre'

__LOG_LEVEL__ = logging.DEBUG

def getLogger(name=''):
    if name != '':
        logname = '{0} : {1}'.format('Tweaks', name)
    else:
        logname = 'Tweaks'
    log = logging.getLogger(logname)
    log.setLevel(__LOG_LEVEL__)
    return log

LOG = getLogger()

def Gui():
    """Wrap gui.GUI as GUI for convenience"""
    import gui
    gui.Gui()



def devReload():
    import boTweaks
    reload(boTweaks)
    import boTweaks.gui
    reload(boTweaks.gui)
    import boTweaks.views
    reload(boTweaks.views)
    import boTweaks.core
    reload(boTweaks.core)


def sourceSliders():
    from pymel.core import mel
    result = False
    try:
        if not mel.exists('boSliders'):
            LOG.debug('Sourcing boSliders...')
            mel.source('boSliders')
        result = True
    except:
        LOG.error('Could not find/source `boSliders.mel.` This script is needed for boTweaks to function properly')
    return result

sourceSliders()

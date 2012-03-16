"""
    Bo Rig
    
    Copyright (C) 2010 Bohdon Sayre
    All Rights Reserved.
    bo@bohdon.com
    
    Description:
        A tool for advanced rigging in any area.
    
    Instructions:
        >>> import boRig
        >>> boRig.GUI()
    
    Version 0.1:
        >
    
    Feel free to email me with any bugs, comments, or requests!
"""

__version__ = '0.2.1'
__author__ = 'Bohdon Sayre'


import gui

def GUI():
    """Wrap gui.GUI as GUI for convenience"""
    gui.GUI()
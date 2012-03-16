


from pymel.core import *
import boTools.utils
import boTweaks


LOG = boTweaks.getLogger('core')

BASENAME_FMT = '{0}_tweak_f{1}'


def createTweaks(geo=None, frame=None):
    """Create a tweak for the given geometry on the given frame.
    If frame is None use the current time"""
    if geo is None:
        geo = selected()
    if geo == [] or geo is None:
        return
    
    if frame is None:
        frame = int(currentTime())
    
    LOG.debug('Creating tweaks for {0}'.format(geo))
    for obj in geo:
        createTweak(obj, frame)        



def createTweak(geo, frame):
    """
    Duplicate Geo
    Create/Retrieve Geo's Tweak Group
    Create Tweak Frame Group
    Create Tweak Slider
    Connect Tweak Geo to Base Geo
    """
    LOG.debug('Creating Tweak for {0} at {1}'.format(geo, frame))
    baseName = getBaseName(geo, frame)
    newGeoA, newGeoB = duplicateGeo(geo, baseName)
    tweakGrp = getTweakGrp(geo)
    tweakFrameGrp = createTweakFrameGrp(baseName, newGeo, tweakGrp)
    tweakSliderCtl = createTweakSlider(baseName, newGeo, tweakFrameGrp)
    


def createTweakGrp(geo):
    LOG.debug(' Creating tweak group for {0}'.format(geo))
    tweaksNode = getTweaksNode()
    tweakGrp = group(em=True, n='{0}_tweak_GRP'.format(geo))
    addAttr(tweakGrp, ln='tweaksNode', at='long')
    addAttr(tweakGrp, ln='geo', at='long')
    tweaksNode.tweakGrps >> tweakGrp.tweaksNode 
    geo.message >> tweakGrp.geo
    parent(tweakGrp, tweaksNode)
    return tweakGrp



def getTweakGrp(geo):
    LOG.debug(' Getting tweak group for {0}'.format(geo))
    tweakGrp = None
    tweaksNode = getTweaksNode()
    tweakGrps = getTweakGrps(tweaksNode)
    for grp in tweakGrps:
        grpGeoCons = grp.geo.listConnections()
        if len(grpGeoCons) > 0:
            grpGeo = grpGeoCons[0]
            if grpGeo == geo:
                tweakGrp = grp
    if tweakGrp is None:
        tweakGrp = createTweakGrp(geo)
    return tweakGrp


def createTweakFrameGrp(baseName, geo, tweakGrp):
    tweaksNode = getTweaksNode()
    tweakFrameGrp = group(em=True, n='{0}_GRP'.format(baseName))
    parent(tweakFrameGrp, tweakGrp)
    parent(geo, tweakFrameGrp)
    return tweakFrameGrp


def createTweakSlider(baseName, geo, tweakFrameGrp):
    """Create a boSlider for controlling this tweak.
    Automatically scale and position the slider based on the geo's bounding box"""
    LOG.debug(' Creating tweak slider {0} {1}'.format(geo, baseName))
    sliderGrp = PyNode(mel.bsldrCreateSlider(baseName, 1, 1, 1, .15, [0, 0, 0, 1]))
    sliderGrp.scale.set([2, 2, 2])
    sliderCtl = sliderGrp.getChildren()[0]
    gbb = geo.boundingBox()
    gcp = xform(geo, q=True, a=True, ws=True, rp=True)
    top = [gcp[0], gcp[1] + gbb.max()[1] + 1, gcp[2]]
    xform(sliderGrp, a=True, ws=True, t=top)
    parent(sliderGrp, tweakFrameGrp)
    return sliderGrp, sliderCtl


def duplicateGeo(geo, baseName):
    LOG.debug(' Duplicating tweak geo {0}'.format(geo))
    newGeo = duplicate(geo, n=baseName)[0]
    xform(newGeo, cp=True)
    move(newGeo, [0, 0, 0], rpr=True)
    unlockAttrs(newGeo)
    return newGeo



def connectTweak(target, base):
    """Connect the given target blendshape to the base.
    Create the blendshape node if one does not already exist."""
    pass



def updateTweakPositions():
    """Find all tweak setups in the scene and update their positions.
    This is used to move existing tweaks when new ones are created."""
    pass



def getBaseName(geo, frame, fmt=BASENAME_FMT):
    return fmt.format(geo, frame)


def getTweaksNode():
    """Return the tweak group node. Create it if it doesn't exist."""
    tweakList = boTools.utils.lsAttr('boTweaksNode', returnAttrs=False, regex='.*tweaks.*')
    tweakNode = None
    if tweakList != []:
        tweakNode = tweakList[0]
    else:
        tweakNode = group(em=True, n='tweaks_GRP')
        addAttr(tweakNode, ln='boTweaksNode', at='long')
        addAttr(tweakNode, ln='tweakGrps', at='long')
    return tweakNode


def getTweakGrps(tweakNode):
    return tweakNode.tweakGrps.listConnections()


def unlockAttrs(obj):
    """Unlock all translates, rotates, scales on the given object"""
    obj.translateX.setLocked(False)
    obj.translateY.setLocked(False)
    obj.translateZ.setLocked(False)
    obj.rotateX.setLocked(False)
    obj.rotateY.setLocked(False)
    obj.rotateZ.setLocked(False)
    obj.scaleX.setLocked(False)
    obj.scaleY.setLocked(False)
    obj.scaleZ.setLocked(False)




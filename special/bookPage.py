"""
A special rig type that turns any geometry plane
into an animatable page of a book.
"""

__version__ = '0.8.2'

import sys, os, logging
from pymel.core import *

logger = logging.getLogger('Special : Book Page')
logger.setLevel(logging.DEBUG)

class BookPage(object):
    """Book Page special rig class.
    
    Rigs up a single page with joints for simple animation.
    
    Resulting hierarchy:
    page_RIG
      |__ bindGeo_GRP
      |   \__ page_geo
      |__ page_CTLS
      |   \__ page_ctl
      |       \__ page_ctl2
      |           \__ ...
      \__ page_JOINTS
          \__ root
              \__ jointA
                  \__ ...
    """
    
    def __init__(self):
        self.geo = []
        self.joints = {}
        
    
    def run(self):
        logger.debug('Rigging Book Page(s)...')
        if self.geo == []:
            logger.error('No geometry was specified.')
            return
        
        logger.debug('Geometry (%d): %s' % (len(self.geo), self.geo) )
        
        #variables that will be used during the build
        self.scale = ()
        self.bb = None
        self.jointOrigin = ()
        
        for geo in self.geo:
            select(cl=True)
            if not geo.isReferenced():
                #freeze transformations, delete history, and project uvs
                logger.debug('Freezing transforms, deleting history, and projecting uvs -- %s' % geo)
                makeIdentity(geo, apply=True, t=True, r=True, s=True, n=False)
                select(geo, r=True)
                mel.DeleteHistory()
                mel.ConvertSelectionToFaces()
                polyProjection(ch=False, type='Planar', ibd=True, icx=0.5, icy=0.5, ra=0, isu=1, isv=1, md='x')
            
            #get scales and positining
            self.scale, self.bb, self.jointOrigin = self.getXformsFromGeo(geo)
            logger.debug('Scale: %f x %f' % (self.scale[1], self.scale[2]))
            logger.debug('Joint Origin: %s' % self.jointOrigin)
            
            #build hierarchy and joints with scale and positioning
            rigGrp, ctlGrp, ctlScaleGrp, jointGrp, jointScaleGrp = self.buildGrps(geo)
            joints = self.buildJoints(geo)
            parent(joints['root'], jointScaleGrp)
            logger.debug('Hierarchy built for %s' % geo)
            
            #create the skin cluster
            select(cl=True)
            logger.debug('Creating skin cluster: %s -> %s' % (joints['root'], geo))
            skinCluster([joints['root'], geo], sm=0, nw=2, dr=4.0)
            
            #setup controls
            mainCtl, ctls = self.buildCtls(geo)
            ctlOrients = self.connectCtls(mainCtl, ctls, joints, ctlGrp, ctlScaleGrp, jointScaleGrp)
            
            #pretty up the rig
            self.cleanupRig(ctlGrp, jointGrp)
            
            logger.debug('Importing weights for %s' % geo)
            self.importWeights(geo, joints)
        
    def getXformsFromGeo(self, geo):
        """Return the scale, bounding box, and point of root joint
        based on the geos size and position
        scale = (x scale, y scale, z scale) in relation to (1, 1, 1)
        jointOrigin = dt.Point([x, y, z])
        """
        bb = geo.getBoundingBox()
        scale = ([bb.max()[i] - bb.min()[i] for i in range(0, 3)])
        jointOrigin = dt.Point([ bb.min()[0], (bb.max()[1] + bb.min()[1]) * 0.5, bb.min()[2] ])
        return scale, bb, jointOrigin
    
    def buildGrps(self, geo):
        """Build the main group hierarchy of the rig.
        The top group is always at world level"""
        
        rigGrp = group( em=True, n='%s_RIG' % geo, w=True )
        ctlGrp = group( em=True, n='CTLS', p=rigGrp )
        ctlScaleGrp = group( em=True, n='ctls_scale', p=ctlGrp )
        jointGrp = group( em=True, n='JOINTS', p=rigGrp )
        jointScaleGrp = group( em=True, n='joints_scale', p=jointGrp )
        return rigGrp, ctlGrp, ctlScaleGrp, jointGrp, jointScaleGrp
    
    def buildJoints(self, geo):
        select(cl=True)
        #scale all joint coords based on geo
        jointPts = self.getXformedJointPoints()
        
        #need a shorter notation for controlled and dynamic joint buildout
        #for now each joint is hardcoded
        joints = {}
        joints['root'] = joint(n='root', p=jointPts['root'])
        joints['jointA'] = joint(n='jointA', p=jointPts['jointA'])
        joints['jointB'] = joint(n='jointB', p=jointPts['jointB'])
        joints['jointC'] = joint(n='jointC', p=jointPts['jointC'])
        joints['jointD'] = joint(n='jointD', p=jointPts['jointD'])
        select(joints['jointC'])
        joints['downJointA'] = joint(n='downJointA', p=jointPts['downJointA'])
        joints['downJointB'] = joint(n='downJointB', p=jointPts['downJointB'])
        joints['downJointC'] = joint(n='downJointC', p=jointPts['downJointC'])
        select(joints['jointC'])
        joints['upJointA'] = joint(n='upJointA', p=jointPts['upJointA'])
        joints['upJointB'] = joint(n='upJointB', p=jointPts['upJointB'])
        joints['upJointC'] = joint(n='upJointC', p=jointPts['upJointC'])
        #orient joints
        joint(joints['root'], e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        #scale joint display size
        for j in joints.keys():
            joints[j].radius.set((self.scale[2]*0.02) + 0.5)
        
        return joints
    
    
    def buildCtls(self, geo):
        """Build and attach controls for the rig."""
        h = .03 * (self.scale[1] + self.scale[2])/2
        jointPts = self.getXformedJointPoints()
        ctls = {}
        
        #main ctl
        ctlPt = [(),(),(),(),()]
        ctlPt[0] = (jointPts['root'][0], jointPts['root'][1] + h * 3,  jointPts['root'][2] - h )
        ctlPt[1] = (ctlPt[0][0], jointPts['root'][1] - h * 3, ctlPt[0][2])
        ctlPt[2] = (ctlPt[0][0], ctlPt[1][1], ctlPt[1][2] - h * 6)
        ctlPt[3] = (ctlPt[0][0], ctlPt[0][1], ctlPt[2][2])
        ctlPt[4] = (ctlPt[0])
        mainCtl = curve(p=ctlPt, d=1, n='%s_main_ctl' % geo)
        move([mainCtl.scalePivot, mainCtl.rotatePivot], jointPts['root'])
        
        #root
        ctlPt = [(),(),(),(),()]
        ctlPt[0] = (jointPts['root'][0], self.bb.max()[1] + h * 2, jointPts['root'][2])
        ctlPt[1] = (ctlPt[0][0], ctlPt[0][1]+h, ctlPt[0][2])
        ctlPt[2] = (ctlPt[0][0], ctlPt[1][1], jointPts['jointA'][2]-h)
        ctlPt[3] = (ctlPt[0][0], ctlPt[0][1], ctlPt[2][2])
        ctlPt[4] = (ctlPt[0])
        ctl = curve(p=ctlPt, d=1, n='%s_root_ctl' % geo)
        move([ctl.scalePivot, ctl.rotatePivot], jointPts['root'])
        ctls['root'] = ctl
        
        #jointA
        ctlPt = [(),(),(),(),()]
        ctlPt[0] = (jointPts['jointA'][0], self.bb.max()[1] + h * 2, jointPts['jointA'][2])
        ctlPt[1] = (ctlPt[0][0], ctlPt[0][1]+h, ctlPt[0][2])
        ctlPt[2] = (ctlPt[0][0], ctlPt[1][1], jointPts['jointB'][2]-h)
        ctlPt[3] = (ctlPt[0][0], ctlPt[0][1], ctlPt[2][2])
        ctlPt[4] = (ctlPt[0])
        ctl = curve(p=ctlPt, d=1, n='%s_jointA_ctl' % geo)
        move([ctl.scalePivot, ctl.rotatePivot], jointPts['jointA'])
        ctls['jointA'] = ctl
        
        #jointB
        ctlPt = [(),(),(),(),()]
        ctlPt[0] = (jointPts['jointB'][0], self.bb.max()[1] + h * 2, jointPts['jointB'][2])
        ctlPt[1] = (ctlPt[0][0], ctlPt[0][1]+h, ctlPt[0][2])
        ctlPt[2] = (ctlPt[0][0], ctlPt[1][1], jointPts['jointC'][2]-h)
        ctlPt[3] = (ctlPt[0][0], ctlPt[0][1], ctlPt[2][2])
        ctlPt[4] = (ctlPt[0])
        ctl = curve(p=ctlPt, d=1, n='%s_jointB_ctl' % geo)
        move([ctl.scalePivot, ctl.rotatePivot], jointPts['jointB'])
        ctls['jointB'] = ctl
        
        #jointC
        ctlPt = [(),(),(),(),()]
        ctlPt[0] = (jointPts['jointC'][0], self.bb.max()[1] + h * 2, jointPts['jointC'][2])
        ctlPt[1] = (ctlPt[0][0], ctlPt[0][1]+h, ctlPt[0][2])
        ctlPt[2] = (ctlPt[0][0], ctlPt[1][1], jointPts['jointD'][2]-h)
        ctlPt[3] = (ctlPt[0][0], ctlPt[0][1], ctlPt[2][2])
        ctlPt[4] = (ctlPt[0])
        ctl = curve(p=ctlPt, d=1, n='%s_jointC_ctl' % geo)
        move([ctl.scalePivot, ctl.rotatePivot], jointPts['jointC'])
        ctls['jointC'] = ctl
        
        #top corner
        ctlPt = [(),(),(),(),(),(),()]
        ctlPt[0] = (jointPts['upJointB'][0], jointPts['upJointB'][1], jointPts['upJointC'][2] + h * 2)
        ctlPt[1] = (ctlPt[0][0], ctlPt[0][1], ctlPt[0][2] + h)
        ctlPt[2] = (ctlPt[0][0], (ctlPt[1][1] + jointPts['upJointA'][1]) * 0.5, ctlPt[1][2])
        ctlPt[3] = (ctlPt[0][0], jointPts['upJointA'][1], ctlPt[0][2])
        ctlPt[4] = (ctlPt[0][0], ctlPt[3][1], ctlPt[3][2] - h)
        ctlPt[5] = (ctlPt[0][0], ctlPt[2][1], ctlPt[0][2])
        ctlPt[6] = (ctlPt[0])
        ctl = curve(p=ctlPt, d=1, n='%s_upJointA_ctl' % geo)
        move([ctl.scalePivot, ctl.rotatePivot], jointPts['upJointA'])
        ctls['upJointA'] = ctl
        
        #top corner tip
        ctlPt = [(),(),(),(),(),(),()]
        ctlPt[0] = (jointPts['upJointC'][0], jointPts['upJointC'][1] + h * 2, jointPts['upJointC'][2])
        ctlPt[1] = (ctlPt[0][0], ctlPt[0][1]+h, ctlPt[0][2])
        ctlPt[2] = (ctlPt[0][0], ctlPt[1][1], jointPts['upJointC'][2] + h * 3)
        ctlPt[3] = (ctlPt[0][0], jointPts['upJointB'][1] + h, ctlPt[2][2])
        ctlPt[4] = (ctlPt[0][0], ctlPt[3][1], jointPts['upJointC'][2] + h * 2)
        ctlPt[5] = (ctlPt[0][0], ctlPt[0][1], ctlPt[4][2])
        ctlPt[6] = (ctlPt[0])
        ctl = curve(p=ctlPt, d=1, n='%s_upJointB_ctl' % geo)
        move([ctl.scalePivot, ctl.rotatePivot], jointPts['upJointB'])
        ctls['upJointB'] = ctl
        
        #bottom corner
        ctlPt = [(),(),(),(),(),(),()]
        ctlPt[0] = (jointPts['downJointB'][0], jointPts['downJointB'][1], jointPts['downJointC'][2] + h * 2)
        ctlPt[1] = (ctlPt[0][0], ctlPt[0][1], ctlPt[0][2] + h)
        ctlPt[2] = (ctlPt[0][0], (ctlPt[1][1] + jointPts['downJointA'][1]) * 0.5, ctlPt[1][2])
        ctlPt[3] = (ctlPt[0][0], jointPts['downJointA'][1], ctlPt[0][2])
        ctlPt[4] = (ctlPt[0][0], ctlPt[3][1], ctlPt[3][2] - h)
        ctlPt[5] = (ctlPt[0][0], ctlPt[2][1], ctlPt[0][2])
        ctlPt[6] = (ctlPt[0])
        ctl = curve(p=ctlPt, d=1, n='%s_downJointA_ctl' % geo)
        move([ctl.scalePivot, ctl.rotatePivot], jointPts['downJointA'])
        ctls['downJointA'] = ctl
        
        #bottom corner tip
        ctlPt = [(),(),(),(),(),(),()]
        ctlPt[0] = (jointPts['downJointC'][0], jointPts['downJointC'][1] - h * 2, jointPts['downJointC'][2])
        ctlPt[1] = (ctlPt[0][0], ctlPt[0][1] - h, ctlPt[0][2])
        ctlPt[2] = (ctlPt[0][0], ctlPt[1][1], jointPts['downJointC'][2] + h * 3)
        ctlPt[3] = (ctlPt[0][0], jointPts['downJointB'][1] - h, ctlPt[2][2])
        ctlPt[4] = (ctlPt[0][0], ctlPt[3][1], jointPts['downJointC'][2] + h * 2)
        ctlPt[5] = (ctlPt[0][0], ctlPt[0][1], ctlPt[4][2])
        ctlPt[6] = (ctlPt[0])
        ctl = curve(p=ctlPt, d=1, n='%s_downJointB_ctl' % geo)
        move([ctl.scalePivot, ctl.rotatePivot], jointPts['downJointB'])
        ctls['downJointB'] = ctl
        
        for key in ctls.keys():
            setAttr('%s.visibility' % ctls[key], k=False, cb=True)
            setAttr('%s.sz' % ctls[key], k=False)
        setAttr('%s.visibility' % mainCtl, k=False, cb=True)
        
        return mainCtl, ctls
    
    def connectCtls(self, mainCtl, ctls, joints, ctlGrp, ctlScaleGrp, jointScaleGrp):
        """Create orient nodes and connect controls to joints"""
        
        jointPts = self.getXformedJointPoints()
        ctlOrients = {}
        for key in ctls.keys():
            ctl = ctls[key]
            j = joints[key]
            #create orient and offset nodes
            orient = group(em=True, n='%s_orient' % ctl)
            pc = parentConstraint(j, orient, w=1, mo=False)
            delete(pc)
            parent(ctl, orient)
            makeIdentity(ctl, apply=True)
            offset = group(ctl, n='%s_offset' % ctl)
            move([offset.scalePivot, offset.rotatePivot], jointPts[key])
            ctlOrients[key] = orient
            #parent constrain the joint
            parentConstraint(ctl, j, mo=True)
            ctl.s >> j.s
        
        #orient and point constrain child orients to leading joints
        constrs = {'jointA':'root', 'jointB':'jointA', 'jointC':'jointB',
                    'upJointA':'jointC', 'upJointB':'upJointA',
                    'downJointA':'jointC', 'downJointB':'downJointA'}
        for key, value in constrs.items():
            parentConstraint(joints[value], ctlOrients[key], mo=True)
        
        #connect mainCtls's scale to necessary nodes to create global scale control
        mainCtlOffset = group(mainCtl, n='%s_offset' % mainCtl, p=ctlGrp)
        mainCtlSpace = group(mainCtlOffset, n='%s_space' % mainCtl)
        mainCtlOrient = group(mainCtlSpace, n='%s_orient' % mainCtl)
        move([mainCtlOffset.scalePivot, mainCtlOffset.rotatePivot], jointPts['root'])
        move([mainCtlSpace.scalePivot, mainCtlSpace.rotatePivot], jointPts['root'])
        move([mainCtlOrient.scalePivot, mainCtlOrient.rotatePivot], jointPts['root'])
        move([jointScaleGrp.scalePivot, jointScaleGrp.rotatePivot], jointPts['root'])
        move([ctlScaleGrp.scalePivot, ctlScaleGrp.rotatePivot], jointPts['root'])
        parentConstraint(mainCtl, ctlOrients['root'], mo=True)
        parentConstraint(mainCtl, jointScaleGrp, st=['x', 'y', 'z'], mo=True)
        scaleConstraint(mainCtl, jointScaleGrp)
        scaleConstraint(mainCtl, ctlScaleGrp)
        mainCtl.sz >> mainCtl.sx
        mainCtl.sx.setLocked(True)
        mainCtl.sx.setKeyable(False)
        
        #parent orients to the ctlGrp
        for key in ctlOrients.keys():
            parent(ctlOrients[key], ctlScaleGrp)
        
        return ctlOrients
    
    def cleanupRig(self, ctlGrp, jointGrp):
        ctlGrp.overrideEnabled.set(True)
        ctlGrp.overrideColor.set(17)
        jointGrp.visibility.set(False)
    
    def importWeights(self, geo, joints):
        relDir = os.path.dirname(__file__)
        weightMap = os.path.join(relDir, 'assets/bookPage_weightMap.template')
        tempMap = os.path.join(relDir, 'assets/bookPage_weightMap.weightMap')
        
        #read the template weight map and replace <geo> with the name of the geo
        try:
            f = open(weightMap, 'r')
            mappings = f.read()
            #replace 'geo' with geo name
            mappings = mappings.replace('geo', str(geo))
            #replace joints with their possible long names
            for j in joints.keys():
                mappings = mappings.replace('%s\t' % j, '%s\t' % joints[j])
            try:
                fTmp = open(tempMap, 'w')
                fTmp.write(mappings)
            except IOError, e:
                print e
            finally:
                fTmp.close()
        except IOError, e:
            print e
        finally:
            f.close()
        
        select(cl=True)
        select(geo, r=True)
        mel.source('importSkinMap')
        mel.importSkinWeightMap(tempMap, 'weightMap')
        #delete the temporary .weightMap file
        os.remove(tempMap)
        select(cl=True)
    
    def getXformedJointPoints(self):
        jointPts = self.getJointPoints()
        for key in jointPts.keys():
            v = jointPts[key]
            jointPts[key] = [self.jointOrigin[0], v[1]* self.scale[1] + self.jointOrigin[1], v[2]* self.scale[2] + self.jointOrigin[2]]
        return jointPts
        
    def getJointPoints(self):
        """Define the joint points.
        This determines the much of how the page will
        bend, and could be dynamically controllable
        in the future."""
        
        jointPts = {'root': [0, 0.0, 0.0],
                     'jointA': [0, 0.0, 0.2],
                     'jointB': [0, 0.0, 0.5],
                     'jointC': [0, 0.0, 0.777],
                     'jointD': [0, 0.0, 1.0],
                     'upJointA': [0, 0.125, 0.779],
                     'upJointB': [0, 0.369, 0.911],
                     'upJointC': [0, 0.5, 1.0],
                     'downJointA': [0, -0.125, 0.779],
                     'downJointB': [0, -0.369, 0.911],
                     'downJointC': [0, -0.5, 1.0],}
        return jointPts




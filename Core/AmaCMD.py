# -------------------------------
# Author:WangYan   
# Email:
# Date:
# Update:None                       
#-------------------------------
import maya.cmds as mc
import maya.mel as mm

def attachObjectOnCurve(object,uValue,curve,prefix,span=0):
    '''
    rebuild the selected curve and attach curves on it
    return: motionPath node
    '''
    #rebuild the curve
    if span:
        mc.rebuildCurve(curve,ch=0,rpo=1,rt=0,end=1,kr=0,kcp=0,kep=1,kt=0,s=span,d=3,tol=0.01)
    #create motionPath node
    motionPathNode=mc.createNode('motionPath',n=prefix + '_MPN')
    #get curve shape
    curveShape=mc.listRelatives(curve,s=True,type='nurbsCurve')[0]
    #make connections
    mc.connectAttr(curveShape + '.worldSpace[0]', motionPathNode + '.geometryPath')
    for attrOut,attrIn in (['.rotateOrder', '.rotateOrder'],['.rotate', '.rotate'],['.allCoordinates', '.translate']):
        mc.connectAttr(motionPathNode + attrOut, object + attrIn)
    #set uValue
    mc.setAttr(motionPathNode + '.fractionMode', 1)
    mc.setAttr(motionPathNode + '.uValue', uValue)
    mc.setAttr(motionPathNode + '.frontAxis', 0)
    mc.setAttr(motionPathNode + '.upAxis', 1)
    return motionPathNode

def addShapesToTransform(transform,shape,type):
    '''
    parent shape to transfrom
    _type = 'replace'   replace _transform's shape to _shape
    _type = 'add'       add _shape to _transform's shape transform
    '''
    getShape=mc.listRelatives(shape,s=True)

    mc.parent(shape,transform)
    mc.makeIdentity(shape)
    mc.parent(shape,w=True)

    if type == 'add':
        for i in getShape:
            mc.parent(i,transform,add=True,s=True)

    if type == 'replace':
        mc.delete(mc.listRelatives(transform,s=True))
        for i in getShape:
            mc.parent(i,transform,add=True,s=True)

def addAttributeGroup(obj,shuffix):
    '''
    add a group as obj's parent
    '''
    up=mc.listRelatives(obj,p=True)
    grp=mc.group(n=obj[0]+'_'+shuffix,em=True)

    mc.delete(mc.parentConstraint(obj,grp,mo=False),mc.scaleConstraint(obj,grp,mo=False))
    mc.parent(obj,grp)

    if up:
        mc.parent(grp,up)
    else:
        pass

def overrideSelectedColor(obj,index):
    '''
    index           set color index
    '''
    if mc.getAttr(obj+'.overrideEnabled')<>1:
        mc.setAttr(obj+'.overrideEnabled',1)
    mc.setAttr(obj+'.overrideColor',index)

def messageTrack(input):
    '''
    create a unknown node and link its attr "message" to _inputs same attr
    return node
    '''
    tracker=mc.createNode("unknown")
    mc.addAttr(tracker,ln="tracking",multi=True,at="message",im=False)

    for i in _input:
        mc.connectAttr(i+'.message',tracker+'.tracking',na=True)

    return tracker

def createLookUpSlider(inputPlane,inputCtrl):
    '''
    create a locator which controled by inputCtrl and sliding on inputPlane
    :return: None
    '''
    #check the inputPlane type
    shapeNode = mc.listRelatives(inputPlane,s=True)[0]
    #if its nurbs
    if mc.nodeType(shapeNode) == 'nurbsSurface':
        #prepare the node that we need later
        dcm1 = mc.createNode('decomposeMatrix',n=inputCtrl+'_DCM1')
        dcm2 = mc.createNode('decomposeMatrix',n=inputCtrl+'_DCM2')
        cpos = mc.createNode('closestPointOnSurface',n=inputCtrl+'_CPOS')
        posi = mc.createNode('pointOnSurfaceInfo',n=inputCtrl+'_POSI')
        fbfm = mc.createNode('fourByFourMatrix',n=inputCtrl+'_FBFM')
        #create lookup locator
        loc1 = mc.spaceLocator(n = inputCtrl + '_LookupLoc')
        #make connections
        #get closet point on surface
        mc.connectAttr(inputCtrl+'.worldMatrix',dcm1+'.inputMatrix')
        mc.connectAttr(dcm1+'.outputTranslate',cpos+'.inPosition')
        mc.connectAttr(shapeNode+'.worldSpace',cpos+'.inputSurface')
        mc.connectAttr(shapeNode+'.worldSpace',posi+'.inputSurface')
        mc.connectAttr(cpos+'.result.parameterU',posi+'.parameterU')
        mc.connectAttr(cpos+'.result.parameterV',posi+'.parameterV')
        #construct new matrix
        mc.connectAttr(posi+'.result.normalizedNormal.normalizedNormalX',fbfm+'.in00')
        mc.connectAttr(posi+'.result.normalizedNormal.normalizedNormalY',fbfm+'.in01')
        mc.connectAttr(posi+'.result.normalizedNormal.normalizedNormalZ',fbfm+'.in02')
        mc.connectAttr(posi+'.result.normalizedTangentU.normalizedTangentUX',fbfm+'.in10')
        mc.connectAttr(posi+'.result.normalizedTangentU.normalizedTangentUY',fbfm+'.in11')
        mc.connectAttr(posi+'.result.normalizedTangentU.normalizedTangentUZ',fbfm+'.in12')
        mc.connectAttr(posi+'.result.normalizedTangentV.normalizedTangentVX',fbfm+'.in20')
        mc.connectAttr(posi+'.result.normalizedTangentV.normalizedTangentVY',fbfm+'.in21')
        mc.connectAttr(posi+'.result.normalizedTangentV.normalizedTangentVZ',fbfm+'.in22')
        mc.connectAttr(posi+'.result.position.positionX',fbfm+'.in30')
        mc.connectAttr(posi+'.result.position.positionY',fbfm+'.in31')
        mc.connectAttr(posi+'.result.position.positionZ',fbfm+'.in32')
        #decompse new matrix
        mc.connectAttr(fbfm+'.output',dcm2+'.inputMatrix')
        #connect transform attributes
        mc.connectAttr(dcm2+'.outputTranslate',loc1[0]+'.translate')
        mc.connectAttr(dcm2+'.outputRotate',loc1[0]+'.rotate')
        #if its polygon
    else:
        print "InputPlane needs to be NurbsSurface "
        return
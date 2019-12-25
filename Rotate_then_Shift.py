# Name:         RotateFC.py  
# Purpose:      Rotates a feature class  
# Author:       Curtis Price, cprice@usgs.gov  
# Created:      09/17/2013 11:49:25 AM  
# Environment:  ArcGIS 10.x  
# -------------------------------------------------------------------  
  
import os  
import sys  
import traceback  
import arcpy  
from arcpy import env  

def shift_features(in_features, x_shift=None, y_shift=None):
    """
    Shifts features by an x and/or y value. The shift values are in
    the units of the in_features coordinate system.
 
    Parameters:
    in_features: string
        An existing feature class or feature layer.  If using a
        feature layer with a selection, only the selected features
        will be modified.
 
    x_shift: float
        The distance the x coordinates will be shifted.
 
    y_shift: float
        The distance the y coordinates will be shifted.
    """
 
    with arcpy.da.UpdateCursor(in_features, ['SHAPE@XY']) as cursor:
        for row in cursor:
            cursor.updateRow([[row[0][0] + (x_shift or 0),
                               row[0][1] + (y_shift or 0)]])
 
    return

def RotateFeatureClass(inputFC, outputFC,  
                       angle=0, pivot_point=None):  
    """Rotate Feature Class  
  
    inputFC     Input features  
    outputFC    Output feature class  
    angle       Angle to rotate, in degrees  
    pivot_point X,Y coordinates (as space-separated string)  
                Default is lower-left of inputFC  
  
    As the output feature class no longer has a "real" xy locations,  
    after rotation, it no coordinate system defined.  
    """  
    print "STEP-1"
    def RotateXY(x, y, xc=0, yc=0, angle=0, units="DEGREES"):  
        """Rotate an xy cooordinate about a specified origin  
  
        x,y      xy coordinates  
        xc,yc   center of rotation  
        angle   angle  
        units    "DEGREES" (default) or "RADIANS"  
        """  
        import math  
        x = x - xc  
        y = y - yc  
        # make angle clockwise (like Rotate_management)  
        angle = angle * -1  
        if units == "DEGREES":  
            angle = math.radians(angle)  
        xr = (x * math.cos(angle)) - (y * math.sin(angle)) + xc  
        yr = (x * math.sin(angle)) + (y * math.cos(angle)) + yc  
        return xr, yr  
  
    # temp names for cleanup  
    env_file = None  
    lyrFC, lyrTmp, lyrOut   = [None] * 3  # layers  
    tmpFC  = None # temp dataset  
    Row, Rows, oRow, oRows = [None] * 4 # cursors  
    print "STEP-2"
    try:  
        # process parameters  
        try:
            print "STEP-3 Try"
            print pivot_point
            xcen, ycen = [float(xy) for xy in pivot_point.split()]
            print "STEP-3.1 Try"
            pivot_point = xcen, ycen
            print "STEP-4"
        except:  
            # if pivot point was not specified, get it from  
            # the lower-left corner of the feature class  
            ext = arcpy.Describe(inputFC).extent  
            xcen, ycen  = ext.XMin, ext.YMin  
            pivot_point = xcen, ycen  
  
        angle = float(angle)  
        
        # set up environment  
        env_file = arcpy.CreateScratchName("xxenv",".xml","file",  
                                           os.environ["TEMP"])  
        arcpy.SaveSettings(env_file)  
  
        # Disable any GP environment clips or project on the fly  
        arcpy.ClearEnvironment("extent")  
        arcpy.ClearEnvironment("outputCoordinateSystem")  
  
        WKS = env.workspace  
        if not WKS:  
            if os.path.dirname(outputFC):  
                WKS = os.path.dirname(outputFC)  
            else:  
                WKS = os.path.dirname(  
                    arcpy.Describe(inputFC).catalogPath)  
        env.workspace = env.scratchWorkspace = WKS  
  
        # Disable GP environment clips or project on the fly  
        arcpy.ClearEnvironment("extent")  
        arcpy.ClearEnvironment("outputCoordinateSystem")  
  
        # get feature class properties  
        lyrFC = "lyrFC"  
        arcpy.MakeFeatureLayer_management(inputFC, lyrFC)  
        dFC = arcpy.Describe(lyrFC)  
        shpField = dFC.shapeFieldName  
        shpType = dFC.shapeType  
        FID = dFC.OIDFieldName  
  
        # create temp feature class  
        tmpFC = arcpy.CreateScratchName("xxfc","","featureclass")  
        arcpy.CreateFeatureclass_management(os.path.dirname(tmpFC),  
                                            os.path.basename(tmpFC),  
                                            shpType)
        print "created"
        lyrTmp = "lyrTmp"  
        arcpy.MakeFeatureLayer_management(tmpFC, lyrTmp)  
        # set up id field (used to join later)  
        TFID = "XXXX_FID"  
        arcpy.AddField_management(lyrTmp, TFID, "LONG")  
        arcpy.DeleteField_management(lyrTmp, "ID")  
  
        # rotate the feature class coordinates  
        # only points, polylines, and polygons are supported  
  
        # open read and write cursors  
        Rows = arcpy.SearchCursor(lyrFC, "", "",  
                                  "%s;%s" % (shpField,FID))  
        oRows = arcpy.InsertCursor(lyrTmp)  
  
        if shpType  == "Point":  
            for Row in Rows:  
                shp = Row.getValue(shpField)  
                pnt = shp.getPart()  
                pnt.X, pnt.Y = RotateXY(pnt.X,pnt.Y,xcen,ycen,angle)  
                oRow = oRows.newRow()  
                oRow.setValue(shpField, pnt)  
                oRow.setValue(TFID,Row.getValue(FID))  
                oRows.insertRow(oRow)  
        elif shpType in ["Polyline","Polygon"]:  
            parts = arcpy.Array()  
            rings = arcpy.Array()  
            ring = arcpy.Array()  
            for Row in Rows:  
                shp = Row.getValue(shpField)  
                p = 0  
                for part in shp:  
                    for pnt in part:  
                        if pnt:  
                            x, y = RotateXY(pnt.X, pnt.Y, xcen, ycen, angle)  
                            ring.add(arcpy.Point(x, y, pnt.ID))  
                        else:  
                            # if we have a ring, save it  
                            if len(ring) > 0:  
                                rings.add(ring)  
                                ring.removeAll()  
                    # we have our last ring, add it  
                    rings.add(ring)  
                    ring.removeAll()  
                    # if only one, remove nesting  
                    if len(rings) == 1: rings = rings.getObject(0)  
                    parts.add(rings)  
                    rings.removeAll()  
                    p += 1  
  
                # if only one, remove nesting  
                if len(parts) == 1: parts = parts.getObject(0)  
                if dFC.shapeType == "Polyline":  
                    shp = arcpy.Polyline(parts)  
                else:  
                    shp = arcpy.Polygon(parts)  
                parts.removeAll()  
                oRow = oRows.newRow()  
                oRow.setValue(shpField, shp)  
                oRow.setValue(TFID,Row.getValue(FID))  
                oRows.insertRow(oRow)  
        else:  
            raise Exception, "Shape type {0} is not supported".format(shpType)  
  
        del oRow, oRows # close write cursor (ensure buffer written)  
        oRow, oRows = None, None # restore variables for cleanup  
  
        # join attributes, and copy to output  
        arcpy.AddJoin_management(lyrTmp, TFID, lyrFC, FID)  
        env.qualifiedFieldNames = False  
        arcpy.Merge_management(lyrTmp, outputFC)  
        lyrOut = "lyrOut"  
        arcpy.MakeFeatureLayer_management(outputFC, lyrOut)  
        # drop temp fields 2,3 (TFID, FID)  
        fnames = [f.name for f in arcpy.ListFields(lyrOut)]  
        dropList = ";".join(fnames[2:4])  
        arcpy.DeleteField_management(lyrOut, dropList)  
  
    except MsgError, xmsg:
        print str(xmsg)
        arcpy.AddError(str(xmsg))  
    except arcpy.ExecuteError:  
        tbinfo = traceback.format_tb(sys.exc_info()[2])[0]  
        arcpy.AddError(tbinfo.strip())  
        arcpy.AddError(arcpy.GetMessages())  
        numMsg = arcpy.GetMessageCount()  
        for i in range(0, numMsg):  
            arcpy.AddReturnMessage(i)
        print str(numMsg)
    except Exception, xmsg:  
        tbinfo = traceback.format_tb(sys.exc_info()[2])[0]  
        arcpy.AddError(tbinfo + str(xmsg))
        print str(xmsg)
    finally:  
        # reset environment  
        if env_file: arcpy.LoadSettings(env_file)  
        # Clean up temp files  
        for f in [lyrFC, lyrTmp, lyrOut, tmpFC, env_file]:  
            try:  
                if f: arcpy.Delete_management(f)  
            except:  
                pass  
        # delete cursors  
        try:  
            for c in [Row, Rows, oRow, oRows]: del c  
        except:  
            pass  
  
        # return pivot point  
        try:  
            pivot_point = "{0} {1}".format(*pivot_point)  
        except:  
            pivot_point = None  
  
        return pivot_point  
  
inputFC = r'C:\GRID_EXPERIMENT\Parcel_0301014.shp'
outputFC_rotated = r'C:\GRID_EXPERIMENT\rotate_move\Parcel_0301014_rotated_using_code.shp'
outputFC_rotated_then_moved = r'C:\GRID_EXPERIMENT\rotate_move\Parcel_0301014_rotated_then_moved_using_code.shp'
desc = arcpy.Describe(inputFC)
# Create a Describe object from the shapefile
#
desc = arcpy.Describe(inputFC)

# Print dataset properties
#
# print(("Dataset Type: {0}".format(desc.datasetType)))
# print(("Extent:\n  XMin: {0}, XMax: {1}, YMin: {2}, YMax: {3}".format(
#    desc.extent.XMin, desc.extent.XMax, desc.extent.YMin, desc.extent.YMax)))


west = desc.extent.XMin
south = desc.extent.YMin
pivot_point = str(west)+" "+str(south)
print pivot_point
RotateFeatureClass(inputFC, outputFC_rotated,  
                       angle=-0.4835, pivot_point=pivot_point)

arcpy.CopyFeatures_management(outputFC_rotated, outputFC_rotated_then_moved)

"""
	9150226.209	3328801.225	9149675.777	3327960.411	3327960.411		-550.4	-840.8
	9150053.05	3328965.19	9149674.572	3327955.586	3327953.708		-378.5	-1009.6
	9150061.55	3329175.657	9149655.145	3328172.201			        -406.4	-1003.5

"""
shift_features(outputFC_rotated_then_moved, x_shift=-406.4, y_shift=-1003.5)

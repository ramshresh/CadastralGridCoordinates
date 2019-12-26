# Source: https://gis.stackexchange.com/questions/16204/automating-define-projection-within-python-script-tool

import arcpy 
try:
   coordinateSystem ="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
   fc = arcpy.GetParameterAsText(0) #your featureclass file
   dessr = arcpy.Describe(fc)
   srr = dessr.spatialReference
   arcpy.AddMessage("Your previous projection: %s" % (srr))

   arcpy.DefineProjection_management(fc, coordinateSystem)
   arcpy.AddMessage("Your process finished...")
except:
   arcpy.AddMessage("Cant trasformed new projection")

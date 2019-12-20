## Source: https://community.esri.com/thread/18204 

import arcpy  
import time  
  
fc_workspace = "c:/test"  
fc_name = "test.shp"  
fc_fields = (  
 ("a", "TEXT", None, None, 50, "", "NULLABLE", "NON_REQUIRED"),  
 ("b", "LONG", 8, None, None, "", "NULLABLE", "NON_REQUIRED"),  
 ("c", "SHORT", 4, None, None, "", "NULLABLE", "NON_REQUIRED"),  
 ("d", "DOUBLE", 11, 8, None, "", "NULLABLE", "NON_REQUIRED"),  
 ("e", "FLOAT", 5, 2, None, "", "NULLABLE", "NON_REQUIRED"),  
 ("f", "DATE", None, None, None, "", "NULLABLE", "NON_REQUIRED")  
 )  
  
arcpy.env.workspace = fc_workspace  
  
total_start = time.clock()  
  
start = time.clock()  
fc = arcpy.CreateFeatureclass_management(fc_workspace, fc_name, "POINT", spatial_reference="c:/Program Files/ArcGIS/Desktop10.0/Coordinate Systems/Geographic Coordinate Systems/World/WGS 1984.prj")  
end = time.clock()  
arcpy.AddMessage("Create Feature Class %.3f" % (end - start))  
  
start = time.clock()  
for fc_field in fc_fields:  
 arcpy.AddField_management(fc, *fc_field)  
end = time.clock()  
arcpy.AddMessage("Create Fields %.3f" % (end - start))  
  
start = time.clock()  
arcpy.DeleteField_management(fc, "Id")  
end = time.clock()  
arcpy.AddMessage("Delete Id Field %.3f" % (end - start))  
  
total_end = time.clock()  
arcpy.AddMessage("Total %.3f" % (total_end - total_start))  

import os, arcpy
arcpy.env.workspace = r'C:\GRID_EXPERIMENT\SampleSites'
arcpy.env.overwriteOutput = True

sheet_numbers = [
    "0300953", "0300954", "0300955",
    "0300993", "0300994", "0300995",
    "0301033", "0301034", "0301035",

    "0300973", "0300974", "0300975",
    "0301013", "0301014", "0301015",
    "0301053", "0301054", "0301055",

    "0300427", "0300428", "0300429", "0300388", "0300389", "0300469",
    "0300468", "0300467", "0300466", "0300465", "0300505", "0300506", "0300507", "0300508", "0300509",

    "0300196", "0300197", "0300198", "0300236", "0300237", "0300238", "0300277", "0300278", "0300317",
    "0300157", "0300158", "0300159", "0300119", "0300079", "0300080", "0300120", "0300041", "0300040",
    "0300039"
]

in_dir = r'C:\LandUseProject\Rukum_Parcels'
out_dir = r'C:\GRID_EXPERIMENT\SampleSites\original_parcels'
merged_shp = r'C:\GRID_EXPERIMENT\SampleSites\merged_parcels\Parcels_merged_sample_site_81.shp'


def dp_NEPAL_MUTM_CM_81_EVEREST_1830(fc):
    try:
       coordinateSystem = r'PROJCS["NEPAL_MUTM_CM_81_EVEREST_1830",GEOGCS["GCS_Everest_1830",DATUM["D_Everest_1830",SPHEROID["Everest_1830",6377276.345,300.8017]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",81.0],PARAMETER["Scale_Factor",0.9999],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
       #fc = r'C:\GRID_EXPERIMENT\rotate_move\s.shp'
       dessr = arcpy.Describe(fc)
       srr = dessr.spatialReference
       print "Your previous projection: %s" % (srr)

       arcpy.DefineProjection_management(fc, coordinateSystem)
       print "Your process finished..."
    except:
       print "Cant trasformed new projection"


def copy_parcels(dir, sheet_numbers):
    fcs = []
    for s in sheet_numbers:
        name = "Parcel_"+str(s)+".shp"
        fc_in = os.path.join(in_dir,name)
        fc_out = os.path.join(out_dir,name)
        print [fc_out, fc_in]

        if os.path.exists(fc_in):
            arcpy.CopyFeatures_management(fc_in, fc_out)
        else:
            print 'Parcel shapefile with grid number %s not found' %(fc_in)

        if os.path.exists(fc_out):
            dp_NEPAL_MUTM_CM_81_EVEREST_1830(fc_out)
            fcs.append(fc_out)
        else:
            print 'Parcel shapefile with grid number %s not found' %(fc_out)
    return fcs


def merge_parcels(parcels_dir,fc_out):
    arcpy.env.workspace = parcels_dir
    fcs = arcpy.ListFeatureClasses()
    arcpy.Merge_management(fcs, fc_out)
    dp_NEPAL_MUTM_CM_81_EVEREST_1830(fc_out)


copy_parcels(in_dir, sheet_numbers)
merge_parcels(out_dir,merged_shp)
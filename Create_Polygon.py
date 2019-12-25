import time

total_start = time.clock()
import numpy as np
import os, arcpy

arcpy.env.workspace = r"C:\LandUseProject\CadastralGridCalculator\output"
arcpy.env.overwriteOutput = True


def get_four_corners(sheetno, proj_cm):
    C6 = str(sheetno)  # "0670101"

    # print "C6 = "+C6
    # IF3 = IF(AND((LEFT(C6,3))/1<181,(LEFT(C6,3)/1>0)),LEFT(C6,3),"Error")
    # (LEFT(C6,3) ~ C6[:3]
    if (int(C6[:3]) < 181 and int(C6[:3]) > 0):
        IF3 = str(C6[:3])
    else:
        IF3 = None
    ##print "IF3 = "+str(IF3)

    """
    IG3 =IF(AND(
                LEN(C6)>6,
                (RIGHT((LEFT(C6,7)),4)/1<1601),
                (RIGHT((LEFT(C6,7)),4)/1>0)
                ),
            (RIGHT((LEFT(C6,7)),4)/1),
            "ERROR"
            )
    """
    # RIGHT((LEFT(C6,7)),4) ~ C6[:7][-4:]
    if len(C6) > 6 and int(C6[:7][-4:]) < 1601 and int(C6[:7][-4:]) > 0:
        IG3 = str(C6[:7][-4:])
    else:
        IG3 = None
    ##print "IG3 = "+str(IG3)

    """
    IH3 = =IF(LEN(C6)<8,
                0,
                IF((LEN(C6)=8),
                    RIGHT(C6,1),
                    RIGHT(C6,2)
                    )
                )
    """
    if len(C6) < 8:
        IH3 = str(0)
    else:
        if len(C6) == 8:
            IH3 = str(C6[-1:])
        else:
            IH3 = str(C6[-2:])

    ##print "IH3 = "+str(IH3)

    """
    IH5 = IF(AND(
                LEN(IH3)=1,
                (IH3)/1<5,
                (IH3)/1>0
                ),
                IH3/1,
                IF(AND(
                    LEN(IH3)=1,
                    (IH3)/1>4
                    ),
                    "ERROR",
                    0)
                )
    """
    IF5 = int(IF3) if int(IF3) >= 1 and int(IF3) <= 180 else None
    IG5 = int(IG3) if int(IG3) >= 1 and int(IG3) <= 1600 else None

    if len(IH3) == 1 and int(IH3) <= 4 and int(IH3) >= 1:
        IH5 = int(IH3)
    else:
        if len(IH3) == 1 and int(IH3) > 4:
            IH5 = None
        else:
            IH5 = 0
    ##print [IF5, IG5, IH5]
    """
    II5=IF(AND(LEN(IH3)=2,(IH3)/1<26,(IH3)/1>0),IH3/1,IF(AND(LEN(IH3)=2,(IH3)/1>25),"ERROR",0))
    """
    if len(IH3) == 2 and int(IH3) <= 25 and int(IH3) >= 1:
        II5 = int(IH3)
    else:
        if len(IH3) == 2 and int(IH3) > 25:
            II5 = None
        else:
            II5 = 0

    ##print [IF5, IG5, IH5, II5]

    def get_constants(cm):
        if cm == 81:
            return [[600000, 300000], [900000, 600000], [1200000, 900000]]

        if cm == 84:
            return [[300000, 0], [600000, 300000], [900000, 600000]]

        if cm == 87:
            return [[0, -300000], [300000, 0], [600000, 300000]]

    cnst = get_constants(proj_cm);

    if IF5 > 0 and IF5 < 61:
        if ((float(IF5) / float(6) % 1)) == 0:
            IL5 = cnst[0][0]
        else:
            IL5 = round(((float(IF5) / float(6) % 1)) * 300000 + cnst[0][1], 4)
    elif IF5 > 60 and IF5 < 121:
        if (float(IF5) / float(6) % 1) == 0:
            print (IF5 / 6) % 1
            print float(IF5) / float(6)
            IL5 = cnst[1][0]
        else:
            IL5 = round(((float(IF5) / float(6) % 1)) * 300000 + cnst[1][1], 4)
    elif IF5 > 120 and IF5 < 181:
        if ((float(IF5) / float(6) % 1) * 300000) == 0:
            IL5 = cnst[2][0]
        else:
            IL5 = round(((float(IF5) / float(6) % 1)) * 300000 + cnst[2][1], 4)

    """
    IM5 = =IF(IF5>120,IF5-120,IF5)
    """
    if IF5 > 120:
        IM5 = IF5 - 120
    else:
        IM5 = IF5

    """
    IN5 = IF(IM5>60,IM5-60,IM5)
    """
    if IM5 > 60:
        IN5 = IM5 - 60
    else:
        IN5 = IM5
    """
    IO5 = QUOTIENT(IN5,6.00001)
    """
    IO5 = IN5 // 6.00001

    """
    IP5 = IF(IG5=0,
             0,
             IF((MOD((IG5/40),1)=0),
                50000-1250,
                ((MOD((IG5/40),1))*50000)-1250)
             )

    """

    if IG5 == 0:
        IP5 = 0
    else:
        if ((float(IG5) / 40) % 1) == 0:
            IP5 = 50000 - 1250
        else:
            IP5 = ((float(IG5) / 40) % 1) * 50000 - 1250

    """
    IQ5 = =IF(IH5="ERROR",
              "ERROR",
              IF(AND(IH5>0,IH5<5),
                 (
                     IF((MOD((IH5/2),1)=0),
                        1250-625,
                        ((MOD((IH5/2),1))*1250)-625)
                     ),
                 0
                 )
              )
    """

    if IH5 is None:
        IQ5 = None
    else:
        if IH5 > 0 and IH5 < 5:
            if ((float(IH5 / 2)) % 1) == 0:
                IQ5 = 1250 - 625
            else:
                IQ5 = ((float(IH5) / 2) % 1) * 1250 - 625
        else:
            IQ5 = 0
    """
    IR5 = IF((LEN(IH3)=2),
             (IF((MOD((II5/5),1)=0),
                 1250-250,
                 ((MOD((II5/5),1))*1250)-250)
              ),
             0
             )
    """
    if len(IH3) == 2:
        if (float(II5) / 5) % 1 == 0:
            IR5 = 1250 - 250
        else:
            IR5 = (((float(II5) / 5)) % 1) * 1250 - 250
    else:
        IR5 = 0

    ##print [IL5, IM5, IN5, IO5, IP5, IQ5, IR5]

    """
    IS5 = =IF(IF5=0,0,3400000-50000-(IO5*50000))
    """
    if IF5 == 0:
        IS5 = 0
    else:
        IS5 = 3400000 - 50000 - (IO5 * 50000)
    """
    IT5 = =IF(IG5=0,0,50000-1250-((QUOTIENT(IG5,40.00000000001))*1250))
    """
    if IG5 == 0:
        IT5 = 0
    else:
        IT5 = 50000 - 1250 - ((float(IG5) // 40.00000000001) * 1250)
    """
    IU5 = =IF(AND(IH5>0,IH5<5),(625-((QUOTIENT(IH5,2.000000001))*625)),0)
    """
    if IH5 > 0 and IH5 < 5:
        IU5 = (625 - ((float(IH5) // 2.000000001) * 625))
    else:
        IU5 = 0
    """    
    IV5 = IF((LEN(IH3)=2),(1250-250-((QUOTIENT(II5,5.0000001))*250)),0)
    """
    if len(IH3) == 2:
        IV5 = (1250 - 250 - ((float(II5) // 5.0000001) * 250))
    else:
        IV5 = 0
    ##print [IS5, IT5, IU5, IV5]

    IV1 = 2500

    Left_Top_E = round(IL5 + IP5 + IQ5 + IR5,4)
    Left_Bottom_E = Left_Top_E
    Right_Bottom_E = Left_Top_E + round((IV1 / 2),4)
    Right_Top_E = Left_Bottom_E + round((IV1 / 2),4)

    Left_Bottom_N = IS5 + IT5 + IU5 + IV5
    Left_Top_N = Left_Bottom_N + round((float(IV1) / 2),4)
    Right_Bottom_N = Left_Bottom_N
    Right_Top_N = Right_Bottom_N + round((IV1 / 2),4)

    Left_Top_XY = [Left_Top_E, Left_Top_N]
    Left_Bottom_XY = [Left_Bottom_E, Left_Bottom_N]
    Right_Bottom_XY = [Right_Bottom_E, Right_Bottom_N]
    Right_Top_XY = [Right_Top_E, Right_Top_N]

    ##print Left_Top_XY
    ##print Left_Bottom_XY
    ##print Right_Bottom_XY
    ##print Right_Top_XY

    return [Left_Top_XY, Left_Bottom_XY, Right_Bottom_XY, Right_Top_XY]


# print get_four_corners('0030104')


# https://community.esri.com/thread/18204
# Create a feature class with a spatial reference of GCS WGS 1984


"""
result = arcpy.management.CreateFeatureclass(
    arcpy.env.scratchGDB, 
    "esri_square", "POLYGON", spatial_reference=4326)
"""
start = time.clock()
fc = arcpy.CreateFeatureclass_management(
    r"C:\LandUseProject\CadastralGridCalculator\output",
    r"grid_Rukum_W_cm81.shp", "POLYGON",
)
end = time.clock()
arcpy.AddMessage("Create Feature Class %.3f" % (end - start))

start = time.clock()
arcpy.AddField_management(in_table=fc, field_name="GRID_NO", field_type="TEXT")
end = time.clock()
arcpy.AddMessage("Create Fields %.3f" % (end - start))

start = time.clock()
arcpy.DeleteField_management(fc, "Id")
end = time.clock()
arcpy.AddMessage("Delete Id Field %.3f" % (end - start))

# majorGrids = ['102']
majorGrids = ['024', '030', '079', '085']
# majorGrids = range(1,181)
# majorGrids = ['001', '002', '003', '004', '005', '006', '061', '062','063', '064','065', '066', '121', '122','123', '124','125', '126']
# majorGrids = ['030']
"""
majorGrids = ['001','002', '003', '004', '005', '006',
              '061', '062', '063', '064', '065', '066',
              '121', '122', '123', '124', '125', '126'
              ]
"""

for mg in majorGrids:
    # for g2500 in ['0001']:
    for g2500 in range(1, 1601):
        sheetnumber = str(mg).rjust(3, '0') + str(g2500).rjust(4, '0')
        print sheetnumber
        # print str(mg)+ str(g2500).rjust(4, '0')
        coordinates = get_four_corners(sheetnumber, 81)
        print coordinates
        start = time.clock()
        # Write feature to new feature class
        with arcpy.da.InsertCursor(fc, ['SHAPE@', 'GRID_NO']) as cursor:
            cursor.insertRow([coordinates, sheetnumber])
        end = time.clock()
        print "Added feature sheet no : %s in %.3f" % (sheetnumber, end - start)
total_end = time.clock()
print "Total %.3f Seconds elapsed" % (total_end - total_start)






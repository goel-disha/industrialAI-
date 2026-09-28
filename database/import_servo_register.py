import sqlite3

conn = sqlite3.connect("database/project.db")
cursor = conn.cursor()

servo_devices = [

# =====================================================
# X INPUTS
# =====================================================

("X1","X",None,"X1","Servo Input","BOOL","0",1),
("X8","X",None,"X8","Servo Input","BOOL","0",1),
("X9","X",None,"X9","Servo Input","BOOL","0",1),
("X0A","X",None,"X0A","Servo Input","BOOL","0",1),
("X23","X",None,"X23","Servo Input","BOOL","0",1),
("X26","X",None,"X26","Servo Input","BOOL","0",1),
("X27","X",None,"X27","Servo Input","BOOL","0",1),
("X28","X",None,"X28","Servo Input","BOOL","0",1),
("X29","X",None,"X29","Servo Input","BOOL","0",1),
("X2A","X",None,"X2A","Servo Input","BOOL","0",1),
("X2B","X",None,"X2B","Servo Input","BOOL","0",1),
("X2C","X",None,"X2C","Servo Input","BOOL","0",1),
("X2D","X",None,"X2D","Servo Input","BOOL","0",1),
("X2E","X",None,"X2E","Servo Input","BOOL","0",1),

# =====================================================
# Y OUTPUTS
# =====================================================

("Y0","Y",None,"Y0","Servo Output","BOOL","0",1),
("Y1","Y",None,"Y1","Servo Output","BOOL","0",1),
("Y4D","Y",None,"Y4D","Servo Output","BOOL","0",1),

# =====================================================
# M INTERNAL RELAYS
# =====================================================

("M90","M",None,"M90","Internal Relay","BOOL","0",1),
("M100","M",None,"M100","Internal Relay","BOOL","0",1),
("M126","M",None,"M126","Internal Relay","BOOL","0",1),
("M127","M",None,"M127","Internal Relay","BOOL","0",1),
("M128","M",None,"M128","Internal Relay","BOOL","0",1),
("M129","M",None,"M129","Internal Relay","BOOL","0",1),
("M130","M",None,"M130","Internal Relay","BOOL","0",1),
("M131","M",None,"M131","Internal Relay","BOOL","0",1),
("M253","M",None,"M253","Internal Relay","BOOL","0",1),
("M255","M",None,"M255","Internal Relay","BOOL","0",1),
("M257","M",None,"M257","Internal Relay","BOOL","0",1),
("M500","M",None,"M500","Internal Relay","BOOL","0",1),
("M1501","M",1,"M1501","Servo Axis 1","BOOL","0",1),
("M1502","M",2,"M1502","Servo Axis 2","BOOL","0",1),
("M1503","M",3,"M1503","Servo Axis 3","BOOL","0",1),
("M1601","M",1,"M1601","Servo Axis 1","BOOL","0",1),
("M1602","M",2,"M1602","Servo Axis 2","BOOL","0",1),
("M1603","M",3,"M1603","Servo Axis 3","BOOL","0",1),

# =====================================================
# TIMER
# =====================================================

("T552","T",None,"T552","Servo Timer","TIMER","0",1),

# =====================================================
# SPECIAL RELAY
# =====================================================

("SM400","SM",None,"SM400","Always ON","BOOL","1",1),

]

# =====================================================
# L RELAYS
# =====================================================

servo_devices.extend([

("L501","L",None,"L501","AUTO_CYCLE START BIT","BOOL","0",1),
("L502","L",1,"L502","AUTO SERVO-1 RUN BIT","BOOL","0",1),
("L504","L",2,"L504","AUTO SERVO-2 RUN BIT","BOOL","0",1),
("L506","L",3,"L506","AUTO SERVO-3 RUN BIT","BOOL","0",1),

("L516","L",1,"L516","SERVO-1 COMPLETE","BOOL","0",1),
("L518","L",2,"L518","SERVO-2 COMPLETE","BOOL","0",1),

("L540","L",None,"L540","AUTO CYCLE STOP","BOOL","0",1),
("L541","L",None,"L541","AUTO RESET","BOOL","0",1),

("L610","L",1,"L610","AXIS-1 POSITION COMPLETE","BOOL","0",1),
("L611","L",2,"L611","AXIS-2 POSITION COMPLETE","BOOL","0",1),
("L612","L",3,"L612","AXIS-3 POSITION COMPLETE","BOOL","0",1),

("L700","L",1,"L700","AXIS-1 READY","BOOL","0",1),
("L701","L",2,"L701","AXIS-2 READY","BOOL","0",1),
("L702","L",3,"L702","AXIS-3 READY","BOOL","0",1),

("L704","L",None,"L704","SERVO ORIGIN COMPLETE","BOOL","0",1),
("L706","L",None,"L706","AUTO MODE ENABLE","BOOL","0",1),
("L708","L",None,"L708","MANUAL MODE ENABLE","BOOL","0",1),

("L710","L",None,"L710","SERVO READY","BOOL","0",1),
("L712","L",None,"L712","SERVO BUSY","BOOL","0",1),
("L714","L",None,"L714","SERVO ERROR","BOOL","0",1),
("L716","L",None,"L716","WAIT POSITION","BOOL","0",1),
("L718","L",None,"L718","POSITION REACHED","BOOL","0",1),
("L720","L",None,"L720","HOME POSITION","BOOL","0",1),
("L722","L",None,"L722","MACHINE READY","BOOL","0",1),

# ==========================
# MODEL SELECTION
# ==========================

("L800","L",None,"L800","UL2 MODEL SELECT","BOOL","0",1),
("L802","L",None,"L802","WN MODEL SELECT","BOOL","0",1),
("L804","L",None,"L804","WC MODEL SELECT","BOOL","0",1),
("L806","L",None,"L806","U24A MODEL SELECT","BOOL","0",1),

("L808","L",None,"L808","MODEL-5 SELECT","BOOL","0",1),
("L810","L",None,"L810","MODEL-6 SELECT","BOOL","0",1),
("L812","L",None,"L812","MODEL-7 SELECT","BOOL","0",1),
("L814","L",None,"L814","MODEL-8 SELECT","BOOL","0",1),
("L816","L",None,"L816","MODEL-9 SELECT","BOOL","0",1),
("L818","L",None,"L818","MODEL-10 SELECT","BOOL","0",1),
("L820","L",None,"L820","MODEL-11 SELECT","BOOL","0",1),
("L822","L",None,"L822","MODEL-12 SELECT","BOOL","0",1),

# ==========================
# SEQUENCE BITS
# ==========================

("L1020","L",None,"L1020","SERVO SEQUENCE START","BOOL","0",1),
("L1032","L",None,"L1032","POSITION CHECK","BOOL","0",1),
("L1035","L",1,"L1035","AXIS-1 POSITIONING","BOOL","0",1),
("L1036","L",2,"L1036","AXIS-2 POSITIONING","BOOL","0",1),
("L1037","L",3,"L1037","AXIS-3 POSITIONING","BOOL","0",1)

])

# =====================================================
# D REGISTERS
# =====================================================

def add_d(start, end, axis, name, description):

    for d in range(start, end + 1):

        servo_devices.append(
            (
                f"D{d}",
                "D",
                axis,
                name,
                description,
                "INT",
                "0",
                1
            )
        )


add_d(300,307,1,"SERVO1_PD","UL2 SERVO PD")
add_d(310,317,1,"SERVO1_PD","WN MODEL SERVO PD")
add_d(320,327,1,"SERVO1_PD","WC MODEL SERVO PD")
add_d(330,337,1,"SERVO1_PD","U24A MODEL SERVO PD")
add_d(340,347,1,"SERVO1_PD","MODEL5 SERVO PD")
add_d(350,357,1,"SERVO1_PD","MODEL6 SERVO PD")
add_d(360,367,1,"SERVO1_PD","MODEL7 SERVO PD")
add_d(370,377,1,"SERVO1_PD","MODEL8 SERVO PD")
add_d(380,387,1,"SERVO1_PD","MODEL9 SERVO PD")
add_d(390,397,1,"SERVO1_PD","MODEL10 SERVO PD")
add_d(400,407,1,"SERVO1_PD","MODEL11 SERVO PD")
add_d(410,417,1,"SERVO1_PD","MODEL12 SERVO PD")

add_d(500,507,2,"SERVO2_PD","UL2 SERVO2 PD")
add_d(510,517,2,"SERVO2_PD","WN SERVO2 PD")
add_d(520,527,2,"SERVO2_PD","WC SERVO2 PD")
add_d(530,537,2,"SERVO2_PD","U24A SERVO2 PD")
add_d(540,547,2,"SERVO2_PD","MODEL5 SERVO2 PD")
add_d(550,557,2,"SERVO2_PD","MODEL6 SERVO2 PD")
add_d(560,567,2,"SERVO2_PD","MODEL7 SERVO2 PD")
add_d(570,577,2,"SERVO2_PD","MODEL8 SERVO2 PD")
add_d(580,587,2,"SERVO2_PD","MODEL9 SERVO2 PD")
add_d(590,597,2,"SERVO2_PD","MODEL10 SERVO2 PD")
add_d(600,607,2,"SERVO2_PD","MODEL11 SERVO2 PD")
add_d(610,617,2,"SERVO2_PD","MODEL12 SERVO2 PD")

add_d(700,707,3,"SERVO3_PD","UL2 SERVO3 PD")
add_d(710,717,3,"SERVO3_PD","WN SERVO3 PD")
add_d(720,727,3,"SERVO3_PD","WC SERVO3 PD")
add_d(730,737,3,"SERVO3_PD","U24A SERVO3 PD")
add_d(740,747,3,"SERVO3_PD","MODEL5 SERVO3 PD")
add_d(750,757,3,"SERVO3_PD","MODEL6 SERVO3 PD")
add_d(760,767,3,"SERVO3_PD","MODEL7 SERVO3 PD")
add_d(770,777,3,"SERVO3_PD","MODEL8 SERVO3 PD")
add_d(780,787,3,"SERVO3_PD","MODEL9 SERVO3 PD")
add_d(790,797,3,"SERVO3_PD","MODEL10 SERVO3 PD")
add_d(800,807,3,"SERVO3_PD","MODEL11 SERVO3 PD")
add_d(810,817,3,"SERVO3_PD","MODEL12 SERVO3 PD")

add_d(900,901,1,"SERVO1_SPEED","SERVO1 SPEED DATA")
add_d(910,911,2,"SERVO2_SPEED","SERVO2 SPEED DATA")
add_d(920,921,3,"SERVO3_SPEED","SERVO3 SPEED DATA")

servo_devices.extend([

("D940","D",1,"AXIS1_ERROR","AXIS 1 ERROR NUMBER","WORD","0",1),
("D942","D",2,"AXIS2_ERROR","AXIS 2 ERROR NUMBER","WORD","0",1),
("D944","D",3,"AXIS3_ERROR","AXIS 3 ERROR NUMBER","WORD","0",1),

])

add_d(1000,1003,1,"SERVO1_POSITION","SERVO1 POSITION DATA")
add_d(1010,1013,1,"SERVO1_POSITION","SERVO1 POSITION DATA")

add_d(1020,1023,2,"SERVO2_POSITION","SERVO2 POSITION DATA")
add_d(1030,1033,2,"SERVO2_POSITION","SERVO2 POSITION DATA")

add_d(1040,1043,3,"SERVO3_POSITION","SERVO3 POSITION DATA")
add_d(1050,1053,3,"SERVO3_POSITION","SERVO3 POSITION DATA")

add_d(1100,1103,1,"CURRENT_POSITION","CURRENT VALUE OF AXIS1")
add_d(1110,1113,2,"CURRENT_POSITION","CURRENT VALUE OF AXIS2")
add_d(1120,1123,3,"CURRENT_POSITION","CURRENT VALUE OF AXIS3")

# =====================================================
# MOTION CPU REGISTERS (U0/G)
# =====================================================

def add_motion(start, end, axis, name, description):

    for g in range(start, end + 1):

        servo_devices.append(
            (
                f"U0/G{g}",
                "U0/G",
                axis,
                name,
                description,
                "DWORD",
                "0",
                1
            )
        )

add_motion(800,805,1,"CURRENT_FEED","Axis1 Current Feed Value")
add_motion(806,811,1,"ERROR_NO","Axis1 Error Number")

add_motion(900,905,2,"CURRENT_FEED","Axis2 Current Feed Value")
add_motion(906,911,2,"ERROR_NO","Axis2 Error Number")

add_motion(1500,1517,1,"POSITION_START","Axis1 Position Start Number")
add_motion(1600,1617,2,"POSITION_START","Axis2 Position Start Number")
add_motion(1700,1717,3,"POSITION_START","Axis3 Position Start Number")

add_motion(1928,1935,None,"EXTERNAL_INPUT","External Input Signal")

add_motion(2004,2007,1,"COMMAND_SPEED","Axis1 Command Speed")
add_motion(8004,8007,2,"COMMAND_SPEED","Axis2 Command Speed")
add_motion(14004,14007,3,"COMMAND_SPEED","Axis3 Command Speed")

servo_devices.extend([

("U0/G1518","U0/G",1,"SERVO_STATUS","Axis1 Servo Status","WORD","0",1),
("U0/G1618","U0/G",2,"SERVO_STATUS","Axis2 Servo Status","WORD","0",1),
("U0/G1718","U0/G",3,"SERVO_STATUS","Axis3 Servo Status","WORD","0",1),

])

cursor.executemany("""

INSERT OR IGNORE INTO servo_devices(

address,
device_type,
axis,
symbol,
description,
datatype,
current_value,
simulated

)

VALUES(?,?,?,?,?,?,?,?)

""", servo_devices)

conn.commit()

print(f"{len(servo_devices)} Servo Devices Imported Successfully")

conn.close()
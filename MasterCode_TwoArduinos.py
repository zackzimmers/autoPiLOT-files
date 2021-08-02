import thread
import threading
import time
import serial
from scipy.signal import savgol_filter
import numpy
import Queue
from itertools import count
from datetime import datetime
import csv

from configparser import SafeConfigParser

# Define a function for the thread

def qrd1114_reader(threadName, boxsize):
    print "%s: %s" % (threadName, time.ctime(time.time()))
    start_time = time.time()
    qrd1114_raw = []
    qrd1114_avged = []

    # activate serial transmission of sensor data from arduino
    ser2.write(b"A\n")
    time.sleep(.1)

    while True:

        if qrd_in != "Sensor Ready":
            qrd1114_raw.append(int(qrd_in))

            if len(qrd1114_raw) >= (3):
                avg = (int(qrd_in) + int(qrd1114_raw[-1]) + int(qrd1114_raw[-2])) / 3
                qrd1114_avged.append(avg)
                
                if len(qrd1114_avged) > 109:
                    arr = numpy.array(qrd1114_avged)
                    arr_filt1 = savgol_filter(arr, 101, 8)
                    arr_filt2 = savgol_filter(arr_filt1, 109, 3)
                    # print(arr_filt2[-1])

                    if time.time() > (start_time + 1) and arr_filt2[-1] > 19:
                        sense1_air.set()
                        time.sleep(.1)
                    
                    elif arr_filt2[-1] < 19:
                        sense1_water.set()
                        time.sleep(.1)
                        

def recon_pass(threadName):

    parser = SafeConfigParser()
    parser.read('zz_config.ini')


    print "%s: %s" % (threadName, time.ctime(time.time()))
    baseline_time = time.time()

    ser.write('<hey,-10000,100>')
    time.sleep(2)
    sense1_water.clear()
    sense1_water.wait()
    water1_time = time.time()
    print "%s: %s" % ("Water1", time.ctime(time.time()))
    time.sleep(2)
    sense1_air.clear()
    sense1_air.wait()
    air1_time = time.time()
    print "%s: %s" % ("Air1", time.ctime(time.time()))

    time.sleep(1)
    sense1_water.clear()
    sense1_water.wait()
    water2_time = time.time()
    print "%s: %s" % ("Water2", time.ctime(time.time()))
    time.sleep(2)
    sense1_air.clear()
    sense1_air.wait()
    air2_time = time.time()
    print "%s: %s" % ("Air2", time.ctime(time.time()))

    time.sleep(1)
    sense1_water.clear()
    sense1_water.wait()
    water3_time = time.time()
    print "%s: %s" % ("Water3", time.ctime(time.time()))
    time.sleep(1)
    sense1_air.clear()
    sense1_air.wait()
    air3_time = time.time()
    print "%s: %s" % ("Air3", time.ctime(time.time()))

    time.sleep(1)
    sense1_water.clear()
    sense1_water.wait()
    water4_time = time.time()
    print "%s: %s" % ("Water4", time.ctime(time.time()))
    time.sleep(2)
    sense1_air.clear()
    sense1_air.wait()
    air4_time = time.time()
    print "%s: %s" % ("Air4 End of Tube, Beginning Cycling", time.ctime(time.time()))


    time.sleep(3)  # for magnet to reach end of chamber
    ser.write('<hey,-10000,0>') #stop the motor
    
    # initialize variables from config file
    cycle = 0
    slow_speed = parser.get('params', 'slow_speed')
    slow_speed = int(slow_speed)
    shake_speed = parser.get('params', 'shake_speed')
    shake_speed = int(shake_speed)
    fluor_speed = parser.get('params', 'fluor_speed')
    fluor_speed = int(fluor_speed)
    cyclemax = parser.get('params', 'num_cycles')
    cyclemax = int(cyclemax)
    
    # calculate all locations in stepper motor steps
    # all times recorded at 100 steps/s speed of stepper motor   
    water1_spot = int(-100 * (water1_time - baseline_time)) - 200
    water2_spot = int(-100 * (water2_time - baseline_time)) - 200
    water3_spot = int(-100 * (water3_time - baseline_time)) - 200
    water4_spot = int(-100 * (water4_time - baseline_time)) - 200

    air1_spot = int(-100 * (air1_time - baseline_time)) - 125
    air2_spot = int(-100 * (air2_time - baseline_time)) - 125
    air3_spot = int(-100 * (air3_time - baseline_time)) - 125
    air4_spot = int(-100 * (air4_time - baseline_time)) - 125
    
    # begin movement to first db chamber
    ser.write('<air3,%s,%s>' % (air3_spot, str(slow_speed)))
    time.sleep((abs(air4_spot - air3_spot)/slow_speed) + 5)
    
    while cycle <= cyclemax:
        
        print("This is cycle number %s" % (cycle))
        
        # mix and incubate
        ser.write('<air3-800,%s,%s>' % (air3_spot - 800, str(shake_speed)))
        time.sleep(800/shake_speed)
        ser.write('<air3+800,%s,%s>' % (air3_spot + 800, str(shake_speed)))
        time.sleep(1600/shake_speed)
        ser.write('<air3-1250,%s,%s>' % (air3_spot - 1250, str(shake_speed)))
        time.sleep(1800)
        
        # recollect beads
        ser.write('<air3,%s,%s>' % (air3_spot, str(shake_speed)))
        time.sleep(3)

        # go to wash chamber
        ser.write('<water2-200,%s,%s>' % (water2_spot - 200, str(slow_speed)))
        time.sleep((abs((air3_spot) - (water2_spot-200))/slow_speed))
        
        # mixy mixy
        ser.write('<water2+500,%s,%s>' % (water2_spot + 500, str(shake_speed)))
        time.sleep(600/shake_speed)
        ser.write('<water2-900,%s,%s>' % (water2_spot - 900, str(shake_speed)))
        time.sleep(1600/shake_speed)
        ser.write('<water2+500,%s,%s>' % (water2_spot + 500, str(shake_speed)))
        time.sleep(1500/shake_speed)
        
        # aim Qiagen at edge of dbDNA 1
        ser.write('<water3-1700,%s,%s>' % (water3_spot - 1700, str(shake_speed)))
        time.sleep(3)
        
        # read the fluorescence
        print('Fluorescence read')

        # cross wash chamber across Qiagen sight
        ser.write('<air1-1600,%s,%s>' % (air1_spot - 1600, str(fluor_speed)))
        time.sleep((abs((water3_spot-1700) - (air1_spot-1600))/fluor_speed) + 1)

        # recollect beads
        ser.write('<air2-100,%s,%s>' % (air2_spot-100, str(shake_speed)))
        time.sleep(2)
        
        # bring beads to dbDNA 2
        ser.write('<air1,%s,%s>' % (air1_spot, str(slow_speed)))
        time.sleep((abs((air1_spot) - (air2_spot-100))/slow_speed))
        
        # mix and incubate
        ser.write('<air1-800,%s,%s>' % (air1_spot - 800, str(shake_speed)))
        time.sleep(800/shake_speed)
        ser.write('<air1+800,%s,%s>' % (air1_spot + 800, str(shake_speed)))
        time.sleep(1600/shake_speed)
        ser.write('<water3-1700,%s,%s>' % (water3_spot - 1700, str(shake_speed)))
        time.sleep(1800)
        
        # recollect beads
        ser.write('<water1-300,%s,%s>' % (water1_spot - 300, str(shake_speed)))
        time.sleep(3)
        
        # go back to dbDNA 1
        ser.write('<air3-200,%s,%s>' % (air3_spot - 200, str(slow_speed)))
        time.sleep((abs((air3_spot-200) - (water1_spot-200))/slow_speed) + 3)

        print('Cycle Completed')
        print(('--------------'))
        
        cycle = cycle + 1



if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)  # connection to stepper motor controlling arduino
    ser2 = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # connection to sensor reading arduino
    ser.flush()
    ser2.flush()

    sense1_air = threading.Event()
    sense1_water = threading.Event()
    
    sense_on = threading.Event()
    fluor_read_go = threading.Event()
    start_Qiagen = threading.Event()

    q1 = Queue.Queue()

    while True:
        if ser2.in_waiting > 0:
            # line = ser.readline().decode('utf-8').rstrip()
            qrd_in = ser2.readline().decode('ISO-8859-1').rstrip()

            if qrd_in == "Home Marked, Awaiting Serial Command":
                print(qrd_in)
                # Create new threads as follows
                try:
                    #sense_on.set()
                    thread.start_new_thread(qrd1114_reader, ("QRD Reader Thread", 4,))
                    thread.start_new_thread(recon_pass, ("Reconnaissance Pass",))
                    break
                except:
                    print "Error: unable to start either Reader or Recon Pass thread"

    print('Threads Successfully Started')

    # temporary to skip to this step
    # cycling_complete.set()

    while True:
        if ser2.in_waiting > 0:
            qrd_in = ser2.readline().decode('utf-8').rstrip()
            # print(qrd_in)
            
        # if ser.in_waiting > 0:
            # qrd_in = ser.readline().decode('utf-8').rstrip()
            # print(qrd_in)
'''!
@file main.py
    This file contains a modified version of JR Ridgely's
    basic_task.py (https://github.com/spluttflob/ME405-Support)
    that creates tasks for running two seperate motors step responses at
    the same time
@author Lucas Sandsor
@author Jack Barone
@author Jack Meyers
@date 1-Feb-2022
'''

import gc
import pyb
import cotask
import task_share
import motorDriver
import encoderDriver
import controls
import utime


def task1_encoder ():
    """!
    This task creates a driver for one of the encoders being used.
    It puts the curent value of the encoder into a share to be used by other tasks
    """
    enc = encoderDriver.EncoderDriver(pyb.Pin.board.PB6,pyb.Pin.board.PB7, 4)
    while True:
        enc.update()
        share_enc1.put(enc.read())
        yield (0)
        
def task2_motor ():
    """!
    This task creates a driver for one of the motors being used.
    It puts the current duty cycle of the motor into a share to be used by other tasks
    """
    moe = motorDriver.MotorDriver(pyb.Pin.board.PA10,
        pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    while True:
        moe.set_duty_cycle(share_motor1.get())
        yield(0)
        
def task3_control ():
    """!
    This task creates a controller for using the shared encoder
    value and uses it to adjust the speed of a motor to get to a desired position
    given by the user. It also stores the time and ticks of an encoder for outside
    analysis
    """
    start_time = utime.ticks_ms();
    controller = controls.Controls(8192, 2000/8192, 0)
    while True:
        share_motor1.put(controller.controlLoop(share_enc1.get()))
        # Next 4 lines of code are used for storing encoder values for anaylsis
        if(share_enc1.get()!= 0):
            print(utime.ticks_diff(utime.ticks_ms(), start_time), end=",")
            print(share_enc1.get())
        if(utime.ticks_diff(utime.ticks_ms(), start_time) > 15000):
            print(b'EOF')
        yield(0)
        
def task4_encoder ():
    """!
    This task creates a driver for one of the encoders being used.
    It puts the curent value of the encoder into a share to be used by other tasks
    """
    enc = encoderDriver.EncoderDriver(pyb.Pin.board.PC6,pyb.Pin.board.PC7, 8)
    while True:
        enc.update()
        share_enc2.put(enc.read())
        yield (0)
        
def task5_motor ():
    """!
    This task creates a driver for one of the motors being used.
    It puts the current duty cycle of the motor into a share to be used by other tasks
    """
    moe = motorDriver.MotorDriver(pyb.Pin.board.PC1,
        pyb.Pin.board.PA0, pyb.Pin.board.A1, 5)
    while True:
        moe.set_duty_cycle(share_motor2.get())
        yield(0)
        
def task6_control ():
    """!
    This task creates a controller for using the shared encoder
    value and uses it to adjust the speed of a motor to get to a desired position
    given by the user. It also stores the time and ticks of an encoder for outside
    analysis
    """
    controller = controls.Controls(8192, 2000/8192, 0)
    while True:
        share_motor2.put(controller.controlLoop(share_enc2.get()))
        yield(0)

"""! This main code creates multiple shares for the two motor duty cycles and encoder ticks.
     It then adds the tasks to cotask to be ran. The tasks run until somebody presses ENTER, at
     which time the scheduler stops and printouts show diagnostic information about the
     tasks and shares"""
if __name__ == "__main__":
    
    # Creates four shares for properly running the two motor step responses
    share_enc1 = task_share.Share ('i', thread_protect = False, name = "Share Encoder")
    share_motor1 = task_share.Share ('f', thread_protect = False, name = "Share Motor")
    share_enc2 = task_share.Share ('i', thread_protect = False, name = "Share Encoder")
    share_motor2 = task_share.Share ('f', thread_protect = False, name = "Share Motor")
    

    # Create the tasks with appropriate priorities and names
    task1 = cotask.Task (task1_encoder, name = 'Encoder1', priority = 2, 
                         period = 10, profile = True, trace = False)
    task2 = cotask.Task (task2_motor, name = 'Motor1', priority = 1, 
                         period = 1, profile = True, trace = False)
    task3 = cotask.Task (task3_control, name = 'Controller1', priority = 1, 
                         period = 1, profile = True, trace = False)
    task4 = cotask.Task (task4_encoder, name = 'Encoder2', priority = 2, 
                         period = 10, profile = True, trace = False)
    task5 = cotask.Task (task5_motor, name = 'Motor2', priority = 1, 
                         period = 8, profile = True, trace = False)
    task6 = cotask.Task (task6_control, name = 'Controller2', priority = 1, 
                         period = 8, profile = True, trace = False)
    cotask.task_list.append (task1)
    cotask.task_list.append (task2)
    cotask.task_list.append (task3)
    cotask.task_list.append (task4)
    cotask.task_list.append (task5)
    cotask.task_list.append (task6)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    # Run the scheduler with the chosen scheduling algorithm. Quit if any 
    # character is received through the serial port
    vcp = pyb.USB_VCP ()
    while not vcp.any ():
        cotask.task_list.pri_sched()

    # Empty the comm port buffer of the character(s) just pressed
    vcp.read ()
    

    # Print a table of task data and a table of shared information data
    print ('\n' + str (cotask.task_list))
    print (task_share.show_all ())
    print ('\r\n')

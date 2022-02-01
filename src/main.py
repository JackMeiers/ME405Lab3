"""!
@file basic_tasks.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

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
    runs the enoder value
    """
    enc = encoderDriver.EncoderDriver(pyb.Pin.board.PB6,pyb.Pin.board.PB7, 4)
    while True:
        enc.update()
        share_enc1.put(enc.read())
        yield (0)
        
def task2_motor ():
    """!
    """
    moe = motorDriver.MotorDriver(pyb.Pin.board.PA10,
        pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)
    while True:
        moe.set_duty_cycle(share_motor1.get())
        yield(0)
        
def task3_control ():
    """!
    """
    start_time = utime.ticks_ms();
    controller = controls.Controls(8192, 2000/8192, 0)
    while True:
        #possible old code: controller.controlLoop(share_enc.get())
        share_motor1.put(controller.controlLoop(share_enc1.get()))
        if(share_enc1.get()!= 0):
            print(utime.ticks_diff(utime.ticks_ms(), start_time), end=",")
            print(share_enc1.get())
        if(utime.ticks_diff(utime.ticks_ms(), start_time) > 15000):
            print(b'EOF')
        yield(0)
        
def task4_encoder ():
    """!
    
    """
    enc = encoderDriver.EncoderDriver(pyb.Pin.board.PC6,pyb.Pin.board.PC7, 8)
    while True:
        enc.update()
        share_enc2.put(enc.read())
        yield (0)
        
def task5_motor ():
    """!
    Creates a motor driver for the second motor and creates a shared value
    for the duty cycle of the second motor.
    """
    moe = motorDriver.MotorDriver(pyb.Pin.board.PC1,
        pyb.Pin.board.PA0, pyb.Pin.board.A1, 5)
    while True:
        moe.set_duty_cycle(share_motor2.get())
        yield(0)
        
def task6_control ():
    """!
    A controller for the second motor
    """
    start_time = utime.ticks_ms();
    controller = controls.Controls(8192, 2000/8192, 0)
    while True:
        #possible useful old code: controller.controlLoop(share_enc.get())
        share_motor2.put(controller.controlLoop(share_enc2.get()))
        yield(0)

"""! This code creates a share, a queue, and two tasks, then starts the tasks. The
     tasks run until somebody presses ENTER, at which time the scheduler stops and
     printouts show diagnostic information about the tasks, share, and queue."""
if __name__ == "__main__":
    print ('\033[2JTesting ME405 stuff in cotask.py and task_share.py\r\n'
           'Press ENTER to stop and show diagnostics.')

    # Create a share and a queue to test function and diagnostic printouts
    share_enc1 = task_share.Share ('i', thread_protect = False, name = "Share Encoder")
    share_motor1 = task_share.Share ('f', thread_protect = False, name = "Share Motor")
    share_enc2 = task_share.Share ('i', thread_protect = False, name = "Share Encoder")
    share_motor2 = task_share.Share ('f', thread_protect = False, name = "Share Motor")
    

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
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
        cotask.task_list.pri_sched ()

    # Empty the comm port buffer of the character(s) just pressed
    vcp.read ()
    

    # Print a table of task data and a table of shared information data
    print ('\n' + str (cotask.task_list))
    print (task_share.show_all ())
    print (task1.get_trace ())
    print ('\r\n')

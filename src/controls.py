'''!@file controls.py
    @brief Closed loop control
    @details This file contains necessary methods and attributes for closed
    loop control of motor. Program can run closed loop position control, 
    change gain values, and create a list used for data analysis
    @author Lucas Sandsor
    @author Jack Barone
    @author Jackson Myers
    @date 25-Jan-2022 
'''
import pyb
class Controls:
    '''!
    @brief This class impliments the motor controller for ME405
    '''
    def __init__(self, setpoint, gain, error_signal):
        '''!@brief Initalizes proportional closed loop control driver
            @param setpoint    Desired # of motor ticks for a step response
            @param gain    K_p which has units of percent duty cycle per. Determines
            how quickly the motor will adjust its speed to get to given position
            encoder count
            @param error_signal    Difference between setpoint and measure value that
            is used alongside gain to adjust which is used to control motor speed
        '''
        self.setpoint = setpoint
        self.gain = gain
        self.error_signal = error_signal
        self.time_list = []
        self.tick_list = []
        

    def controlLoop(self, position):
        '''!@brief applys proportional CL control on input signal by multiplying
            the gain by the error signal to get the new the amount it needs to
            shift by
            @param position    Input signal in ticks 
            @return actuation    Signal produced after CL control
        '''
        self.error_signal = self.setpoint - position
        actuation = self.error_signal * self.gain
        return actuation

    def set_setpoint(self, new_setpoint):
        '''!@brief sets new desired set point used in CL control
            @param new_setpoint    New desired setpoint in # ticks
        '''
        self.setpoint = new_setpoint
        
    def set_gain(self, new_gain):
        '''!@brief sets new gain value, K_p used in CL control
            @param new_gain    Updated gain value K_p so that motor
            can update new speed to get to setpoint
        '''
        self.gain = new_gain
        
    def print_list(self, time_ms, ticks):
        '''!@brief prints time and ticks to the user
            @param time_ms    Time in miliseconds at the time print_list is called
            @param ticks    Encoder ticks at the time print_list is called
        '''
        print(time_ms, ticks)
        
    def store_list(self, time_ms, ticks):
        '''!@brief stores list of time and ticks at the moment when it is called
            to store values for later use
            @param time_ms    Time in milliseconds when store_list is called
            @param ticks    Encoder ticks at moment when store_list is called
        '''
        self.time_list.append(time_ms)
        self.tick_list.append(ticks)
        
        
    

        

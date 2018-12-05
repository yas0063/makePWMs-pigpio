#!/usr/bin/env python

import time
import pigpio

"""
This script shows an example of generating various PWM
on multiple GPIO at the same time with pigpio.

Waves have a resolution of one microsecond.

The following diagram illustrates PWM for one GPIO.
In this case, there are two puluses in one cycle.

1      +------------+             +------------+
       |    GPIO    |             |    GPIO    |
       |<--- on --->|             |<--- on --->|
       |    time    |             |    time    |
0 -----+            +-------------+            +-----------------
     on^         off^           on^         off^
  +--------------------------+--------------------------+-------+
  ^    ^            ^        ^                          ^       ^
  0    pS         pS+pH   pS+pH+pL                 pS+2(pH+pL) micros 
  |<----------------------- cycle time ------------------------>|
cycle                                                         cycle
start                                                         start


To create a new PWM, the following method is provided:

set_waves(ch, pS_, pH_, pL_, times):

ch is 0 for the first GPIO, 1 for the second, etc.
pS_ is a time when the first pulse becomes on. (microseconds)
pH_ is a length of on state of puluse. (microseconds)
pL_ is a length of off state of puluse. (microseconds)
times is a number of pulses in one cycle.


All PWMs have to same micors (length of 1 cycle. 1000000 / frequency). 
Therefore, high frequency PWM needs to fill with pulses in one cycle.


"""

class PWMs:
   def __init__(self, pi, gpio, frequency=1000):
      """
      Instantiate with the pi and list of gpio used to output PWM.

      Optionally the frequency may be specified in Hertz (cycles
      per second).  The frequency defaults to 1000 Hertz.
      """
      self.pi = pi
      self.frequency = frequency
      self.micros = 1000000.0 / frequency
      self.gpio = gpio
      self.channels = len(gpio)
      self.waves=[0]*self.channels
      self.used=[False]*self.channels
      self.old_wid = None

      # set wave GPIO to output mode.
      for g in gpio:
         self.pi.set_mode(g, pigpio.OUTPUT)


   def set_waves(self, ch, pS_, pH_, pL_, times):
      g = self.gpio[ch]
      pS=int(pS_)
      pH=int(pH_)
      pL=int(pL_)
      micros=int(self.micros)

      wave = [pigpio.pulse(0, 1<<g, pS)]
      for i in range(times):
         wave.append(pigpio.pulse(1<<g, 0, pH))
         wave.append(pigpio.pulse(0, 1<<g, pL))
      wave.append(pigpio.pulse(0, 1<<g, micros-(pH+pL)*times-pS))

      self.waves[ch] = wave
      self.used[ch] = True

   def startPWM(self):
      
      for ch in range(len(self.gpio)):
         if self.used[ch] == True:
            self.pi.wave_add_generic(self.waves[ch] )

      new_wid = self.pi.wave_create()

      if self.old_wid is not None:
         self.pi.wave_send_using_mode(new_wid, pigpio.WAVE_MODE_REPEAT_SYNC)

         while self.pi.wave_tx_at() != new_wid:
            pass
         
         self.pi.wave_delete(old_wid)

      else:
         self.pi.wave_send_repeat(new_wid)

      self.old_wid = new_wid

   def stopPWM(self):
      """
      Stop PWM on the GPIO.
      """
      self.pi.wave_tx_stop()

      if self.old_wid is not None:
         self.pi.wave_delete(self.old_wid)

      
if __name__ == "__main__":

   import time
   import pigpio
   import mkPWMs

   PWM1=22
   PWM2=19

   GPIO=[PWM1, PWM2]

   pi = pigpio.pi()
   if not pi.connected:
      exit(0)

   pwm = mkPWMs.PWMs(pi,GPIO,100)
   pwm.set_waves(0, 0, 1000000/1000*0.3, 1000000/1000*0.7, 5);
   pwm.set_waves(1, 1000000/1000/2, 1000000/1000*0.3, 1000000/1000*0.7, 5);

   try:
      pwm.startPWM()
      while True:
         pass
   
   except KeyboardInterrupt:
      pwm.stopPWM()
      pi.stop()





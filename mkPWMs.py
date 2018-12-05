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


One function is provided:

set_waves(ch, pS_, pH_, pL_, times, micros_):

ch is 0 for the first GPIO, 1 for the second, etc.
pS_ is a time when the first pulse becomes on. (microseconds)
pH_ is a length of on state of puluse. (microseconds)
pL_ is a length of off state of puluse. (microseconds)
times is a number of pulses in 1 cycle.
micors_ is a length of 1 cycle. (microseconds)


All waves has to have same micros_.

"""

PWM1=22
PWM2=19
PWM3=24
PWM4=25

GPIO=[PWM1, PWM2, PWM3, PWM4]

_channels = len(GPIO)
_waves=[0]*_channels
_used=[False]*_channels

old_wid = None

def set_waves(ch, pS_, pH_, pL_, times, micros_):

   g = GPIO[ch]
   micros = int(micros_)
   pS=int(pS_)
   pH=int(pH_)
   pL=int(pL_)
   

   wave = [pigpio.pulse(0, 1<<g, pS)]
   for i in range(times):
      wave.append(pigpio.pulse(1<<g, 0, pH))
      wave.append(pigpio.pulse(0, 1<<g, pL))

   wave.append(pigpio.pulse(0, 1<<g, micros-(pH+pL)*times-pS))

   _waves[ch] = wave
   _used[ch] = True

def startPWM():

   global old_wid

   for ch in range(_channels):

      if _used[ch] == True:
         pi.wave_add_generic(_waves[ch] )

   new_wid = pi.wave_create()

   if old_wid is not None:

      pi.wave_send_using_mode(new_wid, pigpio.WAVE_MODE_REPEAT_SYNC)

      while pi.wave_tx_at() != new_wid:
         pass

      pi.wave_delete(old_wid)

   else:

      pi.wave_send_repeat(new_wid)

   old_wid = new_wid

pi = pigpio.pi()
if not pi.connected:
   exit(0)

# Need to explicity set wave GPIO to output mode.
for g in GPIO:
   pi.set_mode(g, pigpio.OUTPUT)


set_waves(0, 0, 1000000/1000/2, 1000000/1000/2, 5, 1000000/100);
set_waves(1, 1000000/1000/2, 1000000/1000/2, 1000000/1000/2, 5, 1000000/100);
startPWM()
   



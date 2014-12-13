import time

# I guess it's like an enum
class TimerType:
    MINUTE = 1
    SECOND = 2

# "Timer" that sets a future time defined in minutes or seconds, depending
# on the method chosen.
# Has to be manually checked, does not work automatically.

# Time delay is not unique. Delay is only in terms of minutes or seconds.
# This means they can repeat by the minute or hour. Implementations in this
# bot take care of that. Any others should too.
class Timer:
    timeDelay = None
    timerType = None

    # Timers must be initialized using minTimer or secTimer before checking
    def minTimer(self, minutes):
        currentMin = time.localtime()[4]
        if (currentMin + minutes) > 59:
            self.timeDelay = (currentMin + minutes) - 59
        else:
            self.timeDelay = currentMin + minutes
        self.timerType = TimerType.MINUTE

    def secTimer(self, seconds):
        currentSec = time.localtime()[5]
        if (currentSec + seconds) > 61:
            self.timeDelay = (currentSec + seconds) - 61
        else:
            self.timeDelay = currentSec + seconds
        self.timerType = TimerType.SECOND

    # Returns true if timer is done, false otherwise
    def check(self):
        if self.timeDelay == None:
            raise RuntimeError("Timer not initialized")

        if self.timerType == TimerType.MINUTE:
            return time.localtime()[4] == self.timeDelay
        elif self.timerType == TimerType.SECOND:
            return time.localtime()[5] == self.timeDelay

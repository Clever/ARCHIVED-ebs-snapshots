from threading import Timer,Thread,Event
import threading

class PerpetualTimer():
  """ In a thread, call a method every t seconds """

  def __init__(self, t, hFunction):
    self.t = t 
    self.hFunction = hFunction
    self.thread = Timer(self.t,self.handle_function)
  
  def handle_function(self):
    self.hFunction()
    self.thread = Timer(self.t,self.handle_function)
    self.thread.start()

  def start(self):
    self.thread.start()

  def cancel(self):
    self.thread.cancel()

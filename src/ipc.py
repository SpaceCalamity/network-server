import comm_handler

import queue
import socket
import threading

class IPC:
  created = False
  def __init__(self, port):
    if IPC.created:
      raise Exception('IPC already created')
    IPC.created = True
    self.port = port
    self.active = False
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.comm_queue = queue.Queue()

  def ipc_connect(self, port):
    self.active = True
    try:
      self.sock.connect(('localhost', port))
      try:
        thread = threading.Thread(target=self.__pipe)
        thread.start()
      except Exception as e:
        print('IPC Error: Failed to create receive thread')
        raise
    except Exception as e:
      print('IPC Error: Failed to connect to game server')

  def close(self):
    self.sock.close()

  def __pipe(self):
    try:
      while self.active:
        while not self.comm_queue.empty():
          try:
            comm = self.comm_queue.get()
          except Exception:
            print('IPC Error: Queue is empty on get')
            comm = ''
          self.sock.sendall(IPC.__flush(comm))
        data = ''
        while (byte := self.sock.recv(1)) != b'\n':
          data += byte.decode()
        comm_handler.handle(data)
    except Exception e:
      print('IPC Error: Pipe connection failed')
      print(e)
      self.close()
  
  @staticmethod
  def __flush(message):
    return '%s\n' % message

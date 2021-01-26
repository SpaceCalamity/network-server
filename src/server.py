import commands
import conn_handler

import queue
import socket
import threading
import uuid

class Server:
  created = False
  next_uuid = uuid.uuid1()
  def __init__(self):
    if Server.created:
      raise Exception('Server already created')
    Server.created = True
    self.listen_active = False
    self.ipc_active = False
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.comm_queue = queue.Queue()
    self.users = {}

  def ipc_connect(self, port):
    self.ipc_active = True
    try:
      self.sock.connect(('localhost', port))
      try:
        ipc_in = threading.Thread(target=self.__pipe_in)
        ipc_in.start()
        ipc_out = threading.Thread(target=self.__pipe_out)
        ipc_out.start()
      except Exception as e:
        print('IPC Error: Failed to create receive thread')
        raise
    except Exception as e:
      print('IPC Error: Failed to connect to game server')
      raise

  def listen(self, context, port):
    self.listen_active = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
      sock.bind(('', port))
      sock.listen(5)
      with context.wrap_socket(socket, server_side=True) as ssock:
        while self.listen_active:
          conn, addr = ssock.accept()
          newUser = conn_handler.User(Server.next_uuid, this, conn, addr) 
          users[Server.next_uuid] = newUser
          Server.next_uuid = uuid.uuid1()

  def close(self):
    self.ipc_active = False
    try:
      self.sock.close()
    except:
      pass

  def load_command(self, command):
    self.comm_queue.put(command)

  def __handle(self, data):
    data_parsed = data.split()
    size = len(data_parsed)
    if size < 2:
      print('IPC Error: Received insufficient data: %s' % data)
      return
    session_id = data_parsed[0]
    command = data_parsed[1]
    if session_id not in users:
      print('IPC Error: session_id not found: %s' % session_id)
      return
    user = users[session_id] 
    user.load_command(data_parsed[1:])

  def __pipe_out(self):
    try:
      while self.ipc_active:
        while not self.comm_queue.empty():
          try:
            comm = self.comm_queue.get()
          except:
            print('IPC Error: Queue is empty on get')
            comm = ''
          if comm:
            self.sock.sendall(__flush(comm))
    except Exception as e:
      print('IPC Error: Pipe connection failed (out thread)')
      print(e)
      self.close()

  def __pipe_in(self):
    try:
      while self.ipc_active:
        data = ''
        while (byte := self.sock.recv(1)) != b'\n':
          data += byte.decode()
        self.__handle(data)
    except Exception as e:
      print('IPC Error: Pipe connection failed (in thread)')
      print(e)
      self.close()

def __flush(message):
  return ('%s\n' % message).encode()

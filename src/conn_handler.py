import commands

import queue
import threading

class User:
  def __init__(self, uuid, server, conn, addr):
    if not server:
      raise Exception('Server not yet initialized')
    self.session_id = uuid 
    self.server = server
    self.conn = conn
    self.addr = addr
    self.comm_queue = queue.Queue()
    self.active = True
    thread_in = threading.Thread(target=self.__socket_in)
    thread_in.start()
    thread_out = threading.Thread(target=self.__socket_out)
    thread_out.start()

  def load_command(self, command):
    self.comm_queue.put(command)

  def close(self):
    self.active = False
    to_print = False
    try:
      self.conn.close()
      to_print = True
    except Exception as e:
      print('Server: Unable to close connection')
      print(e)
    try:
      self.server.users.pop(self.session_id)
      to_print = True
    except Exception as e:
      print('Server: Unable to remove user from users')
      print(e)
    if to_print:
      print('Server: Closing connection with: %s' % self.addr[0])

  def __socket_in(self):
    print('Server: Received connection from: %s' % self.addr[0])
    try:
      auth = False
      while not auth:
        data = __read_data(self.conn)
        data_parsed = data.split()
        if data_parsed:
          command = data_parsed[0]
          if command == commands.QUIT:
            return
          elif command == commands.REGISTER:
            if len(data_parsed) != 4:
              self.load_command('%s Error: expected arguments:' +
                                ' <email> <handle> <password>' 
                                % commands.ERROR)
            else:
              self.server.load_command('%s %s %s' 
                % (command, self.session_id, ' '.join(data_parsed[1:])))
          elif command == commands.LOGIN:
            if len(data_parsed) != 3:
              self.load_command('%s Error: expected arguments:' +
                                ' <email/handle> <password>'
                                % commands.ERROR)
            else:
              self.server.load_command('%s %s' 
                % (self.session_id, data))
          else:
            self.load_command('%s Error: unexpected token: %s'
                              % (commands.ERROR, command))
      while self.active:
        data = __read_data(self.conn)
        data_parsed = data.split()
        if data_parsed:
          if command == commands.QUIT:
            return
          self.server.load_command('%s %s' % (session_id, data))
    except Exception as e:
      print('Server Error: Connection failure from: %s (socket in)' % self.addr[0])
      print(e)
    finally:
      self.close()

  def __socket_out(self):
    try:
      while self.active:
        while not self.comm_queue.empty():
          try:
            comm = self.comm_queue.get()
          except:
            print('Server Error: Queue is empty on get (%s)' % self.addr[0])
            comm = ''
          if comm:
            self.conn.sendall(__flush(comm))
    except Exception as e:
      print('Server Error: Connection failure from: %s (socket out)' % self.addr[0])
      print(e)
    finally:
      self.close()

  def __read_data(self):
    data = ''
    while (byte := self.conn.recv(1)) != b'\n':
      data += byte.decode()
    return data

def __flush(message):
  return ('%s\n' % message).encode()

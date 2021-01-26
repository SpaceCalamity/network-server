import server

import socket
import ssl
import sys

def start(certfile, keyfile, port, usersport):
  context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
  context.load_cert_chain(certfile, keyfile)
  try:
    server = server.Server()
    server.ipc_connect(port)
    server.listen(context, usersport)
  except Exception as e:
    print('Server failure')
    print(e)

if __name__ == '__main__':
  args = sys.argv[1:]
  if len(args) != 4:
    print('Error: expected 4 arguments (certfile, keyfile, port, usersport)')
    return
  print('Args: certfile=%s; keyfile=%s, port=%s; usersport=%s)' % (*args))
  start(*args)

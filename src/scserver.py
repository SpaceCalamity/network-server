import socket
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('/path/to/certchain.pem', '/path/to/private.key')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(('0.0.0.0', 8443))
    sock.listen(5)
    with context.wrap_socket(sock, server_side=True) as ssock:
        conn, addr = ssock.accept()
        try:
            print('Received connection from: ' + addr[0])
            while True:
                data = ''
                while (byte := conn.recv(1)) != b'\n':
                    data += byte.decode()
                print(data)
                conn.sendall(('%s\n' % data).encode())
                print('Sent')
        except Exception as e:
            print("Server Error: %s" % str(e))
        finally: 
            conn.close()
            sock.close()

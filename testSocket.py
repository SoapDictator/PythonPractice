import socket, string

#host
def do_something(x):
	lst = map(None, x);
	lst.reverse();
	return string.join(lst, "")
		
HOST = "localhost" # localhost
PORT = 33333
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.bind((HOST, PORT))

while 1:
	print("Listening port 33333")
	srv.listen(1)
	sock, addr = srv.accept()
	while 1:
		pal = sock.recv(1024)
		if pal:
			break
	print("Received from %s: %s" % (addr, pal))
	lap = do_something(pal)
	print("Sent %s: %s" % (addr, lap))
	sock.send(lap)
	sock.close()
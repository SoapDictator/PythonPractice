import socket

class sock():
	def __init__( self, maxpeers, serverport, myid=None, serverhost = None ):
		self.debug = 0

		self.maxpeers = int(maxpeers)
		self.serverport = int(serverport)

			# If not supplied, the host name/IP address will be determined
		# by attempting to connect to an Internet host like Google.
		self.serverhost = serverhost

			# If not supplied, the peer id will be composed of the host address
			# and port number
		if myid: 
			self.myid = myid
		else: 
			self.myid = '%s:%d' % (self.serverhost, self.serverport)

			# list (dictionary/hash table) of known peers
		self.peers = {}  

			# used to stop the main loop
		self.shutdown = False  

		self.handlers = {}
		self.router = None
		
	def makeserversocket(self, backlog=5):
		s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
		s.bind( ( '', self.serverport ) )
		s.listen( backlog )
		return s
		
	def mainloop( self ):
		s = self.makeserversocket( self.serverport )
		s.settimeout(2)
		print( 'Server started: %s (%s:%d)'
				  % ( self.myid, self.serverhost, self.serverport ) )

		while not self.shutdown:
			try:
				print( 'Listening for connections...' )
				clientsock, clientaddr = s.accept()
				clientsock.settimeout(None)

				t = self.__handlepeer(clientsock)
				t.start()
			except KeyboardInterrupt:
				break

		print( 'Exiting main loop' )
		s.close()
		
	def __handlepeer( self, clientsock ):
		print( 'Connected ' + str(clientsock.getpeername()) )

		host, port = clientsock.getpeername()
		peerconn = BTPeerConnection( None, host, port, clientsock, debug=False )
		
		try:
			msgtype, msgdata = peerconn.recvdata()
			if msgtype: 
				msgtype = msgtype.upper()
			if msgtype not in self.handlers:
				print( 'Not handled: %s: %s' % (msgtype, msgdata) )
			else:
				print( 'Handling peer msg: %s: %s' % (msgtype, msgdata) )
				self.handlers[ msgtype ]( peerconn, msgdata )
		except KeyboardInterrupt:
			raise
		except:
			if self.debug:
				traceback.print_exc()
		
		print( 'Disconnecting ' + str(clientsock.getpeername()) )
		peerconn.close()
		
	def sendtopeer( self, peerid, msgtype, msgdata, waitreply=True ):
		if self.router:
			nextpid, host, port = self.router( peerid )
		if not self.router or not nextpid:
			print( 'Unable to route %s to %s' % (msgtype, peerid) )
			return None
		return self.connectandsend( host, port, msgtype, msgdata, pid=nextpid, waitreply=waitreply )
		
	def connectandsend( self, host, port, msgtype, msgdata, pid=None, waitreply=True ):
		msgreply = []   # list of replies
		try:
			peerconn = BTPeerConnection( pid, host, port, debug=self.debug )
			peerconn.senddata( msgtype, msgdata )
			print( 'Sent %s: %s' % (pid, msgtype) )
			
			if waitreply:
				onereply = peerconn.recvdata()
				while (onereply != (None,None)):
					msgreply.append( onereply )
					print( 'Got reply %s: %s' % ( pid, str(msgreply) ) )
					onereply = peerconn.recvdata()
				peerconn.close()
		except KeyboardInterrupt:
			raise
		except:
			if self.debug:
				traceback.print_exc()
		
		return msgreply
		
class main():
	def __init__(self):
		newSock = sock(1, 30715, 0, "192.168.0.0")
		newSock.mainloop()
		
start = main()
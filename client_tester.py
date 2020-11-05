from socket import *
import sys, os
import threading

def client_thread () :	
	while True :	
		sentence = input("Request : ")
		clientSocket.send(sentence.encode())

def client_recieve() :		
	while True :	
		try :	
			modifiedSentence = clientSocket.recv(1024)
			modifiedSentence = modifiedSentence.decode()
			if len(modifiedSentence) == 0 :
				print("Server got disconnected")
				clientSocket.close()
				os._exit(1)
			print(modifiedSentence)
		except :
			print("Server got disconnected")
			clientSocket.close()
			os._exit(1)

server_name = "127.0.0.1"
try :
	server_port = int(sys.argv[1])
	client_name = sys.argv[2]
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((server_name,server_port))
	print("Connected to the server")
	threading.Thread(target = client_thread).start()
	threading.Thread(target = client_recieve).start()
except :
	print("Please provide correct port number and username as commandline arguments")
	exit()
import sys, threading, os.path, time
from time import gmtime, strftime
from socket import *
import json

serversocket = socket(AF_INET,SOCK_STREAM)
serverport = int(sys.argv[1])

try :
	serversocket.bind(('', serverport))
except :
	print("Given port is busy. Please select another one")
	exit()

serversocket.listen(5)

STATUS_CODES = {
    100: "Informational",
    200: "OK",
    300: "Redirection",
    304: "Not Modified",
    400: "Client-Error",
    404: "Not Found",
    500: "Server-Error"
}

def current_time() :
	return strftime("%a, %d %b %Y %H:%M:%S GMT",gmtime())

def get_content_type(file_name) :
	postfix = file_name.rsplit('.', 1)[-1]
	print(postfix)
	if postfix == "html" :
		return "text/html"
	elif postfix == "jpg" or postfix == "jpeg" :
		return "image/jpeg"
	elif postfix == "png" :
		return "image/png"
	elif postfix == "gif" :
		return "image/gif"
	elif postfix == "css" :
		return "text/css"
	elif postfix == "xml" :
		return "text/xml"
	elif postfix == "js" :
		return "text/javascript"
	else :
		return "text/plain"

def get_file_encoded(file_name, type) :
	a = ["text/html", "text/css", "text/xml", "text/javascript", "text/plain"]
	b = ["image/png", "image/jpeg", "image/gif", ]
	print(file_name)
	if type in a :
		f = open(file_name, "r")
		body = f.read().encode()
	elif type in b :
		f = open(file_name, "rb")
		body = f.read()
	return body, len(body)


def get_modification_time(file_name) :
	return strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(os.path.getmtime(file_name)))

def decode_uri(url) :
	temp_variables = url.split("?")
	file_name = temp_variables[0]
	get_variable = {}
	if len(temp_variables) != 1 :
		for var in temp_variables[1].split("&") :
			key, value = var.split("=")
			get_variable[key] = value
	return file_name, get_variable

def encode_headers(http_v, status_code, res_headers) :
	reply = http_v
	reply = reply + " " + str(status_code) + " " + STATUS_CODES[status_code] + "\n"
	for key in res_headers :
		if res_headers[key] != None :
			reply = reply + "{}: {}\r\n".format(key, str(res_headers[key]))
	reply = reply + "\r\n"
	reply = reply.encode() 
	return reply


def client_function (connection_socket) :
	data = connection_socket.recv(1024).decode()
	fields = data.split("\r\n")
	print(fields)
	main_header = fields[0].split(" ")
	fields = fields[2:]
	req_headers = {}
	res_headers = {}
	for f in fields :
		if f.find(": ") != -1 :
			key, value = f.split(': ', 1)
			req_headers[key] = value
	# print(data)

	print("\n--------------------" + main_header[1] + "---------------")
	res_headers["Date"] = current_time()
	res_headers["Server"] = "RON_Server/0.0.1 (Ubuntu18)"
	res_headers["Connection"] = "Closed"
	
	if main_header[0] == "GET" or main_header[0] == "HEAD":
		req_headers["If-Modified-Since"] = None
		req_headers["If-Unmodified-Since"] = None
		# req_headers["If-Modified-Since"] = "Wed, 21 Oct 2020 21:15:53 GMT"

		main_header[1], get_variable = decode_uri(main_header[1])
		print(main_header[1])
		print(get_variable)
		if main_header[1] == "/" :
			main_header[1] = "/index.html"
		if os.path.exists(main_header[1][1:]) :
			send_file_name = main_header[1][1:]
			is_body = True
			print(send_file_name)
			status_code = 200
			res_headers["Content-Type"] = get_content_type(send_file_name)
			body, res_headers["Content-length"] = get_file_encoded(send_file_name, res_headers["Content-Type"])
			res_headers["Last-Modified"] = get_modification_time(send_file_name)
		else :
			send_file_name = "error.html"
			is_body = True
			status_code = 404
			res_headers["Content-Type"] = get_content_type(send_file_name)
			body, res_headers["Content-length"] = get_file_encoded(send_file_name, res_headers["Content-Type"])
			res_headers["Last-Modified"] = get_modification_time(send_file_name)
		# body = f.read()
		if status_code == 200 and req_headers["If-Modified-Since"] != None:
			print(res_headers["Last-Modified"])
			print(req_headers["If-Modified-Since"])
			if req_headers["If-Modified-Since"] == res_headers["Last-Modified"] :
				status_code = 304
				print("Hey ron")
				res_headers["Content-Type"] = None
				res_headers["Content-length"] = None
				is_body = False
			else :
				print("yooo")
				is_body = True

		reply = encode_headers(main_header[2], status_code, res_headers)
		if main_header[0] == "GET" and is_body:
			reply = reply + body + '\n'.encode()
		else :
			reply = reply + "\n".encode()
		print(reply)

	elif main_header[0] == "POST" :
		print(req_headers["Content-Type"])
		if req_headers["Content-Type"] == "application/x-www-form-urlencoded" :
			post_data = {} 
			for var in fields[-1].split("&") :
				key, value = var.split("=")
				post_data[key] = value
			with open('post_data.json', 'a+') as fp:
				json.dump(post_data, fp)
		elif req_headers["Content-Type"] == "text/plain" :
			post_data = fields[-1]
			with open("post_data.txt", "a+") as fp :
				f.write(post_data)
		status_code = 200
		res_headers["Content-Location"] = "/post_data.txt"
		reply = encode_headers(main_header[2], status_code, res_headers)
		fp.close()
		print(post_data)
	elif main_header[0] == "PUT" :
		if (req_headers["Content-Type"].split("/"))[0] == "text" :
			f = open(main_header[1][1:], "w+") 
			f.write(fields[-1])
		elif (req_headers["Content-Type"].split("/"))[0] == "image" :
			f = open(main_header[1][1:], "w+b")
			f.write(fields[-1])
		res_headers["Content-Location"] = "/" + main_header[1][1:]
		status_code = 200
		reply = encode_headers(main_header[2], status_code, res_headers)
		f.close()
	connection_socket.send(reply)
	connection_socket.close()
	print("\n\n")


while True :
	connectionSocket, addr = serversocket.accept()
	print("new request received from : ")
	print(addr)
	print("connectionSocket is : ")
	print(connectionSocket);
	print("\n\n")
	threading.Thread(target = client_function, args = (connectionSocket,)).start()
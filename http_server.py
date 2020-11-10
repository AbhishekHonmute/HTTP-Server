import sys, threading, os.path, time
from time import gmtime, strftime
import datetime
import socket
import json
import re
# for genrerating cookie 
import shortuuid

# Constants
connected_clients = []
connection_queue_limit = 5
request_data_limit = 1024

serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# serverport = 90
serverport = int(sys.argv[1])

# status codes 
status_codes = {
    100: "Informational",
    200: "OK",
	201: "Created",
	202: "Accepted",
    300: "Redirection",
    304: "Not Modified",
    400: "Client-Error",
	403: "Forbidden",
    404: "Not Found",
	405: "Method Not Allowed",
	411: "Length Required",
	412: "Precondition Failed",
    500: "Server-Error",
	505: "HTTP Version Not Supported"
}

# binding port 
try :
	serversocket.bind(('', serverport))
	print("Server started")
except :
	print("Given port is busy. Please select another one")
	exit()

# listening
serversocket.listen(5)

# returns current time in http format string
def current_time() :
	return strftime("%a, %d %b %Y %H:%M:%S GMT",gmtime())

# returns the content type of the input file
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

# returns encoaded body and the content length
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

# returns the file last modification time in http format string
def get_modification_time(file_name) :
	return strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(os.path.getmtime(file_name)))

# extracts the given url to check if it contains the url encoaded data if exists then it returns the data and file name
def decode_uri(url) :
	temp_variables = url.split("?")
	file_name = temp_variables[0]
	get_variable = {}
	if len(temp_variables) != 1 :
		for var in temp_variables[1].split("&") :
			key, value = var.split("=")
			get_variable[key] = value
	return file_name, get_variable

# returns the encoded response headers if a header is None then it skips it
def encode_headers(http_v, status_code, res_headers) :
	reply = http_v
	reply = reply + " " + str(status_code) + " " + status_codes[status_code] + "\n"
	for key in res_headers :
		if res_headers[key] != None :
			reply = reply + "{}: {}\r\n".format(key, str(res_headers[key]))
	reply = reply + "\r\n"
	print(reply)
	reply = reply.encode() 
	return reply

# main client function which is assigned to each request using multithreading
def client_function (client_socket) :
	# to take inputs greater than the one time limit
	fragments = []
	while True :
		request_data = client_socket.recv(request_data_limit)
		fragments.append(request_data)
		if len(request_data) < request_data_limit :
			break
	request_data = b''.join(fragments)

	# if no or empty request is made then server closes the connection
	if len(request_data) == 0 :
		print("No request, closing connection...")
		client_socket.close()
		return

	# decoding data
	# try:
	# 	request_headers = request_data.decode('utf-8')
	# 	request_body = None
	# 	binary_data = False
	# 	print("No binary data")

	# except:
	# request_data = request_data.split(b'\r\n\r\n', 1)
	# try :	
	# 	request_body = request_data[1]
	# 	is_req_body = True
	# except :
	# 	request_body = None
	# 	is_req_body = False
	# request_headers = request_data[0].decode('utf-8')
	# print("RON")
	# print(request_data.decode())
	request_data = request_data.split(b'\r\n\r\n', 1)
	# print("Sam")
	# print(request_data)
	try :
		request_body = request_data[1]
	except :
		request_body = b""
	request_data = request_data[0].decode('utf-8')
	# print(len(request_body))
	request_headers = request_data
	# print(len(request_body))
	# binary_data = True
	# print("Binary data exists")

	# printing the request headers
	print("#############")
	print(request_headers)
	print("#############")
	# print(request_body.decode('utf-8'))
	print("#############")
	fields = request_headers.split("\r\n")
	main_req_line = fields[0]
	main_req_header = fields[0].split(" ")
	fields = fields[1:]
	req_headers = {}
	res_headers = {}
	for f in fields :
		if f.find(": ") != -1 :
			key, value = f.split(': ', 1)
			req_headers[key] = value
	# print(data)

	print("\n--------------------" + main_req_header[1] + "---------------")
	res_headers["Date"] = current_time()
	res_headers["Server"] = "RON_Server/0.0.1 (Ubuntu18)"
	res_headers["Connection"] = "Closed"

	# set cookie if not 
	if 'Cookie' not in req_headers.keys() :
		cookie_id = shortuuid.uuid()
		res_headers['Set-Cookie'] = "user_id=" + cookie_id + "; Max-Age=3576"
		print("cookie set")
	else :
		cookie_id = req_headers['Cookie']

	# remove starting '/' from the uri
	main_req_header[1] = main_req_header[1][1:]

	# to handle http version not supported
	reply = "hey"
	print(main_req_header[2])
	if main_req_header[2] != "HTTP/1.1" :
		status_code = 505
		reply = encode_headers(main_req_header[2], status_code, res_headers)
		print(reply)
		# from here it check the type of method of request and responds accordingly
	elif main_req_header[0] == "GET" or main_req_header[0] == "HEAD":
		# getting url encoded data to file 
		main_req_header[1], get_variables = decode_uri(main_req_header[1])
		# if len(get_variables) != 0 :
		# 	get_variable_path = "GET_DATA/get_data.json"
		# 	f = open(get_variable_path, "a+")
		# 	f.write(json.dumps(get_variables))
		# 	f.close()
		# If no file is specified then it autoatically takes index.html from given directory
		# if not os.path.exists(main_req_header[1]) and os.path.isdir(main_req_header[1]) :
		# 	main_req_header[1] = main_req_header[1] + "index.html"
		# 	print("Hey ron")
		if main_req_header[1] == "" :
			main_req_header[1] = "index.html"
		elif main_req_header[1][-1] == "/" :
			main_req_header[1] = main_req_header[1] + "index.html"
		elif os.path.isdir(main_req_header[1]) :
			main_req_header[1] = main_req_header[1] + "/index.html"
		print("path : ", main_req_header[1])
		print(main_req_header[1])
		print(get_variables)
		is_body = False
		# valiidate path 
		# file path = main_request_header[1]
		if os.path.exists(main_req_header[1]) :
			if os.access(main_req_header[1], os.R_OK): 
				# Conditional get
				last_modified = os.path.getmtime(main_req_header[1])
				last_modified = datetime.datetime.fromtimestamp(last_modified, datetime.timezone.utc).replace(microsecond=0 ,tzinfo=None)
				print(last_modified)
				modified_flag = False
				# if If-Modified-Since header is given in request then check if file is modified after given time. if modified then 
				# continue with regular get else send 304 file not modified status line
				if 'If-Modified-Since' in req_headers.keys() :
					if_modified_since = req_headers['If-Modified-Since']
					if_modified_since = datetime.datetime.strptime(if_modified_since, "%a, %d %b %Y %X %Z")
					if if_modified_since >= last_modified :
						status_code = 304
						modified_flag = True
				# req_headers["If-Modified-Since"] = "Wed, 21 Oct 2020 21:15:53 GMT"
				# if If-Unmodified-Since header is given then check if 
				elif 'If-Unmodified-Since' in req_headers.keys() :
					if_unmodified_since = req_headers['If-Unmodified-Since']
					if_unmodified_since = datetime.datetime.strptime(if_unmodified_since, "%a, %d %b %Y %X %Z")
					if if_unmodified_since < last_modified :
						status_code = 412
						modified_flag = True
				# regular get request
				if not modified_flag:
					send_file_name = main_req_header[1]
					print("regular")
					is_body = True
					print(send_file_name)
					status_code = 200
					res_headers["Content-Type"] = get_content_type(send_file_name)
					body, res_headers["Content-length"] = get_file_encoded(send_file_name, res_headers["Content-Type"])
					res_headers["Last-Modified"] = get_modification_time(send_file_name)
					# appending url data in get file
					if len(get_variables) != 0 :
						get_variable_path = "GET_DATA/get_data.json"
						f = open(get_variable_path, "a+")
						f.write(json.dumps(get_variables))
						f.close()
			else :
				is_body = True
				status_code = 403
				res_headers["Content-Type"] = "text/plain"
				body = b"403 Forbidden"
				res_headers["Content-length"] = len(body)
		else :
			is_body = True
			status_code = 404
			res_headers["Content-Type"] = "text/plain"
			body = b"404 Not Found"
			res_headers["Content-length"] = len(body)
			# body = f.read()
			# if status_code == 200 and req_headers["If-Modified-Since"] != None:
			# 	print(res_headers["Last-Modified"])
			# 	print(req_headers["If-Modified-Since"])
			# 	if req_headers["If-Modified-Since"] == res_headers["Last-Modified"] :
			# 		status_code = 304
			# 		print("Hey ron")
			# 		res_headers["Content-Type"] = None
			# 		res_headers["Content-length"] = None
			# 		is_body = False
			# 	else :
			# 		print("yooo")
			# 		is_body = True

		reply = encode_headers(main_req_header[2], status_code, res_headers)
		if is_body and main_req_header[0] != "HEAD":
			reply = reply + body + '\n'.encode()	
		else :
			reply = reply + "\n".encode()
		# print(reply)


	# post request handler
	elif main_req_header[0] == "POST" :
		do_post = False
		# check path
		# main_req_header[1] = "POST_DATA/post_data.json"
		print(main_req_header[1])
		if not os.path.exists(main_req_header[1]) :
			# if file not exists then check if given uri is not directory
			if os.path.isdir(main_req_header[1]):
				status_code = 403
				body = b"403 Forbidden. Given url is a directory, must be a file"
				is_body = True
			else :
				last_file_name = os.path.basename(main_req_header[1])
				if len(last_file_name) > 0:
					# now check if directory exists 
					if os.path.exists(os.path.dirname(main_req_header[1])) or "/" not in main_req_header[1]:
						try:
							file_type = last_file_name.split('.')[1]
							# For POST
							if file_type == 'json':
								f = open(main_req_header[1], 'a+')
								status_code = 201
								body = b"file created successfully"
								print("A")
								do_post = True
						except:
							pass
				if not do_post :
					status_code = 404
					body = b"404 Not Found."
		else :
			# check the access for the file
			last_file_name = os.path.basename(main_req_header[1])
			file_type = last_file_name.split('.')[1]
			print(file_type)
			if file_type == "json" :
				if os.access(main_req_header[1], os.W_OK):
					f = open(main_req_header[1], 'a+')
					status_code = 200
					body = b"Data Posted successfully"
					print("B")
					do_post = True
				else :
					print("GOd")
					status_code = 403
					body = b"403 Forbidden. permission denied"
			else :
				status_code = 403
				body = b"403 Forbidden. file is not json"
		
		# Actual post process
		if do_post :
			if 'Content-Length' not in req_headers.keys() :
				status_code = 411
				body = b"Content Length required"
			elif int(req_headers['Content-Length']) != len(request_body) :
				print("++++++")
				print(req_headers['Content-Length'])
				print(len(request_body))
				print("++++++")
				status_code = 400
				body = b"Bad Request. Content length missmatch"
			else :
				if req_headers['Content-Type'] == 'application/x-www-form-urlencoded' :
					# print(request_body.decode('utf-8'))
					post_data = {}
					request_body = request_body.decode('utf-8')
					for var in request_body.split('&') :
						key, value = var.split('=')
						post_data[key] = value
					f.write(json.dumps(post_data))
					print("C")
					f.close()
				elif 'multipart/form-data' in req_headers['Content-Type'] :
					# Extract the boundary from content type header
					boundary = req_headers['Content-Type'].split('; boundary=')[1]
					boundary = "--" + boundary
					print("Boundary : ", boundary)
					# request_body = request_body.decode('utf-8')
					req_body_dict = {}
					# remove end of the body 
					end_of_body = '\r\n' + boundary + '--\r\n'
					print(end_of_body)
					end_of_body = end_of_body.encode('utf-8')
					if end_of_body in request_body :
						request_body.replace(end_of_body, b"")
						print("remove end")
					# split body at boundary
					temp_boundary = '\r\n' + boundary + '\r\n'
					temp_boundary = temp_boundary.encode('utf-8')
					request_body = request_body.split(temp_boundary)
					for block in request_body :
						if len(block) == 0 :
							continue
						block_part = block.split(b"\r\n\r\n", 1)
						block_headers = {}
						block_head = (block_part[0].decode('utf-8')).split("; ")
						for temp in block_head :
							if ":" in temp :
								key, value = temp.split(": ")
							elif "=" in temp :
								# temp.replace("\"", "")
								key, value = temp.split("=")
							block_headers[key] = value
						name = block_headers['name']
						name = name[1:-1]
						# name.replace("\"", "")
						if 'filename' in block_headers.keys() :
							value = "POST_DATA/" + block_headers['filename']
							try :	
								f1 = open(value, "wb")
								f1.write(block_part[1])
								f1.close()
							except :
								pass
						else :
							value = block_part[1].decode('utf-8')
							value = value.split("\r\n")[0]
						req_body_dict[name] = value
					f.write(json.dumps(req_body_dict))
					print(req_body_dict)
					print("post it is")
					f.close()


		reply = encode_headers(main_req_header[2], status_code, res_headers)
		reply = reply + body + '\n'.encode('utf-8')
		# print(req_headers["Content-Type"])
		# if req_headers["Content-Type"] == "application/x-www-form-urlencoded" :
		# 	post_data = {} 
		# 	for var in fields[-1].split("&") :
		# 		key, value = var.split("=")
		# 		post_data[key] = value
		# 	with open('post_data.json', 'a+') as fp:
		# 		json.dump(post_data, fp)
		# elif req_headers["Content-Type"] == "text/plain" :
		# 	post_data = fields[-1]
		# 	with open("post_data.txt", "a+") as fp :
		# 		f.write(post_data)
		# status_code = 200
		# res_headers["Content-Location"] = "/post_data.txt"
		# reply = encode_headers(main_req_header[2], status_code, res_headers)
		# fp.close()
		# print(post_data)


	elif main_req_header[0] == "PUT" :
		# if (req_headers["Content-Type"].split("/"))[0] == "text" :
		# 	f = open(main_req_header[1], "w+") 
		# 	f.write(fields[-1])
		# elif (req_headers["Content-Type"].split("/"))[0] == "image" :
		# 	f = open(main_req_header[1], "w+b")
		# 	f.write(fields[-1])
		# res_headers["Content-Location"] = "/" + main_req_header[1]
		# status_code = 200
		# reply = encode_headers(main_req_header[2], status_code, res_headers)
		# f.close()
		dir_name = os.path.dirname(main_req_header[1])
		print(main_req_header[1])
		if os.path.exists(dir_name) or "/" not in main_req_header[1]: 
			if 'Content-Type' in req_headers.keys() :
				if 'Content-Length' in req_headers.keys() :
					if int(req_headers['Content-Length']) == len(request_body) :
						if os.path.exists(main_req_header[1]) :
							if os.access(main_req_header[1], os.W_OK) :
								f = open(main_req_header[1], "wb")
								status_code = 200
								body = "200 ok. file saved"
							else :
								status_code = 403
								body = "403 access denied"
						else :
							f = open(main_req_header[1], "w+")
							f.close()
							f = open(main_req_header[1], "wb")
							status_code = 201
							body = "201 file created"
						f.write(request_body)
						f.close()
					else :
						status_code = 400
						body = "400 Bad request. Content length missmatch"
				else :
					status_code = 411
					body = "411 Content Length required"
			else :
				status_code = 400
				body = "400 Bad request. Content type not given"
		else :
			status_code = 404
			body = "404 Not found"
		reply = encode_headers(main_req_header[2], status_code, res_headers)
		# put request has no body in reqponse this is for test
		# reply = reply + body.encode('utf-8') + '\n'.encode('utf-8')
		reply = reply + '\n'.encode('utf-8')



	elif main_req_header[0] == "DELETE" :
		# check if file exists
		if os.path.exists(main_req_header[1]) :
			if os.access(main_req_header[1], os.W_OK) :
				status_code = 200
				body = "200 Ok. File deleted"
				try :
					os.remove(main_req_header[1])
				except :
					status_code = 202
					body = "202 Accepted. Unable to delete"
			else :
				status_code = 202
				body = "202 Accepted. file not deleted"
		else :
			status_code = 404
			body = "404 not found"
		reply = encode_headers(main_req_header[2], status_code, res_headers)
		reply = reply + body.encode('utf-8') + '\n'.encode('utf-8')

	else :
		status_code = 405
		body = "405 Method Not Allowed"
		reply = encode_headers(main_req_header[2], status_code, res_headers)
		reply = reply + body + '\n'.encode('utf-8')

	# to save request in log file
	log_file = open("log_files/access.log", "a+")
	log_data = res_headers['Date'] + " --- " + main_req_line + " --- " + status_code + " --- " + req_headers['User-Agent'] + "\r\n"
	log_file.write(log_data)
	log_file.close()
	
	# if error found then store the info in error.log file
	error_codes = [400, 403, 404, 405, 411, 412, 500, 505]
	if status_code in error_codes :
		log_file = open("log_files/error.log", "a+")
		log_data = res_headers['Date'] + " --- " + main_req_line + " --- " + status_code + " --- " + status_codes[status_code] + "\r\n"
		print(log_data)
		log_file.write(log_data)
		log_file.close()

	# Replying to the client
	try :	
		client_socket.send(reply)
		print("reply sent")
	except :
		print("Unable to send the response.")
	client_socket.close()
	print("\n\n")


while True :
	client_socket, addr = serversocket.accept()
	print("new request received from : ")
	print(addr)
	print("client socket is : ")
	print(client_socket)
	print("\n\n")
	threading.Thread(target = client_function, args = (client_socket,)).start()
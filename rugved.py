import socket
import sys
import threading
import re
import os
import datetime
import mimetypes
import random
import string
from urllib.parse import parse_qs
import json
import base64
import pathlib

#MIMEtypes(content type), logging, config.py(for configuration file with username, password), webbrowser(For multithreading test case)
# for cookies, make a new cookie per client and when the same client makes a new request,
#  check if the cookie is present with us, and send the same cookie, don't send a different cookie to the same client. Use random library
#import webbrowser for simultaneous requests(open_new-tab funtion)
#maintain a list of running threads to check for max simultaneous connections and remove from list when closing the connection. 503 Service Unavailable for max simultaneous connections exceeded
#parse_qs: for parsing POST body: from urllib.parse import * 
#glob: In Python, the glob module is used to retrieve files/pathnames matching a specified pattern.  
 
connected_clients = []
address_family = socket.AF_INET
socket_type = socket.SOCK_STREAM
request_queue_size = 5
# set request limit length
limit_request_length = 1024

host = ''
port = 8800


class webserver():
    # Class variable
    set_cookie = True
    cookie_size = 8
    # set Max-Age to 24 hours, set it as a string so that it can be concatenated later in the set-cookie response
    cookie_max_age = '86400' #Seconds in 24 hrs

    def __init__(self, client_connection, client_address):
        self.client_connection = client_connection
        self.client_address = client_address


    def handle_request(self):
        
        # receive data from client and parse the request
        # while self.client+c
        # self.request_data = self.client_connection.recv(limit_request_length)
        # print(self.request_data)
        
        # self.request_data = b''

        # To receive bigger amount of data we use an array instead of a string, because
        # the append operation in an array is faster than '+' in a string
        fragments = []
        # receive data from client and parse the request
        while True:
            data = self.client_connection.recv(limit_request_length)
            # print(len(data))
            # self.request_data += data
            fragments.append(data)
            if len(data) < limit_request_length:
                # print("ENded")
                break
        # Here we join the array into an array
        self.request_data = b''.join(fragments)

            
        



        """
        client_connection.sendall(self.request_data)
        client_connection.close()
        return 
        """
        """ with open('request_data_store_temp.txt', 'wb') as f:
            f.write(self.request_data)
            f.close()

        self.request_data = ''
        self.byte_data = b''
        count = ''
        with open('request_data_store_temp.txt' , 'rb') as f:
            while f.read(1):
                
                f.seek(-1, 1)
                d = f.read(1)
                
                try:
                    self.request_data += d.decode('utf-8')
                    count += d
                    print('777777777777777777777777777777777')
                    if len(count) == 4 and count == 'POST':

                        check_image = True
                    
                    if check_image:
                        if 'filename="' in self.request_data:
                            print('____')
                            file = ''
                            while f.read(1).decode('utf-8') != '"':
                                f.seek(-1, 1)
                                file += f.read(1).decode('utf-8')
                            print('+++++', file)
                            f.read(3)
                            file_type = mimetypes.guess_type('file')[0].split('/')[0]
                            if file_type != 'text':
                                check_image = True
                                self.request_data += file + '"\r\n'
                                last_data = f.read()


                except:
                    self.byte_data += d
                """
        try:
            self.request_data = self.request_data.decode('utf-8')
            print("No binary data")
            # set request body to None so that it can be parsed in the parse request function if it doesn't contain binary data
            self.request_body = None
            # print(len(self.request_body))
            self.binary_data = False

        except:
            # Means it contains binary data, then we split the received data at ('\r\n\r\n', 1) i.e separate head and body
            self.request_data = self.request_data.split(b'\r\n\r\n', 1)
            self.request_body = self.request_data[1]
            self.request_data = self.request_data[0].decode('utf-8')
            print(len(self.request_body))
            self.binary_data = True

        

        self.request_binary_data = None
        print(self.request_data)
        print('----------------')
        # print(self.byte_data[-100:-50])
        # print(len(self.request_body))


        # self.request_data = self.request_data.decode('utf-8')


        # self.request_data = base64.b64encode(self.request_data)
        # print(self.request_data)
        # print("=============")
        # self.request_data = base64.b64decode(self.request_data)
        # print(self.request_data)

        # If only a connection is created, but no request is made, close the connection so that only
        # when request is to be made the next time, new connection will be made
        if len(self.request_data) == 0:
            print(self.request_data)
            self.client_connection.close()
            return


        # print(''.join(f'< {line}\n' for line in self.request_data.splitlines()))
        # print(self.request_data)



        # call parse request to get the request line
        self.parse_request()

        #call parse header to parse the request headers
        self.parse_header()

        # complete_request_body to use it later if required to find length of body etc
        self.complete_request_body = self.request_body

        """ # Check the Request Body(New)
        body = ''
        image = b''
        if binary_data and self.request_method == 'POST':
            # for i in self.request_body.split(b'\r\n\r\n'):
            # Split at the last value, considering we're submitting image as the last value only

            
            temp = self.request_body.rsplit(b'\r\n\r\n', 1)
            try:
                body += temp[0].decode('utf-8')
                
            except:
                print("Error in binary_data")
            # Binary data with last boundary is stored in image
            image += temp[1]
            # here, request_body contains all the data before the image data, with textual fields like name etc and the 
            # reqeust_binary_dadta will contain the binary data of the file like an image with the '\r\n' and last boundary which needs to be 
            # removed from the binary_data to get only the file data which can be saved in the file at path which needs to be parsed from the reqeust body
            self.request_body = body
            self.request_binary_data = image
            print('@@@@@')
            print(self.request_body)
            print('@@@@@') """
            




        # Check for the HTTP version to be 1.1
        if self.request_version != "HTTP/1.1":
            #505 HTTP Version not supported
            self.status = "505 HTTP Version Not Supported"

        #Respond according to the request_method
        if self.request_method == "GET":
            self.GET_response()

        elif self.request_method == "POST":
            self.POST_response()

        elif self.request_method == "HEAD":
            self.HEAD_response()

        elif self.request_method == "PUT":
            self.PUT_response()

        elif self.request_method == "DELETE": 
            self.DELETE_response()

        else:
            #400 Bad request
            pass
       
    def parse_request(self):

        '''
        split the request at newline. Eg of request: 
        GET /hello.html HTTP/1.1
        User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
        Host: www.tutorialspoint.com
        Accept-Language: en-us
        Accept-Encoding: gzip, deflate
        Connection: Keep-Alive

        request_body
        '''
        # split at '\r\n\r\n' to seperate body and headers if it doesn't contain binary data
        if self.request_body is None:
            request = self.request_data.split('\r\n\r\n', 1)
            try:
                # storing request body. If request body is absent, exception will occur
                self.request_body = request[1]
                print('No Binary body data, but with body')
            except:
                print("No body")
            finally:
                # storing the request_data in an array
                self.request_array = request[0].splitlines()

        # If there is binary data in the reqeust, then the request_data holds the header data and reqeust_body already holds the body data
        else:
            # storing the request_data in an array
            self.request_array = self.request_data.splitlines()
        # print(request)
    
        
        

        """ 
        # storing the request_data in an array
        self.request_array = self.request_data.splitlines()

        # Remove the "\r\n" line which is present after the request header and before the 
        # request body. After splitlines is used that line just becomes '' i.e empty string
        i = self.request_array.index('')
        #removes the first occurance of '' which is the '\r\n' between request header and request body
        self.request_array.remove('')

        #For POST:
        if len(self.request_array) > i:
            #request_body is an array/list eg. If the request body contains only 1 line 
            # as in case ofapplication/x-www-form-urlencoded body = ['field1=value1&field2=value2']
            # or in case of multipart/form-data body = [[4lines field1=value1], [4 lines field2=value2]]
            self.request_body = self.request_array[i:]
            
            # To clear the elements in the list after the index i as the elements 
            # after i have been copied at ith position
            for j in range(len(self.request_array)-1, i-1, -1):
                self.request_array.pop(j)

            # Getting rid of " that are present around name and filename in the content-type multipart/form-data
            # temp = []
            # for k in self.request_body:
            #     temp.append(k.replace('"', ''))

            # self.request_body = temp

            request_body_string = ""
            for k in self.request_body:
                request_body_string += k + '\r\n'

            self.request_body = request_body_string = request_body_string.rstrip().lstrip()

            print(self. request_body)
        """


        #get the request line which is the first line in request
        request_line = self.request_array[0].rstrip('\r\n')
        
        #Break down the request line into components
        (self.request_method,       #GET
        self.path,                  #/path
        self.request_version        #HTTP/1.1
        ) = request_line.split(" ")

        # Add Current working directory path
        self.parse_request_path()
        self.path = os.getcwd() + self.path


    def parse_header(self):
        # Forming a dictionary of the request header fields and storing it in self.header
        self.header = [
            element.rstrip("\r\n").split(": ") for element in self.request_array[1:]
        ]
        # Make self.header a dictionary of header fields present in request header without 
        # the request line(1st) and the request body
        self.header = {
            key: value for key, value in self.header
        }
        """ 
        print(''.join(
            f'{key}: {value}\n' for key, value in self.header.items()
        )) 
        """


    def check_path(self):
        #check if path exists
        if not os.path.exists(self.path):
            # For POST request if the file doesn't exist, then make a new file and 
            # return status as 201 Created with the file location as the response body
            if self.request_method in ['POST', 'PUT']:
                # First check if a file name is present at the end of the path
                basename = os.path.basename(self.path)
                if len(basename) > 0:
                    # Now check if the path without the filename exists
                    if os.path.exists(os.path.dirname(self.path)):
                        # Also check if the file is a .json file
                        try:
                            f = basename.split('.')[1]
                            # For POST
                            if f == 'json' and self.request_method == 'POST':
                                self.post_file_data = open(self.path, 'w')
                                self.status = "201 Created"
                                self.file_data = b"File created successfully"
                                return
                            # For PUT no need to check file type, only check if there is a file and open the file in write+binary
                            if f and self.request_method == 'PUT':
                                self.put_file_data = open(self.path, 'wb')
                                self.status = "201 Created"
                                # For PUT there should not be any response body
                                self.file_data = b'File Created Successfully'
                                return

                        except:
                            pass

                            

            #404 Not Found
            self.status = "404 Not Found"
            self.file_data = b'404 Not Found. Path does not exist'
            return

        if os.path.isfile(self.path):
            #send the file data
            if self.request_method in ("GET", "HEAD"):
                if os.access(self.path, os.R_OK):
                    self.file_data = open(self.path, 'rb')
                    self.file_data = self.file_data.read()
                    self.status = "200 OK"
                    return

            elif self.request_method in ("POST"):
                basename = os.path.basename(self.path)
                f = basename.split('.')[1]
                if f == 'json':
                    if os.access(self.path, os.W_OK):
                        self.post_file_data = open(self.path, 'a')
                        self.status = "200 OK"
                        self.file_data = b"Data stored successfully"
                        return

            elif self.request_method == 'PUT':
                if os.access(self.path, os.W_OK):
                    self.put_file_data = open(self.path, 'wb')
                    self.status = "200 OK"
                    self.file_data = b"File written successfully"
                    return


                
                    
            #Give error 403 Forbidden as the read/write permission is not available
            self.status = "403 Forbidden"
            self.file_data = b'403 Forbidden'
            return

        elif os.path.isdir(self.path):

            if self.request_method in ("POST", 'PUT'):
                # Check if this is okay. This is done because if a dir location is given
                # then we can't open a file
                self.status = "403 Forbidden"
                self.file_data = b'403 Forbidden'
                return

            #send the index.html file if exists, else send error 404
            if not os.path.exists(self.path + 'index.html'):
                #send error 404
                self.status = "404 Not Found"
                self.file_data = b'404 Not Found. File Not Found'
                return

            else:
                #send the file index.html
                self.path += 'index.html'
                if self.request_method in ("GET", "HEAD"):
                    if os.access(self.path, os.R_OK):
                        """ 
                        print("---------file found----------")
                        print(self.path)
                        """
                        self.file_data = open(self.path, 'rb')
                        self.file_data = self.file_data.read()
                        self.status = "200 OK"
                        return
                    #Give error 403 Forbidden as the read permission is not available
                    self.status = "403 Forbidden"
                    self.file_data = b'403 Forbidden'
                    return

    def check_headers(self):

        # First need to check if the file is present and access is also available, to prevent errors while accessing file path(eg.Accept, ifs)
        if self.status not in ("404 Not Found", "403 Forbidden"):
            
            # ACCEPT: Check if the specific media type (eg. video/mp4) or all okay(*/*) or only primary type defined and present (eg. video/*)
            if 'Accept' in self.header and self.request_method in ['GET', 'HEAD', 'PUT']:
                #check the header conditions present in the request header like if modified, accept etc.
                content_type = mimetypes.guess_type(self.path)
                self.accept()
                if content_type not in self.accepted_media_types and '*/*' not in self.accepted_media_types and content_type.split('/')[0] + '/*' not in self.accepted_media_types:
                    self.status = "406 Not Acceptable" 
                    self.file_data = b"406 Not Acceptable"
            #HOST: If no host header is present respond with 400 (Bad Request)
            # if 'Host' in self.header:
            self.host()
            if self.host is None:
                self.status = "400 Bad Request"
                self.file_data = b"400 Bad Request. Host header not included"
            

            if self.request_method in ['GET', 'HEAD'] and not self.query:
                #IF-MODIFIED-SINCE: If the file has been modified after the time specified in the request, then send continue with the regular request.
                # else if the file has not been modified, then send 304 NOT MODIFIED also, if the date given in the request is invalid(date format may be wrong 
                # or the date may be later than servers current time), continue with regular GET
            
                last_modified = os.path.getmtime(self.path)
                # last_modified = datetime.datetime.fromtimestamp(last_modified, datetime.timezone.utc)
                last_modified = datetime.datetime.fromtimestamp(last_modified, datetime.timezone.utc).replace(microsecond=0 ,tzinfo=None)

                if 'If-Modified-Since' in self.header:
                    self.if_modified_since()
                    if self.if_modified_since_time >= last_modified:
                        self.status = "304 Not Modified"
                        # The 304 response MUST NOT contain a message-body, and thus is always 
                        # terminated by the first empty line after the header fields. 
                        self.file_data = None
                # IF-UNMODIFIED-SINCE: If the file has not been modified since the date given, then continue with the regular GET. 
                # but if the file has been modified, then send 412 Precondition Failed. Also if the initial status is not 2XX ignore this header
                # Also incase other IFs conditional GETs are used, then this is not defined
                if 'If-Unmodified-Since' in self.header:
                    self.if_unmodified_since()
                    if self.status == "200 OK" and self.if_unmodified_since_time < last_modified:
                        self.status = "412 Precondition Failed"
                        # The 412 response must send the error
                        self.file_data = b"412 Precondition Failed. Error in If-Modified-Sincse"

            if 'Cookie' in self.header:
                self.cookie()
            

            # For POST and PUT Header:-
            if 'Content-Type' in self.header:
                self.get_content_type()
                
                print("*****", self.request_content_type)
                if  'multipart/form-data' in self.request_content_type and self.request_method == 'POST':
                    # Content-Type: multipart/form-data; boundary=12345
                    self.request_content_type =  self.request_content_type.split('; boundary=')
                    self.post_boundary = self.request_content_type[1]
                    # Actual post_boundary
                    self.post_boundary = '--' + self.post_boundary
                    self.request_content_type = self.request_content_type[0]
                    print("*****", self.post_boundary)
                    

        
        
    # Parse the request body for POST(for now) and maybe PUT
    def parse_request_body(self):
        if self.status in ['200 OK', '201 Created']:
            if self.request_content_type == 'application/x-www-form-urlencoded':

                # Check the content-length as well\
                # If a request contains a message-body and a Content-Length is not given,
                # the server SHOULD respond with 400 (bad request) if it cannot
                # determine the length of the message, or with 411 (length required) if
                # it wishes to insist on receiving a valid Content-Length.
                if 'Content-Length' not in self.header:
                    self.status = '411 Length Required'
                    self.body = "Content-Length header is missing in the request"
                    return
                else:
                    content_length = self.header['Content-Length']
                    if int(content_length) != len(self.complete_request_body):
                        self.status = '400 Bad Request'
                        self.body = "Content-Length header is present in the request, but does not match the real content length"
                        return

                self.request_body = self.request_body.rstrip().lstrip()
                # Converts the request body into a dictionary of name:value type
                self.request_body_dict = parse_qs(self.request_body)

                print(self.request_body_dict)
                # Write/append the request_body_data into the post_file_data which is a json file
                if self.post_file_data.mode == 'w':
                    s = []
                    s.append(self.request_body_dict)
                    json.dump(s, self.post_file_data)
                elif self.post_file_data.mode == 'a':
                    with open(self.path, 'r') as f:
                        s = json.load(f)
                    
                    s.append(self.request_body_dict)
                    self.post_file_data.close()
                    self.post_file_data = open(self.path, 'w')
                    json.dump(s, self.post_file_data)


                # json.dump(self.request_body_dict, self.post_file_data)
                self.post_file_data.close()




            elif self.request_content_type == 'multipart/form-data':
                # print(f"----{self.content_type}----")
                """Example: Here 
                --boundary 
                Content-Disposition: form-data; name="field1" 

                value1 
                --boundary 
                Content-Disposition: form-data; name="field2"; filename="example.txt"
                Content-Type: text/plain

                value2
                --boundary--"""
                # Check the content-length as well\
                # If a request contains a message-body and a Content-Length is not given,
                # the server SHOULD respond with 400 (bad request) if it cannot
                # determine the length of the message, or with 411 (length required) if
                # it wishes to insist on receiving a valid Content-Length.
                if 'Content-Length' not in self.header:
                    self.status = '411 Length Required'
                    self.body = "Content-Length header is missing in the request"
                    return
                else:
                    content_length = self.header['Content-Length']
                    # Calculate the content length
                    l = len(self.complete_request_body)
                    print("++++++++", l)
                    # print(self.request_body)
                    if int(content_length) != l:
                        self.status = '400 Bad Request'
                        self.body = "Content-Length header is present in the request, but does not match the real content length"
                        return




                # Check the Request Body(New)
                body = ''
                image = b''
                if self.binary_data and self.request_method == 'POST':
                    self.request_body_dict = {}
                    b = self.post_boundary + '\r\n'
                    b = b.encode('utf-8')
                    self.request_body = self.request_body.split(b)
                    for i in self.request_body:
                        if len(i) == 0:
                            #to skip '' which can be a entry as well in the list
                            continue
                        t = '\r\n' + self.post_boundary + '--'
                        t = t.encode('utf-8')
                        if t in i:
                            i.replace(t, b'')

                        v = i.split(b'\r\n\r\n')
                        if len(v) > 1:
                            value = v[1].lstrip().rstrip()
                            # print("-> ", value) 

                        i = v[0].decode('utf-8')
                        i = i.splitlines()
                        name = i[0]
                        pattern = "\"(.*?)\""
                        names_list = re.findall(pattern, name)
                        name = names_list[0]
                        print(name, type(name))

                        if len(names_list) > 1:
                            print("+++++Inside Saving File+++++")
                            file_name = names_list[1]
                            name = names_list[0]
                            # print(file_name, name)
                            # print(value)

                            # Create a file with the name given in the file_name and write the data
                            # in the file. Create the file in the POST_data folder
                            with open("POST_data/" + file_name, 'wb') as file_to_write:
                                # if self.request_binary_data:
                                    # t = '\r\n' + self.post_boundary + '--'
                                    # t = t.encode('utf-8')
                                # self.request_binary_data.replace(t, b'')
                                file_to_write.write(value)
                                # else:
                                #     file_to_write.write(value.encode('utf-8'))

                            # Store the path of the file as the value in the JSON file
                            value = "POST_data/" + file_name
                            print("-> -> ->", value)
                        else:
                            value = value.decode('utf-8')

                            
                        self.request_body_dict[name] = value
                        print("->", value)

                    print(f"+++++{self.request_body_dict}+++++")
                    # Write/append the request_body_data into the post_file_data which is a json file
                    if self.post_file_data.mode == 'w':
                        s = []
                        s.append(self.request_body_dict)
                        json.dump(s, self.post_file_data)
                    elif self.post_file_data.mode == 'a':
                        with open(self.path, 'r') as f:
                            s = json.load(f)
                        
                        s.append(self.request_body_dict)
                        # self.post_file_data.close()
                        self.post_file_data = open(self.path, 'w')
                        print(s)
                        json.dump(s, self.post_file_data)
                        
                    # json.dump(self.request_body_dict, self.post_file_data)
                    self.post_file_data.close()
                    return

                        
                    
                    







                    """ # for i in self.request_body.split(b'\r\n\r\n'):
                    # Split at the last value, considering we're submitting image as the last value only

                    
                    temp = self.request_body.rsplit(b'\r\n\r\n', 1)
                    try:
                        body += temp[0].decode('utf-8')
                        
                    except:
                        print("Error in binary_data")
                    # Binary data with last boundary is stored in image
                    image += temp[1]
                    # here, request_body contains all the data before the image data, with textual fields like name etc and the 
                    # reqeust_binary_dadta will contain the binary data of the file like an image with the '\r\n' and last boundary which needs to be 
                    # removed from the binary_data to get only the file data which can be saved in the file at path which needs to be parsed from the reqeust body
                    self.request_body = body
                    self.request_binary_data = image
                    print('@@@@@')
                    print(self.request_body)
                    print('@@@@@') """







                # what i think is, save name: value fields in the data dic
                # until a filename field is encountered and when a filename is 
                # found, write all the data stored in the data dict into the file
                # and clear the dict

                # Here, if the data is just form data, then it contains a name and value only, 
                # which can be added to the dictionary. But if it contains a file, like text or jpg,
                # it also contains a filename which is the filename of the uploaded file and may also contain
                # Content-Type field in the next line of name

                self.request_body = self.request_body.rstrip().lstrip()
                
                self.request_body_dict = {}
                self.request_body = self.request_body.split(self.post_boundary + '\r\n')
                
                # print(self.request_body)
                for i in self.request_body:
                    if len(i) == 0:
                        #to skip '' which can be a entry as well in the list
                        continue
                        
                    # for the last entry, may contain extra boundary
                    if self.post_boundary + '--' in i:
                        i = i.replace('\r\n' + self.post_boundary + '--', '')
                    # if self.post_boundary in i:
                    #     i = i.replace('\r\n' + self.post_boundary, '')
                    
                    v = i.split('\r\n\r\n')
                    if len(v) > 1:
                        value = v[1].lstrip().rstrip()
                        print("-> ", value)

                    i = v[0]
                    i = i.splitlines()
                    name = i[0]
                    pattern = "\"(.*?)\""
                    names_list = re.findall(pattern, name)
                    name = names_list[0]

                    if len(names_list) > 1:
                        print("+++++Inside Saving File+++++")
                        file_name = names_list[1]
                        name = names_list[0]
                        # print(file_name, name)
                        # print(value)

                        # Create a file with the name given in the file_name and write the data
                        # in the file. Create the file in the POST_data folder
                        with open("POST_data/" + file_name, 'wb') as file_to_write:
                            if self.request_binary_data:
                                t = '\r\n' + self.post_boundary + '--'
                                t = t.encode('utf-8')
                                self.request_binary_data.replace(t, b'')
                                file_to_write.write(self.request_binary_data)
                            else:
                                file_to_write.write(value.encode('utf-8'))

                        # Store the path of the file as the value in the JSON file
                        value = "POST_data/" + file_name
                        print("-> -> ->", value)
                        
                    self.request_body_dict[name] = value

                print(f"+++++{self.request_body_dict}+++++")
                # Write/append the request_body_data into the post_file_data which is a json file
                if self.post_file_data.mode == 'w':
                    s = []
                    s.append(self.request_body_dict)
                    json.dump(s, self.post_file_data)
                elif self.post_file_data.mode == 'a':
                    with open(self.path, 'r') as f:
                        s = json.load(f)
                    
                    s.append(self.request_body_dict)
                    self.post_file_data.close()
                    self.post_file_data = open(self.path, 'w')
                    json.dump(s, self.post_file_data)
                    
                # json.dump(self.request_body_dict, self.post_file_data)
                self.post_file_data.close()


                """ 
                data = {}
                for i in range(0, len(self.request_body)-1, 4):
                    name = self.request_body[i+1].split(' name=')
                    name = name[1].split('; filename=   ')
                    value = self.request_body[i+3]
                    data[name[0]] = value


                # After parsing, name[0] will be the name, name[1](if present) will be the filename in what to write
                # and value will be the value for the name which is to be actually written
                    if len(name) > 1:
                        print(name, value)
                        # Open the file with the name in the field name[1]
                        file = open(name[1], 'ab')
                        # Using ';' as the delimiter
                        values_to_write = ';'.join(i for i in data.values())
                        file.write(values_to_write)
                        file.close()
                        data.clear() """

                        
                
            


        

        
       


        
    # Get the response head to send with the response
    def start_response(self):
        self.current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %X GMT")
        self.server_response_header = [('Date', self.current_time)]
        self.server_version = "111803084/1.0 (Linux)"
        self.server_response_header.append(('Server', self.server_version))
        self.connection = 'close'
        self.server_response_header.append(('Connection', self.connection))

        if self.status in ["200 OK", "201 Created"]:

            if self.request_method in ['GET', 'HEAD'] and not self.query:
                #check the self.path here. It might not be file path, it may be a directory or something, or maybe we need to specify index.html file path
                self.last_modified = os.path.getmtime(self.path)
                self.last_modified = datetime.datetime.fromtimestamp(self.last_modified, datetime.timezone.utc).strftime("%a, %d %b %Y %X GMT")
                self.server_response_header.append(('Last-Modified', self.last_modified))
                #check the self.path here too. Check above comment
                self.content_length = os.path.getsize(self.path)
                self.server_response_header.append(('Content-Length', self.content_length))
                #content type to be given and other headers to be added
                self.content_type = mimetypes.guess_type(self.path)[0]
                self.content_type += '; charset=UTF-8'
                self.server_response_header.append(('Content-Type', self.content_type))

            elif self.request_method in ['POST']:
                self.content_length = len(self.file_data) 
                self.server_response_header.append(('Content-Length', self.content_length))

                self.content_type = 'text/plain' + '; charseet=UTF-8'
                self.server_response_header.append(('Content-Type', self.content_type))

            # If self.set_cookie is True, then either the client has connected for the first time or the cookie has expired
            if self.set_cookie:
                self.set_cookie_value = 'cookie_id=' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(self.cookie_size)) + '; ' + 'Max-Age=' + self.cookie_max_age
                self.server_response_header.append(('Set-Cookie', self.set_cookie_value))
        
        else:
            self.server_response_header = [
                ('Date', self.current_time), 
                ('Server', self.server_version),
                ('Connection', self.connection)
            ]

        
    # Collect all the data and send it to the client
    def finish_response(self):
        try:
            response = f'HTTP/1.1 {self.status}\r\n'
            for header in self.server_response_header:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            # response = b''.join((response, self.file_data))
            # response += self.file_data

            #print formatted response data
            print(''.join(
                f'> {line}\n' for line in response.splitlines()
            ))
            
            response_bytes = response.encode()

            if self.file_data:
                response_bytes += self.file_data
            self.client_connection.send(response_bytes)
            # if self.status == "200 OK":
            print(self.file_data)
            #Do not send file date for HEAD request
            # if self.request_method != 'HEAD' and self.file_data is not None:
            #     self.client_connection.send(self.file_data)

        finally:
            self.client_connection.close()



    def parse_request_path(self):
        p = 'http://localhost:' + str(port)
        if p in self.path:
            self.path = self.path.replace(p, '')
            print(self.path)

        s = self.path.split('?')
        self.path = s[0]
        if len(s) > 1:
            self.query = parse_qs(s[1])
        else:
            self.query = None
        # print(self.query)
        
        

    def accept(self):
        try:
            accept = self.header['Accept']
            # Use RegEx to split the media types without condidering q values
            pattern = ';q=\d\.\d,|;q=\d,|;q=\d\.\d|;q=\d'
            accept = re.split(pattern, accept)
            accept = [i.split(',') for i in accept if len(i) > 0]
            self.accepted_media_types = []
            for i in accept:
                for j in i:
                    self.accepted_media_types.append(j)
            # print("In Accept")
            return
        except:
            return

    def host(self):
        try:
            self.host = self.header['Host'] 
        except:
            self.host = None

    def if_modified_since(self):
        time = self.header['If-Modified-Since']
        try:
            self.if_modified_since_time = datetime.datetime.strptime(time, "%a, %d %b %Y %X %Z")
        except:
            self.if_modified_since_time = None

    def if_unmodified_since(self):
        time = self.header['If-Unmodified-Since']
        try:
            self.if_unmodified_since_time = datetime.datetime.strptime(time, "%a, %d %b %Y %X %Z")
        except:
            self.if_unmodified_since_time = None

    def cookie(self):
        try:
            cookie = self.header['Cookie']
            # set Max-Age to 24 hours: Not using this to update the cookie expiry for now.
            self.cookie_max_age = '3576' #24 Hrs in secs
            self.set_cookie = False

        except:
            self.set_cookie = True
        
    # For POST
    def get_content_type(self):
        try:
            self.request_content_type = self.header['Content-Type']
        except:
            if self.request_method == 'POST':
                self.request_content_type = "application/x-www-form-urlencoded"
            if self.request_method == 'PUT':
                self.request_content_type = None
            










    def GET_response(self):
        # Check the path first
        self.check_path()
        # Check the request headers
        self.check_headers()
        # Make the response header
        self.start_response()

        # Check if the GET is query GET and check if the file is .json
        print(self.query, pathlib.Path(self.path).suffix)
        if self.query and self.status == '200 OK':
            if pathlib.Path(self.path).suffix == '.json':
                with open(self.path, 'r') as f:
                    data = json.load(f)
                    self.file_data = []
                    for d in data:
                        # s is T/F if the query is a subset of the dictionary
                        s = all(item in d.items() for item in self.query.items())
                        if s:
                            self.file_data.append(d)
                        
                # Dumps converts the python list to a json string which needs to encoded before final_response
                self.file_data = json.dumps(self.file_data).encode('utf-8')
                self.content_length = len(self.file_data) 
                self.server_response_header.append(('Content-Length', self.content_length))
                print("=+=+=+=+")
                print(self.file_data)

                self.content_type = 'application/json' + '; charseet=UTF-8'
                self.server_response_header.append(('Content-Type', self.content_type))

        # Finish Response
        self.finish_response()
        return

    def HEAD_response(self):
        #Same as GET, just do not send the message body with the response
        # Check the path first
        self.check_path()
        # Check the request headers
        self.check_headers()
        # Make the response header
        self.start_response()
        # Finish Response
        self.finish_response()
        return

    def POST_response(self):
        # First check the path in URI. If its a form submission and the file is not present on the server
        # create the file and send 201 created response along with the file path in the response body.
        # If the file is present, then first chech the file permissions and then open the file in append form and then
        # write the parsed data received through the body of POST request
        # Check the path first
        self.check_path()
        # # Check the request headers
        self.check_headers()
        


        # # Work on the request_body
        self.parse_request_body()

        #start response
        self.start_response()
        # finish response
        self.finish_response()


    def PUT_response(self):
        # Similar to POST, only instead of appending to the file, we write(200 Ok) into the file at the location
        # provided in the uri. If the uri does not exist, then check if that uri can represent a file, and if so 
        # then create the file(201 Created)
        self.check_path()
        self.check_headers()

        try:
            content_length = self.header['Content-Length']
        except:
            pass


        if self.request_content_type is None:
            self.status = '400 Bad Request'
            self.file_data = b'400 Bad Request. Content type not provided'
        else:
            c = mimetypes.guess_type(self.path)[0]
            print("Content type")
            print(c, self.request_content_type)
            print("type of content")
            print(type(c), type(self.request_content_type))
            if c != self.request_content_type:
                self.status = '400 Bad Request'
                self.file_data = b'400 Bad Request. Content type not correct'


            elif 'Content-Length' not in self.header:
                    self.status = '411 Length Required'
                    self.file_data = b"Content-Length header is missing in the request"
                    
            if int(content_length) != len(self.complete_request_body):
                self.status = '400 Bad Request'
                self.file_data = b"Content-Length header is present in the request, but does not match the real content length"

            else:
                print("In PUT else")
                # print(len(self.request_body))
                self.put_file_data.write(self.request_body)
                self.put_file_data.close()
        self.start_response()
        self.finish_response()












#first called funtion to get requests from clients by making a server object
def make_server(client_connection, client_address):

    server = webserver(client_connection, client_address)
    server.handle_request()
    return


if __name__ == "__main__":

    print("Server is running:")

    #make a socket instance and pass 2 parameters. AF_NET: ipv4 family and SOCK_STREAM: TCP Protocol
    try: 
        s = socket.socket(address_family, socket_type)
        print("Socket Created Succesfully")

    except socket.error:
        print("Socket creation failed due to error", socket.error)

    

    s.bind((host, port))
    print("Socket binded to port: ", port)

    #Socket in listening mode
    s.listen(request_queue_size)
    print("Socket is listening")

    #Infinite loop to accept requests

    #ADD start, stop and close flags
    while True:
        #establish a connection with one client at a time
        client_connection, client_address = s.accept()

        #store the client info in the array connected_clients
        connected_clients.append(client_connection)

        print("Connected to: ", client_address)

        #Make a thread per client
        threading.Thread(target=make_server, args=(client_connection, client_address, )).start()

    s.close()


        

    
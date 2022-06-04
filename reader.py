#!/usr/bin/env python3
import socket
import os
import sys
import signal
import re

def searchfile(file_name, searched_text):
    try:
        with open('data/'+file_name) as currfile:
            lines=currfile.readlines()
            print(lines)
            res = [i for i in lines if searched_text in i]
            return res
    except OSError:
            return []
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',9999))
s.listen(5)
signal.signal(signal.SIGCHLD,signal.SIG_IGN)
metody={'READ\n','LS\n','LENGTH\n','SEARCH\n','SELECT\n'}
readfun={'File','To','From'}
selectfun={'File','String'}
rangefrom=rangeto=-1
filename='/'
count=0
status_num,status_comm=(100, 'OK')
while True:
    connected_socket,client_address=s.accept()
    pid_chld=os.fork()
    if pid_chld==0:
        s.close()
        f=connected_socket.makefile(mode='rw',encoding='utf-8')
        while True:
            rangefrom=rangeto=-1
            bs=f.readline()
            if not bs:
                status_num,status_comm=(200, 'Bad request')
            if bs in metody:
            	if bs=='READ\n':
            	    while True:
                        req=f.readline()
                        head=req.split(':')
                        if len(head)==2 and head[0] in readfun:
                            if head[0]=='File':
                                if '/' not in head[1]:
                                    filename=head[1]
                                    filename=filename[:-1]
                                else:
                                    status_num,status_comm=(200, 'Bad request')
                            if head[0]=='From':
                                try:
                                    rangefrom=int(head[1])
                                except ValueError:
                                    status_num,status_comm=(200, 'Bad request')
                                    break
                                if int(head[1]) < -1:
                                    status_num,status_comm=(200, 'Bad request')
                                    break
                            if head[0]=='To':
                                try:
                                    rangeto=int(head[1])
                                except ValueError:
                                    status_num,status_comm=(200, 'Bad request')
                                    break
                                if int(head[1]) < -1:
                                    status_num,status_comm=(200, 'Bad request')
                                    break
                        f.flush()
                        if rangefrom > -1 and rangeto > -1 and filename != '/':
                            if rangefrom <= rangeto:
                                try:
                                    with open('data/'+filename) as my_file:
                                        lines=my_file.readlines()
                                    count=len(lines)
                                except FileNotFoundError:
                                    status_num,status_comm=(202, 'No such file')
                                    break
                                except OSError:
                                    status_num,status_comm=(203, 'Read error')
                                    break
                                if rangeto > count:
                                    status_num,status_comm=(201, 'Bad line number')
                                    break
                                else:
                                    status_num,status_comm=(100, 'OK')
                                    f.write('100 OK\nLines:'+str(rangeto-rangefrom)+'\n\n')
                                    try:
                                        for i in range(rangefrom, rangeto):
                                            text=lines[i]
                                            text=text[:-1]
                                            f.write(text+'\n')
                                    except OSError:
                                        status_num,status_comm=(203, 'Read error')
                                        break
                                    f.flush()
                                break
                                f.flush()
                            else:
                                status_num,status_comm=(200, 'Bad request')
                                break
            	elif bs=='LS\n':
            	    f.write(str(status_num)+' '+status_comm+'\n')
            	    fileList=os.listdir('data')
            	    f.write('Lines:'+str(len(fileList))+'\n'+'\n')
            	    status_num,status_comm=(100, 'OK')
            	    for i in fileList:
            	    	f.write(i+'\n')
            	    f.flush()
            	elif bs=='LENGTH\n':
            	    req=f.readline()
            	    head=req.split(':')
            	    if len(head)==2 and head[0]=='File':
            	        if '/' not in head[1]:
            	            filename=head[1][:-1]
            	        else:
            	            status_num,status_comm=(200, 'Bad request')
            	        try:
            	            with open('data/'+filename) as my_file:
            	                lines=my_file.readlines()
            	                count=len(lines)
            	                status_num,status_comm=(100, 'OK')
            	                f.write(str(status_num)+' '+status_comm+'\n')
            	                f.write('Lines: 1'+'\n\n'+str(len(lines))+'\n')
            	                f.flush()
            	        except FileNotFoundError:
            	            status_num,status_comm=(202, 'No such file')
            	        except OSError:
            	            status_num,status_comm=(203, 'Read Error')
            	    else:
            	        status_num,status_comm=(200, 'Bad request')
            	elif bs=='SEARCH\n':
            	    rawstr=f.readline()
            	    head=rawstr.split(':')
            	    files_list=''
            	    count_lists=0
            	    if len(head)==2 and head[0]=='String' and head[1].startswith('"') and head[1].endswith('"\n'):
            	        fileList=os.listdir('data')
            	        for i in fileList:
            	            listOfOcurr=searchfile(i,head[1][1:-2])
            	            if listOfOcurr:
            	            	files_list+=i+'\n'
            	            	count_lists+=1
            	        print(files_list)
            	        status_num,status_comm=(100, 'OK')
            	        f.write('100 OK\nLines: '+str(count_lists)+'\n\n'+files_list)
            	    else:
            	    	status_num,status_comm=(200, 'Bad request')
            	    f.flush()
            	elif bs=='SELECT\n':
            	    selected_file=selected_text='/'
            	    while True:
            	        print(selected_file+'+'+selected_text+'!')
            	        rawstr=f.readline()
            	        head=rawstr.split(':')
            	        if len(head)==2 and head[0] in selectfun:
            	            if head[0]=='File':
            	                if '/' not in head[1]:
            	                    selected_file=head[1][:-1]
            	                else:
            	                    status_num,status_comm=(200, 'Bad request')
            	            else:
            	                if head[1].startswith('"') and head[1].endswith('"\n'):
            	                    selected_text=head[1][1:-2]
            	                else:
            	                    status_num,status_comm=(200, 'Bad request')
            	        else:
            	            status_num,status_comm=(200, 'Bad request')
            	            break
            	        if '/' not in selected_file and '/' not in selected_text:
            	            try:
            	                with open('data/'+selected_file) as currfile:
            	                    l=currfile.readlines()
            	            except FileNotFoundError:
            	                status_num,status_comm=(202, 'No such file')
            	                break
            	            except OSError:
            	                status_num,status_comm=(203, 'Read error')
            	                break
            	            listOfOcurr=searchfile(selected_file, selected_text)
            	            sizeofOcurr=len(listOfOcurr)
            	            listConv=''.join(listOfOcurr)
            	            status_num,status_comm=(100, 'OK')
            	            f.flush()
            	            f.write('100 OK\nLines: '+str(sizeofOcurr)+'\n\n'+listConv)
            	            f.flush()
            	            break
            	        f.flush()
            	else:
            	    status_num,status_comm=(204, 'Unknown method')
            	    break
            else:
            	count=0
            if status_num != 100:
                f.write(str(status_num)+' '+status_comm+'\n\n')
                f.flush()
                connected_socket.close()
                continue
        sys.exit(0)
    else:
        connected_socket.close()



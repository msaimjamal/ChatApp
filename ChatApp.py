from socket import *
import threading
import sys

import time

userList = []
client_userList = []

#these commands are allowed to client in single-chat mode
allowed_cmds = ["send", "userlist", "dereg", "create_group", "list_groups", "join_group"]

#these commands are allowed to client in group-chat mode
group_allowed_cmds = ["send_group", "list_members", "leave_group", "dereg"]

#client direct message acknowledgement
c_msg_ack = 0

#client group message ack received
c_g_msg_ack = 0

#deregistration acknowledgement to allow thread to exit
dereg_quit = 0

#to check if client has received register acknowledgement
registered = 0

#if received ack from server to join group
join_group_ack = 0

leave_group_ack = 0

#this is the list of groups for server use
groupList = []

#this is the group that the client is currently in
client_Group = ""

message_buffer = ""


class MyUser:
    def __init__(self, name, client_address, status):
        self.name = name
        self.client_address = client_address
        self.status = status

class MyGroup:
    def __init__(self, name):
        self.name = name
        self.users = []
    def add(self, userName):
        self.users.append(userName)

#def serverRespond(server_socket, target_addr, target_port):

    #ack = "ack\nThis is an ack from server"
    #server_socket.sendto(ack.encode(), (target_addr, target_port))
    #print(">>>[Sent the ack.]\n")
    #print("I have received.")

def clientListen(port, client_socket):
    print(">>>[Client now listening.]")
    # listen_socket = socket(AF_INET, SOCK_DGRAM)
    # listen_socket.bind(('', port))
    while True:
        # buf, sender_address = listen_socket.recvfrom(4096)
        buf, sender_address = client_socket.recvfrom(4096)
        buf = buf.decode()  # always need to encode/decode messages according to my protocol
        lines = buf.splitlines()
        header = lines[0]

        if header == "[Client table updated.]":
            global client_userList
            client_userList = lines[1:]
            print(buf)
            #print("\n>>>", end=" ")
        if header == "[Group table updated.]":

            print(">>>[Group " + lines[1] + " created by Server.]")
            print("\n>>>", end=" ")
        if header == "welcome":
            print(lines[1])
            global registered
            registered = 1
        if header == "ack":
            print(lines[1])
            #print("\n>>>", end=" ")
        if header == "msg":
            #if client_Group != "":
            if lines[2] != None:
                print("\n>>>" + lines[1] + ": " + lines[2])
            else:
                print("\n>>>" + lines[1] + ": ")
            print("\n>>>", end=" ")
            #else:
            #    global message_buffer
            #    if lines[2] != None:
            #        message_buffer = message_buffer + lines[1] + ": " + lines[2] + "\n"
            client_socket.sendto("msg_ack".encode(), sender_address)
        if header == "dereg_ack":
            print("\n>>>[You are offline. Bye.]")
            global dereg_quit
            dereg_quit = 1
            exit()
        if header == "msg_ack":
            global c_msg_ack
            c_msg_ack = 1
        if header == "grouplist":
            print(">>>[Available group chats:]")
            print(lines[1:])
            print("\n>>>", end=" ")
        if header == "join_group_ack":
            global join_group_ack
            join_group_ack = 1
        if header == "members":
            print("\n>>>(" + client_Group + ") [Group Members:]")
            print(lines[1])
            print("\n>>>(" + client_Group + ")", end=" ")
        if header == "server_group_message_ack":
            global c_g_msg_ack
            c_g_msg_ack = 1
        if header == "group_msg":
            print("\n" + lines[1])
            print("\n>>>", end= " ")
        if header == "leave_ack":
            global leave_group_ack
            leave_group_ack = 1

    #implement multithread clientrespond


def serverMode(port):
    server_socket = socket(AF_INET, SOCK_DGRAM)
    # note that bind takes a tuple, and empty string for IP address. Could also pass in 'localhost' for IP
    server_socket.bind(('', port))
    print(">>>[Server is online.]")

    while True:
        # buffer contains the datastream, client_address is a tuple of (ip_addr, port)
        # the port won't be the actual listening port
        # print("server is listening")
        buffer, client_address = server_socket.recvfrom(4096)
        print(">>>[The client address is:", client_address)

        #blueprint for decoding my protocol
        buffer = buffer.decode() # always need to encode/decode messages according to my protocol
        lines = buffer.splitlines()
        header = lines[0]
        client_port = client_address[1]

        #int(lines[2])
        #client_name = lines[4]
        #message = lines[6] this is commented because the first register request does not have message. TO CHANGE
        #message = ""


        print(">>>[The header is: " + header + "]")
        # serverRespond(server_socket, client_address[0], client_port)
        if header == "register":
            client_name = lines[2]
            User1 = MyUser(client_name, client_address, "Online")
            checker = 0
            for i in userList:
                if i.name == client_name:
                    checker = 1
                    if i.status == "Offline":
                        i.status = "Online"
                    else:
                        message = "ack\n[User already online]"
                        server_socket.sendto(message.encode(), client_address)
                        continue
            if checker == 0:
                userList.append(User1)
                print(">>>[USERNAME " + User1.name + " added to table.]")
            server_socket.sendto("welcome\n[Welcome, you are registered.]\n".encode(), client_address)
            message = "[Client table updated.]"
            for p in userList:
                message = message + "\n" + p.name + " " + p.client_address[0] + " " +str(p.client_address[1]) + " " + \
                          p.status
            for i in userList:
                server_socket.sendto(message.encode(), i.client_address)
            #print("Uesrlist has been updated...")

        if header == "dereg":
            client_name = lines[2]
            for i in userList:
                if i.name == client_name:
                    i.status = "Offline"
                    print(">>>[Username " + client_name + " is now offline. Table updated.]")
            message = "[Client table updated.]"
            for p in userList:
                message = message + "\n" + p.name + " " + p.client_address[0] + " " + str(p.client_address[1]) + " " + \
                          p.status
            for i in userList:
                server_socket.sendto(message.encode(), i.client_address)
            dereg_ack = "dereg_ack"
            server_socket.sendto(dereg_ack.encode(), client_address)

            '''
            for i in groupList:
                for j in i.users:
                    if j.name == client_name:
                        i.users.remove(j) 
            '''

        if header == "create_group":
            client_name = lines[2]
            group_name = lines[4]
            found = 0
            for i in groupList:
                if i.name == group_name:
                    found = 1
            if found == 0:
                Group1 = MyGroup(group_name)
                #Group1.add(client_name)
                groupList.append(Group1)
                message = "[Group table updated.]"
                for p in groupList:
                    message = message + "\n" + p.name
                server_socket.sendto(message.encode(), client_address) #this is ack so client knows group created
            else:
                kickout_client("Group already exists")
                message = "ack\n[Group already exists.]"
                server_socket.sendto(message.encode(), client_address)
                #implement server ack so client knows group not created

        if header == "list_groups":
            message = "grouplist\n"
            for i in groupList:
                message = message + i.name + "\n"

            server_socket.sendto(message.encode(), client_address)

        if header == "join_group":
            client_name = lines[2]
            group_name = lines[4]
            message = "join_group_ack\n"
            User1 = MyUser(None, None, None)
            for i in groupList:
                if i.name == group_name:
                    for p in userList:
                        if p.name == client_name:
                            User1 = p
                    i.add(User1)
                    print(client_name + " added to group " + group_name)
                    #implement ack functionality to say group no exist
                    server_socket.sendto(message.encode(), client_address)

        if header == "list_members":
            group_name = lines[2]
            message = "members\n"
            for i in groupList:
                if i.name == group_name:
                    for p in i.users:
                        message = message + p.name + " "
            server_socket.sendto(message.encode(), client_address)
            time.sleep(.5)

        if header == "group_msg":
            message = "server_group_message_ack"
            server_socket.sendto(message.encode(), client_address)
            client_name = lines[1]
            group_name = lines[3]
            group_message = lines[5]
            message = "group_msg\n>>>(" + group_name + ") " + client_name + ": " + group_message
            for i in groupList:
                if i.name == group_name:
                    for p in i.users:
                        server_socket.sendto(message.encode(), p.client_address)

        if header == "leave_group":
            client_name = lines[2]
            group_name = lines[4]
            for i in groupList:
                if i.name == group_name:
                    for p in i.users:
                        if p.name == client_name:
                            i.users.remove(p)
                            print("User " + client_name + " removed from group " + group_name)
                            message = "leave_ack"
                            server_socket.sendto(message.encode(), client_address)

        '''
        # multithreading. Should expand functionality with ACK type.
        server_send = threading.Thread(target=serverRespond, args=(server_socket, client_address[0], client_port))
        server_send.start() 
        '''


def clientMode(user_name, server_ip, server_port, client_port):

    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.bind(('', client_port))

    #this will send the first message to register the user according to my protocol
    first_msg = "register\n" + "name:\n" + user_name
    client_socket.sendto(first_msg.encode(), (server_ip, server_port))
    print(">>>[Registration message was sent.]")

    # multi-threading
    listen = threading.Thread(target=clientListen, args=(client_port, client_socket))
    listen.start()

    global registered
    time.sleep(.5)
    if registered == 0:
        for i in range(5):
            if registered == 0:
                client_socket.sendto(first_msg.encode(), (server_ip, server_port))
            time.sleep(.5)

    if registered == 0:
        print(">>>[Server not responding. Registration failed.]")
        exit()

    #this sleep is to allow the >>> to be after the generated user table
    time.sleep(.5)

    while True:
        print(">>>", end="")
        #temp = input()  # take inputs in the terminal
        #input_list = temp.split()
        #recv_name = ""
        try:
            temp = input()  # take inputs in the terminal
            input_list = temp.split()
            recv_name = ""
            header = input_list[0]
            if header not in allowed_cmds:
                raise Exception("Unknown Command")
            if header == "dereg":
                if user_name != input_list[1]:
                    raise Exception("Bad deregister")
            if header == "send":
                recv_name = input_list[1]
        except KeyboardInterrupt:
            for t in range(5):  # send a request to server 5 times if no ACK
                if (dereg_quit == 0):
                    dereg_request(client_socket, user_name, server_ip, server_port)
                    time.sleep(.5)
            if (dereg_quit == 0):
                print(">>>[Server not responding.]")
                print(">>>[Exiting.}")
                exit()
            else:
                exit()
        except:
            print(">>>[Invalid input.]")
            continue


        #For debugging
        if header == "userlist":
            print(client_userList)

        #This is to implement client send function
        if header == "send":
            recv_name = input_list[1]
            recipient = ""
            found = 0
            message = ""
            for i in client_userList:
                if i[0:i.find(" ")] == recv_name:
                    found = 1
                    recipient = i
            recvr_list = recipient.split()
            if found == 0:
                print(">>>[User not found.}")
            else:
                for i in range(2, len(input_list)):
                    message = message + input_list[i] + " "
                #recvr_list = recipient.split()
                message = "msg\n" + user_name + "\n" + message
                ' '.join(message)
                client_socket.sendto(message.encode(), (recvr_list[1], int(recvr_list[2])))
                global c_msg_ack
                time.sleep(.5)
                if c_msg_ack == 1:
                    print(">>>[Message received by " + recv_name + ".]")
                    c_msg_ack = 0
                else:
                    for i in range(5):
                        if c_msg_ack == 0:
                            print(">>>[No ack received from " + recv_name + ", message not delivered.]")
                            time.sleep(.5)
                            client_socket.sendto(message.encode(), (recvr_list[1], int(recvr_list[2])))
                    if c_msg_ack == 0:
                        print(">>>[No ack received. Message not delivered.")


        #this is for client to deregister with command >>>dereg [CLIENT_NAME]
        if header == "dereg":
            name = input_list[1]
            for i in client_userList:
                if i[0:len(name)] == name:
                    #i.status = "Offline"
                    #message = "dereg\nname\n" + user_name
                    #client_socket.sendto(message.encode(), (server_ip, server_port))
                    for t in range(5): #send a request to server 5 times if no ACK
                        if (dereg_quit == 0):
                            dereg_request(client_socket, user_name, server_ip, server_port)
                            time.sleep(.5)
                    if (dereg_quit == 0):
                        print(">>>[Server not responding.]")
                        print(">>>[Exiting.}")
                        exit()
                    else:
                        exit()
            print(">>>[Error, user not found.]")

        if header == "create_group":
            if input_list[1] != None:
                group_name = input_list[1]
                message = "create_group\n" + "name\n" + user_name + "\ngroup_name:\n" + group_name
                client_socket.sendto(message.encode(), (server_ip, server_port))
            else:
                print(">>>[Please enter a group name.]")
                continue

        if header == "list_groups":
            message = "list_groups\n"
            client_socket.sendto(message.encode(), (server_ip, server_port))

        if header == "join_group":
            if input_list[1] != None:
                global client_Group
                client_Group = input_list[1]
                message = "join_group\n" + "name:\n" + user_name + "\ngroup_name:\n" + client_Group
                client_socket.sendto(message.encode(), (server_ip, server_port))
                time.sleep(.5)
                if join_group_ack == 1:
                    clientGroupMode(user_name, server_ip, server_port, client_port, client_socket)
                    print(">>>" + message_buffer)

def clientGroupMode(user_name, server_ip, server_port, client_port, client_socket):
    global client_Group
    print(">>>(" + client_Group + ") " + "[Sucessfully joined group.]")
    while True:
        print(">>>(" + client_Group + ") ", end="")

        try:
            temp = input()  # take inputs in the terminal
            input_list = temp.split()
            recv_name = ""
            header = input_list[0]
            if header not in group_allowed_cmds:
                raise Exception("Unknown Command")
            if header == "dereg":
                if user_name != input_list[1]:
                    raise Exception("Bad deregister")
            if header == "send":
                recv_name = input_list[1]
        except KeyboardInterrupt:

            message = "leave_group\n" + "name:\n" + user_name + "\ngroup:\n" + client_Group
            client_socket.sendto(message.encode(), (server_ip, server_port))
            for t in range(5):  # send a request to server 5 times if no ACK
                if (dereg_quit == 0):
                    dereg_request(client_socket, user_name, server_ip, server_port)
                    time.sleep(.5)
            if (dereg_quit == 0):
                print(">>>[Server not responding.]")
                print(">>>[Exiting.}")
                exit()
            else:
                exit()
        except:
            print(">>>[Invalid input.]")
            continue

        if header == "dereg":
            name = input_list[1]
            for i in client_userList:
                if i[0:len(name)] == name:
                    #i.status = "Offline"
                    #message = "dereg\nname\n" + user_name
                    #client_socket.sendto(message.encode(), (server_ip, server_port))
                    for t in range(5): #send a request to server 5 times if no ACK
                        if (dereg_quit == 0):
                            dereg_request(client_socket, user_name, server_ip, server_port)
                            time.sleep(.5)
                    if (dereg_quit == 0):
                        print(">>>(" + client_Group + ") " + "[Server not responding.]")
                        print(">>>(" + client_Group + ") " + "[Exiting.]")
                        exit()
                    else:
                        exit()
            print(">>>(" + client_Group + ") " + "[Error, user not found.]")

        if header == "list_members":
            message = "list_members\n" + "group:\n" + client_Group
            client_socket.sendto(message.encode(), (server_ip, server_port))

        if header == "send_group":
            message = ""
            for i in range(1, len(input_list)):
                message = message + input_list[i] + " "
                # recvr_list = recipient.split()
            message = "group_msg\n" + user_name + "\nserver:\n" + client_Group + "\nmsg\n" + message
            #' '.join(message)
            client_socket.sendto(message.encode(), (server_ip, server_port))
            global c_g_msg_ack
            time.sleep(.5)
            if c_g_msg_ack == 1:
                print("(" + client_Group + ") " + "[Message received by server]")
                c_g_msg_ack = 0
            else:
                print(">>>(" + client_Group + ") " + "[No ack received from server, message not delivered.]")

        if header == "leave_group":
            message = "leave_group\n" + "name:\n" + user_name + "\ngroup:\n" + client_Group
            client_socket.sendto(message.encode(), (server_ip, server_port))
            global leave_group_ack
            time.sleep(.5)
            if leave_group_ack == 1:
                leave_group_ack = 0
                client_Group = ""
                return



def dereg_request(client_socket, user_name, server_ip, server_port): #This is for clients
    print(">>>[Attempting to disconnect...]")
    message = "dereg\nname\n" + user_name
    client_socket.sendto(message.encode(), (server_ip, server_port))

#this checks if the user trying to log in is already online
def kickout_client(reason):
    print("User already online???")
    '''
    for i in client_userList:
        if i[len(i)-7] == "Online":
            print(">>>[User is already online. Shutting down...]")
    '''

#Implement user trying to log in with already connected name
if __name__ == "__main__":
    mode = sys.argv[1]

    if mode == '-s':  # in server mode
        s_port = int(sys.argv[2])  # port numbers must be type int!
        serverMode(s_port)

    elif mode == '-c':  # in client mode
        user_name = sys.argv[2]
        server_ip = sys.argv[3]
        server_port = int(sys.argv[4])
        client_port = int(sys.argv[5])

        clientMode(user_name, server_ip, server_port, client_port)

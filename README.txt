UNI: msj2150
NAME: Mohammad Saim Jamal

Hello! This is a simple chat app that allows users to register with a server and communicate directly with eachother or create a group chat. This utilizes my own application protocol and UDP for transport layer protocol.


Command line INPUT is:

python3 ChatApp.py -s [Port Number]
--for server mode

python3 ChatApp.py -c [Username] [Server_address] [Server port] [Client port]
--for client mode

Design Descicions:
If you create a group on a client, it doesn't automatically join it. You have to join it afterwords with the
join_group command.



Problems:
if you try to send a message to an offline client then the terminal will give an error but it will
correctly say that no ack has been received and continue running. If you try to send an offline user a message again
then the error won't appear and it will go as usual.

Also, i haven't managed to nail down the ">>>" looking pretting,
so if it doesn't appear you should still be able to input commands.

After client table has been updated and it is broadcasted to the clients, the >>> doesnt appear
but the client is still taking in commands.

Commands work as specified in the homework assignment. Server takes no input.

The thing is that if a server is disconnected the client won't know unless it tries to
deregister and server doesn't respond

I didn't have time to implement buffer where it sends private messages after you leave the chat room.

I also didn't add the send 5 requests before exit for most of them exist for dereg. Send doesn't exit if there is
no ack.

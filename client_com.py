import socket
import threading


class ClientComm:
    """
    class to represent client  (communication)
    """

    def __init__(self, server_ip, port, msg_q, chat_dict):
        """
        init the object
        :param server_ip: server_ip
        :param port: port of communication
        :param msg_q: deliver messages to main client program
        :param chat_dict: deliver chat messages to main client
        """
        self.socket = None  # client's socket
        self.server_ip = server_ip
        self.port = port
        self.q = msg_q
        self.chat = chat_dict
        threading.Thread(target=self._main_loop, daemon=True).start()

    def _main_loop(self):
        """
        connect to server and handle server's messages
        """
        self.socket = socket.socket()
        try:
            # connect to server
            self.socket.connect((self.server_ip, self.port))
        except Exception as e:
            print("ClientComm - _main_loop - 1", str(e))
        else:
            while True:
                try:
                    # get command index
                    data = int(self.socket.recv(1).decode())
                except Exception as e:
                    print("ClientComm - _main_loop - 2", str(e))
                    break
                else:
                    if data == 1:
                        # answer if nickname valid or not
                        try:
                            data = self.socket.recv(3).decode()
                        except Exception as e:
                            print("ClientComm - _main_loop - 3", str(e))
                            break
                        else:
                            self.q.put(data)

                    elif data == 2:
                        # to start a game
                        try:
                            data = self.socket.recv(3).decode()
                        except Exception as e:
                            print("ClientComm - _main_loop - 4", str(e))
                            break
                        else:
                            self.q.put(data)

                    elif data == 3:
                        # mouse position to draw - (if not painter)
                        try:
                            x = int(self.socket.recv(3).decode())
                            y = int(self.socket.recv(3).decode())
                        except Exception as e:
                            print("ClientComm - _main_loop - 4", str(e))
                            break
                        else:
                            # organize as a tuple
                            self.q.put((x, y))

                    elif data == 4:
                        # list of words to choose from - (only for painter)
                        try:
                            length = int(self.socket.recv(2).decode())
                            words = (self.socket.recv(length).decode()).split(",")
                        except Exception as e:
                            print("ClientComm - _main_loop - 5", str(e))
                            break
                        else:
                            print(words)
                            self.q.put(words)

                    elif data == 5:
                        # answer if guessed correctly - (not for painter)
                        try:
                            ack = self.socket.recv(3).decode()
                        except Exception as e:
                            print("ClientComm - _main_loop - 6", str(e))
                            break
                        else:
                            self.q.put(ack)

                    elif data == 6:
                        # chat message - (not for painter)
                        try:
                            length = int(self.socket.recv(2).decode())
                            msg = self.socket.recv(length).decode()
                        except Exception as e:
                            print("ClientComm - _main_loop - 7", str(e))
                        else:
                            # add message to chat list
                            for i in range(7, 0, -1):
                                self.chat[i] = self.chat[i - 1]
                            self.chat[0] = msg
                            # alert new message arrived
                            self.q.put("C")

                    elif data == 7:
                        # round ended
                        self.q.put("E")
                        print("ENDGAME")

                    elif data == 8:
                        # game finished
                        self.q.put("F")
                        print("FINAL")

                    elif data == 9:
                        # player's name and score - to place on podium
                        try:
                            length = int(self.socket.recv(2).decode())
                            msg = self.socket.recv(length).decode()
                        except Exception as e:
                            print("ClientComm - _main_loop - 8", str(e))
                        else:
                            self.q.put("P" + msg)

    def send(self, msg):
        """
        send message to server
        :param msg: the message to send
        """
        if type(msg) == str:
            # if the message require encoding
            msg = msg.encode()
        try:
            # send the message
            self.socket.send(msg)
        except Exception as e:
            print("ClientComm - send", e)
            exit()
        else:
            print(f"send '{msg}' to server")

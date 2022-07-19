import socket
import threading
import select
from player import Player
import random
import time


class ServerComm:
    """
    class to represent client  (communication)
    """

    def __init__(self, port):
        """
        init the object
        :param port: port of communication
        """
        self.socket = None      # server's socket
        self.word = None        # chosen word each round
        self.port = port
        self.open_clients = {}  # all logged clients, soc -> ip
        self.waiting = {}       # all clients waiting for validation, soc -> ip
        self.suggested = {}     # all words sent for current painter -> their difficulty
        self.painter = None     # current painter's socket
        self.players = []       # list of all players
        self.guessed = 0        # how many guessed correctly each round
        self.draws = 0          # how many painters already was
        self.score_mult = 43    # the multiplier by seconds to multiply the score
        self.game = False       # if game is waiting to start or not
        self._connect()
        threading.Thread(target=self._main_loop).start()

    def _connect(self):
        """
        set up the server's socket
        """
        self.socket = socket.socket()
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(3)

    def _main_loop(self):
        """
        run through the game phases and handle messages from clients
        """
        while True:
            # initialize all parameters before a new game
            self.open_clients.clear()
            self.waiting.clear()
            self.suggested.clear()
            self.players.clear()
            self.guessed = 0
            self.draws = 0
            self.game = False

            flag = True
            while True:
                if self.game:
                    # starting a game
                    self.draws += 1
                    if self.draws > len(self.players):
                        # if everyone draw - end game
                        self.send_all("8", 0)
                        scores = {}  # to send scoreboard to clients

                        for player in self.players:
                            scores[player.score] = player.name  # keep name by score
                        scores_list = list(scores.keys())
                        scores_list.sort(reverse=True)  # sort the scores from big to small

                        for score in scores_list:
                            # send all names and scores from 1st place to last
                            tos = scores[score] + ": " + str(score)
                            self.send_all("9" + str(len(tos)).zfill(2) + tos, 0)
                        break

                    self.guessed = 0

                    for i in range(len(self.players)-1):
                        # every round change painter by order
                        if self.players[i].painter:
                            self.players[i].set_painter(False)
                            self.players[i+1].set_painter(True)
                            self.game = False
                            self.painter = self.players[i+1].soc    # keep painter's socket
                            break

                    if self.game:
                        # to set first as the painter if his turn
                        self.players[-1].set_painter(False)
                        self.players[0].set_painter(True)
                        self.painter = self.players[0].soc
                        self.game = False

                    self.send_all("2non", self.painter)  # if not painter
                    self.send(self.painter, "2yes")      # to painter
                    self.send(self.painter, self._generate_words())  # suggest words to painter
                if self.word is not None and flag:
                    # tell all clients to start a game
                    self.send_all("2str", 0)
                    threading.Thread(target=self._timer).start()
                    flag = False

                rlist, wlist, xlist = select.select([self.socket]+list(self.open_clients.keys()) +
                                                    list(self.waiting.keys()), list(self.open_clients.keys()), [])
                for current_socket in rlist:
                    if current_socket is self.socket:
                        # if new client connecting
                        if len(self.players) < 3:
                            client, addr = self.socket.accept()
                            print(f"{addr[0]} - connected")
                            self.waiting[client] = addr[0]
                    else:
                        # if got a message from client
                        try:
                            # get command
                            com = int(current_socket.recv(1).decode())
                        except Exception as e:
                            print("ServerComm - _main_loop", str(e))
                            self._disconnect_client(current_socket)
                        else:
                            print(com)
                            if com == "":
                                # if client disconnected
                                self._disconnect_client(current_socket)

                            elif com == 1 and current_socket in self.waiting.keys():
                                # sent nickname - waiting for validation
                                try:
                                    length = int(current_socket.recv(1).decode())
                                    data = current_socket.recv(length).decode()
                                except Exception as e:
                                    print("ServerComm - _main_loop - 1", str(e))
                                    self._disconnect_client(current_socket)
                                else:
                                    ack = True
                                    for player in self.players:
                                        # check if name taken
                                        if data == player.name:
                                            ack = False
                                    if ack:
                                        # if valid - put into logged in list and tell client
                                        self.players.append(Player(data, current_socket, False))
                                        self.open_clients[current_socket] = self.waiting[current_socket]
                                        del self.waiting[current_socket]
                                        self.send(current_socket, "1ACK")
                                        if len(self.players) >= 3:
                                            # if 3 players logged
                                            self.game = True
                                    else:
                                        self.send(current_socket, "1INV")

                            elif com == 3:
                                # mouse position for drawing from server
                                try:
                                    data = current_socket.recv(6).decode()
                                except Exception as e:
                                    print("ServerComm - _main_loop", str(e))
                                    self._disconnect_client(current_socket)
                                else:
                                    # send position to all other clients
                                    self.send_all("3" + data, current_socket)

                            elif com == 4:
                                # word the painter chose
                                try:
                                    length = current_socket.recv(2).decode()
                                    length = int(length)
                                    self.word = current_socket.recv(length).decode()
                                except Exception as e:
                                    print("ServerComm - _main_loop - 2", str(e))
                                    self._disconnect_client(current_socket)
                                else:
                                    print(self.word)
                                    flag = True

                            elif com == 5:
                                # guesses from other clients
                                try:
                                    length = current_socket.recv(2).decode()
                                    length = int(length)
                                    guess = current_socket.recv(length).decode()
                                except Exception as e:
                                    print("ServerComm - _main_loop - 3", str(e))
                                else:
                                    name = ""
                                    cur_player = None
                                    painter_player = None
                                    for player in self.players:
                                        if player.soc is current_socket:
                                            # find guesser's player object
                                            name = player.name
                                            cur_player = player
                                        elif player.soc is self.painter:
                                            # find painter's player object
                                            painter_player = player
                                        if painter_player is not None and cur_player is not None:
                                            break

                                    if self.word.lower() == guess.lower():
                                        # if guessed correctly add score to guesser and painter
                                        score_to_add = self.score_mult * self.suggested[self.word] * 30
                                        cur_player.add_score(int(score_to_add))
                                        painter_player.add_score(int(score_to_add * 0.75))  # painter gets 75% of score
                                        self.send(current_socket, "5ACK")   # tell client that guessed correctly
                                        send = name + " succeeded!"  # send to chat
                                        self.send_all("6" + str(len(send)).zfill(2) + send, self.painter)
                                        self.guessed += 1   # count guesses
                                        if self.guessed >= len(self.players) - 1:
                                            # if everyone guessed - end round
                                            self.send_all("7", 0)
                                            for i in range(8):
                                                # clear chat
                                                self.send_all("601 ", 0)
                                            self.game = True
                                            break
                                    else:
                                        self.send(current_socket, "5INV")
                                        send = name + ": " + guess  # send guess to chat
                                        self.send_all("6" + str(len(send)).zfill(2) + send, self.painter)

                            elif com == 7:
                                # if painter says time over (count time by painter)
                                if current_socket is self.painter:
                                    # end everyone's round
                                    self.send_all("7", 0)
                                    print("TIME OVER")
                                    for i in range(8):
                                        # clear chat
                                        self.send_all("601 ", 0)
                                    self.game = True    # start a new round

    def send_all(self, data, sock):
        """
        send msg to all clients except one
        :param data: the message
        :param sock: the one not to send the message to
        """
        flag = False
        if type(data) == str:
            # if message require encoding
            data = data.encode()
        for soc in self.open_clients.keys():
            if soc is not sock:
                # skip the socket received
                try:
                    soc.send(data)
                except Exception as e:
                    print("ServerComm - send_all", str(e))
                    self._disconnect_client(soc)
                else:
                    # print if message sent
                    flag = True
                    print(f"send to {self.open_clients[soc]} - {data}")
        if not flag:
            # print if message hasn't been sent
            print(f"sent {data} to nobody")

    def send(self, soc, msg):
        """
        send message to only one client
        :param soc: the client to send the message to
        :param msg: the message
        """
        if type(msg) == str:
            # if the message require encoding
            msg = msg.encode()
        try:
            # send the message
            soc.send(msg)
        except Exception as e:
            print("ServerComm - send", e)
            self._disconnect_client(soc)
        else:
            # print the ip and the message
            if soc in self.open_clients.keys():
                print(f"send to {self.open_clients[soc]} - {msg}")
            elif soc in self.waiting.keys():
                print(f"send to {self.waiting[soc]} - {msg}")

    def _disconnect_client(self, sock):
        """
        disconnect client
        :param sock: the client socket
        """
        if sock in self.open_clients.keys():
            # remove from connected clients
            print(f"{self.open_clients[sock]} - disconnected")
            del self.open_clients[sock]
            sock.close()
        elif sock in self.waiting.keys():
            # remove from waiting for validation if is waiting
            print(f"{self.waiting[sock]} - disconnected")
            del self.waiting[sock]
            sock.close()

    def _generate_words(self):
        """
        generate string of 3 words in three difficulties to send to painter
        :return: str of 3 words
        """
        # open words files - each word and her difficulty are on the same line separated by '-'
        file = open("easy.txt", 'r')
        file2 = open("medium.txt", 'r')
        file3 = open("hard.txt", 'r')

        # read the files
        words1 = file.read().split("\n")
        words2 = file2.read().split("\n")
        words3 = file3.read().split("\n")

        # choose randomly 3 words
        pair1 = random.choice(words1)
        pair2 = random.choice(words2)
        pair3 = random.choice(words3)

        # keep the three words with their difficulties
        word1 = pair1.split('-')[0]
        self.suggested[word1] = float(pair1.split('-')[1])
        word2 = pair2.split('-')[0]
        self.suggested[word2] = float(pair2.split('-')[1])
        word3 = pair3.split('-')[0]
        self.suggested[word3] = float(pair3.split('-')[1])

        # build a string of the words with command number (4) and string's length
        words_str = word1 + "," + word2 + "," + word3
        words_tos = "4" + str(len(words_str)).zfill(2) + words_str
        print(words_tos)

        # close files
        file.close()
        file2.close()
        file3.close()

        return words_tos

    def _timer(self):
        """
        a timer of 43 seconds and print on screen
        multiply the score by how many seconds left
        """
        # countdown 43 seconds

        self.score_mult = 43

        for j in range(43, -1, -1):
            time.sleep(1)   # waits 1 second
            self.score_mult -= 1

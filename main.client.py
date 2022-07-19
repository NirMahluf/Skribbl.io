import queue
import threading
from client_com import ClientComm
from paint import Paint
import pygame
import pygame.gfxdraw
import time
from TextInputBox import TextInputBox


def _timer(screen):
    """
    a timer of 40 seconds and print on screen
    :param screen: screen to print timer on
    """

    global time_over    # if time is over or not

    # countdown 40 seconds
    for sec in range(40, -1, -1):
        sleep(1)   # waits 1 second
        # choose the pattern according to the length of the number
        if time_over:
            # if game is over - pause timer
            break
        if len(str(sec)) < 2:
            print_time_on_screen(f"00:0{sec}", screen)
        else:
            print_time_on_screen(f"00:{sec}", screen)
    time_over = True    # if timer done


def print_time_on_screen(text, screen):
    """
    print the timer on the play screen
    :param text: the text to print
    :param screen: the pygame screen parameter to print
    """
    global time_over    # if timer is over or not
    if not time_over:
        # make a font
        pygame.font.init()
        timer_font = pygame.font.SysFont('Verdana', 40)
        # make the surface of the text
        textsurface = timer_font.render(text, True, (255, 0, 0), (0, 0, 0))
        # print on screen
        screen.blit(textsurface, (50, 20))
        pygame.display.flip()


chat_list = []  # list of chat messages
for i in range(8):
    # initialize chat - 8 messages
    chat_list.append("")

recv_q = queue.Queue()  # queue to hold messages
comm = ClientComm('127.0.0.1', 1000, recv_q, chat_list)  # creating client communication object

sleep = time.sleep

while True:

    # Initializing pygame module
    pygame.init()

    # Screen variables
    screen_width = 900
    screen_height = 506

    drawingwindow = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Skribbl.io")
    drawingwindow.fill((255, 255, 255))

    paint = Paint(drawingwindow, False)     # creating paint object

    backimg = pygame.image.load("lobby.png").convert_alpha()    # printing lobby screen
    drawingwindow.blit(backimg, (0, 0))
    pygame.display.update()

    font = pygame.font.Font("Action_Man.ttf", 40)

    # Creating two text boxes
    text_input_box = TextInputBox((0, 0, 0), 230, 350, 410, font, backcolor=(47, 56, 176),
                                  default_text="enter nickname...", max_letters=6)  # creating text box

    # Creating group of text
    group = pygame.sprite.Group(text_input_box)

    inv = False
    data = ""
    while True:
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                # if quited the game
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # if pressed enter - send nickname to server
                    tos = "1" + str(len(text_input_box.get_text())) + text_input_box.get_text()
                    text_input_box.clear()
                    comm.send(tos)

        if not recv_q.empty():
            data = recv_q.get()
            if data == "ACK":
                # if nickname is valid
                break
            elif data == "INV" and not inv:
                # if nickname is not valid
                text_input_box = TextInputBox((0, 0, 0), 230, 350, 410, font, backcolor=(47, 56, 176),
                                              default_text="already taken", max_letters=6)
                group = pygame.sprite.Group(text_input_box)
                event_list.clear()
                inv = True
        # Updating the text boxes
        group.update(event_list)
        group.draw(drawingwindow)
        pygame.display.update()

    final = False

    while True:

        pygame.mouse.set_cursor(*pygame.cursors.arrow)

        backimg = pygame.image.load("loading.png").convert_alpha()  # loading screen
        drawingwindow.blit(backimg, (0, 0))
        pygame.display.update()

        while True:
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            if not recv_q.empty():
                data = recv_q.get()
                if data == "yes":
                    # if chosen as painter
                    painter = True
                    break
                elif data == "non":
                    # if chosen guesser
                    painter = False
                    break
                elif data == "F":
                    # if game ended
                    final = True
                    painter = False
                    break
            pygame.display.update()

        if painter:
            # if chosen painter
            backimg = pygame.image.load("word_choose.png").convert_alpha()  # word choose screen
            drawingwindow.blit(backimg, (0, 0))
            pygame.display.update()

            while True:
                if not recv_q.empty():
                    data = recv_q.get()
                    print(type(data))
                    if type(data) == list and len(data) == 3:
                        # printing words to choose from
                        font = pygame.font.Font("Action_Man.ttf", 40)
                        op1 = font.render(data[0], True, (255, 255, 255))   # easy
                        op2 = font.render(data[1], True, (255, 255, 255))   # medium
                        op3 = font.render(data[2], True, (255, 255, 255))   # hard
                        left1 = (screen_width - op1.get_width()) / 2
                        left2 = (screen_width - op2.get_width()) / 2
                        left3 = (screen_width - op3.get_width()) / 2
                        rect1 = pygame.draw.rect(drawingwindow, (0, 255, 0), pygame.Rect(left1, screen_height * 0.4,
                                                                                         op1.get_width() + 20,
                                                                                         op1.get_height()))
                        drawingwindow.blit(op1, (rect1.x + 10, rect1.y + 2))
                        rect2 = pygame.draw.rect(drawingwindow, (241, 152, 18), pygame.Rect(left2, screen_height * 0.6,
                                                                                            op2.get_width() + 20,
                                                                                            op2.get_height()))
                        drawingwindow.blit(op2, (rect2.x + 10, rect2.y + 2))
                        rect3 = pygame.draw.rect(drawingwindow, (255, 0, 0), pygame.Rect(left3, screen_height * 0.8,
                                                                                         op3.get_width() + 20,
                                                                                         op3.get_height()))
                        drawingwindow.blit(op3, (rect3.x + 10, rect3.y + 2))
                        pygame.display.update()
                        break

            word = None

            while word is None:
                # wait for painter to choose word
                for event in pygame.event.get():
                    mousepos = (0, 0)
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    t = pygame.mouse.get_pressed()
                    if t[0] == 1:
                        mousepos = pygame.mouse.get_pos()
                        if rect1.collidepoint(mousepos):
                            word = data[0]
                            break
                        elif rect2.collidepoint(mousepos):
                            word = data[1]
                            break
                        elif rect3.collidepoint(mousepos):
                            word = data[2]
                            break

            comm.send('4' + str(len(word)).zfill(2) + word)  # send chosen word to server

            while True:
                # wait for server to start the round
                event_list = pygame.event.get()
                for event in event_list:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                if not recv_q.empty():
                    data = recv_q.get()
                    if data == "str":
                        # server started the game
                        break
                pygame.display.update()

            # Loading backgroud image and drawing it on screen
            backimg = pygame.image.load("painter.png").convert_alpha()
            drawingwindow.blit(backimg, (0, 0))

            time_over = False
            threading.Thread(target=_timer, args=(drawingwindow,)).start()  # starting timer

            pygame.mouse.set_cursor(*pygame.cursors.broken_x)
            end = ""

            # printing word to draw at the top of the screen
            opWord = font.render(word, True, (255, 0, 0))
            rectWord = pygame.draw.rect(drawingwindow, (47, 56, 176),
                                        pygame.Rect(800, 48 - opWord.get_height() - 2, opWord.get_width() + 2,
                                                    opWord.get_height()))
            drawingwindow.blit(opWord, (800 - opWord.get_width() / 2, rectWord.y + 2))

            # Gameloop
            while True:

                for event in pygame.event.get():
                    mousepos = (0, 0)
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    t = pygame.mouse.get_pressed()
                    if t[0] == 1:
                        mousepos = pygame.mouse.get_pos()
                    # send mouse position to paint class and to server
                    check = paint.draw(mousepos)
                    tos = str(3) + str(mousepos[0]).zfill(3) + str(mousepos[1]).zfill(3)
                    if tos != "3000000":
                        comm.send(tos)
                    if check[1] and not check[0]:
                        # if eraser - change cursor
                        pygame.mouse.set_cursor(*pygame.cursors.diamond)
                    elif check[1] and check[0]:
                        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
                    if not recv_q.empty():
                        end = recv_q.get()
                        if end == "E":
                            # if ended round
                            time_over = True
                            break
                    if time_over:
                        # if time over - tell server
                        comm.send("7")
                if end == "E":
                    # if round ended
                    time_over = True
                    break
                if not recv_q.empty():
                    end = recv_q.get()
                    if end == "E":
                        # if round ended
                        time_over = True
                        break
                if time_over:
                    comm.send("7")

        elif not final:
            # if guesser
            while True:
                # wait for server to start the game
                event_list = pygame.event.get()
                for event in event_list:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                if not recv_q.empty():
                    data = recv_q.get()
                    if data == "str":
                        break
                pygame.display.update()

            backimg = pygame.image.load("guesser.png").convert_alpha()  # guesser screen
            drawingwindow.blit(backimg, (0, 0))

            # start timer
            time_over = False
            threading.Thread(target=_timer, args=(drawingwindow,)).start()

            font = pygame.font.Font("Action_Man.ttf", 25)

            # Creating text box
            input_box = TextInputBox((0, 0, 0), 734, 401, 135, font, backcolor=(255, 255, 255),
                                     default_text="guess", max_letters=9)
            group2 = pygame.sprite.Group(input_box)

            word_correct = False
            guess = ""

            while True:
                mousepos = (0, 0)
                event_list = pygame.event.get()
                for event in event_list:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and not word_correct:
                            # send guess to server
                            print("enter")
                            guess = input_box.get_text()
                            to_send = "5" + str(len(guess)).zfill(2) + guess
                            comm.send(to_send)
                            input_box.clear()
                if not recv_q.empty():
                    data = recv_q.get()
                    if type(data) == tuple:
                        # send position from server to paint class to view painter's paint
                        mousepos = data
                        paint.draw(mousepos)
                    elif type(data) == str:
                        if data == "ACK":
                            # if guessed correctly
                            word_correct = True
                            font = pygame.font.Font("Action_Man.ttf", 25)
                            # print correct message and the correct word
                            opCor = font.render("correct!", True, (0, 0, 0))
                            rectCor = pygame.draw.rect(drawingwindow, (255, 255, 255),
                                                       pygame.Rect(735, 401, 134,
                                                                   opCor.get_height() + 20))
                            drawingwindow.blit(opCor, (735 + 67 - opCor.get_width()/2, rectCor.y + 10))

                            opWord = font.render(guess, True, (255, 0, 0))
                            rectWord = pygame.draw.rect(drawingwindow, (47, 56, 176),
                                                        pygame.Rect(800, 48 - opWord.get_height() - 2,
                                                                    opWord.get_width() + 2, opWord.get_height()))
                            drawingwindow.blit(opWord, (800 - opWord.get_width() / 2, rectWord.y + 2))
                        elif data == "C":
                            # if there is new message in chat - update
                            font = pygame.font.Font("Action_Man.ttf", 15)
                            for i in range(8):
                                opChat = font.render(chat_list[i], True, (0, 0, 0))
                                rectChat = pygame.draw.rect(drawingwindow, (255, 255, 255),
                                                            pygame.Rect(737, 64+39.625*(7-i), 128, 38))
                                drawingwindow.blit(opChat, (739, rectChat.y))
                        elif data == "E":
                            # if round ended
                            time_over = True
                            break
                if not word_correct:
                    # if guessed correctly - block text box
                    group2.draw(drawingwindow)
                    group2.update(event_list)

                pygame.display.update()
        else:
            # if game ended - show podium screen
            backimg = pygame.image.load("podium.png").convert_alpha()
            drawingwindow.blit(backimg, (0, 0))
            pygame.display.update()

            player1 = None
            player2 = None
            player3 = None

            flag = True
            flag2 = True
            while True:
                event_list = pygame.event.get()
                for event in event_list:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit("done")
                if not recv_q.empty() and flag:
                    msg = recv_q.get()
                    if msg[0] == "P":
                        # get players' names and scores according to position
                        if player1 is None:
                            player1 = msg[1:].split(": ")
                        elif player2 is None:
                            player2 = msg[1:].split(": ")
                        else:
                            player3 = msg[1:].split(": ")
                            flag = False
                elif flag2:
                    # print players and their score according to position
                    flag2 = False
                    font = pygame.font.Font("Action_Man.ttf", 25)

                    op1 = font.render(player1[0], True, (255, 255, 255))
                    op2 = font.render(player2[0], True, (255, 255, 255))
                    op3 = font.render(player3[0], True, (255, 255, 255))
                    rect1 = pygame.draw.rect(drawingwindow, (47, 56, 176),
                                             pygame.Rect(368 + (130-op1.get_width())/2, 143, op1.get_width() + 2,
                                                         op1.get_height()))
                    drawingwindow.blit(op1, (rect1.x + 1, rect1.y))
                    rect2 = pygame.draw.rect(drawingwindow, (47, 56, 176),
                                             pygame.Rect(264 + (107-op2.get_width())/2, 195, op2.get_width() + 2,
                                                         op2.get_height()))
                    drawingwindow.blit(op2, (rect2.x + 1, rect2.y))
                    rect3 = pygame.draw.rect(drawingwindow, (47, 56, 176),
                                             pygame.Rect(496 + (101-op3.get_width())/2, 210, op3.get_width() + 2,
                                                         op3.get_height()))
                    drawingwindow.blit(op3, (rect3.x + 1, rect3.y))

                    op1 = font.render(player1[1], True, (255, 255, 255))
                    op2 = font.render(player2[1], True, (255, 255, 255))
                    op3 = font.render(player3[1], True, (255, 255, 255))

                    rect1 = pygame.draw.rect(drawingwindow, (47, 56, 176),
                                             pygame.Rect(368 + (130 - op1.get_width()) / 2, 118, op1.get_width() + 2,
                                                         op1.get_height()))
                    drawingwindow.blit(op1, (rect1.x + 1, rect1.y))
                    rect2 = pygame.draw.rect(drawingwindow, (47, 56, 176),
                                             pygame.Rect(264 + (107 - op2.get_width()) / 2, 170, op2.get_width() + 2,
                                                         op2.get_height()))
                    drawingwindow.blit(op2, (rect2.x + 1, rect2.y))
                    rect3 = pygame.draw.rect(drawingwindow, (47, 56, 176),
                                             pygame.Rect(496 + (101 - op3.get_width()) / 2, 185, op3.get_width() + 2,
                                                         op3.get_height()))
                    drawingwindow.blit(op3, (rect3.x + 1, rect3.y))
                pygame.display.update()

import pygame
import pygame.gfxdraw


class Paint:
    def __init__(self, drawingscreen, painter):
        """
        initialize all paint data
        :param drawingscreen: screen to print on
        :param painter: if painter or not
        """
        self.drawingwindow = drawingscreen
        self.white = (255, 255, 255)     # define color white
        self.blue = (0, 0, 255)          # define color blue
        self.red = (255, 0, 0)           # define color red
        self.black = (0, 0, 0)           # define color black
        self.green = (0, 255, 0)         # define color green
        self.pink = (255, 0, 255)        # define color pink
        self.orange = (255, 128, 64)     # define color orange
        self.yellow = (255, 255, 0)      # define color yellow
        self.purple = (192, 4, 198)      # define color purple
        self.brown = (128, 64, 0)        # define color brown
        self.light_blue = (0, 255, 255)  # define color light blue
        # rect for the drawing area
        self.clearrect = (42, 36, 623, 430)
        # Defining rect value for colors in colorbox
        self.col1 = (801, 79, 59, 53)   # black position
        self.col2 = (801, 136, 59, 53)  # blue position
        self.col3 = (738, 136, 59, 53)  # red position
        self.col4 = (738, 79, 59, 53)   # green position
        self.col5 = (738, 192, 59, 53)  # pink position
        self.col6 = (738, 248, 59, 53)  # orange position
        self.col7 = (801, 248, 59, 53)  # yellow position
        self.col8 = (801, 304, 59, 53)  # purple position
        self.col9 = (801, 192, 59, 53)  # light_blue position
        self.col0 = (738, 304, 59, 53)  # brown position
        self.buttonselect = (801, 79, 59, 53)   # marking chosen color
        self.pencolour = (0, 0, 0)      # pen color
        self.painter = painter

    def set_painter(self, painter):
        """
        update if is painter or not
        :param painter: if painter or not
        """
        self.painter = painter

    def _drawrectangle(self):
        """
        draw color palette
        """
        pygame.gfxdraw.box(self.drawingwindow, self.col1, self.black)
        pygame.gfxdraw.box(self.drawingwindow, self.col2, self.blue)
        pygame.gfxdraw.box(self.drawingwindow, self.col3, self.red)
        pygame.gfxdraw.box(self.drawingwindow, self.col4, self.green)
        pygame.gfxdraw.box(self.drawingwindow, self.col5, self.pink)
        pygame.gfxdraw.box(self.drawingwindow, self.col6, self.orange)
        pygame.gfxdraw.box(self.drawingwindow, self.col7, self.yellow)
        pygame.gfxdraw.box(self.drawingwindow, self.col8, self.purple)
        pygame.gfxdraw.box(self.drawingwindow, self.col9, self.light_blue)
        pygame.gfxdraw.box(self.drawingwindow, self.col0, self.brown)

    def draw(self, mouse_pos):
        """
        draw by mouse position
        :param mouse_pos: position of the mouse
        :return: if to change to eraser cursor or not
        """
        # Check for button clicks
        mouse = True
        press = False

        if not mouse_pos == (0, 0):
            if 45 < mouse_pos[0] < 660 and 40 < mouse_pos[1] < 462:
                # if in the drawing window - draw by color
                pygame.gfxdraw.filled_ellipse(self.drawingwindow, mouse_pos[0], mouse_pos[1], 4, 4, self.pencolour)

            # change color by position
            elif 800 < mouse_pos[0] < 860 and 78 < mouse_pos[1] < 132:
                # black
                self.pencolour = self.black
                if self.painter:
                    # if painter - print palette with chosen color marked
                    self._drawrectangle()
                self.buttonselect = self.col1
                press = True

            elif 800 < mouse_pos[0] < 860 and 135 < mouse_pos[1] < 189:
                # blue
                self.pencolour = self.blue
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = self.col2
                press = True

            elif 733 < mouse_pos[0] < 797 and 135 < mouse_pos[1] < 189:
                # red
                self.pencolour = self.red
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = self.col3
                press = True

            elif 733 < mouse_pos[0] < 797 and 78 < mouse_pos[1] < 132:
                # green
                self.pencolour = self.green
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = self.col4
                press = True

            elif 733 < mouse_pos[0] < 797 and 191 < mouse_pos[1] < 245:
                # pink
                self.pencolour = self.pink
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = self.col5
                press = True

            elif 733 < mouse_pos[0] < 797 and 247 < mouse_pos[1] < 301:
                # orange
                self.pencolour = self.orange
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = self.col6
                press = True

            elif 800 < mouse_pos[0] < 860 and 247 < mouse_pos[1] < 301:
                # yellow
                self.pencolour = self.yellow
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = self.col7
                press = True

            elif 800 < mouse_pos[0] < 860 and 303 < mouse_pos[1] < 356:
                # purple
                self.pencolour = self.purple
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = self.col8
                press = True

            elif 800 < mouse_pos[0] < 860 and 191 < mouse_pos[1] < 245:
                # light blue
                self.pencolour = self.light_blue
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = self.col9
                press = True

            elif 733 < mouse_pos[0] < 797 and 303 < mouse_pos[1] < 356:
                # brown
                self.pencolour = self.brown
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = self.col0
                press = True

            # Eraser
            elif 730 < mouse_pos[0] < 869 and 383 < mouse_pos[1] < 430:
                self.pencolour = self.white
                if self.painter:
                    self._drawrectangle()
                self.buttonselect = (0, 0, 0, 0)
                press = True    # if button pressed
                mouse = False   # false cause is not regular press - eraser

            # clear
            elif 734 < mouse_pos[0] < 863 and 444 < mouse_pos[1] < 487:
                pygame.gfxdraw.box(self.drawingwindow, self.clearrect, self.white)

        if self.painter:
            # draw the color marking
            pygame.gfxdraw.rectangle(self.drawingwindow, self.buttonselect, self.white)
        pygame.display.update()
        return mouse, press


if __name__ == "__main__":

    # Initializing pygame module
    pygame.init()

    # Screen variables
    screen_width = 900
    screen_height = 506

    drawingwindow = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Skribbl.io")
    drawingwindow.fill((255, 255, 255))

    # Loading backgroud image and drawing it on screen
    backimg = pygame.image.load("guesser.png").convert_alpha()
    drawingwindow.blit(backimg, (0, 0))

    pygame.mouse.set_cursor(*pygame.cursors.broken_x)
    exit_game = False

    paint = Paint(drawingwindow, True)

    # Gameloop
    while not exit_game:

        for event in pygame.event.get():
            mousepos = (0, 0)
            if event.type == pygame.QUIT:
                exit_game = True
            t = pygame.mouse.get_pressed()
            if t[0] == 1:
                mousepos = pygame.mouse.get_pos()
            check = paint.draw(mousepos)
            if check[1] and not check[0]:
                pygame.mouse.set_cursor(*pygame.cursors.diamond)
            elif check[1] and check[0]:
                pygame.mouse.set_cursor(*pygame.cursors.broken_x)
    pygame.quit()


class Player:
    """
    a class that represent a player and keep all required data
    """
    def __init__(self, name, soc, painter):
        """
        initializing player's data
        :param name: player's nickname
        :param soc: player's socket
        :param painter: if the player is the painter or not
        """
        self.name = name
        self.soc = soc
        self.painter = painter
        self.score = 0  # player's score - starts at 0

    def set_painter(self, painter):
        """
        set if the player is the painter or not
        :param painter: True if want to make painter - false if not
        """
        self.painter = painter

    def add_score(self, score_to_add):
        """
        add points to player's score
        :param score_to_add: how many points to add
        """
        self.score += score_to_add

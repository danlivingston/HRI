class OpeningLine:
    def __init__(self, name, hints, moves_uci):
        self.name = name
        self.hints = hints
        self.moves_uci = moves_uci
        self.current_move_index = 0

    def get_name(self):
        return self.name

    def get_hint(self):
        return self.hints[self.current_move_index]

    def increment_move_index(self):
        if self.current_move_index < len(self.moves_uci):
            self.current_move_index += 1

    def reset(self):
        self.current_move_index = 0

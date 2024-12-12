import threading

import chess
from speaker import Speaker
import chess.pgn
import chess.svg
from openings import openings
import random
from voice_recognizer import VoiceRecognizer
from chessboardAnalyzer import ChessCubeAnalyzer
import time


class Game:
    PIECE_NAMES = {
        'K': 'King',
        'Q': 'Queen',
        'R': 'Rook',
        'B': 'Bishop',
        'N': 'Knight',
        'P': 'Pawn'
    }

    def __init__(self):
        self.board = chess.Board()
        self.speaker = Speaker()
        self.opening_line = random.choice(openings)
        self.voice_recognizer = VoiceRecognizer()
        self.is_listening_for_help = False
        self.chessboard_analyzer = ChessCubeAnalyzer(config_path=r'../resources/config/settings.yaml', debug=False)
        self.chessboard_analyzer.initial()

    def update_board(self, move):
        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move in self.board.legal_moves:
                self.speaker.speak(self.expand_san(self.board.san(chess_move)))
                self.board.push(chess_move)
            else:
                print("Illegaler Zug!")
                return False
        except Exception as e:
            print("Ungültiges Format für den Zug!", e)
            return False
        return True

    def save_board_as_svg(self, filename="chess_board.svg"):
        with open(filename, "w") as f:
            f.write(chess.svg.board(board=self.board))
        print(f"Das Schachbrett wurde als {filename} gespeichert. Öffnen Sie die Datei, um es anzusehen.")

    def expand_san(self, san_move):
        if san_move[0] in Game.PIECE_NAMES:
            piece = Game.PIECE_NAMES[san_move[0]]
            position = san_move[1:]
        else:
            piece = "Pawn"
            position = san_move
        position = position.replace("+", "").replace("#", "").split("=")[0]
        return f"{piece} {position.upper()}"

    def print_board_and_save_svg(self):
        print(self.board)
        self.save_board_as_svg()

    def print_result(self):
        print("Das Spiel ist vorbei!")
        print(self.board.result())
        print(self.board)

    def validate_uci(self, uci_move):
        try:
            move = chess.Move.from_uci(uci_move)
            if move in self.board.legal_moves:
                return True
            print("Ungültiger Zug!")
            return False
        except Exception as e:
            print("Ungültiges Format für den Zug!", e)
            return False

    def get_move_input(self, is_white):
        if is_white:
            correct_move = self.opening_line.moves_uci[self.opening_line.current_move_index]
            input_hint = "Weisser Zug (Schachnotation z.B. e2e4) oder 'help' für einen Tipp: "

            # Thread einmalig vor der Schleife starten
            self.is_listening_for_help = True
            t1 = threading.Thread(target=self.listen_for_help, daemon=True)
            t1.start()

            while True:
                #user_input = input(input_hint).lower()
                user_input = self.analyze_player_move_from_camera()

                if user_input == correct_move:
                    print("Correct move")
                    self.is_listening_for_help = False  # Den Thread stoppen
                    t1.join()  # Warten, bis der Thread sauber beendet wird
                    return user_input  # gültiger, erwarteter Zug wird zurückgegeben
                else:
                    print("Das ist nicht der richtige Zug. Versuche es erneut.")
                    self.speaker.speak("That's not the correct move. Try again or ask for help.")
        else:
            # Automatischer Zug für Schwarz
            black_move = self.opening_line.moves_uci[self.opening_line.current_move_index]
            print(f"Schwarzer Zug: {black_move}")
            return black_move

    def listen_for_start(self):
        if self.voice_recognizer.listen_for_start(self.speaker):
            self.play()

    def listen_for_help(self):
        self.speaker.speak("Say 'help' and I will give you the solution")
        while self.is_listening_for_help:
            if self.voice_recognizer.listen_for_help(self.speaker):
                hint = self.opening_line.get_hint()
                print(hint)
                self.speaker.speak(hint)

        print("Exiting thread")

    def analyze_player_move_from_camera(self):
        has_moved = False

        while not has_moved:
            self.chessboard_analyzer.update()
            movement = self.chessboard_analyzer.compareMove()

            if movement == "obstacle detected":
                print("Obstacle detected. Cannot compare moves.")
            elif movement == "initial positions not set":
                print("Initial positions not set. Please set initial positions first by pressing 'i'.")
            elif movement == "updated positions not set":
                print("Updated positions not set. Please update positions first by pressing 'u'.")
            elif movement:
                print(f"Movement detected: {movement}")
                has_moved = True

            time.sleep(5)

        return movement

    def play(self):
        self.print_board_and_save_svg()

        while not self.board.is_game_over():
            if self.board.is_game_over():
                break

            # Weisser Zug - Benutzer muss den korrekten Zug eingeben
            white_move = self.get_move_input(is_white=True)

            if not self.update_board(white_move):
                continue  # ungültiger Zug, Eingabe erneut anfordern
            self.print_board_and_save_svg()
            self.opening_line.increment_move_index()  # Fortschritt in der Eröffnungslinie

            if self.board.is_game_over():
                break

            # Schwarzer Zug - automatisch aus der Eröffnungssequenz
            black_move = self.get_move_input(is_white=False)
            if not self.update_board(black_move):
                print("Automatischer schwarzer Zug war ungültig.")  # Sollte theoretisch nicht passieren
            self.print_board_and_save_svg()
            self.opening_line.increment_move_index()  # Fortschritt in der Eröffnungslinie

        self.print_result()


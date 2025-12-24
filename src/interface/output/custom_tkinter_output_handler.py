# Description: CustomTkinter-based output handler for the Apples to Apples game.

# Standard Libraries
from typing import List, Tuple, TYPE_CHECKING
import logging

# Third-party Libraries
try:
    import customtkinter as ctk
except ImportError:
    logging.error("CustomTkinter not installed. Install with: pip install customtkinter")
    raise ImportError("CustomTkinter is required for this UI. Install with: pip install customtkinter")

# Local Modules
from src.ui.gui.tkinter.tkinter_widgets import GreenAppleCard, RedAppleCard

# Type Checking to prevent circular imports
if TYPE_CHECKING:
    from src.agent_model.agent import Agent
    from src.apples.apples import GreenApple, RedApple


class CustomTkinterOutputHandler(OutputHandler):
    """CustomTkinter implementation of OutputHandler."""

    def __init__(self, root: ctk.CTk):
        """Initialize the CustomTkinter output handler."""
        self.root = root
        self.ui = None  # Will be set later
        self._submitted_red_apples: List[Tuple["Agent", "RedApple"]] = []

    def set_ui(self, ui: "CustomTkinterUI"):
        """Set the UI reference after initialization."""
        self.ui = ui

    def display_message(self, message: str) -> None:
        """Display a general message in the UI."""
        if self.ui and hasattr(self.ui, 'status_label'):
            self.ui.status_label.configure(text=message)
            logging.info(message)
            self.root.update_idletasks()

    def display_error(self, message: str) -> None:
        """Display an error message in the UI."""
        if self.ui and hasattr(self.ui, 'status_label'):
            self.ui.status_label.configure(text=f"ERROR: {message}")
        dialog = CTkMessageBox(self.root, title="Error", message=message, icon="cancel")
        dialog.get()
        logging.error(message)

    def display_new_game_message(self) -> None:
        """Display a message indicating a new game is starting."""
        self.display_message("Starting new game...")

    def display_game_header(self, game_number: int, total_games: int) -> None:
        """Display the game header with game number information."""
        if self.ui:
            self.ui.game_label.configure(text=f"Game: {game_number}/{total_games}")
            self.ui.points_label.configure(text=f"Points to Win: {self.ui.points_to_win}")
        self.display_message(f"Game {game_number} of {total_games}")

    def display_initializing_decks(self) -> None:
        """Display message about initializing decks."""
        self.display_message("Initializing card decks...")

    def display_deck_loaded(self, deck_name: str, count: int) -> None:
        """Display message about a deck being loaded."""
        self.display_message(f"Loaded {count} {deck_name.lower()}.")

    def display_expansion_deck_loaded(self, deck_name: str, count: int) -> None:
        """Display message about an expansion deck being loaded."""
        self.display_message(f"Loaded {count} {deck_name.lower()} from expansion.")

    def display_deck_sizes(self, green_deck_size: int, red_deck_size: int) -> None:
        """Display the sizes of the green and red apple decks."""
        self.display_message(f"Green Apple deck: {green_deck_size} cards, Red Apple deck: {red_deck_size} cards.")

    def display_initializing_players(self) -> None:
        """Display message about initializing players."""
        self.display_message("Initializing players...")

    def display_player_count(self, count: int) -> None:
        """Display the number of players in the game."""
        self.display_message(f"Total players: {count}")

    def display_starting_judge(self, judge_name: str) -> None:
        """Display the name of the starting judge."""
        self.display_message(f"{judge_name} is the starting judge.")

    def display_next_judge(self, judge_name: str) -> None:
        """Display the name of the next judge."""
        self.display_message(f"{judge_name} is the next judge.")

    def display_round_header(self, round_number: int) -> None:
        """Display the round header with round number information."""
        if self.ui:
            self.ui.round_label.configure(text=f"Round: {round_number}")
        self.display_message(f"Round {round_number} starting!")

    def display_player_points(self, player_points: List[Tuple[str, int]]) -> None:
        """Display all players' points."""
        points_str = ", ".join([f"{name}: {points}" for name, points in player_points])
        self.display_message(f"Current points: {points_str}")

        # Update player widgets if they exist
        if self.ui and hasattr(self.ui, 'player_widgets'):
            for player, widget in self.ui.player_widgets.items():
                for name, points in player_points:
                    if player.get_name() == name:
                        widget.update_points(points)

    def prompt_judge_draw_green_apple(self, judge: "Agent") -> None:
        """Prompt the judge to draw a green apple."""
        self.display_message(f"{judge.get_name()}, please draw a green apple.")

    def display_green_apple(self, judge: "Agent", green_apple: "GreenApple") -> None:
        """Display the green apple card in play."""
        message = f"{judge.get_name()} drew the green apple '{green_apple.get_adjective()}'."
        self.display_message(message)

        # Display the green apple card in the UI
        if self.ui and hasattr(self.ui, 'green_apple_card_frame'):
            # Clear existing cards
            for widget in self.ui.green_apple_card_frame.winfo_children():
                widget.destroy()

            # Create the green apple card
            card = GreenAppleCard(self.ui.green_apple_card_frame, green_apple.get_adjective(),
                                  ", ".join(green_apple.get_synonyms() or []))
            card.pack(pady=5)

    def prompt_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Prompt a player to select a red apple."""
        self.display_message(f"{player.get_name()}, select a red apple that goes well with '{green_apple.get_adjective()}'.")

    def display_player_red_apples(self, player: "Agent") -> None:
        """Display the red apples held by a player."""
        if not self.ui:
            logging.error("UI not set for display_player_red_apples.")
            return

        # Update player widgets to show the current player
        for p, widget in self.ui.player_widgets.items():
            widget.set_as_current_player(p == player)

        # Clear existing cards
        for widget in self.ui.player_cards_container.winfo_children():
            widget.destroy()

        # Create frame for cards
        cards_frame = ctk.CTkFrame(self.ui.player_cards_container)
        cards_frame.pack(fill="x")

        # Get red apples from player
        red_apples = player.get_red_apples()

        # Reset tracking lists in UI
        self.ui.active_cards = []
        self.ui.selected_card_index = None

        # Create card widgets with click handlers for human players
        for i, apple in enumerate(red_apples):
            command = None
            if player.is_human():
                command = lambda idx=i: self.ui._handle_card_selection(idx)

            card = RedAppleCard(
                cards_frame,
                apple.get_noun(),
                apple.get_description(),
                command=command
            )
            card.grid(row=i//7, column=i%7, padx=5, pady=5)
            self.ui.active_cards.append(card)

        self.root.update_idletasks()

    def display_red_apple_chosen(self, player: "Agent", red_apple: "RedApple") -> None:
        """Display that a player has chosen a red apple."""
        message = f"{player.get_name()} chose the red apple '{red_apple.get_noun()}'."
        self.display_message(message)

        # Add to submitted cards list
        self._submitted_red_apples.append((player, red_apple))
        self.display_submitted_red_apples(self._submitted_red_apples)

        self.root.update_idletasks()

    def display_submitted_red_apples(self, red_apples: List[Tuple["Agent", "RedApple"]]) -> None:
        """Display all submitted red apple cards."""
        if not self.ui:
            return

        # Clear existing cards
        for widget in self.ui.submitted_cards_container.winfo_children():
            widget.destroy()

        # Create card widgets for each submitted apple
        for player, apple in red_apples:
            frame = ctk.CTkFrame(self.ui.submitted_cards_container)
            frame.pack(side="left", padx=5, pady=5)

            card = RedAppleCard(
                frame,
                apple.get_noun(),
                apple.get_description()
            )
            card.pack()

            # Add player name label
            player_label = ctk.CTkLabel(frame, text=player.get_name())
            player_label.pack()

        self.root.update_idletasks()

    def prompt_judge_select_winner(self, judge: "Agent") -> None:
        """Display prompt for the judge to select the winning red apple."""
        self.display_message(f"{judge.get_name()}, please select the winning red apple.")

    def display_winning_red_apple(self, judge: "Agent", red_apple: "RedApple") -> None:
        """Display the winning red apple card."""
        message = f"{judge.get_name()} chose the winning red apple '{red_apple.get_noun()}'."
        self.display_message(message)

        try:
            # Highlight the winning card
            for widget in self.ui.submitted_cards_container.winfo_children():
                widget.destroy()

            # Display submitted cards with winner highlighted
            winner_found = False
            for player, apple in self._submitted_red_apples:
                is_winner = (apple == red_apple)
                frame = ctk.CTkFrame(self.ui.submitted_cards_container)
                frame.pack(side="left", padx=5, pady=5)

                if is_winner:
                    winner_found = True
                    # Create card with special styling for winner
                    card = RedAppleCard(
                        frame,
                        apple.get_noun(),
                        apple.get_description(),
                        highlight=True
                    )
                    card.pack()

                    # Add winner label
                    winner_label = ctk.CTkLabel(frame, text="WINNER",
                                               text_color=("green", "#00FF00"),
                                               font=("Arial", 12, "bold"))
                    winner_label.pack()

                    # Add player name
                    player_label = ctk.CTkLabel(frame, text=player.get_name())
                    player_label.pack()
                else:
                    # Regular card for non-winners
                    card = RedAppleCard(
                        frame,
                        apple.get_noun(),
                        apple.get_description()
                    )
                    card.pack()

                    # Add player name
                    player_label = ctk.CTkLabel(frame, text=player.get_name())
                    player_label.pack()

            # Process UI events
            self.root.update()
        except Exception as e:
            logging.warning(f"Error in display_winning_red_apple: {e}")

    def display_round_winner(self, winner: "Agent") -> None:
        """Display the round winner."""
        message = f"{winner.get_name()} has won the round!"
        self.display_message(message)

        try:
            # Update UI
            self.root.update()

            # Show dialog
            dialog = CTkMessageBox(self.root, title="Round Winner",
                                  message=message, icon="info")
            dialog.get()

            # Clear submitted red apples
            self._submitted_red_apples = []

            # Update UI again
            self.root.update()
        except Exception as e:
            logging.warning(f"Error in display_round_winner: {e}")
            self._submitted_red_apples = []

    def display_game_winner(self, winner: "Agent") -> None:
        """Display the game winner."""
        message = f"{winner.get_name()} has won the game!"
        self.display_message(message)

        dialog = CTkMessageBox(self.root, title="Game Winner",
                              message=message, icon="info")
        dialog.get()

    def display_game_time(self, minutes: int, seconds: int) -> None:
        """Display the total game time."""
        message = f"Total game time: {minutes} minute(s), {seconds} second(s)"
        self.display_message(message)

    def display_resetting_models(self) -> None:
        """Display message about resetting AI opponent models."""
        self.display_message("Resetting AI opponent models...")

    def display_training_green_apple(self, green_apple_text: str) -> None:
        """Display the green apple card in training mode."""
        self.display_message(f"Training with green apple: {green_apple_text}")

        # Display the card in the UI (if needed)
        if self.ui and hasattr(self.ui, 'green_apple_card_frame'):
            # Clear existing cards
            for widget in self.ui.green_apple_card_frame.winfo_children():
                widget.destroy()

            # Create green apple card
            card = GreenAppleCard(self.ui.green_apple_card_frame, green_apple_text)
            card.pack(pady=5)

    def prompt_training_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Prompt a player to select a red apple in training mode."""
        self.display_message(f"{player.get_name()}, select a red apple that goes well with '{green_apple.get_adjective()}'.")

    def prompt_training_select_bad_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Prompt a player to select a bad red apple in training mode."""
        self.display_message(f"{player.get_name()}, select a red apple that does NOT go well with '{green_apple.get_adjective()}'.")

    # Helper methods
    def log_agent_chose_red_apple(self, agent_name: str, red_apple: "RedApple") -> None:
        """Log that an agent chose a red apple."""
        logging.info(f"{agent_name} chose red apple: {red_apple.get_noun()}")

    def log_model_training(self, agent_name: str, opponent_name: str,
                          green_apple: "GreenApple", winning_red_apple: "RedApple",
                          losing_red_apples: List["RedApple"]) -> None:
        """Log model training information."""
        logging.info(f"{agent_name} trained on {opponent_name}'s preferences for {green_apple.get_adjective()}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        logging.error(message)

    def clear_current_selecting_player(self):
        pass # TODO: implement

    def draw_current_players_hand(self, hand):
        pass

    def draw_game_state(self, state):
        pass

    def get_submitted_red_card_rects(self):
        return []

    def set_current_selecting_player(self, player):
        pass

    def set_state_manager(self, manager):
        self.manager = manager

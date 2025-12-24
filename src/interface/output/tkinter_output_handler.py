# Description: Tkinter-based output handling for Apples to Apples game.

# Standard Libraries
from typing import List, Tuple, TYPE_CHECKING
import logging

# Third-party Libraries
try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    logging.error("Tkinter not installed. Install with: pip install tkinter")
    raise ImportError("Tkinter is required for this UI. Install with: pip install tkinter")

# Local Modules
from src.interface.output.output_handler import OutputHandler
from src.ui.gui.tkinter.tkinter_widgets import GreenAppleCard, RedAppleCard

# Type Checking to prevent circular imports
if TYPE_CHECKING:
    from src.agent_model.agent import Agent
    from src.apples.apples import GreenApple, RedApple
    from src.ui.gui.tkinter.tkinter_ui import TkinterUI


class TkinterOutputHandler(OutputHandler):
    """Implementation of OutputHandler for Tkinter GUI interface."""

    def __init__(self, root: tk.Tk, ui: "TkinterUI"):
        """
        Initialize the Tkinter output handler.

        Args:
            root: The Tkinter root window
            ui: The TkinterUI instance
        """
        self.root = root
        self.ui = ui
        # List to track submitted red apples for UI display purposes
        self._submitted_red_apples: List[Tuple["Agent", "RedApple"]] = []

    def set_ui(self, ui: "TkinterUI") -> None:
        """Set the UI reference after initialization."""
        self.ui = ui

    def display_message(self, message: str) -> None:
        """Display a general message in the UI."""
        if self.ui and hasattr(self.ui, 'status_label'): # Check if UI and widget exist
            self.ui.status_label.config(text=message)
            logging.info(message)
            try:
                # Use update() to ensure status messages appear promptly
                self.root.update()
            except tk.TclError as e:
                 logging.warning(f"Ignoring TclError during root.update() in display_message: {e}")
        else:
            logging.warning("TkinterOutputHandler: UI or status_label not available for display_message.")

    def display_error(self, message: str) -> None:
        """Display an error message in the UI."""
        self.ui.status_label.config(text=f"ERROR: {message}")
        messagebox.showerror("Error", message)
        logging.error(message)
        self.root.update_idletasks()

    def display_new_game_message(self) -> None:
        """Display a message indicating a new game is starting."""
        message = "Starting new 'Apples to Apples' game."
        self.display_message(message)

    def display_game_header(self, game_number: int, total_games: int) -> None:
        """Display the game header with game number information."""
        # Update the UI label without needing to store state in the UI
        self.ui.game_label.config(text=f"Game: {game_number}/{total_games}")
        self.root.update_idletasks()

    def display_round_header(self, round_number: int) -> None:
        """Display the round header with round number information."""
        # Update the UI label without needing to store state in the UI
        self.ui.round_label.config(text=f"Round: {round_number}")
        self.root.update_idletasks()

    def display_initializing_decks(self) -> None:
        """Display message about initializing decks."""
        self.display_message("Initializing decks...")

    def display_deck_loaded(self, deck_name: str, count: int) -> None:
        """Display message about a deck being loaded."""
        self.display_message(f"Loaded {count} {deck_name.lower()}.")

    def display_expansion_deck_loaded(self, deck_name: str, count: int) -> None:
        """Display message about an expansion deck being loaded."""
        self.display_message(f"Loaded {count} {deck_name.lower()} from the expansion.")

    def display_deck_sizes(self, green_deck_size: int, red_deck_size: int) -> None:
        """Display the sizes of the green and red apple decks."""
        self.display_message(f"Green apples: {green_deck_size}, Red apples: {red_deck_size}")

    def display_initializing_players(self) -> None:
        """Display message about initializing players."""
        self.display_message("Initializing players...")

    def display_player_count(self, count: int) -> None:
        """Display the number of players in the game."""
        self.display_message(f"There are {count} players in the game.")
        # Points to win equals the number of players
        self.ui.points_label.config(text=f"Points to Win: {count}")
        self.root.update_idletasks()

    def display_starting_judge(self, judge_name: str) -> None:
        """Display the name of the starting judge."""
        self.display_message(f"{judge_name} is the starting judge.")

        # Update player widgets to show the judge
        for player, widget in self.ui.player_widgets.items():
            widget.set_as_judge(player.get_name() == judge_name)

        self.root.update_idletasks()

    def display_next_judge(self, judge_name: str) -> None:
        """Display the name of the next judge."""
        self.display_message(f"{judge_name} is the next judge.")

        # Update player widgets to show the judge
        for player, widget in self.ui.player_widgets.items():
            widget.set_as_judge(player.get_name() == judge_name)

        self.root.update_idletasks()

    def display_player_points(self, player_points: List[Tuple[str, int]]) -> None:
        """Display all players' points."""
        for name, points in player_points:
            for player, widget in self.ui.player_widgets.items():
                if player.get_name() == name:
                    widget.update_points(points)

        self.root.update_idletasks()

    def display_green_apple(self, judge: "Agent", green_apple: "GreenApple") -> None:
        """Display the green apple card in play."""
        # Clear existing card
        for widget in self.ui.green_apple_card_frame.winfo_children():
            widget.destroy()

        # Create new green apple card
        card = GreenAppleCard.from_green_apple(
            self.ui.green_apple_card_frame,
            green_apple
        )
        card.pack()

        message = f"{judge.get_name()} drew the green apple '{green_apple.get_adjective()}'."
        self.display_message(message)
        self.root.update_idletasks()

    def display_player_red_apples(self, player: "Agent") -> None:
        """Display the red apples held by a player."""
        # Update player widgets to show the current player
        for p, widget in self.ui.player_widgets.items():
            widget.set_as_current_player(p == player)

        # Clear existing cards
        for widget in self.ui.player_cards_container.winfo_children():
            widget.destroy()

        # Create container for cards
        cards_frame = tk.Frame(self.ui.player_cards_container)
        cards_frame.pack(fill=tk.X)

        # Get red apples from player
        red_apples = player.get_red_apples()

        # Reset tracking lists
        self.ui.active_cards = []
        self.ui.selected_card_index = None

        # Remove confirm button if it exists
        if self.ui.confirm_button is not None:
            self.ui.confirm_button.destroy()
            self.ui.confirm_button = None

        # Create card widgets with click handlers for human players
        for i, apple in enumerate(red_apples):
            # Only add click handlers for human players
            command = None
            if player.is_human():
                command = lambda idx=i: self._handle_card_selection(idx)

            card = RedAppleCard.from_red_apple(
                cards_frame,
                apple,
                command=command
            )
            card.grid(row=i//7, column=i%7, padx=5, pady=5)
            self.ui.active_cards.append(card)

        self.root.update_idletasks()

    def _handle_card_selection(self, index: int) -> None:
        """Handle a card being selected by clicking."""
        # Deselect previously selected card if any
        if self.ui.selected_card_index is not None and self.ui.active_cards:
            prev_card = self.ui.active_cards[self.ui.selected_card_index]
            prev_card.config(highlightthickness=0)

        # Select new card
        self.ui.selected_card_index = index
        if index < len(self.ui.active_cards):
            card = self.ui.active_cards[index]
            card.config(highlightbackground="blue", highlightthickness=3)

            # Immediately call the confirmation callback
            if self.ui.on_card_confirm is not None:
                self.ui.on_card_confirm()

    def display_red_apple_chosen(self, player: "Agent", red_apple: "RedApple") -> None:
        """Display that a player has chosen a red apple."""
        message = f"{player.get_name()} chose the red apple '{red_apple.get_noun()}'."
        self.display_message(message)

        # Add to submitted cards (in our local tracking list)
        self._submitted_red_apples.append((player, red_apple))
        self.display_submitted_red_apples(self._submitted_red_apples)

        self.root.update_idletasks()

    def display_winning_red_apple(self, judge: "Agent", red_apple: "RedApple") -> None:
        """Display the winning red apple card."""
        logging.debug(f"Displaying winning red apple: {red_apple.get_noun()} chosen by {judge.get_name()}")
        message = f"{judge.get_name()} chose the winning red apple '{red_apple.get_noun()}'."
        self.display_message(message)

        try:
            # Highlight the winning card in the submitted cards area
            for widget in self.ui.submitted_cards_container.winfo_children():
                widget.destroy()

            # Display submitted cards with winner highlighted
            winner_found = False
            for player, apple in self._submitted_red_apples:
                is_winner = (apple == red_apple)
                frame = tk.Frame(self.ui.submitted_cards_container)
                frame.pack(side=tk.LEFT, padx=5, pady=5)

                if is_winner:
                    winner_found = True
                    # Create card with special styling for winner
                    card = RedAppleCard.from_red_apple(
                        frame,
                        apple
                    )
                    card.config(highlightbackground="gold", highlightthickness=3)
                    card.pack()

                    # Add winner label
                    winner_label = tk.Label(frame, text="WINNER", foreground="green", font=("Arial", 10, "bold"))
                    winner_label.pack()
                else:
                    # Regular card for non-winners
                    card = RedAppleCard.from_red_apple(
                        frame,
                        apple
                    )
                    card.pack()

            # Process UI events BEFORE clearing data
            self.root.update()
        except tk.TclError as e:
            logging.warning(f"TclError in display_winning_red_apple: {e}")

        # Don't clear submitted red apples yet - leave them visible for round winner announcement

    def display_round_winner(self, winner: "Agent") -> None:
        """Display the round winner."""
        logging.debug(f"Display round winner: {winner.get_name()}")
        message = f"{winner.get_name()} has won the round!"
        self.display_message(message)

        try:
            # Process pending events before showing dialog
            self.root.update()

            # Show dialog - this blocks until user acknowledges
            messagebox.showinfo("Round Winner", message)

            # NOW clear the submitted cards after user has seen the results
            self._submitted_red_apples = []

            # Final update to refresh UI
            self.root.update()
        except tk.TclError as e:
            logging.warning(f"TclError in display_round_winner: {e}")
            # Make sure to clear submitted cards even if error occurs
            self._submitted_red_apples = []

    def display_game_winner(self, winner: "Agent") -> None:
        """Display the game winner."""
        message = f"{winner.get_name()} has won the game!"
        self.display_message(message)
        messagebox.showinfo("Game Winner", message)

    def display_game_time(self, minutes: int, seconds: int) -> None:
        """Display the total game time."""
        message = f"Total game time: {minutes} minute(s), {seconds} second(s)"
        self.display_message(message)

    def display_resetting_models(self) -> None:
        """Display message about resetting AI opponent models."""
        self.display_message("Resetting opponent models for all AI agents.")

    def display_training_green_apple(self, green_apple: "GreenApple") -> None:
        """Display the green apple card in training mode."""
        message = f"The green apple is '{green_apple.get_adjective()}'."
        self.display_message(message)

    def prompt_judge_draw_green_apple(self, judge: "Agent") -> None:
        """Display prompt for the judge to draw a green apple."""
        message = f"{judge.get_name()}, please draw a green apple."
        self.display_message(message)

    def prompt_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Display prompt for a player to select a red apple."""
        message = f"{player.get_name()}, please select a red apple."
        self.display_message(message)
        self.display_player_red_apples(player)

    def prompt_training_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Display prompt for a player to select a good red apple in training mode."""
        message = f"{player.get_name()}, please select a good red apple."
        self.display_message(message)
        self.display_player_red_apples(player)

    def prompt_training_select_bad_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Display prompt for a player to select a bad red apple in training mode."""
        message = f"{player.get_name()}, please select a bad red apple."
        self.display_message(message)
        self.display_player_red_apples(player)

    def prompt_judge_select_winner(self, judge: "Agent") -> None:
        """Display prompt for the judge to select the winning red apple."""
        message = f"{judge.get_name()}, please select the winning red apple."
        self.display_message(message)

    def display_submitted_red_apples(self, red_apples: List[Tuple["Agent", "RedApple"]]) -> None:
        """Display all submitted red apple cards."""
        # Clear existing cards
        for widget in self.ui.submitted_cards_container.winfo_children():
            widget.destroy()

        # Create card widgets for each submitted apple
        for player, apple in red_apples:
            frame = tk.Frame(self.ui.submitted_cards_container)
            frame.pack(side=tk.LEFT, padx=5, pady=5)

            card = RedAppleCard.from_red_apple(
                frame,
                apple
            )
            card.pack()

            # Add player name label
            player_label = tk.Label(frame, text=player.get_name())
            player_label.pack()

        self.root.update_idletasks()

    def display_agent_drew_cards(self, agent_name: str, count: int) -> None:
        """Display message that an agent drew cards."""
        message = f"{agent_name} picked up {count} red apple{'s' if count != 1 else ''}."
        self.display_message(message)

    def display_agent_cant_draw_cards(self, agent_name: str) -> None:
        """Display message that an agent cannot draw more cards."""
        message = f"{agent_name} cannot pick up any more red apples."
        self.display_message(message)

    def display_model_reset(self, agent_name: str, opponent_name: str) -> None:
        """Display message that an agent's model for an opponent was reset."""
        message = f"Reset {opponent_name}'s model."
        self.display_message(message)

    def log_agent_chose_red_apple(self, agent_name: str, red_apple: "RedApple") -> None:
        """Log that an agent chose a red apple."""
        logging.info(f"{agent_name} chose the red apple '{red_apple}'.")

    def log_model_training(self, agent_name: str, opponent_name: str,
                          green_apple: "GreenApple", winning_red_apple: "RedApple",
                          losing_red_apples: List["RedApple"]) -> None:
        """Log model training information."""
        message = f"Trained {agent_name}'s model for '{opponent_name}'. Green apple '{green_apple}'. Winning red apple '{winning_red_apple}'."
        logging.debug(message)

    def log_error(self, message: str) -> None:
        """Log an error message."""
        logging.error(message)

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        logging.debug(message)

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

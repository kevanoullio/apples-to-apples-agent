# Description: Terminal-based output handler for the Apples to Apples game.

# Standard Libraries
from typing import List, Tuple, TYPE_CHECKING
import logging

# Third-party Libraries

# Local Modules
from src.interface.output.output_handler import OutputHandler

# Type Checking to prevent circular imports
if TYPE_CHECKING:
    from src.agent_model.agent import Agent
    from src.apples.apples import GreenApple, RedApple
    from src.core.state import GameStateManager


class TerminalOutputHandler(OutputHandler):
    """Implementation of OutputHandler for terminal/console interface."""

    def __init__(self, print_in_terminal: bool = True):
        """
        Initialize the terminal output handler.

        Args:
            print_in_terminal: Whether to print output to the terminal
        """
        self.print_in_terminal = print_in_terminal

    def set_state_manager(self, state_manager: "GameStateManager") -> None:
        """Set the reference to the game state manager."""
        # Terminal handler might not need to store this, but must implement the method
        pass

    def set_current_selecting_player(self, player: "Agent") -> None:
        """Set the current player who is selecting a card."""
        # Terminal handler might not need to store this, but must implement the method
        pass

    def clear_current_selecting_player(self) -> None:
        """Clear the current selecting player."""
        # Terminal handler might not need to store this, but must implement the method
        pass

    def display_message(self, message: str) -> None:
        """Display a general message via terminal output."""
        if self.print_in_terminal:
            print(message)

    def display_error(self, message: str) -> None:
        """Display an error message via terminal output."""
        if self.print_in_terminal:
            print(f"ERROR: {message}")

    def display_new_game_message(self) -> None:
        """Display a message indicating a new game is starting via terminal output."""
        if self.print_in_terminal:
            message = "\nStarting new 'Apples to Apples' game."
            print(message)
            logging.info(message)

    def display_game_header(self, game_number: int, total_games: int) -> None:
        """Display the game header via terminal output."""
        if self.print_in_terminal:
            message = f"\n------------- GAME {game_number} of {total_games} -------------"
            print(message)
            logging.info(message)

    def display_round_header(self, round_number: int) -> None:
        """Display the round header via terminal output."""
        if self.print_in_terminal:
            message = f"\n===================\nROUND {round_number}:\n===================\n"
            print(message)
            logging.info(message)

    def display_initializing_decks(self) -> None:
        """Display message about initializing decks via terminal output."""
        if self.print_in_terminal:
            print("Initializing decks.")

    def display_deck_loaded(self, deck_name: str, count: int) -> None:
        """Display message about a deck being loaded via terminal output."""
        if self.print_in_terminal:
            print(f"Loaded {count} {deck_name.lower()}.")

    def display_expansion_deck_loaded(self, deck_name: str, count: int) -> None:
        """Display message about an expansion deck being loaded via terminal output."""
        if self.print_in_terminal:
            print(f"Loaded {count} {deck_name.lower()} from the expansion.")

    def display_deck_sizes(self, green_deck_size: int, red_deck_size: int) -> None:
        """Display the sizes of the decks via terminal output."""
        if self.print_in_terminal:
            print(f"Size of green apples deck: {green_deck_size}")
            print(f"Size of red apples deck: {red_deck_size}")

    def display_initializing_players(self) -> None:
        """Display message about initializing players via terminal output."""
        if self.print_in_terminal:
            message = "Initializing players."
            print(message)
            logging.info(message)

    def display_player_count(self, count: int) -> None:
        """Display the number of players via terminal output."""
        if self.print_in_terminal:
            message = f"\nThere are {count} player{'s' if count != 1 else ''} in the game."
            print(message)
            logging.info(message)

    def display_starting_judge(self, judge_name: str) -> None:
        """Display the name of the starting judge via terminal output."""
        if self.print_in_terminal:
            print(f"\n{judge_name} is the starting judge.")

    def display_next_judge(self, judge_name: str) -> None:
        """Display the name of the next judge via terminal output."""
        if self.print_in_terminal:
            print(f"{judge_name} is the next judge.")

    def display_player_points(self, player_points: List[Tuple[str, int]]) -> None:
        """Display all players' points via terminal output."""
        if self.print_in_terminal:
            for name, points in player_points:
                print(f"{name}: {points} points")

    def display_green_apple(self, judge: "Agent", green_apple: "GreenApple") -> None:
        """Display the green apple card via terminal output."""
        message = f"\n{judge.get_name()} drew the green apple '{green_apple}'."
        logging.info(message)
        if self.print_in_terminal:
            print(message)

    def display_player_red_apples(self, player: "Agent") -> None:
        """Display the red apples held by a player via terminal output."""
        if self.print_in_terminal:
            message1 = f"\n{player.get_name()}'s red apples:"
            print(message1)
            logging.info(message1)
            for i, red_apple in enumerate(player.get_red_apples()):
                message2 = f"{i + 1}. {red_apple}"
                print(message2)
                logging.info(message2)

    def draw_current_players_hand(self, player: "Agent") -> List:
        """Draw the current player's hand of red apples."""
        if self.print_in_terminal:
            print(f"\n{player.get_name()}'s hand:")
            for i, red_apple in enumerate(player.get_red_apples()):
                print(f"{i + 1}. {red_apple}")
        return player.get_red_apples()

    def display_red_apple_chosen(self, player: "Agent", red_apple: "RedApple") -> None:
        """Display the red apple chosen by a player via terminal output."""
        if self.print_in_terminal:
            message = f"{player.get_name()} chose the red apple '{red_apple.get_noun()}'."
            print(message)
            logging.info(message)

    def display_winning_red_apple(self, judge: "Agent", red_apple: "RedApple") -> None:
        """Display the winning red apple card via terminal output."""
        if self.print_in_terminal:
            message = f"{judge.get_name()} chose the winning red apple '{red_apple.get_noun()}'."
            print(message)
            logging.info(message)

    def display_round_winner(self, winner: "Agent") -> None:
        """Display the round winner via terminal output."""
        if self.print_in_terminal:
            message = f"\n***{winner.get_name()} has won the round!***"
            print(message)
            logging.info(message)

    def display_game_winner(self, winner: "Agent") -> None:
        """Display the game winner via terminal output."""
        if self.print_in_terminal:
            message = f"### {winner.get_name()} has won the game! ###"
            print(message)
            logging.info(message)

    def display_game_time(self, minutes: int, seconds: int) -> None:
        """Display the total game time via terminal output."""
        if self.print_in_terminal:
            message = f"Total game time: {minutes} minute(s), {seconds} second(s)"
            print(message)
            logging.info(message)

    def display_resetting_models(self) -> None:
        """Display message about resetting AI opponent models via terminal output."""
        if self.print_in_terminal:
            print("Resetting opponent models for all AI agents.")

    def display_training_green_apple(self, green_apple: "GreenApple") -> None:
        """Display the green apple card in training mode via terminal output."""
        if self.print_in_terminal:
            message = f"\nThe green apple is '{green_apple.get_adjective()}'."
            print(message)
            logging.info(message)

    # === Prompts for Player Actions ===

    def prompt_judge_draw_green_apple(self, judge: "Agent") -> None:
        """Display prompt for the judge to draw a green apple via terminal output."""
        if self.print_in_terminal:
            message = f"\n{judge.get_name()}, please draw a green apple."
            print(message)
            logging.info(message)

    def prompt_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Display prompt for a player to select a red apple via terminal output."""
        if self.print_in_terminal:
            message = f"\n{player.get_name()}, please select a red apple."
            print(message)
            logging.info(message)

    def prompt_training_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Display prompt for a player to select a good red apple in training mode via terminal output."""
        if self.print_in_terminal:
            message = f"\n{player.get_name()}, please select a good red apple."
            print(message)
            logging.info(message)

    def prompt_training_select_bad_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Display prompt for a player to select a bad red apple in training mode via terminal output."""
        if self.print_in_terminal:
            message = f"\n{player.get_name()}, please select a bad red apple."
            print(message)
            logging.info(message)

    def prompt_judge_select_winner(self, judge: "Agent") -> None:
        """Display prompt for the judge to select the winning red apple via terminal output."""
        if self.print_in_terminal:
            message = f"\n{judge.get_name()}, please select the winning red apple."
            print(message)
            logging.info(message)

    def display_submitted_red_apples(self, red_apples: List[Tuple["Agent", "RedApple"]]) -> None:
        """Display all submitted red apple cards via terminal output."""
        if self.print_in_terminal:
            print("Red cards submitted by the other agents:")
            for i, (agent, red_apple) in enumerate(red_apples):
                print(f"{i + 1}. {red_apple}")

    def display_agent_drew_cards(self, agent_name: str, count: int) -> None:
        """Display message that an agent drew cards via terminal output."""
        if self.print_in_terminal:
            message = f"{agent_name} picked up {count} red apple{'s' if count != 1 else ''}."
            print(message)

    def display_agent_cant_draw_cards(self, agent_name: str) -> None:
        """Display message that an agent cannot draw more cards via terminal output."""
        if self.print_in_terminal:
            message = f"{agent_name} cannot pick up any more red apples. Agent already has enough red apples."
            print(message)

    def display_model_reset(self, agent_name: str, opponent_name: str) -> None:
        """Display message that an agent's model for an opponent was reset via terminal output."""
        if self.print_in_terminal:
            message = f"Reset {opponent_name}'s model."
            print(message)

    def log_agent_chose_red_apple(self, agent_name: str, red_apple: "RedApple") -> None:
        """Log that an agent chose a red apple."""
        logging.info(f"{agent_name} chose the red apple '{red_apple}'.")

    def log_model_training(self, agent_name: str, opponent_name: str,
                          green_apple: "GreenApple", winning_red_apple: "RedApple",
                          losing_red_apples: List["RedApple"]) -> None:
        """Log model training information."""
        message = f"Trained {agent_name}'s model for '{opponent_name}'. Green apple '{green_apple}'. Winning red apple '{winning_red_apple}'."
        if losing_red_apples:
            message += f" Losing red apples: {losing_red_apples}."
        logging.debug(message)

    def log_error(self, message: str) -> None:
        """Log an error message."""
        logging.error(message)

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        logging.debug(message)

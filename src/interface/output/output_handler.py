# Description: Abstract output handling for Apples to Apples game.

# Standard Libraries
from abc import ABC, abstractmethod
from typing import List, Tuple, TYPE_CHECKING

# Third-party Libraries

# Local Modules

# Type Checking to prevent circular imports
if TYPE_CHECKING:
    from src.agent_model.agent import Agent
    from src.apples.apples import GreenApple, RedApple
    from src.core.state import GameStateManager


class OutputHandler(ABC):
    """Abstract class for handling output in various UIs."""

    @abstractmethod
    def set_state_manager(self, state_manager: "GameStateManager") -> None:
        """
        Set the reference to the game state manager.

        Args:
            state_manager: The game state manager instance
        """
        pass

    @abstractmethod
    def set_current_selecting_player(self, player: "Agent") -> None:
        """Set the player who is currently selecting a card."""
        pass

    @abstractmethod
    def clear_current_selecting_player(self) -> None:
        """Clear the current selecting player."""
        pass

    @abstractmethod
    def display_message(self, message: str) -> None:
        """
        Display a general message to the user.

        Args:
            message: The message to display
        """
        pass

    @abstractmethod
    def display_error(self, message: str) -> None:
        """
        Display an error message to the user.

        Args:
            message: The error message to display
        """
        pass

    @abstractmethod
    def display_new_game_message(self) -> None:
        """Display a message indicating a new game is starting."""
        pass

    @abstractmethod
    def display_game_header(self, game_number: int, total_games: int) -> None:
        """
        Display the game header with game number information.

        Args:
            game_number: The current game number
            total_games: The total number of games to play
        """
        pass

    @abstractmethod
    def display_round_header(self, round_number: int) -> None:
        """
        Display the round header with round number information.

        Args:
            round_number: The current round number
        """
        pass

    @abstractmethod
    def display_initializing_decks(self) -> None:
        """Display message about initializing decks."""
        pass

    @abstractmethod
    def display_deck_loaded(self, deck_name: str, count: int) -> None:
        """
        Display message about a deck being loaded.

        Args:
            deck_name: The name of the deck
            count: The number of cards loaded
        """
        pass

    @abstractmethod
    def display_expansion_deck_loaded(self, deck_name: str, count: int) -> None:
        """
        Display message about an expansion deck being loaded.

        Args:
            deck_name: The name of the expansion deck
            count: The number of expansion cards loaded
        """
        pass

    @abstractmethod
    def display_deck_sizes(self, green_deck_size: int, red_deck_size: int) -> None:
        """
        Display the sizes of the green and red apple decks.

        Args:
            green_deck_size: The size of the green apple deck
            red_deck_size: The size of the red apple deck
        """
        pass

    @abstractmethod
    def display_initializing_players(self) -> None:
        """Display message about initializing players."""
        pass

    @abstractmethod
    def display_player_count(self, count: int) -> None:
        """
        Display the number of players in the game.

        Args:
            count: The number of players
        """
        pass

    @abstractmethod
    def display_starting_judge(self, judge_name: str) -> None:
        """
        Display the name of the starting judge.

        Args:
            judge_name: The name of the starting judge
        """
        pass

    @abstractmethod
    def display_next_judge(self, judge_name: str) -> None:
        """
        Display the name of the next judge.

        Args:
            judge_name: The name of the next judge
        """
        pass

    @abstractmethod
    def display_player_points(self, player_points: List[Tuple[str, int]]) -> None:
        """
        Display all players' points.

        Args:
            player_points: List of tuples containing player names and their point totals
        """
        pass

    @abstractmethod
    def display_green_apple(self, judge: "Agent", green_apple: "GreenApple") -> None:
        """
        Display the green apple card in play.

        Args:
            judge: The judge who drew the green apple
            green_apple: The green apple card to display
        """
        pass

    @abstractmethod
    def display_player_red_apples(self, player: "Agent") -> None:
        """
        Display the red apples held by a player.

        Args:
            player: The player whose red apples to display
        """
        pass

    @abstractmethod
    def display_red_apple_chosen(self, player: "Agent", red_apple: "RedApple") -> None:
        """
        Display that a player has chosen a red apple.

        Args:
            player: The player who chose the red apple
            red_apple: The chosen red apple card
        """
        pass

    @abstractmethod
    def display_winning_red_apple(self, judge: "Agent", red_apple: "RedApple") -> None:
        """
        Display the winning red apple card.

        Args:
            judge_name: The name of the judge who made the selection
            red_apple: The winning red apple card
        """
        pass

    @abstractmethod
    def display_round_winner(self, winner: "Agent") -> None:
        """
        Display the round winner.

        Args:
            winner_name: The name of the round winner
        """
        pass

    @abstractmethod
    def display_game_winner(self, winner: "Agent") -> None:
        """
        Display the game winner.

        Args:
            winner_name: The name of the game winner
        """
        pass

    @abstractmethod
    def display_game_time(self, minutes: int, seconds: int) -> None:
        """
        Display the total game time.

        Args:
            minutes: Minutes elapsed
            seconds: Seconds elapsed
        """
        pass

    @abstractmethod
    def display_resetting_models(self) -> None:
        """Display message about resetting AI opponent models."""
        pass

    @abstractmethod
    def display_training_green_apple(self, green_apple: "GreenApple") -> None:
        """
        Display the green apple card in training mode.

        Args:
            adjective: The adjective of the green apple
        """
        pass

    @abstractmethod
    def prompt_judge_draw_green_apple(self, judge: "Agent") -> None:
        """
        Display prompt for the judge to draw a green apple.

        Args:
            judge_name: The name of the judge
        """
        pass

    @abstractmethod
    def prompt_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """
        Display prompt for a player to select a red apple.

        Args:
            player_name: The name of the player
        """
        pass

    @abstractmethod
    def prompt_training_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """
        Display prompt for a player to select a good red apple in training mode.

        Args:
            player: The player selecting the card
        """
        pass

    @abstractmethod
    def prompt_training_select_bad_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """
        Display prompt for a player to select a bad red apple in training mode.

        Args:
            player_name: The name of the player
        """
        pass

    @abstractmethod
    def prompt_judge_select_winner(self, judge: "Agent") -> None:
        """
        Display prompt for the judge to select the winning red apple.

        Args:
            judge_name: The name of the judge
        """
        pass

    @abstractmethod
    def display_submitted_red_apples(self, red_apples: List[Tuple["Agent", "RedApple"]]) -> None:
        """
        Display all submitted red apple cards.

        Args:
            red_apples: List of tuples with agents and their submitted red apples
        """
        pass

    @abstractmethod
    def display_agent_drew_cards(self, agent_name: str, count: int) -> None:
        """
        Display message that an agent drew cards.

        Args:
            agent_name: Name of the agent
            count: Number of cards drawn
        """
        pass

    @abstractmethod
    def display_agent_cant_draw_cards(self, agent_name: str) -> None:
        """
        Display message that an agent cannot draw more cards.

        Args:
            agent_name: Name of the agent
        """
        pass

    @abstractmethod
    def display_model_reset(self, agent_name: str, opponent_name: str) -> None:
        """
        Display message that an agent's model for an opponent was reset.

        Args:
            agent_name: Name of the agent
            opponent_name: Name of the opponent
        """
        pass

    @abstractmethod
    def log_agent_chose_red_apple(self, agent_name: str, red_apple: "RedApple") -> None:
        """
        Log that an agent chose a red apple.

        Args:
            agent_name: Name of the agent
            red_apple: The chosen red apple
        """
        pass

    @abstractmethod
    def log_model_training(self, agent_name: str, opponent_name: str,
                          green_apple: "GreenApple", winning_red_apple: "RedApple",
                          losing_red_apples: List["RedApple"]) -> None:
        """
        Log model training information.

        Args:
            agent_name: Name of the agent being trained
            opponent_name: Name of the opponent/judge
            green_apple: The green apple in play
            winning_red_apple: The winning red apple
            losing_red_apples: List of losing red apples
        """
        pass

    @abstractmethod
    def log_error(self, message: str) -> None:
        """
        Log an error message.

        Args:
            message: Error message to log
        """
        pass

    @abstractmethod
    def log_debug(self, message: str) -> None:
        """
        Log a debug message.

        Args:
            message: Debug message to log
        """
        pass

    # Abstract methods for UI-specific drawing functions
    @abstractmethod
    def draw_game_state(self) -> None:
        """Draw the current game state."""
        pass

    @abstractmethod
    def draw_current_players_hand(self, player: "Agent") -> List:
        """
        Draw the current player's hand.

        Args:
            player: The player whose hand to draw
        """
        pass

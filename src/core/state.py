# Description: Game state management for Apples to Apples.

# Standard Libraries
import logging
from typing import Optional, TYPE_CHECKING, Dict, List, Any

# Local Modules
from src.data_classes.data_classes import (
    GameLog, GameState, RoundState, ApplesInPlay, ChosenApples,
    PathsConfig, GameConfig, ModelConfig, BetweenGameConfig
)

if TYPE_CHECKING:
    from src.agent_model.agent import Agent
    from src.apples.apples import GreenApple, RedApple


class GameStateManager:
    """Manages the state of the Apples to Apples game."""

    def __init__(self, game_log: GameLog,
                 between_game_config: BetweenGameConfig = BetweenGameConfig(),
                 model_config: ModelConfig = ModelConfig()):
        """Initialize the game state manager with game log and configuration."""
        self.game_log = game_log
        self.between_game_config = between_game_config
        self.model_config = model_config

    def start_new_game(self) -> None:
        """Initialize a new game state and add it to the game log."""
        game_state = GameState()
        self.game_log.add_game(game_state)

    def start_new_round(self, judge: "Agent", first_player: "Agent") -> None:
        """Initialize a new round state with the specified judge and first player."""
        round_state = RoundState(current_judge=judge, current_players_turn=first_player)
        self.game_log.add_round(round_state)

    def set_green_apple_in_play(self, green_apple_dict: Dict["Agent", "GreenApple"]) -> None:
        """Set the green apple in play for the current round."""
        self.game_log.set_green_apple_in_play(green_apple_dict)
        self.game_log.set_chosen_green_apple(green_apple_dict)

    def add_red_apple_in_play(self, red_apple_dict: Dict["Agent", "RedApple"]) -> None:
        """Add a red apple to the list of red apples in play for the current round."""
        self.game_log.add_red_apple_in_play(red_apple_dict)

    def set_round_winner(self, winning_red_apple_dict: Dict["Agent", "RedApple"]) -> None:
        """Set the winning red apple and round winner."""
        self.game_log.set_winning_red_apple(winning_red_apple_dict)

        # Set the losing red apples
        apples_in_play = self.game_log.get_apples_in_play()
        for red_apple_dict in apples_in_play.red_apples:
            if red_apple_dict != winning_red_apple_dict:
                self.game_log.add_losing_red_apple(red_apple_dict)

        # Extract the round winner
        round_winner = self.game_log.get_chosen_apples().get_red_apple_winner()

        # Verify the round winner is in the list of players
        if round_winner not in self.game_log.get_game_players():
            logging.error(f"Round winner {round_winner} not in list of players.")
            raise ValueError(f"Round winner {round_winner} not in list of players.")

        # Set the round winner and award the additional point
        self.game_log.set_round_winner(round_winner)

    def check_game_over(self) -> bool:
        """Check if the game is over (any player has reached the points to win)."""
        for player in self.game_log.get_game_players():
            if player.get_points() >= self.game_log.points_to_win:
                self.game_log.set_game_winner(player)
                return True
        return False

    def discard_chosen_apples(self) -> None:
        """Add the chosen apples to the discard pile."""
        self.game_log.discard_chosen_apples(self.game_log.get_chosen_apples())

    def reset_player_points_and_judge_status(self) -> None:
        """Reset player points and judge status for a new game."""
        for player in self.game_log.get_game_players():
            player.reset_points()
            player.set_judge_status(False)

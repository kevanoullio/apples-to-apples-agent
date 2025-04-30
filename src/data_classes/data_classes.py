# Description: Data classes for the game state and preference updates.

# Standard Libraries
from typing import TYPE_CHECKING # Type hinting to avoid circular imports
import os
import logging
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field

# Third-party Libraries

# Local Modules
if TYPE_CHECKING:
    from src.apples.apples import GreenApple, RedApple
    from src.agent_model.agent import Agent
    from src.data_classes.data_classes import PathsConfig


@dataclass
class ApplesInPlay:
    green_apple: dict["Agent", "GreenApple"] | None = None
    red_apples: list[dict["Agent", "RedApple"]] = field(default_factory=list)

    def __post_init__(self) -> None:
        logging.debug(f"Created ApplesInPlay object: {self}")

    def __str__(self) -> str:
        return f"ApplesInPlay(green_apple={self.green_apple}, red_apples={self.red_apples})"

    def to_dict(self) -> dict[str, dict[str, str] | list[dict[str, str]] | None]:
        return {
            "Green Apple": {agent.get_name(): green_apple.get_adjective() for agent, green_apple in self.green_apple.items()} if self.green_apple is not None else None,
            "Red Apples": [{agent.get_name(): red_apple.get_noun() for agent, red_apple in red_apple_dict.items()} for red_apple_dict in self.red_apples]
        }

    def get_green_apple(self) -> "GreenApple":
        if self.green_apple is None:
            raise ValueError("Green apple is not in play.")
        return list(self.green_apple.values())[0]

    def get_red_apples(self) -> list["RedApple"]:
        return list(self.red_apples[0].values())

    def get_green_apple_dict(self) -> dict["Agent", "GreenApple"]:
        if self.green_apple is None:
            raise ValueError("Green apple is not in play.")
        return self.green_apple

    def get_red_apples_dicts(self) -> dict["Agent", "RedApple"]:
        if self.red_apples is None:
            raise ValueError("Red apples are not in play.")
        final_dict = {}
        for red_apple_dict in self.red_apples:
            for agent, red_apple in red_apple_dict.items():
                final_dict[agent] = red_apple
        return final_dict


    def get_red_apple_by_agent(self, agent: "Agent") -> "RedApple | None":
        for red_apple_dict in self.red_apples:
            if agent in red_apple_dict:
                return red_apple_dict[agent]
        return None


@dataclass
class ChosenApples:
    green_apple: dict["Agent", "GreenApple"] = field(default_factory=dict)
    winning_red_apple: dict["Agent", "RedApple"] = field(default_factory=dict)
    losing_red_apples: list[dict["Agent", "RedApple"]] = field(default_factory=list)

    def __post_init__(self) -> None:
        logging.debug(f"Created ChosenApples object: {self}")

    def __str__(self) -> str:
        return f"ChosenApples(green_apple={self.green_apple}, winning_red_apple={self.winning_red_apple}, losing_red_apples={self.losing_red_apples})"

    def to_dict(self) -> dict[str, dict[str, str] | list[dict[str, str]] | None]:
        return {
            "Green Apple": {agent.get_name(): green_apple.get_adjective() for agent, green_apple in self.green_apple.items()} if self.green_apple is not None else None,
            "Winning Red Apple": {agent.get_name(): red_apple.get_noun() for agent, red_apple in self.winning_red_apple.items()} if self.winning_red_apple is not None else None,
            "Losing Red Apples": [{agent.get_name(): red_apple.get_noun() for agent, red_apple in red_apple_dict.items()} for red_apple_dict in self.losing_red_apples]
        }

    def get_green_apple(self) -> "GreenApple":
        if self.green_apple is None:
            raise ValueError("Green apple has not been drawn yet.")
        return list(self.green_apple.values())[0]

    def get_winning_red_apple(self) -> "RedApple":
        if self.winning_red_apple is None:
            raise ValueError("Winning red apple has not been picked yet.")
        return list(self.winning_red_apple.values())[0]

    def get_red_apple_winner(self) -> "Agent":
        if self.winning_red_apple is None:
            raise ValueError("Winning red apple has not been picked yet.")
        return list(self.winning_red_apple.keys())[0]

    def get_losing_red_apples(self) -> list["RedApple"]:
        red_apple_list: list["RedApple"] = []
        for losing_red_apple_dict in self.losing_red_apples:
            for red_apple in losing_red_apple_dict.values():
                red_apple_list.append(red_apple)
        return red_apple_list


@dataclass
class ChosenAppleVectors:
    green_apple_vector: np.ndarray
    winning_red_apple_vector: np.ndarray
    losing_red_apple_vectors: np.ndarray
    green_apple_vector_extra: np.ndarray
    winning_red_apple_vector_extra: np.ndarray
    losing_red_apple_vectors_extra: np.ndarray

    def __post_init__(self) -> None:
        logging.debug(f"Created ChosenAppleVectors object: {self}")

    def __str__(self) -> str:
        return f"ChosenAppleVectors(green_apple_vector={self.green_apple_vector}, "\
               f"winning_red_apple_vector={self.winning_red_apple_vector}, "\
               f"losing_red_apple_vectors={self.losing_red_apple_vectors}, "\
               f"green_apple_vector_extra={self.green_apple_vector_extra}, "\
               f"winning_red_apple_vector_extra={self.winning_red_apple_vector_extra}, "\
               f"losing_red_apple_vectors_extra={self.losing_red_apple_vectors_extra})"


@dataclass
class RoundState:
    current_judge: "Agent" = field(init=True) # Required field, needs to be defined prior to the other fields with default values
    current_players_turn: "Agent" = field(init=True) # Required field, needs to be defined prior to the other fields with default values
    current_round: int = 0 # Initialize to 0, adding first round to GameState will increment to 1
    apples_in_play: ApplesInPlay = field(default_factory=ApplesInPlay)
    chosen_apples: ChosenApples = field(default_factory=ChosenApples)
    round_winner: "Agent | None" = None

    def __post_init__(self) -> None:
        logging.debug(f"Created RoundState object: {self}")

    def __str__(self) -> str:
        return f"RoundState("\
                f"current_round={self.current_round}, "\
                f"current_judge={self.current_judge.get_name()}, "\
                f"current_players_turn={self.current_players_turn.get_name()}, "\
                f"apples_in_play={self.apples_in_play}, "\
                f"chosen_apples={self.chosen_apples}, "\
                f"round_winner={self.round_winner.get_name() if self.round_winner is not None else None})"

    def to_dict(self) -> dict[str, list[str] | str | int | ApplesInPlay | ChosenApples | None]:
        return {
            "current_round": self.current_round,
            "current_judge": self.current_judge.get_name(),
            "current_players_turn": self.current_players_turn.get_name(),
            "apples_in_play": self.apples_in_play if self.apples_in_play is not None else None,
            "chosen_apples": self.chosen_apples if self.chosen_apples is not None else None,
            "round_winner": self.round_winner.get_name() if self.round_winner is not None else None
        }

    def round_winner_to_dict(self) -> dict[str, str | None]:
        return {
            "round_winner": self.round_winner.get_name() if self.round_winner is not None else None
        }

    def set_current_round(self, round_number: int) -> None:
        self.current_round = round_number

    def get_current_round(self) -> int:
        return self.current_round

    def get_current_judge(self) -> "Agent":
        return self.current_judge

    def get_current_players_turn(self) -> "Agent":
        return self.current_players_turn

    def set_green_apple_in_play(self, green_apple_dict: "dict[Agent, GreenApple]") -> None:
        self.apples_in_play.green_apple = green_apple_dict

    def add_red_apple_in_play(self, red_apple_dict: "dict[Agent, RedApple]") -> None:
        self.apples_in_play.red_apples.append(red_apple_dict)

    def get_apples_in_play(self) -> ApplesInPlay:
        return self.apples_in_play

    def set_chosen_green_apple(self, green_apple_dict: "dict[Agent, GreenApple]") -> None:
        self.chosen_apples.green_apple = green_apple_dict

    def set_chosen_winning_red_apple(self, red_apple_dict: "dict[Agent, RedApple]") -> None:
        self.chosen_apples.winning_red_apple = red_apple_dict

    def add_chosen_losing_red_apple(self, red_apple_dict: "dict[Agent, RedApple]") -> None:
        self.chosen_apples.losing_red_apples.append(red_apple_dict)

    def get_chosen_apples(self) -> ChosenApples:
        return self.chosen_apples

    def set_round_winner(self, winner: "Agent") -> None:
        self.round_winner = winner

    def get_round_winner(self) -> "Agent | None":
        return self.round_winner


@dataclass
class GameState:
    current_game: int = 0 # Initialize to 0, adding first game to GameLog will increment to 1
    number_of_players: int = 0 # Smallest number of players is 3 for regular gameplay and 2 for training mode
    game_players: list["Agent"] = field(default_factory=list) # Field ensures that each instance of the dataclass gets its own separate list.
    game_winner: "Agent | None" = None
    round_states: list[RoundState] = field(default_factory=list)
    discard_pile: list[ChosenApples] = field(default_factory=list)
    slope_and_bias_history: dict["Agent", dict["Agent", dict[str, np.ndarray]]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        logging.debug(f"Created GameState object: {self}")

    def __str__(self) -> str:
        return f"GameState("\
                f"current_game={self.current_game}, "\
                f"number_of_players={self.number_of_players}, "\
                f"game_players={[player.get_name() for player in self.game_players]}, "\
                f"game_winner={self.game_winner.get_name() if self.game_winner is not None else None}, "\
                f"round_states={[round_state for round_state in self.round_states]}, "\
                f"discard_pile={[discard.to_dict() for discard in self.discard_pile]}), "\
                f"slope_and_bias_history={[slope_and_bias for slope_and_bias in self.slope_and_bias_history]}"

    def to_dict(self) -> dict[str, list[str] | list[dict] | str | int | ApplesInPlay | None]:
        return {
            "current_game": self.current_game,
            "number_of_players": self.number_of_players,
            "game_players": [player.get_name() for player in self.game_players],
            "game_winner": self.game_winner.get_name() if self.game_winner is not None else None,
            "round_states": [round_state.to_dict() for round_state in self.round_states],
            "discard_pile": [discard.to_dict() for discard in self.discard_pile]
        }

    def round_winner_to_dict(self) -> dict[str, str | None]:
        return self.get_current_round().round_winner_to_dict()

    def game_winner_to_dict(self) -> dict[str, str | None]:
        return {
            "game_winner": self.game_winner.get_name() if self.game_winner is not None else None
        }

    def training_to_dict(self) -> dict[str, list[str] | list[dict] | str | int | ApplesInPlay | None]:
        return {
            "current_game": self.current_game,
            "number_of_players": self.number_of_players,
            "game_players": [player.get_name() for player in self.game_players],
            "game_winner": self.game_winner.get_name() if self.game_winner is not None else None,
            "discard_pile": [discard.to_dict() for discard in self.discard_pile]
        }

    def add_player(self, player: "Agent") -> None:
        self.game_players.append(player)
        self.number_of_players += 1

    def get_number_of_players(self) -> int:
        return self.number_of_players

    def get_current_round(self) -> RoundState:
        if len(self.round_states) == 0:
            message = "No round states have been added."
            logging.error(message)
            raise ValueError(message)
        return self.round_states[-1]

    def add_round(self, round_state: RoundState) -> None:
        # Automatically increment the current round number
        if len(self.round_states) > 0:
            round_state.set_current_round(self.get_current_round().get_current_round() + 1)
        else:
            round_state.set_current_round(1)

        # Add the round state to the list of round states
        self.round_states.append(round_state)

    def get_current_round_number(self) -> int:
        if len(self.round_states) == 0:
            return 0
        return self.get_current_round().get_current_round()

    def get_current_round_judge(self) -> "Agent":
        return self.get_current_round().get_current_judge()

    def set_current_round_green_apple_in_play(self, green_apple_dict: "dict[Agent, GreenApple]") -> None:
        self.get_current_round().set_green_apple_in_play(green_apple_dict)

    def add_current_round_red_apple_in_play(self, red_apple_dict: "dict[Agent, RedApple]") -> None:
        self.get_current_round().add_red_apple_in_play(red_apple_dict)

    def get_current_round_apples_in_play(self) -> ApplesInPlay:
        return self.get_current_round().get_apples_in_play()

    def set_current_round_chosen_green_apple(self, green_apple_dict: "dict[Agent, GreenApple]") -> None:
        self.get_current_round().set_chosen_green_apple(green_apple_dict)

    def set_current_round_chosen_winning_red_apple(self, red_apple_dict: "dict[Agent, RedApple]") -> None:
        self.get_current_round().set_chosen_winning_red_apple(red_apple_dict)

    def add_current_round_chosen_losing_red_apple(self, red_apple_dict: "dict[Agent, RedApple]") -> None:
        self.get_current_round().add_chosen_losing_red_apple(red_apple_dict)

    def get_chosen_apples(self) -> ChosenApples:
        return self.get_current_round().get_chosen_apples()

    def get_current_round_chosen_apples(self) -> ChosenApples:
        return self.get_current_round().get_chosen_apples()

    def set_current_round_winner(self, winner: "Agent") -> None:
        self.get_current_round().set_round_winner(winner)

    def get_current_round_winner(self) -> "Agent | None":
        return self.get_current_round().get_round_winner()

    def discard_chosen_apples(self, chosen_apples: ChosenApples) -> None:
        self.discard_pile.append(chosen_apples)

    def get_discard_pile(self) -> list[ChosenApples]:
        return self.discard_pile

    def add_slope_and_bias(self, player: "Agent", judge: "Agent", slope: np.ndarray, bias: np.ndarray) -> None:
        if player not in self.slope_and_bias_history:
            self.slope_and_bias_history[player] = {}
        self.slope_and_bias_history[player][judge] = {"slope": slope, "bias": bias}

    def get_slope_and_bias_history_by_player(self, player: "Agent") -> dict["Agent", dict[str, np.ndarray]]:
        return self.slope_and_bias_history[player]


@dataclass
class GameLog:
    naming_scheme: str = ""
    total_number_of_players: int = 0
    max_cards_in_hand: int = 0
    points_to_win: int = 0
    total_games: int = 0
    all_game_players: list["Agent"] = field(default_factory=list) # TODO - make this the master list of players, GameState references them so that any change in GameState affects this list
    game_states: list[GameState] = field(default_factory=list)

    def __post_init__(self) -> None:
        logging.debug(f"Created GameLog object: {self}")

    def __str__(self) -> str:
        return f"GameLog("\
                f"naming_scheme={self.naming_scheme}, "\
                f"total_number_of_players={self.total_number_of_players}, "\
                f"all_game_players={[player.get_name() for player in self.all_game_players]}, "\
                f"max_cards_in_hand={self.max_cards_in_hand}, "\
                f"points_to_win={self.points_to_win}, "\
                f"total_games={self.total_games}, "\
                f"game_states={[game for game in self.game_states]})"

    def to_dict(self) -> dict[str, list[str] | int | list[dict]]:
        return {
            "total_number_of_players": self.total_number_of_players,
            "all_game_players": [player.get_name() for player in self.all_game_players],
            "max_cards_in_hand": self.max_cards_in_hand,
            "points_to_win": self.points_to_win,
            "total_games": self.total_games,
            "game_states": [game.to_dict() for game in self.game_states]
        }

    def game_log_to_dict(self) -> dict[str, int | list[str] | str | None]:
        current_judge = self.get_current_judge()
        round_winner = self.get_round_winner()
        game_winner = self.get_game_winner()

        return {
            "points_to_win": self.points_to_win,
            "total_games": self.total_games,
            "current_game": self.get_current_game_number(),
            "current_round": self.get_current_round_number(),
            "number_of_players": self.get_number_of_players(),
            "game_players": [player.get_name() for player in self.get_game_players()],
            "current_judge": current_judge.get_name() if current_judge is not None else None,
            "green_apple": self.get_chosen_apples().get_green_apple().get_adjective(),
            "winning_red_apple": self.get_chosen_apples().get_winning_red_apple().get_noun(),
            "losing_red_apples": [red_apple.get_noun() for red_apple in self.get_chosen_apples().get_losing_red_apples()],
            "round_winner": round_winner.get_name() if round_winner is not None else None,
            "game_winner": game_winner.get_name() if game_winner is not None else None,
        }

    def intialize_input_args(self, total_number_of_players: int, max_cards_in_hand: int, points_to_win: int, total_games: int) -> None:
        self.total_number_of_players = total_number_of_players
        self.max_cards_in_hand = max_cards_in_hand
        self.points_to_win = points_to_win
        self.total_games = total_games

    def __format_players_string(self, players: "list[Agent]") -> str:
        # Initialize the abbreviations lists
        ai_abbrev_list = []
        human_abbrev_list = []
        random_list = []

        # Runtime import to avoid circular dependency
        from src.agent_model.agent import AIAgent, HumanAgent, RandomAgent

        # Abbreviate the player names to the first 3 characters
        for player in players:
            if isinstance(player, AIAgent):
                name: str = player.get_name().lower()
                name_parts: list[str] = name.split("-")
                last_part: str = name_parts[-1].strip()
                ai_abbrev_list.append(last_part[:3])
                # # Example: Extract archetype like 'Lit', 'Com', 'Con'
                # name_parts = player.get_name().split('-')
                # archetype = name_parts[0].strip()[:3] if name_parts else 'AI' # Fallback
                # ai_abbrev_list.append(archetype)
            elif isinstance(player, HumanAgent):
                human_abbrev_list.append("hum")
            elif isinstance(player, RandomAgent):
                random_list.append("rnd")

        # Join the lists into a single string
        ai_abbrev = "_".join(sorted(ai_abbrev_list)) # Sort for consistency

        # Count the number of human players
        human_abbrev = ""
        if len(human_abbrev_list) > 0:
            human_abbrev = f"hum_{len(human_abbrev_list)}"

        # Count the number of random players
        random_abbrev = ""
        if len(random_list) > 0:
            random_abbrev = f"rnd_{len(random_list)}"

        # Join the strings, filtering empty parts
        final_string: str = "-".join(filter(None, [ai_abbrev, human_abbrev, random_abbrev]))
        return final_string

    def __create_final_naming_scheme_string(self, date_string: str, total_games: int, points_to_win: int, players_string: str = "", num: int | None = None) -> str:
        num_string = f"{num}-" if num else ""
        # Ensure players_string is included
        return f"{date_string}{num_string}{total_games}_games-{points_to_win}_pts-{players_string}"

    def format_naming_scheme(self, paths_config: "PathsConfig") -> None:
        """Formats the naming scheme for logging based on game parameters."""
        # Get the current date
        date = datetime.now().strftime("%Y_%m_%d")

        # Get the list of players and format the players string using the internal method
        # Use all_game_players which should be populated before this is called
        if not self.all_game_players:
             logging.warning("Attempting to format naming scheme before all_game_players is populated.")
             players_string = "UNKNOWN_PLAYERS"
        else:
             players_string = self.__format_players_string(self.all_game_players)

        # Format the initial naming scheme
        date_string = f"{date}-"
        num = 1
        final_string = self.__create_final_naming_scheme_string(date_string, self.total_games, self.points_to_win, players_string, num)

        # Check if there already exists a directory with the same naming scheme
        while os.path.exists(os.path.join(paths_config.logging_base_directory, final_string)):
            num += 1
            final_string = self.__create_final_naming_scheme_string(date_string, self.total_games, self.points_to_win, players_string, num)

        # Assign the generated string to the instance variable
        self.naming_scheme = final_string
        logging.info(f"Generated GameLog naming scheme: {self.naming_scheme}")

    def add_game(self, game_state: GameState) -> None:
        # Automatically increment the current game number
        if len(self.game_states) > 0:
            game_state.current_game = self.get_current_game_state().current_game + 1
        else:
            game_state.current_game = 1

        # Add the game state to the list of game states
        self.game_states.append(game_state)

    def add_round(self, round_state: RoundState) -> None:
        self.get_current_game_state().add_round(round_state)

    def get_current_game_state(self) -> GameState:
        """Get the current game state."""
        return self.game_states[-1]

    def get_previous_game_state(self) -> GameState:
        return self.game_states[-2]

    def get_current_game_number(self) -> int:
        if len(self.game_states) == 0:
            message = "No game states have been added."
            logging.error(message)
            raise ValueError(message)
        return self.get_current_game_state().current_game

    def get_number_of_players(self) -> int:
        return self.get_current_game_state().get_number_of_players()

    def get_game_players(self) -> list["Agent"]:
        return self.get_current_game_state().game_players

    def add_player_to_current_game(self, player: "Agent") -> None:
        self.get_current_game_state().add_player(player)

    def sort_players_by_name(self) -> None:
        self.all_game_players.sort(key=lambda x: x.get_name())
        self.get_current_game_state().game_players.sort(key=lambda x: x.get_name())

    def copy_players_to_new_game(self) -> None:
        self.get_current_game_state().game_players = self.get_previous_game_state().game_players.copy()
        self.get_current_game_state().number_of_players = self.get_previous_game_state().number_of_players
        logging.debug(f"Copied players from game {self.get_previous_game_state().current_game} to game {self.get_current_game_state().current_game}")
        logging.debug(f"Players in game {self.get_previous_game_state().current_game}: {[player.get_name() for player in self.get_previous_game_state().game_players]}")
        logging.debug(f"Players in game {self.get_current_game_state().current_game}: {[player.get_name() for player in self.get_current_game_state().game_players]}")
        logging.debug(f"Copied number of players from game {self.get_previous_game_state().current_game} to game {self.get_current_game_state().current_game}")
        logging.debug(f"Number of players in game {self.get_previous_game_state().current_game}: {self.get_previous_game_state().number_of_players}")
        logging.debug(f"Number of players in game {self.get_current_game_state().current_game}: {self.get_current_game_state().number_of_players}")

    def set_game_winner(self, winner: "Agent") -> None:
        self.get_current_game_state().game_winner = winner

    def get_game_winner(self) -> "Agent | None":
        return self.get_current_game_state().game_winner

    def discard_chosen_apples(self, chosen_apples: ChosenApples) -> None:
        self.get_current_game_state().discard_chosen_apples(chosen_apples)

    def get_discard_pile(self) -> list[ChosenApples]:
        return self.get_current_game_state().get_discard_pile()

    def get_current_round_number(self) -> int:
        if len(self.game_states) == 0:
            message = "No game states have been added."
            logging.error(message)
            raise ValueError(message)
        return self.get_current_game_state().get_current_round_number()

    def get_current_judge(self) -> "Agent":
        return self.get_current_game_state().get_current_round_judge()

    def set_current_judge(self, judge: "Agent") -> None:
        self.get_current_game_state().get_current_round().current_judge = judge

    def get_current_players_turn(self) -> "Agent":
        """Get the player whose turn it currently is."""
        return self.get_current_game_state().get_current_round().get_current_players_turn()

    def set_current_players_turn(self, player: "Agent") -> None:
        """Set the current player's turn."""
        self.get_current_game_state().get_current_round().current_players_turn = player

    def set_green_apple_in_play(self, green_apple_dict: "dict[Agent, GreenApple]") -> None:
        self.get_current_game_state().set_current_round_green_apple_in_play(green_apple_dict)

    def add_red_apple_in_play(self, red_apple_dict: "dict[Agent, RedApple]") -> None:
        self.get_current_game_state().add_current_round_red_apple_in_play(red_apple_dict)

    def get_apples_in_play(self) -> ApplesInPlay:
        return self.get_current_game_state().get_current_round_apples_in_play()

    def set_chosen_green_apple(self, green_apple_dict: "dict[Agent, GreenApple]") -> None:
        self.get_current_game_state().set_current_round_chosen_green_apple(green_apple_dict)

    def set_winning_red_apple(self, red_apple_dict: "dict[Agent, RedApple]") -> None:
        self.get_current_game_state().set_current_round_chosen_winning_red_apple(red_apple_dict)

    def add_losing_red_apple(self, red_apple_dict: "dict[Agent, RedApple]") -> None:
        self.get_current_game_state().add_current_round_chosen_losing_red_apple(red_apple_dict)

    def get_chosen_apples(self) -> ChosenApples:
        return self.get_current_game_state().get_current_round_chosen_apples()

    def set_round_winner(self, winner: "Agent") -> None:
        self.get_current_game_state().set_current_round_winner(winner)
        current_round_winner: Agent | None = self.get_current_game_state().get_current_round_winner()
        logging.debug(f"Current round winner: {current_round_winner.get_name() if current_round_winner is not None else None}")
        if current_round_winner is not None:
            current_round_winner.set_points(winner.get_points() + 1)
        else:
            message = "Current round winner is None."
            logging.error(message)
            raise ValueError(message)

    def get_round_winner(self) -> "Agent | None":
        return self.get_current_game_state().get_current_round_winner()

    def get_rounds_per_game(self) -> dict[int, int]:
        rounds_per_game = {}
        for game in self.game_states:
            current_game = game.current_game
            total_rounds = game.get_current_round_number()
            rounds_per_game[current_game] = total_rounds
        return rounds_per_game

    def get_slope_and_bias_history_by_player(self, player: "Agent") -> dict["Agent", dict[str, list[np.ndarray]]]:
        slope_and_bias_history_by_player: dict["Agent", dict[str, list[np.ndarray]]] = {}
        for game in self.game_states:
            tmp_slope_and_bias_history = game.get_slope_and_bias_history_by_player(player)
            for judge, slope_and_bias in tmp_slope_and_bias_history.items():
                if judge not in slope_and_bias_history_by_player:
                    slope_and_bias_history_by_player[judge] = {"slope": [], "bias": []}
                slope_and_bias_history_by_player[judge]["slope"].append(slope_and_bias["slope"])
                slope_and_bias_history_by_player[judge]["bias"].append(slope_and_bias["bias"])
        return slope_and_bias_history_by_player


@dataclass
class PreferenceUpdates:
    judge: "Agent"
    player: "Agent"
    game: int
    round: int
    datetime: str
    green_apple: "GreenApple"
    winning_red_apple: "RedApple"
    slope: np.ndarray
    bias: np.ndarray

    def __str__(self) -> str:
        return f"PreferenceUpdates(judge={self.judge.get_name()}, player={self.player.get_name()}, game={self.game}, round={self.round}, "\
               f"datetime={self.datetime}, green apple={self.green_apple.get_adjective()}, winning red apple={self.winning_red_apple.get_noun()}, "\
               f"slope={self.slope}), bias={self.bias}"

    def to_dict(self) -> dict:
        return {
            "judge": self.judge.get_name(),
            "player": self.player.get_name(),
            "game": self.game,
            "round": self.round,
            "datetime": self.datetime,
            "green_apple": self.green_apple.get_adjective(),
            "winning_red_apple": self.winning_red_apple.get_noun(),
            "slope": f"{self.slope}\n",
            "bias": f"{self.bias}\n"
        }


# Configuration classes
@dataclass
class PathsConfig:
    """Configuration settings related to file paths."""
    data_base: str = "./data"
    embeddings: str = "./data/embeddings/GoogleNews-vectors-negative300.bin"
    apples_data: str = "./data/apples"
    model_archetypes: str = "./data/agent_archetypes"
    logging_base_directory: str = "./logs"
    logging_filename: str = "a2a_game.log"
    analysis_output: str = "./analysis_results"

@dataclass
class GameConfig:
    """Configuration settings related to general game rules."""
    default_max_cards_in_hand: int = 7
    training_max_cards_in_hand: int = 25
    training_num_players: int = 2

@dataclass
class ModelConfig:
    """Configuration settings related to AI models."""
    use_extra_vectors: bool = True
    # Add other model-specific settings here if needed
    # learning_rate: float = 0.01

@dataclass
class BetweenGameConfig:
    """Configuration settings for between game options."""
    change_players: bool = False
    cycle_starting_judges: bool = False
    reset_models: bool = False
    reset_cards: bool = False # For training mode


if __name__ == "__main__":
    pass

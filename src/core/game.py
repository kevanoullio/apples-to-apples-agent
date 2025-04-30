# Description: Core game logic for Apples to Apples.

# Standard Libraries
import logging
import time
import os
from typing import Dict, List, Optional, Any, TYPE_CHECKING

# Local Modules
from src.apples.apples import GreenApple, RedApple, Deck
from src.agent_model.agent import Agent, HumanAgent, RandomAgent, AIAgent
from src.agent_model.model import model_type_mapping
from src.logging.game_logger import (
    log_vectors, log_game_state, log_round_winner, log_game_winner, log_training_mode
)
from src.data_classes.data_classes import (
    RoundState, GameState, GameLog, ApplesInPlay,
    PathsConfig, GameConfig, ModelConfig, BetweenGameConfig
)
from src.core.state import GameStateManager

if TYPE_CHECKING:
    from src.embeddings.embeddings import Embedding
    from src.interface.game_interface import GameInterface


class ApplesToApples:
    """Core game logic for Apples to Apples, UI-agnostic."""

    def __init__(self,
                 embedding: "Embedding",
                 interface: "GameInterface",
                 paths_config: PathsConfig = PathsConfig(),
                 game_config: GameConfig = GameConfig(),
                 training_mode: bool = False,
                 load_all_packs: bool = False,
                 green_expansion: str = '',
                 red_expansion: str = '') -> None:
        """
        Initialize the Apples to Apples game.

        Args:
            embedding: The word embedding model
            interface: Interface for user interaction
            paths_config: Configuration for file paths
            game_config: Configuration for game rules
            training_mode: Whether the game is in training mode
            load_all_packs: Whether to load all card packs
            green_expansion_filename: Filename for green apple expansion
            red_expansion_filename: Filename for red apple expansion
            green_apples_deck: Deck of green apples
            red_apples_deck: Deck of red apples
        """
        self.__embedding = embedding
        self.__interface = interface
        self.__paths_config = paths_config
        self.__game_config = game_config
        self.__training_mode = training_mode
        self.__load_all_packs = load_all_packs
        self.__green_expansion_filename = green_expansion
        self.__red_expansion_filename = red_expansion
        self.__green_apples_deck = Deck()
        self.__red_apples_deck = Deck()
        # self.__game_log: Optional[GameLog] = None
        # self.__between_game_config: Optional[BetweenGameConfig] = None
        # self.__model_config: Optional[ModelConfig] = None
        # self.__state_manager: Optional[GameStateManager] = None

    def initalize_game_log(self, game_log: GameLog) -> None:
        """Sets the GameLog instance for the game."""
        self.__game_log = game_log
        logging.info("GameLog initialized in ApplesToApples.")
        # Initialize the state manager
        self.__state_manager = GameStateManager(game_log)

        # Connect the state manager to the output handler
        if hasattr(self.__interface, "output_handler"):
            output_handler = self.__interface.output_handler
            if hasattr(output_handler, "set_state_manager"):
                output_handler.set_state_manager(self.__state_manager)
                logging.info("Set state manager reference in output handler")

    def get_game_log(self) -> GameLog:
        """Returns the current GameLog instance. Raises RuntimeError if not initialized."""
        if self.__game_log is None:
            message = "GameLog has not been initialized yet. Call initalize_game_log() first."
            logging.error(message)
            raise RuntimeError(message)
        return self.__game_log

    def set_game_options(self,
                         between_game_config: BetweenGameConfig = BetweenGameConfig(),
                         model_config: ModelConfig = ModelConfig()
                        ) -> None:
        """Set game options for between-game configuration and model configuration."""
        self.__between_game_config = between_game_config
        self.__model_config = model_config
        if self.__state_manager:
            self.__state_manager.between_game_config = between_game_config
            self.__state_manager.model_config = model_config

        logging.info(f"ApplesToApples using options: change_players={between_game_config.change_players}, "
                     f"cycle_judges={between_game_config.cycle_starting_judges}, "
                     f"reset_models={between_game_config.reset_models}, "
                     f"reset_cards={between_game_config.reset_cards}, "
                     f"use_extra_vectors={model_config.use_extra_vectors}")

    def new_game(self) -> None:
        """
        Start a new game of 'Apples to Apples' and reset the game state.
        Optionally, initialize new players.
        """
        self.__interface.display_new_game_message()

        # Start the game timer
        logging.info("Starting the game timer.")
        start = time.perf_counter()

        # Initialize the GameState and add the game
        self.__state_manager.start_new_game()
        game_number = self.__game_log.get_current_game_number()
        total_games = self.__game_log.total_games

        # Display game information
        self.__interface.display_game_header(game_number, total_games)

        # Initialize the decks
        self.__initialize_decks()

        # Initialize the players for the first game
        if game_number == 1:
            self.__initialize_players()
        elif game_number > 1:
            # Handle player management for subsequent games
            if self.__between_game_config.change_players:
                keep_players = self.__interface.prompt_keep_players_between_games()
                if not keep_players:
                    self.__initialize_players()
                else:
                    self.__game_log.copy_players_to_new_game()
                    logging.info("Keeping the same players as last game.")
            else:
                # Copy players over to the new game
                self.__game_log.copy_players_to_new_game()

            # Reset the player points and judge status
            logging.info("Resetting player points and judge status.")
            self.__state_manager.reset_player_points_and_judge_status()

            # Reset the opponent models for the AI agents, if applicable
            if self.__between_game_config.reset_models:
                self.__reset_opponent_models()

            # Reset the red apples in hand for all players, if applicable
            if self.__training_mode and self.__between_game_config.reset_cards:
                for player in self.__game_log.get_game_players():
                    if isinstance(player, HumanAgent):
                        player.reset_red_apples()
                        player.draw_red_apples(self.__embedding, self.__red_apples_deck,
                                              self.__game_log.max_cards_in_hand,
                                              self.__model_config.use_extra_vectors)

        # Start the game loop
        self.__game_loop()

        # Stop the game timer
        end = time.perf_counter()

        # Calculate and display elapsed time
        total_time = end - start
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)

        self.__interface.display_game_time(minutes, seconds)

    def __initialize_decks(self) -> None:
        """Initialize the green and red apple decks."""
        logging.info("Initializing decks.")
        self.__interface.display_initializing_decks()

        # Clear the decks
        self.__green_apples_deck.clear_deck()
        self.__red_apples_deck.clear_deck()

        # Load and shuffle the decks
        if self.__load_all_packs:
            self.__load_and_shuffle_deck(self.__green_apples_deck, "Green Apples",
                                         f"{self.__paths_config.apples_data}/green_apples-all.csv")
            self.__load_and_shuffle_deck(self.__red_apples_deck, "Red Apples",
                                         f"{self.__paths_config.apples_data}/red_apples-all.csv")
        else:
            self.__load_and_shuffle_deck(self.__green_apples_deck, "Green Apples",
                                        f"{self.__paths_config.apples_data}/green_apples-basic_set_party_set.csv",
                                        self.__green_expansion_filename)
            self.__load_and_shuffle_deck(self.__red_apples_deck, "Red Apples",
                                        f"{self.__paths_config.apples_data}/red_apples-basic_set_party_set.csv",
                                        self.__red_expansion_filename)

        # Display deck sizes
        self.__interface.display_deck_sizes(
            len(self.__green_apples_deck.get_apples()),
            len(self.__red_apples_deck.get_apples())
        )

    def __load_and_shuffle_deck(self, deck: Deck, deck_name: str, base_file: str, expansion_file: str = '') -> None:
        """Load and shuffle a deck of cards from files."""
        # Load the base deck
        deck.load_deck(deck_name, base_file)
        count = len(deck.get_apples())
        logging.info(f"Loaded {count} {deck_name.lower()}.")
        self.__interface.display_deck_loaded(deck_name, count)

        # Load the expansion deck, if applicable
        if expansion_file:
            deck.load_deck(f"{deck_name} Expansion", expansion_file)
            expansion_count = len(deck.get_apples()) - count
            logging.info(f"Loaded {expansion_count} {deck_name.lower()} from the expansion.")
            self.__interface.display_expansion_deck_loaded(deck_name, expansion_count)

        # Shuffle the deck
        deck.shuffle()

    def __generate_unique_agent_name(self, base_name: str) -> str:
        """Generate a unique agent name based on existing agents."""
        # Unpack the existing names (from the game log, not just current game players)
        existing_names = [agent.get_name() for agent in self.__game_log.all_game_players]

        # Generate a unique name
        i = 1
        while f"{base_name} {i}" in existing_names:
            i += 1
        return f"{base_name} {i}"

    def __initialize_players(self) -> None:
        """Initialize the players for the game."""
        self.__interface.display_initializing_players()

        player_count = self.__game_log.total_number_of_players
        self.__interface.display_player_count(player_count)

        if self.__training_mode:
            # For training mode - specific initialization
            self.__initialize_training_players()
        else:
            # For regular game - prompt for player types
            self.__initialize_regular_players()

        # Sort the players alphabetically by name
        self.__game_log.sort_players_by_name()

        # Initialize the models for the AI agents
        for player in self.__game_log.get_game_players():
            if isinstance(player, AIAgent):
                player.initialize_models(self.__embedding, self.__paths_config, self.__game_log.get_game_players())
                logging.info(f"Initialized models for {player.get_name()}.")

        # Format the naming scheme AFTER players are initialized and sorted
        self.__game_log.format_naming_scheme(self.__paths_config)
        logging.info(f"Generated logging naming scheme: {self.__game_log.naming_scheme}")

        # After players are created and added to the game_log
        # Set the input handler for all agents
        for player in self.__game_log.get_game_players():
            # Pass the interface's input handler to each agent
            player.set_input_handler(self.__interface.input_handler)

    def __initialize_training_players(self) -> None:
        """Initialize players specifically for training mode."""
        # Get model type from interface
        model_type = self.__interface.prompt_training_model_type()

        # Get pretrained model type from interface
        pretrained_model_type = self.__interface.prompt_training_pretrained_type()

        # Map the selected model type to its class
        model_type_class = model_type_mapping[model_type]
        logging.debug(f"Model Type Class: {model_type_class.__name__}")

        # Map the pretrained model selection to a string
        pretrained_model_string = {
            '1': "Literalist",
            '2': "Contrarian",
            '3': "Comedian"
        }[pretrained_model_type]
        logging.debug(f"Pretrained Model String: {pretrained_model_string}")

        # Create the AI agent
        new_agent_name = f"AI Agent - {model_type_class.__name__} - {pretrained_model_string}"
        new_agent = AIAgent(
            new_agent_name,
            model_type_class,
            self.__paths_config,
            pretrained_model_string,
            self.__model_config.use_extra_vectors,
            True  # training mode
        )

        # Create the human agent
        human_agent = HumanAgent("Human Agent")

        # Have the human agent pick up cards
        human_agent.draw_red_apples(
            self.__embedding,
            self.__red_apples_deck,
            self.__game_log.max_cards_in_hand,
            self.__model_config.use_extra_vectors
        )

        # Add the agents to the game log and current game
        self.__game_log.add_player_to_current_game(human_agent)  # Human first!
        self.__game_log.add_player_to_current_game(new_agent)
        self.__game_log.all_game_players.append(human_agent)
        self.__game_log.all_game_players.append(new_agent)

        logging.info(f"Added new human player {human_agent.get_name()}.")
        logging.info(f"Added new AI agent {new_agent.get_name()}.")

    def __initialize_regular_players(self) -> None:
        """Initialize players for a regular (non-training) game."""
        for i in range(self.__game_log.total_number_of_players):
            # Get player type from interface
            player_type = self.__interface.prompt_player_type(i + 1)

            if player_type == '1':  # Human
                # Get player name from interface
                name = self.__interface.prompt_human_player_name()
                new_agent = HumanAgent(f"Human Agent - {name}")

            elif player_type == '2':  # Random
                new_agent_name = self.__generate_unique_agent_name("Random Agent")
                new_agent = RandomAgent(new_agent_name)

            elif player_type == '3':  # AI
                # Get machine learning model type
                ml_model_type = self.__interface.prompt_ai_model_type()

                # Get pretrained archetype
                pretrained_archetype = self.__interface.prompt_ai_archetype()

                # Map selections to appropriate types
                ml_model_type_class = model_type_mapping[ml_model_type]
                pretrained_archetype_string = {
                    '1': "Literalist",
                    '2': "Contrarian",
                    '3': "Comedian"
                }[pretrained_archetype]

                # Create AI agent
                new_agent_name = self.__generate_unique_agent_name(
                    f"AI Agent - {ml_model_type_class.__name__} - {pretrained_archetype_string}"
                )
                new_agent = AIAgent(
                    new_agent_name,
                    ml_model_type_class,
                    self.__paths_config,
                    pretrained_archetype_string,
                    self.__model_config.use_extra_vectors,
                    training_mode=False
                )

            # Add the new agent to the game
            self.__game_log.add_player_to_current_game(new_agent)
            self.__game_log.all_game_players.append(new_agent)
            logging.info(f"Added new player {new_agent.get_name()}")

            # Draw initial cards
            new_agent.draw_red_apples(
                self.__embedding,
                self.__red_apples_deck,
                self.__game_log.max_cards_in_hand,
                self.__model_config.use_extra_vectors
            )

    def __determine_starting_judge(self) -> Agent:
        """Choose the starting judge for a game."""
        # Clear judge status for all players
        for i, player in enumerate(self.__game_log.get_game_players()):
            self.__game_log.get_game_players()[i].set_judge_status(False)

        if self.__training_mode:
            # In training mode, always choose the AI agent as judge
            for player in self.__game_log.get_game_players():
                if isinstance(player, AIAgent):
                    judge_index = self.__game_log.get_game_players().index(player)
                    break
        else:
            # If cycle starting judge is True, choose the starting judge automatically
            if self.__between_game_config.cycle_starting_judges:
                # Automatically cycle through judges
                game_num = self.__game_log.get_current_game_number()
                player_count = self.__game_log.total_number_of_players
                judge_index = ((game_num - 1) % player_count) # Subtract 1 since 0-based index and current_game starts at 1
            else: # If cycle starting judge is False, prompt the user to choose the starting judge
                # Let the interface choose the judge
                if self.__between_game_config.change_players:
                    player_count = self.__game_log.get_number_of_players()
                    judge_index = self.__interface.prompt_starting_judge(player_count) - 1
                else:
                    judge_index = 0
        next_judge: "Agent" = self.__game_log.get_game_players()[judge_index]
        next_judge.set_judge_status(True)
        return next_judge

    def __determine_next_judge(self) -> Agent:
        """Determine the next judge for a round."""
        # If first round, choose the starting judge
        if self.__game_log.get_current_round_number() == 0:
            # Choose the starting judge and set the judge status
            next_judge = self.__determine_starting_judge()
            next_judge.set_judge_status(True)

            self.__interface.display_starting_judge(next_judge.get_name())
            logging.info(f"{next_judge.get_name()} is the starting judge.")
        else:
            # Determine the next judge (in training mode, judge stays the same)
            if self.__training_mode:
                next_judge = self.__game_log.get_current_judge()
            else:
                # Get current judge and remove judge status
                current_judge = self.__game_log.get_current_judge()
                current_judge.set_judge_status(False)

                # Find the next judge (cyclically)
                player_count = self.__game_log.get_number_of_players()
                current_index = self.__game_log.get_game_players().index(current_judge)
                next_index = (current_index + 1) % player_count
                next_judge = self.__game_log.get_game_players()[next_index]
                next_judge.set_judge_status(True)

                self.__interface.display_next_judge(next_judge.get_name())
                logging.info(f"{next_judge.get_name()} is the next judge.")

        return next_judge

    def __new_round(self) -> None:
        """Start a new round of the game."""
        # For the first round, determine the starting judge
        if self.__game_log.get_current_round_number() == 0:
            next_judge = self.__determine_starting_judge()
        else:
            # For subsequent rounds, determine the next judge
            next_judge = self.__determine_next_judge()

        # Find the first non-judge player to start the round
        players = self.__game_log.get_game_players()
        judge_index = players.index(next_judge)
        first_player_index = (judge_index + 1) % len(players)
        first_player = players[first_player_index]

        # Initialize the round state with both judge and first player's turn
        round_state = RoundState(current_judge=next_judge, current_players_turn=first_player)
        self.__game_log.add_round(round_state)

        # Display round number
        round_number = self.__game_log.get_current_round_number()
        self.__interface.display_round_header(round_number)

        # Display player points
        if not self.__training_mode:
            player_points = []
            for player in self.__game_log.get_game_players():
                player_points.append((player.get_name(), player.get_points()))
                logging.info(f"{player.get_name()}: {player.get_points()} points")

            self.__interface.display_player_points(player_points)

    def __prompt_judge_draw_green_apple(self) -> None:
        """Prompt the judge to draw a green apple."""
        current_judge = self.__game_log.get_current_judge()

        # Prompt through the interface
        self.__interface.prompt_judge_draw_green_apple(current_judge)

        # Draw the green apple
        green_apple_dict: dict[Agent, GreenApple] = current_judge.draw_green_apple(
            self.__embedding,
            self.__green_apples_deck,
            self.__model_config.use_extra_vectors
        )

        # Update the game state
        self.__state_manager.set_green_apple_in_play(green_apple_dict)

        # Display the drawn green apple
        green_apple = list(green_apple_dict.values())[0]
        self.__interface.display_green_apple(current_judge, green_apple)

    def __prompt_players_select_red_apples(self) -> None:
        """Prompt players to select red apples to play."""
        # Get the current judge and green apple
        current_judge = self.__game_log.get_current_judge()
        green_apple = self.__game_log.get_apples_in_play().get_green_apple()

        # Get the list of all players
        players = self.__game_log.get_game_players()
        player_count = len(players)

        # Initialize a counter to track how many players have played
        players_remaining = player_count - 1  # exclude judge

        while players_remaining > 0:
            # Get current player
            current_player = self.__game_log.get_current_players_turn()

            # Prompt player to select a red apple
            if self.__training_mode:
                self.__interface.display_training_green_apple(green_apple.get_adjective())
                self.__interface.display_player_red_apples(current_player)
                self.__interface.prompt_training_select_red_apple(current_player, green_apple)
            else:
                self.__interface.display_green_apple(current_judge, green_apple)
                self.__interface.display_player_red_apples(current_player)
                self.__interface.prompt_select_red_apple(current_player, green_apple)

            # Let the player choose a red card from their hand
            chosen_red_apple_dict: dict[Agent, RedApple] = current_player.choose_red_apple(current_judge, green_apple)
            self.__state_manager.add_red_apple_in_play(chosen_red_apple_dict)
            self.__interface.display_red_apple_chosen(current_player, chosen_red_apple_dict[current_player])

            # For training mode, prompt for a bad red apple too
            if self.__training_mode:
                self.__interface.display_training_green_apple(green_apple.get_adjective())
                self.__interface.display_player_red_apples(current_player)
                self.__interface.prompt_training_select_bad_red_apple(current_player, green_apple)

                # Choose a bad red apple
                bad_red_apple_dict: dict[Agent, RedApple] = current_player.choose_red_apple(current_judge, green_apple)
                self.__state_manager.add_red_apple_in_play(bad_red_apple_dict)
                self.__interface.display_red_apple_chosen(current_player, chosen_red_apple_dict[current_player])

            # Draw new cards if needed
            if len(current_player.get_red_apples()) < self.__game_log.max_cards_in_hand:
                current_player.draw_red_apples(
                    self.__embedding,
                    self.__red_apples_deck,
                    self.__game_log.max_cards_in_hand,
                    self.__model_config.use_extra_vectors
                )

            # Advance to the next player's turn
            judge_index = players.index(current_judge)
            current_index = players.index(current_player)

            # Find next player, skipping the judge
            next_index = (current_index + 1) % player_count
            if next_index == judge_index:
                next_index = (next_index + 1) % player_count

            # Set the next player as the current player's turn
            next_player = players[next_index]
            self.__game_log.set_current_players_turn(next_player)

            players_remaining -= 1

        # Clear current player indicator when done
        if hasattr(self.__interface, "output_handler") and hasattr(self.__interface.output_handler, "clear_current_selecting_player"):
            self.__interface.output_handler.clear_current_selecting_player()

    def __determine_round_winner(self) -> None:
        """Determine the winner of the current round."""
        current_judge: Agent = self.__game_log.get_current_judge()
        apples_in_play: ApplesInPlay = self.__game_log.get_apples_in_play()

        # In regular mode, prompt judge to select winner
        if not self.__training_mode:
            self.__interface.prompt_judge_select_winner(current_judge)

        # Determine the winning red apple
        if self.__training_mode:
            # In training mode, first submitted card always wins
            winning_red_apple_dict: dict[Agent, RedApple] = apples_in_play.red_apples[0]
        else:
            # In regular mode, judge chooses
            winning_red_apple_dict: dict[Agent, RedApple] = current_judge.choose_winning_red_apple(apples_in_play)

        # Update the game state with the winner
        self.__state_manager.set_round_winner(winning_red_apple_dict)

        # Display the winning card and player
        if not self.__training_mode:
            winning_player = self.__game_log.get_chosen_apples().get_red_apple_winner()
            winning_red_apple = self.__game_log.get_chosen_apples().get_winning_red_apple()

            self.__interface.display_winning_red_apple(
                current_judge,
                winning_red_apple
            )

        # Display the round winner
        round_winner = self.__game_log.get_round_winner()
        if round_winner and not self.__training_mode:
            self.__interface.display_round_winner(round_winner)

    def __train_ai_agents(self) -> None:
        """Train AI agents based on the current round's results."""
        # Train all AI agents
        for player in self.__game_log.get_game_players():
            if isinstance(player, AIAgent):
                if self.__training_mode:
                    # In training mode, train the AI on the human agent
                    for agent in self.__game_log.get_game_players():
                        if isinstance(agent, HumanAgent):
                            player.train_self_judge_model(
                                self.__game_log.get_chosen_apples()
                            )

                            # Get the opponent judge model
                            opponent_judge_model = player.get_opponent_model(agent)
                            if opponent_judge_model is None:
                                logging.error("The opponent judge model is None.")
                                raise ValueError("The opponent judge model is None.")

                            slope, bias = opponent_judge_model.get_slope_and_bias_vectors()
                            log_vectors(
                                self.__paths_config,
                                self.__game_log,
                                self.__game_log.get_current_game_state(),
                                self.__game_log.get_current_judge(),
                                player,
                                slope,
                                bias,
                                True
                            )

                            # Add to game log
                            self.__game_log.get_current_game_state().add_slope_and_bias(
                                player,
                                self.__game_log.get_current_judge(),
                                slope,
                                bias
                            )
                else:
                    # In regular mode, train if player is not the judge
                    if player != self.__game_log.get_current_judge():
                        player.train_opponent_judge_model(
                            self.__game_log.get_current_judge(),
                            self.__game_log.get_chosen_apples()
                        )

                        # Get the opponent judge model
                        opponent_judge_model = player.get_opponent_model(self.__game_log.get_current_judge())
                        if opponent_judge_model is None:
                            logging.error("The opponent judge model is None.")
                            raise ValueError("The opponent judge model is None.")

                        slope, bias = opponent_judge_model.get_slope_and_bias_vectors()
                        log_vectors(
                            self.__paths_config,
                            self.__game_log,
                            self.__game_log.get_current_game_state(),
                            self.__game_log.get_current_judge(),
                            player,
                            slope,
                            bias,
                            True
                        )

                        # Add to game log
                        self.__game_log.get_current_game_state().add_slope_and_bias(
                            player,
                            self.__game_log.get_current_judge(),
                            slope,
                            bias
                        )

    def __reset_opponent_models(self) -> None:
        """Reset the opponent models for all AI agents."""
        # TODO - check if need to skip for training mode
        logging.info("Resetting opponent models for all AI agents.")
        self.__interface.display_resetting_models()

        for player in self.__game_log.get_game_players():
            if isinstance(player, AIAgent):
                player.reset_opponent_models()

    # def __is_game_over(self) -> bool:
    #     """Check if the game is over (a player has reached the required points)."""
    #     return self.__state_manager.check_game_over()

    def __game_loop(self) -> None:
        """Run the main game loop until a winner is determined."""
        while self.__game_log.get_game_winner() is None:
            # Start a new round
            self.__new_round()

            # Prompt judge to draw green apple
            self.__prompt_judge_draw_green_apple()

            # Prompt players to select red apples
            self.__prompt_players_select_red_apples()

            # Determine the round winner
            self.__determine_round_winner()

            # Log round results
            if not self.__training_mode:
                log_round_winner(
                    self.__paths_config,
                    self.__game_log,
                    self.__game_log.get_current_game_state(),
                    True
                )

            # Check for game end
            game_over = self.__state_manager.check_game_over()

            # Log game state
            if self.__training_mode:
                log_training_mode(
                    self.__paths_config,
                    self.__game_log,
                    self.__game_log.get_current_game_state(),
                    True
                )
            else:
                log_game_state(
                    self.__paths_config,
                    self.__game_log,
                    True
                )

            # Train AI agents based on this round
            self.__train_ai_agents()

            # Add chosen apples to discard pile
            self.__state_manager.discard_chosen_apples()

            # If game over, display the winner
            winner = self.__game_log.get_game_winner()
            if winner:
                self.__interface.display_game_winner(winner)

                # Log the winner if not in training mode
                if not self.__training_mode:
                    log_game_winner(
                        self.__paths_config,
                        self.__game_log,
                        self.__game_log.get_current_game_state(),
                        True
                    )


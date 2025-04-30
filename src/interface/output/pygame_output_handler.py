# Description: Pygame implementation of the output handler.

# Standard Libraries
import logging
from typing import List, Tuple, Dict, TYPE_CHECKING

# Third-Party Libraries
import pygame

# Local Modules
from src.interface.output.output_handler import OutputHandler
from src.ui.gui.pygame.pygame_ui import BACKGROUND_COLOR

# Type Checking to prevent circular imports
if TYPE_CHECKING:
    from src.agent_model.agent import Agent
    from src.apples.apples import GreenApple, RedApple
    from src.ui.gui.pygame.pygame_ui import PygameUI
    from src.core.state import GameStateManager


class PygameOutputHandler(OutputHandler):
    """Implementation of the output handler for Pygame."""

    def __init__(self, ui: "PygameUI"):
        """Initialize the Pygame output handler."""
        self.ui = ui
        # Game state tracking
        self._submitted_red_apples = []
        self._current_judge = None
        self._current_green_apple = None
        self._winning_red_apple = None
        self._winning_player = None
        self._game_number = 1
        self._total_games = 1
        self._round_number = 1
        self._state_manager = None

    def set_state_manager(self, state_manager: "GameStateManager") -> None:
        """Set the reference to the game state manager."""
        self._state_manager = state_manager

    def set_current_selecting_player(self, player: "Agent") -> None:
        """Set the player who is currently selecting a card."""
        self._current_selecting_player = player

    def clear_current_selecting_player(self) -> None:
        """Clear the current selecting player."""
        self._current_selecting_player = None

    def draw_game_state(self):
        """Draw the current game state on the screen."""
        try:
            # Check if state manager and game log are initialized
            if not self._state_manager or not self._state_manager.game_log:
                logging.debug("State manager or game log not initialized yet")
                # Draw a simple loading screen instead
                self.ui.screen.fill(BACKGROUND_COLOR)
                self.ui.draw_text("Loading game...", self.ui.font_large, (230, 230, 230),
                              self.ui.width // 2, self.ui.height // 2, center=True)
                self._draw_messages()
                return

            # Draw game info header
            self.__draw_game_info()

            # Draw green apple if available
            if self._current_green_apple:
                self.__draw_green_apple()

            # Draw players and scores
            self._draw_players()

            # Draw submitted red apples
            self._draw_red_apples()

            # Draw current player's hand if we're in card selection phase
            if hasattr(self, "_current_selecting_player") and self._current_selecting_player:
                # Determine if this is a human player
                self.draw_current_players_hand(self._current_selecting_player)

            # Draw message area at bottom
            self._draw_messages()

        except Exception as e:
            # Fallback to basic screen
            logging.debug(f"Error drawing game state: {e}")
            self.ui.screen.fill(BACKGROUND_COLOR)
            self.ui.draw_text("Initializing game...", self.ui.font_large, (230, 230, 230),
                          self.ui.width // 2, self.ui.height // 2, center=True)
            self._draw_messages()

    def __draw_game_info(self):
        """Draw game information (game number, round, judge)."""
        # Game number and round
        self.ui.draw_text(f"Game: {self._game_number}/{self._total_games}",
                      self.ui.font_normal, (230, 230, 230), 10, 10)
        self.ui.draw_text(f"Round: {self._round_number}",
                      self.ui.font_normal, (230, 230, 230), 10, 40)

        # Judge name if available
        if self._current_judge:
            judge_text = f"Judge: {self._current_judge.get_name()}"
            self.ui.draw_text(judge_text, self.ui.font_large, (250, 250, 100),
                          self.ui.width // 2, 30, center=True)

    def __draw_green_apple(self):
        """Draw the green apple card."""
        if not self._current_green_apple:
            return

        # Card dimensions and position
        card_width = 300
        card_height = 120
        x = (self.ui.width - card_width) // 2
        y = 80

        self.__draw_single_green_card(self._current_green_apple, x, y, card_width, card_height)

    def __draw_single_green_card(self, green_apple: "GreenApple", x: int, y: int,
                              card_width: int = 300, card_height: int = 120) -> pygame.Rect:
        """
        Draw a single green apple card.

        Args:
            green_apple: The green apple object to draw
            x: X coordinate for the top-left corner
            y: Y coordinate for the top-left corner
            card_width: Width of the card
            card_height: Height of the card

        Returns:
            The pygame.Rect of the drawn card
        """
        # Create card rectangle
        card_rect = pygame.Rect(x, y, card_width, card_height)

        # Draw green card background
        # Outer border (darker green)
        pygame.draw.rect(self.ui.screen, (50, 120, 50),
                      (x-4, y-4, card_width+8, card_height+8),
                      border_radius=10)

        # Card background (green)
        pygame.draw.rect(self.ui.screen, (100, 180, 100),
                      card_rect, border_radius=8)

        # Inner highlight (lighter green)
        pygame.draw.rect(self.ui.screen, (120, 200, 120),
                      (x+2, y+2, card_width-4, card_height-4),
                      width=2, border_radius=7)

        # Card title
        self.ui.draw_text("GREEN APPLE", self.ui.font_small, (30, 80, 30),
                      x + card_width//2, y + 20, center=True)

        # Adjective text
        adjective = green_apple.get_adjective()
        self.ui.draw_text(adjective, self.ui.font_large, (30, 80, 30),
                      x + card_width//2, y + card_height//2, center=True)

        # Draw synonyms if available
        if hasattr(green_apple, "get_synonyms"):
            synonyms = green_apple.get_synonyms()
            if synonyms:
                self.ui.draw_text(f"({synonyms})", self.ui.font_small, (30, 80, 30),
                              x + card_width//2, y + card_height - 25, center=True)

        return card_rect

    def _draw_players(self):
        """Draw the player list with scores."""
        start_y = 150
        x_offset = 20
        y_gap = 30

        # Get players from state manager if available
        players = []
        if self._state_manager and self._state_manager.game_log:
            try:
                players = self._state_manager.game_log.get_game_players()
            except (IndexError, ValueError) as e:
                # Handle case where game state isn't initialized yet
                logging.debug(f"Could not get players yet: {e}")
                return

        for i, player in enumerate(players):
            # Skip if player object is incomplete
            if not hasattr(player, "get_name") or not hasattr(player, "get_points"):
                continue

            name = player.get_name()
            points = player.get_points()
            is_judge = False

            if self._current_judge and player == self._current_judge:
                is_judge = True

            color = (200, 200, 100) if is_judge else (230, 230, 230)
            self.ui.draw_text(f"{name}: {points}", self.ui.font_normal, color,
                          x_offset, start_y + i * y_gap)

    def _draw_red_apples(self):
        """Draw the submitted red apple cards."""
        if not self._submitted_red_apples:
            return

        start_y = 270
        spacing_y = 200
        card_width = 200
        card_height = 200
        spacing_x = 50

        # Calculate actual submissions
        total_submitted = len(self._submitted_red_apples)

        # Get player count from the state manager if available
        if self._state_manager and self._state_manager.game_log:
            total_expected = self._state_manager.game_log.get_number_of_players() - 1
        else:
            # Fallback to using submission count as a reasonable guess
            logging.warning("State manager not available. Using submission count as expected.")
            total_expected = total_submitted

        # Ensure total_expected is at least as large as total_submitted
        total_expected = max(total_expected, total_submitted)

        # Calculate layout after determining total_expected
        cards_per_row = total_expected
        total_width = cards_per_row * (card_width + spacing_x) - spacing_x
        start_x = (self.ui.width - total_width) // 2

        # Display header with submission count
        self.ui.draw_text(f"Submitted Red Apples: {total_submitted}/{total_expected}",
                      self.ui.font_normal, (230, 230, 230),
                      self.ui.width // 2, start_y - 25, center=True)

        # Draw each submitted red apple
        for i, (player, apple) in enumerate(self._submitted_red_apples):
            # Calculate position
            row = i // cards_per_row
            col = i % cards_per_row
            x = start_x + col * (card_width + spacing_x)
            y = start_y + row * spacing_y

            # Determine if this is the winning card
            is_winner = (self._winning_red_apple and self._winning_red_apple == apple)

            # Use the helper method to draw the card
            self.__draw_single_red_card(apple, player, x, y, card_width, card_height, is_winner)

    def __draw_single_red_card(self, red_apple: "RedApple", player: "Agent", x: int, y: int,
                            card_width: int = 200, card_height: int = 200,
                            is_winner: bool | None = False, show_player: bool = True) -> pygame.Rect:
        """
        Draw a single red apple card.

        Args:
            red_apple: The red apple object to draw
            player: The player who owns/submitted this card
            x: X coordinate for the top-left corner
            y: Y Ycoordinate for the top-left corner
            card_width: Width of the card
            card_height: Height of the card
            is_winner: Whether this card is the winning card
            show_player: Whether to show the player name

        Returns:
            The pygame.Rect of the drawn card
        """
        if not red_apple or not hasattr(red_apple, "get_noun"):
            return pygame.Rect(x, y, card_width, card_height)

        # Create card rectangle
        card_rect = pygame.Rect(x, y, card_width, card_height)

        # Outer border color
        border_color = (255, 215, 0) if is_winner else (120, 40, 40)  # Gold for winner
        inner_color = (180, 60, 60) if is_winner else (150, 50, 50)  # Brighter red for winner

        # Draw card with similar style to green cards
        # Outer border
        pygame.draw.rect(self.ui.screen, border_color,
                      (x-4, y-4, card_width+8, card_height+8),
                      border_radius=10)

        # Card background
        pygame.draw.rect(self.ui.screen, (80, 20, 20),
                      card_rect, border_radius=8)

        # Inner highlight
        pygame.draw.rect(self.ui.screen, inner_color,
                      (x+2, y+2, card_width-4, card_height-4),
                      width=2, border_radius=7)

        # Card title
        self.ui.draw_text("RED APPLE", self.ui.font_small, (200, 100, 100),
                      x + card_width//2, y + 20, center=True)

        # Noun text (main content)
        self.ui.draw_text(red_apple.get_noun(), self.ui.font_normal, (255, 200, 200),
                      x + card_width//2, y + 55, center=True)

        # Description text (below the noun) - Multiple lines
        if hasattr(red_apple, "get_description"):
            description = red_apple.get_description()
            if description:
                # Split description into multiple lines (max 4)
                desc_lines = []
                words = description.split()
                current_line = ""

                for word in words:
                    # Increased from 20 to 28 characters per line (80% of card width)
                    if len(current_line + " " + word) <= 28:  # Character limit per line
                        if current_line:
                            current_line += " " + word
                        else:
                            current_line = word
                    else:
                        desc_lines.append(current_line)
                        current_line = word
                        if len(desc_lines) >= 3:  # Limit to 3 lines + the current line
                            break

                if current_line:
                    desc_lines.append(current_line)

                # Add ellipsis if we truncated the description
                if len(desc_lines) == 4 and len(" ".join(desc_lines)) < len(description):
                    desc_lines[3] = desc_lines[3][:17] + "..."

                # Draw each line of the description
                for line_num, line in enumerate(desc_lines):
                    line_y = y + 85 + (line_num * 20)
                    self.ui.draw_text(line, self.ui.font_small, (200, 150, 150),
                                  x + card_width//2, line_y, center=True)

        # Player name at bottom
        if show_player and hasattr(player, "get_name"):
            self.ui.draw_text(f"({player.get_name()})", self.ui.font_small, (200, 150, 150),
                          x + card_width//2, y + card_height - 20, center=True)

        # Winner indicator
        if is_winner:
            # Draw winner ribbon in bottom right corner
            pygame.draw.polygon(self.ui.screen, (255, 215, 0), [
                (x + card_width - 40, y + card_height - 5),
                (x + card_width - 5, y + card_height - 5),
                (x + card_width - 5, y + card_height - 40)
            ])

            # Draw winner text
            winner_surf = self.ui.font_small.render("WINNER", True, (255, 215, 0))
            winner_rect = winner_surf.get_rect()
            winner_rect.midtop = (x + card_width // 2, y + card_height + 5)
            self.ui.screen.blit(winner_surf, winner_rect)

        return card_rect

    def draw_current_players_hand(self, player: "Agent"):
        """
        Draw the current player's hand of red apple cards in the lower section.

        Args:
            player: The current player whose turn it is
            is_human: Whether this player is human (needs to make a selection)

        Returns:
            List of tuples (rect, index) for click detection
        """
        if not player or not hasattr(player, "get_red_apples"):
            return []

        # Get player's cards
        red_apples = player.get_red_apples()
        if not red_apples:
            return []

        # Get green apple
        green_apple = self._current_green_apple
        if not green_apple:
            return []

        # Use standard card size
        card_width = 200
        card_height = 200

        # Position cards above message log area (which starts at self.ui.height - 170)
        message_log_top = self.ui.height - 170
        start_y = message_log_top - card_height - 30  # 30px margin above message log

        # Card spacing
        spacing_x = 30

        # Calculate layout - limit to 7 cards in a row
        cards_per_row = min(7, len(red_apples))

        # Calculate total width needed and center
        total_width = cards_per_row * (card_width + spacing_x) - spacing_x
        start_x = (self.ui.width - total_width) // 2

        # Draw player info header
        self.ui.draw_text(f"{player.get_name()}'s Hand", self.ui.font_normal,
                    (230, 230, 200) if player.is_human() else (180, 180, 180),
                    self.ui.width // 2, start_y - 45, center=True)

        if player.is_human():
            self.ui.draw_text("Click on a card to play it", self.ui.font_small,
                      (200, 200, 150),
                      self.ui.width // 2, start_y - 25, center=True)

        # Store card rectangles with their indices for click detection
        card_rects = []

        # Draw cards
        for i, apple in enumerate(red_apples[:cards_per_row]):
            x = start_x + i * (card_width + spacing_x)

            # Draw the card using the helper method
            card_rect = self.__draw_single_red_card(
                apple, player, x, start_y, card_width, card_height,
                is_winner=False, show_player=False)

            # For human players, add a selection highlight
            if player.is_human():
                # Add a subtle glow effect around the card to indicate it's clickable
                pygame.draw.rect(self.ui.screen, (150, 100, 100),
                            card_rect.inflate(6, 6), width=2, border_radius=10)

            # Store the rectangle and index for click detection
            card_rects.append((card_rect, i))

        return card_rects

    def _draw_messages(self):
        """Draw the message area at bottom of screen."""
        start_y = self.ui.height - 170
        x_offset = 20
        y_gap = 25

        # Draw message box background
        self.ui.draw_rect((50, 50, 50),
                      (10, start_y - 10, self.ui.width - 20, 170),
                      border_radius=5)

        # Draw title
        self.ui.draw_text("Game Messages:", self.ui.font_normal, (230, 230, 230),
                      x_offset, start_y - 5)

        # Draw messages
        for i, message in enumerate(self.ui.messages):
            self.ui.draw_text(message, self.ui.font_small, (230, 230, 230),
                          x_offset, start_y + 25 + i * y_gap)

    # === OutputHandler interface implementation ===

    def display_message(self, message: str) -> None:
        """Display a general message."""
        self.ui.add_message(message)
        logging.info(message)

    def display_error(self, message: str) -> None:
        """Display an error message."""
        self.ui.add_message(f"ERROR: {message}")
        self.ui.show_notification(f"ERROR: {message}")
        logging.error(message)

    def display_new_game_message(self) -> None:
        """Display a message indicating a new game is starting."""
        message = "Starting a new game!"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

        # Reset state for new game
        self._submitted_red_apples = []
        self._winning_red_apple = None
        self._winning_player = None

    def display_game_header(self, game_number: int, total_games: int) -> None:
        """Display the game header with game number information."""
        self._game_number = game_number
        self._total_games = total_games

        message = f"Game {game_number} of {total_games}"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    def display_initializing_decks(self) -> None:
        """Display message about initializing decks."""
        message = "Initializing card decks..."
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility(1.0)  # Shorter delay

    def display_deck_sizes(self, green_deck_size: int, red_deck_size: int) -> None:
        """Display the sizes of the green and red apple decks."""
        message = f"Deck sizes - Green: {green_deck_size}, Red: {red_deck_size}"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility(1.0)  # Shorter delay

    def display_deck_loaded(self, deck_name: str, count: int) -> None:
        """Display message about a deck being loaded."""
        message = f"Loaded {count} cards from {deck_name} deck"
        self.display_message(message)

    def display_expansion_deck_loaded(self, deck_name: str, count: int) -> None:
        """Display message about an expansion deck being loaded."""
        message = f"Loaded {count} additional cards from {deck_name} expansion"
        self.display_message(message)

    def display_initializing_players(self) -> None:
        """Display message about initializing players."""
        message = "Initializing players..."
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility(3.0)

    def display_player_count(self, count: int) -> None:
        """Display the number of players in the game."""
        message = f"Players in game: {count}"
        self.display_message(message)

    def display_submitted_red_apples(self, submissions: Dict["Agent", "RedApple"]) -> None:
        """Display all submitted red apples for the current round."""
        # Store submissions for drawing
        self._submitted_red_apples = [(player, apple) for player, apple in submissions.items()]

        # Show a message
        message = f"All players have submitted their red apples ({len(submissions)} submissions)"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    def display_agent_drew_cards(self, agent_name: str, count: int) -> None:
        """Display message that an agent drew cards."""
        message = f"{agent_name} drew {count} card" + ("s" if count != 1 else "")
        self.display_message(message)

    def display_starting_judge(self, judge_name: str) -> None:
        """Display the name of the starting judge."""
        message = f"{judge_name} is the starting judge"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    def display_next_judge(self, judge_name: str) -> None:
        """Display the name of the next judge."""
        message = f"{judge_name} is the next judge"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    def display_round_header(self, round_number: int) -> None:
        """Display the round header with round number information."""
        self._round_number = round_number
        message = f"Round {round_number}"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

        # Reset round state
        self._submitted_red_apples = []
        self._winning_red_apple = None

    def display_player_points(self, player_points: List[Tuple[str, int]]) -> None:
        """Display all players' points."""
        message = "Current scores: " + ", ".join(f"{name}: {points}" for name, points in player_points)
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

        # Update player data using the state manager
        if self._state_manager and self._state_manager.game_log:
            players = self._state_manager.game_log.get_game_players()

            # Update player data
            for name, points in player_points:
                for player in players:
                    if hasattr(player, 'get_name') and player.get_name() == name:
                        if hasattr(player, 'set_points'):
                            player.set_points(points)

    def display_green_apple(self, judge: "Agent", green_apple: "GreenApple") -> None:
        """Display the green apple card in play."""
        self._current_judge = judge
        self._current_green_apple = green_apple

        message = f"Green apple: {green_apple.get_adjective()}"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    def display_player_red_apples(self, player: "Agent") -> None:
        """Display the red apples held by a player."""
        message = f"Showing {player.get_name()}'s red apples"
        self.display_message(message)
        self.ui.delay_for_visibility(1.0)  # Shorter delay

    def display_red_apple_chosen(self, player: "Agent", red_apple: "RedApple") -> None:
        """Display that a player has chosen a red apple."""
        self._submitted_red_apples.append((player, red_apple))

        message = f"{player.get_name()} chose: {red_apple.get_noun()}"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    def display_winning_red_apple(self, judge: "Agent", red_apple: "RedApple") -> None:
        """Display the winning red apple card."""
        self._winning_red_apple = red_apple

        message = f"{judge.get_name()} chose the winning red apple: {red_apple.get_noun()}"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility(4.0)  # Longer delay for winners

    def display_round_winner(self, winner: "Agent") -> None:
        """Display the round winner."""
        self._winning_player = winner

        message = f"{winner.get_name()} won the round!"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility(4.0)  # Longer delay for winners

    def display_game_winner(self, winner: "Agent") -> None:
        """Display the game winner."""
        message = f"{winner.get_name()} won the game!"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility(5.0)  # Longest delay for game winner

    def display_game_time(self, minutes: int, seconds: int) -> None:
        """Display the total game time."""
        message = f"Game completed in {minutes}m {seconds}s"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    def display_resetting_models(self) -> None:
        """Display message about resetting AI opponent models."""
        message = "Resetting AI models..."
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility(1.0)  # Shorter delay

    def display_training_green_apple(self, adjective: str) -> None:
        """Display the green apple card in training mode."""
        message = f"Training green apple: {adjective}"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    # Prompt message methods

    def prompt_judge_draw_green_apple(self, judge: "Agent") -> None:
        """Display prompt for judge to draw a green apple."""
        message = f"{judge.get_name()} draws a green apple..."
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    def prompt_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Display prompt for a player to select a red apple."""
        message = f"{player.get_name()}, select a red apple to match: {green_apple.get_adjective()}"
        self.display_message(message)
        self.ui.show_notification(message)
        # No delay needed as user interaction will happen

    def prompt_training_select_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Display prompt to select a good red apple in training mode."""
        message = f"Training: Select a GOOD red apple to match: {green_apple.get_adjective()}"
        self.display_message(message)
        self.ui.show_notification(message)
        # No delay needed as user interaction will happen

    def prompt_training_select_bad_red_apple(self, player: "Agent", green_apple: "GreenApple") -> None:
        """Display prompt to select a bad red apple in training mode."""
        message = f"Training: Select a BAD red apple to match: {green_apple.get_adjective()}"
        self.display_message(message)
        self.ui.show_notification(message)
        # No delay needed as user interaction will happen

    def prompt_judge_select_winner(self, judge: "Agent") -> None:
        """Display prompt for judge to select the winning red apple."""
        message = f"{judge.get_name()}, select the winning red apple!"
        self.display_message(message)
        self.ui.show_notification(message)
        # No delay needed as user interaction will happen

    # Player management methods

    def set_players(self, players: List["Agent"]) -> None:
        """Update the current players list."""
        # No longer store players locally - just log and display
        names = [player.get_name() for player in players]
        message = f"Players: {', '.join(names)}"
        self.display_message(message)
        self.ui.delay_for_visibility(1.0)  # Short delay
        logging.debug(f"Updated player list. Total players: {len(players)}")

    def display_training_mode_started(self) -> None:
        """Display message that training mode has started."""
        message = "Training mode started"
        self.display_message(message)
        self.ui.show_notification(message)
        self.ui.delay_for_visibility()

    def display_agent_cant_draw_cards(self, agent_name: str) -> None:
        """Display message that an agent cannot draw more cards."""
        message = f"{agent_name} cannot draw more cards (hand is full)"
        self.display_message(message)

    def display_model_reset(self, agent_name: str, opponent_name: str) -> None:
        """Display message that an agent's model for an opponent was reset."""
        message = f"Reset {agent_name}'s model for {opponent_name}"
        self.display_message(message)

    def log_agent_chose_red_apple(self, agent_name: str, red_apple: "RedApple") -> None:
        """Log that an agent chose a red apple."""
        # Just log to the file, don't display on screen
        logging.info(f"{agent_name} chose red apple: {red_apple.get_noun()}")

    def log_model_training(self, agent_name: str, opponent_name: str,
                          green_apple: "GreenApple", winning_red_apple: "RedApple",
                          losing_red_apples: List["RedApple"]) -> None:
        """Log model training information."""
        # Log training details to file
        winning_noun = winning_red_apple.get_noun() if winning_red_apple else "None"
        losing_nouns = ", ".join(apple.get_noun() for apple in losing_red_apples if apple)
        logging.info(f"Training {agent_name}'s model against {opponent_name}:")
        logging.info(f"  Green apple: {green_apple.get_adjective()}")
        logging.info(f"  Winning red apple: {winning_noun}")
        logging.info(f"  Losing red apples: {losing_nouns}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        logging.error(message)

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        logging.debug(message)

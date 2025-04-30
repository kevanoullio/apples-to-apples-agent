# Description: Pygame implementation of the input handler.

# Standard Libraries
import pygame
import sys
from typing import List, Dict, TYPE_CHECKING

# Local Modules
from src.interface.input.input_handler import InputHandler
from src.ui.gui.pygame.pygame_ui import BACKGROUND_COLOR

# Type Checking to prevent circular imports
if TYPE_CHECKING:
    from src.agent_model.agent import Agent
    from src.apples.apples import GreenApple, RedApple
    from src.ui.gui.pygame.pygame_ui import PygameUI


class PygameInputHandler(InputHandler):
    """Implementation of the input handler for Pygame."""

    def __init__(self, ui: "PygameUI"):
        """Initialize the Pygame input handler."""
        self.ui = ui
        self.selected_index = None
        self.dialog_result = None
        self.waiting_for_input = False
        self.card_buttons = []  # For clickable cards

    def process_event(self, event):
        """Process a pygame event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if any card was clicked
            for i, (rect, _) in enumerate(self.card_buttons):
                if rect.collidepoint(event.pos):
                    self.selected_index = i
                    self.waiting_for_input = False
                    return

    def show_dialog_buttons(self, options, start_y=400):
        """Display clickable buttons for options and wait for selection."""
        self.card_buttons = []
        button_width = 200
        button_height = 40
        spacing = 20

        # Calculate total width needed
        total_width = len(options) * (button_width + spacing) - spacing
        start_x = (self.ui.width - total_width) // 2

        # Create buttons
        for i, option in enumerate(options):
            x = start_x + i * (button_width + spacing)
            rect = pygame.Rect(x, start_y, button_width, button_height)
            self.card_buttons.append((rect, option))

        # Wait for selection
        self.waiting_for_input = True
        self.selected_index = None

        while self.waiting_for_input and self.ui.running:
            # Process events
            if not self.ui.process_events():
                return None

            # Draw background
            self.ui.screen.fill(BACKGROUND_COLOR)

            # Draw buttons
            for rect, text in self.card_buttons:
                # Draw button background
                pygame.draw.rect(self.ui.screen, (80, 80, 80), rect, border_radius=5)
                pygame.draw.rect(self.ui.screen, (120, 120, 120), rect, width=2, border_radius=5)

                # Draw button text
                self.ui.draw_text(text, self.ui.font_normal, (230, 230, 230),
                              rect.centerx, rect.centery, center=True)

            # Update display
            self.ui.update_display()
            pygame.time.wait(50)  # Reduce CPU usage

        # Return selected option
        if self.selected_index is not None and self.selected_index < len(options):
            return options[self.selected_index]
        return None

    # === InputHandler implementations ===

    def prompt_yes_no(self, prompt: str) -> bool:
        """Prompt the user for a yes/no answer."""
        self.ui.show_notification(prompt)
        result = self.show_dialog_buttons(["Yes", "No"])
        return result == "Yes"

    def prompt_player_type(self, player_number: int) -> str:
        """Prompt for the type of player."""
        from src.ui.gui.pygame.pygame_dialogs import PlayerTypeDialog

        # Run the player type dialog
        dialog = PlayerTypeDialog(self.ui.screen, player_number)
        result = dialog.run()

        # If dialog was closed without selection, default to Random
        return result if result else "2"

    def prompt_human_player_name(self) -> str:
        """Prompt for a human player's name."""
        from src.ui.gui.pygame.pygame_dialogs import NameInputDialog

        # Run the name input dialog
        dialog = NameInputDialog(self.ui.screen)
        result = dialog.run()

        # If dialog was closed without selection, use default name
        return result if result else "Player"

    def prompt_ai_model_type(self) -> str:
        """Prompt for the AI model type."""
        from src.ui.gui.pygame.pygame_dialogs import ModelTypeDialog

        # Run the model type dialog
        dialog = ModelTypeDialog(self.ui.screen)
        result = dialog.run()

        # If dialog was closed without selection, default to Linear Regression
        return result if result else "1"

    def prompt_ai_archetype(self) -> str:
        """Prompt for the AI archetype."""
        from src.ui.gui.pygame.pygame_dialogs import ArchetypeDialog

        # Run the archetype dialog
        dialog = ArchetypeDialog(self.ui.screen)
        result = dialog.run()

        # If dialog was closed without selection, default to Literalist
        return result if result else "1"

    def prompt_starting_judge(self, player_count: int) -> int:
        """Prompt for the selection of the starting judge."""
        self.ui.show_notification("Select starting judge")
        options = [f"{i}" for i in range(1, player_count + 1)]
        result = self.show_dialog_buttons(options)
        if result:
            return int(result)
        return 1

    def prompt_human_agent_choose_red_apple(self, player: "Agent", red_apples: List["RedApple"],
                                    green_apple: "GreenApple") -> int:
        """Prompt a human player to select a red apple."""
        # Get a reference to the output handler
        output_handler = self.ui._output_handler

        # Create the message with the green apple adjective
        message = f"{player.get_name()}, select a red apple to match: {green_apple.get_adjective()}"

        # Display prompt text with infinite duration
        self.ui.show_notification(message, float("inf"))  # Set to infinite duration

        # Wait for player to select a card
        selected_index = None
        running = True

        # Set current player in output handler to ensure cards are displayed
        if hasattr(output_handler, "set_current_selecting_player"):
            output_handler.set_current_selecting_player(player)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if player clicked on a card
                    mouse_pos = pygame.mouse.get_pos()

                    # Get card rectangles from the current display
                    card_rects = []
                    if hasattr(output_handler, "draw_current_players_hand"):
                        card_rects = output_handler.draw_current_players_hand(player)

                    # Check for clicks on cards
                    for rect, index in card_rects:
                        if rect.collidepoint(mouse_pos):
                            selected_index = index
                            running = False
                            break

            # Redraw the screen
            self.ui.process_events()

            # Draw game state to show cards
            self.ui.screen.fill(BACKGROUND_COLOR)
            output_handler.draw_game_state()

            # Re-display the notification each frame to ensure it stays visible
            self.ui.show_notification(message, float("inf"))

            # Redraw the screen
            pygame.display.flip()
            pygame.time.wait(30)  # Short delay to reduce CPU usage

        # Clear current player selection state
        if hasattr(output_handler, "clear_current_selecting_player"):
            output_handler.clear_current_selecting_player()

        # Return the selected card index (or default to 0 if somehow nothing was selected)
        return selected_index if selected_index is not None else 0

    def prompt_judge_select_winner(self, judge: "Agent", submissions: Dict["Agent", "RedApple"],
                                green_apple: "GreenApple") -> "Agent":
        """Prompt the judge to select the winning red apple."""
        from src.ui.gui.pygame.pygame_dialogs import JudgeSelectionDialog

        # Run the judge selection dialog
        dialog = JudgeSelectionDialog(self.ui.screen, judge, submissions, green_apple)
        result = dialog.run()

        # If dialog was closed without selection, default to first player
        return result if result else list(submissions.keys())[0]

    def prompt_training_model_type(self) -> str:
        """Prompt for the model type in training mode."""
        from src.ui.gui.pygame.pygame_dialogs import TrainingModelTypeDialog

        # Run the training model type dialog
        dialog = TrainingModelTypeDialog(self.ui.screen)
        result = dialog.run()

        # If dialog was closed without selection, default to Linear Regression
        return result if result else "1"

    def prompt_training_pretrained_type(self) -> str:
        """Prompt for the pretrained model type in training mode."""
        from src.ui.gui.pygame.pygame_dialogs import TrainingPretrainedTypeDialog

        # Run the training pretrained type dialog
        dialog = TrainingPretrainedTypeDialog(self.ui.screen)
        result = dialog.run()

        # If dialog was closed without selection, default to Comedian
        return result if result else "3"

"""
CLI module for autoscheduler2.

Provides the command-line interface for the autoscheduler application.
"""

from ..core.scope_manager import ScopeManager
from ..core.schedule import Schedule


class CLI:
    """Command-line interface for the autoscheduler application."""
    
    def __init__(self):
        """Initialize the CLI with ScopeManager and Schedule instances."""
        self.schedule = Schedule()
        self.scope_manager = ScopeManager(self.schedule)
    
    def run(self):
        """Main program loop that presents user with menu options."""
        print("Welcome to Autoscheduler2")
        print("LLM-driven project management scheduling tool")
        print("-" * 50)
        
        while True:
            self._display_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                print("\n--- Add Activity ---")
                success = self.scope_manager._add_activity()
                self._show_result(success, "Activity operation")
            elif choice == "2":
                print("\n--- Delete Activity ---")
                success = self.scope_manager._delete_activity()
                self._show_result(success, "Delete activity operation")
            elif choice == "3":
                print("\n--- Add Relationship ---")
                success = self.scope_manager._add_relationship()
                self._show_result(success, "Add relationship operation")
            elif choice == "4":
                print("\n--- Delete Relationship ---")
                success = self.scope_manager._delete_relationship()
                self._show_result(success, "Delete relationship operation")
            elif choice == "5":
                print("\n--- Dissolve Relationship ---")
                success = self.scope_manager._dissolve_relationship()
                self._show_result(success, "Dissolve relationship operation")
            elif choice == "6":
                print("\n--- Open Prompt ---")
                success = self.scope_manager._dispatch()
                self._show_result(success, "Natural language prompt operation")
            elif choice == "7":
                print("\n--- Run Schedule ---")
                print("Schedule execution not implemented yet.")
            elif choice == "8":
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please enter a number between 1 and 8.")
            
            input("\nPress Enter to continue...")
    
    def _display_menu(self):
        """Display the main menu options."""
        print("\n" + "=" * 50)
        print("AUTOSCHEDULER2 - MAIN MENU")
        print("=" * 50)
        print("1. Add Activity")
        print("2. Delete Activity")
        print("3. Add Relationship")
        print("4. Delete Relationship")
        print("5. Dissolve Relationship")
        print("6. Open Prompt (Natural Language)")
        print("7. Run Schedule")
        print("8. Quit")
        print("=" * 50)
    
    def _show_result(self, success: bool, operation: str):
        """Display the result of an operation to the user.
        
        Args:
            success (bool): Whether the operation was successful
            operation (str): Description of the operation performed
        """
        if success:
            print(f"\n✓ {operation} completed successfully!")
        else:
            print(f"\n✗ {operation} failed or was cancelled.")


def main():
    """Main entry point for the CLI application."""
    cli = CLI()
    cli.run()
import sys
import os
import pyautogui
pyautogui.FAILSAFE = False  # Disable PyAutoGUI fail-safe (use with caution)
from core.impl.tool.ToolManager import ToolManager
from presentation.contextAction.KeyboardContext import KeyboardContext

def display_menu():
    """Prints the main menu and status."""
    print("\n" + "="*30)
    print("  Sunflower Land Automation")
    print("="*30)
    print("Hotkeys:")
    print("  1 - Start a new Harvest Tool (1 click)")
    print("  2 - Start a new Harvest Tool (3 clicks)")
    print("  3 - Start a new Captcha Passer Tool")
    print("  P - Pause/Resume All | R - Reset All | ESC - Stop All")
    print("  0 - Hide All Overlays | Q - Quit Program")
    print("-"*30)
   


def main():
    """Main entry point to initialize and run the automation tool."""
    # Add the project root to the Python path to ensure correct module resolution
    project_root = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(project_root)

    print("Initializing Sunflower Land Automation...")
    display_menu()

    # No manual mapping; KeyboardContext loads mappings from setting.yaml internally
    def handle_start_simple_clicker():
        ToolManager.add_task_to_queue(2, {
        'type': 'command',
        'command': 'start_new_tool',
        'tool_type': 'simple_clicker',
        'tool_config': {
            "detection_branches": {
                "scenarios": [
                    {
                        "id": "planting",
                        "condition": "all([k in detected_objects['default'] for k in ['base_template.png', 'hole.png']])",
                        "actions": [
                            {"type": "click", "templates": ["hole.png"], "max_items": 10, "click_count": 1}
                        ]
                    },
                    {
                        "id": "havert_crops",
                        "condition": "('base_template.png' in detected_objects['default']) and any([k in detected_objects['default'] for k in ['sunflower_crop_v2.png', 'rhubard_crop.png']])",
                        "actions": [
                            {"type": "click", "templates": ["sunflower_crop_v2.png", "rhubard_crop.png"], "max_items": 10, "click_count": 1}
                        ]
                    },
                    # {
                    #     "id": "harvest_cherry_tree",
                    #     "condition": "all([k in detected_objects['default'] for k in ['base_template.png', 'cherry_tree.png']])",
                    #     "actions": [
                    #         {"type": "click", "templates": ["cherry_tree.png"], "max_items": 10, "click_count": 3}
                    #     ]
                    # },
                    {
                        "id": "close_basket_tool",
                        "condition": "all([k in detected_objects['default'] for k in ['basket_window.png', 'close_button.png']])",
                        "actions": [
                            {"type": "click", "templates": ["close_button.png"], "max_items": 1}
                        ]
                    },
                    {
                        "id": "select_seed_in_basket_tool",
                        "condition": "all([k in detected_objects['default'] for k in ['basket_window.png', 'rhubard_seed.png']])",
                        "actions": [
                            {"type": "click", "templates": ["rhubard_seed.png"], "max_items": 2}
                        ],
                        "childrens": ["close_basket_tool"]
                    },
                    {
                        "id": "detect_seed_tool_not_suitable",
                        "condition": "all([k in detected_objects['default'] for k in ['base_template.png', 'basket_v2.png']]) and not ('rhubard_seed_tool.png' in detected_objects['default'])",
                        "actions": [
                            {"type": "click", "templates": ["basket_v2.png"], "max_items": 1}
                        ],
                        "childrens": ["select_seed_in_basket_tool"]
                    },
                    {
                        "id": "close_captcha",
                        "condition": "'close_text.png' in detected_objects['default']",
                        "actions": [
                             {"type": "click", "templates": ["close_text.png"], "max_items": 1}
                        ]
                    },
                    {
                        "id": "handle_captcha",
                        "condition": "any([(k in detected_objects['captcha_passer']) for k in ['goblin', 'chest', 'skeleton']])",
                        "mode" : "captcha_passer",
                        "actions": [
                            {"type": "click", "templates": ["goblin", "chest", "skeleton"], "max_items": 3},
                            {"type": "change_mode", "mode": "main"}
                        ],
                        "childrens": ["close_captcha"]
                    },
                    {
                        "id": "detect_captcha",
                        "condition": "any([(k in detected_objects['default']) for k in ['attempt_left_blue.png', 'tap_chest.png', 'attempt_left_red.png']])",
                        "actions": [{"type": "change_mode", "mode": "captcha_passer"}],
                        "childrens": ["handle_captcha"]
                    }
                ]
            }
        }
    })

    def handle_shutdown():
        ToolManager.shutdown()

    handler_map = {
        'create_simple_clicker': (handle_start_simple_clicker, ()),
        'quit': (handle_shutdown, ()),
        # Add more mappings as needed
    }

    # Create KeyboardContext and set default context to 'main'
    keyboard_context = KeyboardContext()
    keyboard_context.activate_context('main', handler_map)

    ALL_PROFILES = [ ('binha2pct', 450)] # Profile name and idle timeout in seconds

    for profile_name, idle_timeout in ALL_PROFILES:
        ToolManager.reset()
        print(f"\n--- Starting profile: {profile_name} with idle timeout: {idle_timeout} seconds ---")
        ToolManager.start_event_loop(profile_name=profile_name, idle_timeout=idle_timeout)
        print(f"--- Profile {profile_name} finished ---")

    # Unhook all hotkeys after all profiles have run
    keyboard_context.unhook_all()
    print("All profiles have been processed. Program has terminated.")

if __name__ == "__main__":
    main()



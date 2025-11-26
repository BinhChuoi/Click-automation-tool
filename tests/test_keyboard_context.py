import unittest
from unittest.mock import MagicMock
from common.impl.contextAction.KeyboardManager import KeyboardManager
from common.impl.contextAction.KeyboardContext import KeyboardContext

class TestKeyboardContext(unittest.TestCase):
    def setUp(self):
        # Mock KeyboardManager
        self.mock_manager = MagicMock(spec=KeyboardManager)
        # Define dummy actions
        self.action_map = {
            "start": MagicMock(name="start_action"),
            "stop": MagicMock(name="stop_action"),
        }
        # Provide a test config mapping directly
        self.contexts = {
            "main": {"start": "ctrl+1", "stop": "ctrl+2"},
        }
        # Patch KeyboardContext to skip YAML loading
        self.kc = KeyboardContext(self.mock_manager, self.action_map)
        self.kc.contexts = self.contexts.copy()

    def test_set_context_binds_hotkeys(self):
        self.kc.set_context("main")
        self.mock_manager.add_hotkey.assert_any_call("ctrl+1", self.action_map["start"])
        self.mock_manager.add_hotkey.assert_any_call("ctrl+2", self.action_map["stop"])
        self.assertEqual(self.kc.get_context(), "main")

    def test_unhook_context_removes_hotkeys(self):
        self.kc.set_context("main")
        self.kc.unhook_context("main")
        self.mock_manager.remove_hotkey.assert_any_call("ctrl+1")
        self.mock_manager.remove_hotkey.assert_any_call("ctrl+2")

    def test_trigger_action(self):
        self.kc.register_action("main", "start", self.action_map["start"])
        self.kc.trigger_action("main", "start")
        self.action_map["start"].assert_called_once()

    def test_register_and_unregister_action(self):
        self.kc.register_action("main", "new_action", self.action_map["start"])
        self.assertIn("new_action", self.kc.contexts["main"])
        self.kc.unregister_action("main", "new_action")
        self.assertNotIn("new_action", self.kc.contexts["main"])

    def test_add_context(self):
        self.kc.add_context("edit", {"save": "ctrl+s"})
        self.assertIn("edit", self.kc.get_contexts())
        self.assertEqual(self.kc.contexts["edit"], {"save": "ctrl+s"})

if __name__ == "__main__":
    unittest.main()

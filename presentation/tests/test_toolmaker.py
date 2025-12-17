import pytest
from unittest.mock import patch, MagicMock
from presentation.PresentationManager import PresentationManager
from presentation.ToolMaker import ToolMaker


# def test_start_sets_completion_event():
#     tm = ToolMaker()
#     tm.start()

#     PresentationManager.get_instance().run_event_loop()
#     assert tm._completion_event.is_set()

def test_get_last_draft_returns_draft():
    tm = ToolMaker()
    tm.draft = {'test': 123}
    assert tm._get_last_draft() == {'test': 123}


@patch('presentation.ToolMaker.KeyboardContext')
def test_select_tool_type_sets_draft_and_activates_context(mock_keyboard_context):
    tm = ToolMaker()
    tm.keyboard_context = MagicMock()
    tm.draft = {}  # Ensure draft is initialized
    tm.select_tool_type()
    assert isinstance(tm.draft, dict)
    tm.keyboard_context.activate_context.assert_called_once_with('select_tool_type', {
        "simple_clicker": (tm.open_tool_editor_gui, ()),
        "review_tools": (tm.tool_review, ()),
        "cancel": (tm.go_back, ())
    })

@patch('presentation.ToolMaker.KeyboardContext')
def test_open_tool_editor_gui_activates_context(mock_keyboard_context):
    tm = ToolMaker()
    tm.keyboard_context = MagicMock()
    tm.draft = {}  # Ensure draft is initialized
    tm.open_tool_editor_gui()
    tm.keyboard_context.activate_context.assert_called_once_with('tool_editor', {
        "prompt_tool_mode": (tm.prompt_tool_mode, ()),
        "prompt_tool_scenario": (tm.prompt_tool_scenario, ()),
        "save": (tm.save_tool, ()),
        "cancel": (tm.go_back, ())
    })

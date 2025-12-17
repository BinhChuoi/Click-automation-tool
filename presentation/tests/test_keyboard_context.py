

import pytest
from unittest.mock import patch, MagicMock
from presentation.contextAction.KeyboardContext import KeyboardContext


test_settings = {
    'keyboard_mappings': {
        'main': {
            'start': 'ctrl+1',
            'stop': 'ctrl+2',
        },
        'edit': {
            'save': 'ctrl+s',
        }
    }
}


def test_activate_context_binds_hotkeys():
    with patch('presentation.contextAction.KeyboardContext.load_configuration', return_value=test_settings):
        with patch('presentation.contextAction.KeyboardManager.KeyboardManager.clear_all_hotkeys') as clear_mock, \
             patch('presentation.contextAction.KeyboardManager.KeyboardManager.add_hotkey') as add_hotkey_mock:
            kc = KeyboardContext()
            handler_map = {
                'start': (MagicMock(name='start_handler'), ()),
                'stop': (MagicMock(name='stop_handler'), ())
            }
            kc.activate_context('main', handler_map)
            clear_mock.assert_called_once()
            add_hotkey_mock.assert_any_call('ctrl+1', handler_map['start'][0], ())
            add_hotkey_mock.assert_any_call('ctrl+2', handler_map['stop'][0], ())
            assert kc.current_context == 'main'

def test_activate_context_raises_on_missing_context():
    with patch('presentation.contextAction.KeyboardContext.load_configuration', return_value=test_settings):
        kc = KeyboardContext()
        with pytest.raises(ValueError, match="Context 'unknown' not found"):
            kc.activate_context('unknown', {})

def test_activate_context_with_handler_args():
    with patch('presentation.contextAction.KeyboardContext.load_configuration', return_value=test_settings):
        with patch('presentation.contextAction.KeyboardManager.KeyboardManager.add_hotkey') as add_hotkey_mock:
            kc = KeyboardContext()
            handler_map = {
                'start': (MagicMock(name='start_handler'), (1, 2)),
                'stop': (MagicMock(name='stop_handler'), ('foo',))
            }
            kc.activate_context('main', handler_map)
            add_hotkey_mock.assert_any_call('ctrl+1', handler_map['start'][0], (1, 2))
            add_hotkey_mock.assert_any_call('ctrl+2', handler_map['stop'][0], ('foo',))

def test_context_switching_clears_and_rebinds_hotkeys():
    with patch('presentation.contextAction.KeyboardContext.load_configuration', return_value=test_settings):
        with patch('presentation.contextAction.KeyboardManager.KeyboardManager.clear_all_hotkeys') as clear_mock, \
             patch('presentation.contextAction.KeyboardManager.KeyboardManager.add_hotkey') as add_hotkey_mock:
            kc = KeyboardContext()
            handler_map_main = {
                'start': (MagicMock(name='start_handler'), ())
            }
            handler_map_edit = {
                'save': (MagicMock(name='save_handler'), ())
            }
            kc.activate_context('main', handler_map_main)
            kc.activate_context('edit', handler_map_edit)
            assert kc.current_context == 'edit'
            assert clear_mock.call_count == 2
            add_hotkey_mock.assert_any_call('ctrl+1', handler_map_main['start'][0], ())
            add_hotkey_mock.assert_any_call('ctrl+s', handler_map_edit['save'][0], ())

import pytest
from unittest.mock import MagicMock
from core.main.src.impl.tool.SimpleClickerTool import SimpleClicker, DEFAULT_MODE


@pytest.fixture
def simple_clicker():
    config = {
        'modes': {DEFAULT_MODE: []},
        'detection_branches': {'branch_scenarios': []},
        'base_priority': 5,
        'available_templates': []
    }
    sc = SimpleClicker(tool_configuration=config)
    sc.objects_detected = {}  # Ensure this attribute exists because we won't run full startup
    return sc

def test_change_mode_resets_stack_and_tasks(simple_clicker):
    simple_clicker.mode_tasks = {
        DEFAULT_MODE: {'task1': MagicMock(), 'task2': MagicMock()}
    }
    for t in simple_clicker.mode_tasks[DEFAULT_MODE].values():
        t.resume = MagicMock()
        t.pause = MagicMock()
    simple_clicker.execution_stack = [1, 2, 3]
    simple_clicker.change_mode(DEFAULT_MODE)
    assert simple_clicker.execution_stack == []
    for t in simple_clicker.mode_tasks[DEFAULT_MODE].values():
        t.resume.assert_called()
        t.pause.assert_not_called()

def test_get_template_by_name(simple_clicker):
    simple_clicker.tool_configuration['available_templates'] = [
        {'class_name': 'foo', 'template_path': '/tmp/foo.png'}
    ]
    result = simple_clicker._get_template_by_name('foo')
    assert result['template_path'] == '/tmp/foo.png'
    assert simple_clicker._get_template_by_name('bar') is None

def test_handle_current_scenario_triggers_action(monkeypatch, simple_clicker):
    simple_clicker.execution_stack = [{
        'id': 'branch1',
        'actions': [{'type': 'change_mode', 'mode': 'other'}],
        'childrens': []
    }]
    monkeypatch.setattr(simple_clicker, '_perform_scenario_actions', lambda actions, detected: setattr(simple_clicker, 'action_called', True))
    monkeypatch.setattr('core.main.src.impl.tool.SimpleClickerTool.ContextActionExecutor.evaluate_scenario_condition', lambda *a, **kw: True)
    detected_objects = {'task1': [{'class_name': 'foo'}]}
    simple_clicker.action_called = False
    result = simple_clicker._handle_current_scenario(detected_objects)
    assert simple_clicker.action_called
    assert result is True

def test_perform_scenario_actions_emits_signal(monkeypatch, simple_clicker):
    sent = {}
    simple_clicker.mode_tasks = {DEFAULT_MODE: {'task1': MagicMock()}}
    simple_clicker.objects_detected = {'task1': [{'class_name': 'foo', 'x': 1, 'y': 2}]}
    action = {'type': 'click', 'templates': ['foo']}
    monkeypatch.setattr('shared.utils.Signals.Interaction.send', lambda *a, **kw: sent.update(kw))
    simple_clicker._perform_scenario_actions([action], simple_clicker.objects_detected)
    assert sent['action'] == action
    assert sent['matched_objects'][0]['class_name'] == 'foo'

def test_load_tasks_creates_tasks(monkeypatch, simple_clicker):
    dummy_task = MagicMock()
    monkeypatch.setattr(simple_clicker, 'start_new_task', lambda **kw: dummy_task)
    simple_clicker.tool_configuration['modes'][DEFAULT_MODE] = [{
        'id': 'task1',
        'detector_configs': [],
        'area': {},
        'execution_type': 'non_threaded'
    }]
    tasks = simple_clicker.load_tasks(DEFAULT_MODE)
    assert tasks == [dummy_task]

def test_on_detection_updates_objects_and_process(monkeypatch, simple_clicker):
    monkeypatch.setattr(simple_clicker, '_map_detected_objects', lambda tid, objs: objs)
    monkeypatch.setattr(simple_clicker, 'process_detection_results', lambda tid: setattr(simple_clicker, 'processed', True))
    simple_clicker.on_detection('task1', 'cap1', [{'template_name': 'foo'}])
    assert simple_clicker.objects_detected['task1'][0]['template_name'] == 'foo'
    assert simple_clicker.processed

def test_process_detection_results_handles_empty_stack(simple_clicker):
    simple_clicker.execution_stack = []
    simple_clicker.process_detection_results('task1')

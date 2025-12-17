import pytest
from core.main.src.impl.tool.ToolManager import _ToolManager

class DummyTool:
    def __init__(self, tool_id):
        self.tool_id = tool_id
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

@pytest.fixture
def temp_manager():
    manager = _ToolManager()
    yield manager

@pytest.fixture
def dummy_tool():
    return DummyTool('dummy_id')

def test_register_and_unregister_tool(temp_manager, dummy_tool):
    temp_manager.register_tool_instance(dummy_tool.tool_id, dummy_tool)
    assert dummy_tool.tool_id in temp_manager.active_tools
    temp_manager.unregister_tool_instance(dummy_tool.tool_id)
    assert dummy_tool.tool_id not in temp_manager.active_tools

def test_destroy_tool_instance(temp_manager, dummy_tool, mocker):
    temp_manager.register_tool_instance(dummy_tool.tool_id, dummy_tool)
    mocker.patch.object(dummy_tool, 'stop')
    temp_manager.destroy_tool_instance(dummy_tool.tool_id)
    dummy_tool.stop.assert_called_once()
    assert dummy_tool.tool_id not in temp_manager.active_tools

def test_get_tool_and_get_all_tools(temp_manager, dummy_tool):
    temp_manager.register_tool_instance(dummy_tool.tool_id, dummy_tool)
    assert temp_manager.get_tool(dummy_tool.tool_id) is dummy_tool
    assert dummy_tool in temp_manager.get_all_tools()

def test_clear_all_tools(temp_manager, mocker):
    tool1 = DummyTool('id1')
    tool2 = DummyTool('id2')
    temp_manager.register_tool_instance(tool1.tool_id, tool1)
    temp_manager.register_tool_instance(tool2.tool_id, tool2)
    mocker.patch.object(tool1, 'stop')
    mocker.patch.object(tool2, 'stop')
    temp_manager.clear_all_tools()
    tool1.stop.assert_called_once()
    tool2.stop.assert_called_once()
    assert temp_manager.active_tools == {}

def test_handle_create_tool_registers_tool(temp_manager, mocker):
    dummy_data = {'tool_type': 'simple_clicker', 'tool_config': {'foo': 'bar'}}
    dummy_tool = DummyTool('dummy_id')
    mocker.patch.object(temp_manager, 'build', return_value=dummy_tool)
    mocker.patch.object(temp_manager, 'register_tool_instance')
    temp_manager.handle_create_tool(sender=None, data=dummy_data)
    temp_manager.build.assert_called_once_with('simple_clicker', tool_config={'foo': 'bar'})
    temp_manager.register_tool_instance.assert_called_once_with(dummy_tool.tool_id, dummy_tool)

def test_handle_start_tool_creates_and_starts(temp_manager, mocker):
    dummy_tool = DummyTool('dummy_id')
    # build returns dummy_tool, get_tool returns None first, then dummy_tool
    mocker.patch.object(temp_manager, 'build', return_value=dummy_tool)
    mocker.patch.object(temp_manager, 'get_tool', side_effect=[None, dummy_tool])
    mocker.patch.object(dummy_tool, 'start')
    data = {'tool_id': 'dummy_id', 'tool_type': 'simple_clicker'}
    temp_manager.handle_start_tool(sender=None, data=data)
    dummy_tool.start.assert_called_once()

def test_handle_start_tool_starts_existing(temp_manager, mocker):
    dummy_tool = DummyTool('dummy_id')
    mocker.patch.object(temp_manager, 'get_tool', return_value=dummy_tool)
    mocker.patch.object(dummy_tool, 'start')
    data = {'tool_id': 'dummy_id', 'tool_type': 'simple_clicker'}
    temp_manager.handle_start_tool(sender=None, data=data)
    dummy_tool.start.assert_called_once()

def test_handle_destroy_tool(temp_manager, mocker):
    mocker.patch.object(temp_manager, 'destroy_tool_instance')
    data = {'tool_id': 'dummy_id'}
    temp_manager.handle_destroy_tool(sender=None, data=data)
    temp_manager.destroy_tool_instance.assert_called_once_with('dummy_id')

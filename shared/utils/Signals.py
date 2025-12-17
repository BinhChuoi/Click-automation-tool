from blinker import Signal

# Define signals for UI actions
Interaction = Signal('non_core_action')

CreateTool = Signal('create_tool')
StartTool = Signal('start_tool')
StopTool = Signal('stop_tool')
DestroyTool = Signal('destroy_tool')

TaskStarted = Signal('task_started')
TaskStopped = Signal('task_stopped')
# You can add more signals as needed, e.g.:
# show_overlay = Signal('show_overlay')

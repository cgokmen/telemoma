import numpy as np
from telemoma.human_interface.teleop_core import BaseTeleopInterface, TeleopAction, TeleopObservation
import inputs

from telemoma.utils.general_utils import run_threaded_command

class PS3Interface(BaseTeleopInterface):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.actions = self.get_default_action()

        self.gamepad = kwargs.get("gamepad", None)
        if not self.gamepad:
            self._get_gamepad()

    def _get_gamepad(self):
        """Get a gamepad object."""
        try:
            self.gamepad = inputs.devices.gamepads[0]
        except IndexError:
            raise inputs.UnpluggedError("No gamepad found.")

    def start(self) -> None:
        # start the keyboard subscriber
        self.data_thread = run_threaded_command(self.get_inputs)

    def stop(self) -> None:
        self.data_thread.join()

    def get_inputs(self):
        while True:
            try:
                events = self.gamepad.read()
            except EOFError:
                events = []
            for event in events:
                self._update_internal_data(event)

    def _update_internal_data(self, event) -> None:
        if event.code == 'ABS_Y':
            axis = 0
        elif event.code == 'ABS_X':
            axis = 2
        else:
            return
        
        if event.ev_type != 'Absolute':
            return
        
        self.actions.base[axis] = -(event.state / 128.0 - 1.0)

    def get_action(self, obs: TeleopObservation) -> TeleopAction:
        return self.actions

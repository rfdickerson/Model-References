import os

def synapse_logger_start(step_idx, profile_hw=False):
    syn_log = SynapseLoggerHelpers.synapse_logger()
    if syn_log:
        if profile_hw:
            syn_log.start_hw_profile()
    else:
        logging.warning(
            "Synapse logger has not been enabled. Unable to start logging.")


def synapse_logger_stop(profile_hw=False):
    syn_log = SynapseLoggerHelpers.synapse_logger()
    if syn_log:
        if profile_hw:
            syn_log.stop_hw_profile()
    else:
        logging.warning(
            "Synapse logger has not been enabled. Unable to start logging.")

class SynapseLoggerHook():
    def __init__(self, steps_to_log, profile_hw=True):
        self._step_cnt = 0
        self._profile_hw = profile_hw
        self._steps_to_log = steps_to_log
        self._syn_logger_running = False

    def before_run(self):
        if not self._syn_logger_running:
            if self._step_cnt in self._steps_to_log:
                synapse_logger_start(
                    self._step_cnt, profile_hw=self._profile_hw)
                self._syn_logger_running = True

    def after_run(self):
        self._step_cnt += 1
        if self._syn_logger_running:
            if self._step_cnt not in self._steps_to_log:
                synapse_logger_stop(profile_hw=self._profile_hw)
                self._syn_logger_running = False

class SynapseLoggerHelpers:
    _syn_logger_init_done = False
    _syn_logger_setup_done = False
    _syn_logger = None

    @staticmethod
    def synapse_logger():
        if not SynapseLoggerHelpers._syn_logger_init_done and SynapseLoggerHelpers._synapse_logger_required():
            import sys

            new_path = os.environ.get("BUILD_ROOT_LATEST", False)
            if new_path:
                new_path = os.path.join(new_path)
                sys.path.insert(0, new_path)

            new_path = os.environ.get("TF_MODULES_RELEASE_BUILD", False)
            if new_path:
                new_path = os.path.join(new_path)
                sys.path.insert(0, new_path)

            import py_synapse_logger as syn_log
            SynapseLoggerHelpers._syn_logger = syn_log
            SynapseLoggerHelpers._syn_logger_init_done = True
            SynapseLoggerHelpers._syn_logger.command("disable")
        return SynapseLoggerHelpers._syn_logger

    @staticmethod
    def _get_synapse_logger_env():
        return os.environ.get("HABANA_SYNAPSE_LOGGER", "False").lower()

    @staticmethod
    def _synapse_logger_required():
        return SynapseLoggerHelpers._get_synapse_logger_env() in ["range_hw"]


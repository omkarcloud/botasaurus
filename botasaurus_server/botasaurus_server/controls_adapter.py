_botasaurus_controls = None

def get_botasaurus_controls():
    global _botasaurus_controls
    if _botasaurus_controls is None:
        # The 'require' function is used for dynamic imports in this context,
        # adjust accordingly if your environment does not support 'require'
        from javascript_fixes import require
        _botasaurus_controls = require("botasaurus-controls")
    return _botasaurus_controls

class ControlsAdapter:
    @staticmethod
    def createControls(input_js):
        # Directly use get_botasaurus_controls to access and invoke createControls
        return get_botasaurus_controls().createControls(input_js, timeout=300)
import { createControls } from 'botasaurus-controls'

export class ControlsAdapter {
    static createControls(input_js: any) {
        // Directly use get_botasaurus_controls to access and invoke createControls
        return createControls(input_js);
    }
}
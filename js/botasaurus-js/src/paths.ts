import path from "path";

type ElectronConfig = {
    downloadsPath: string;
    userDataPath: string;
    productName: string;
    protocol: string;
    isDev: boolean;
};

// @ts-ignore
const isElectron = !!global.ELECTRON_CONFIG;

// @ts-ignore
const electronConfig: ElectronConfig = global.ELECTRON_CONFIG as unknown as ElectronConfig;
const isElectronAndDev: boolean = isElectron && electronConfig.isDev;

export function getTargetDirectoryPath() {
    if (isElectron) {
        if (!isElectronAndDev) {
            return electronConfig.userDataPath;
        }
        return path.join(__dirname, "../../");
    }
    return process.cwd();
}
import * as fs from "fs";
import * as path from "path";

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
export const electronConfig: ElectronConfig = global.ELECTRON_CONFIG as unknown as ElectronConfig;
const isElectronAndDev: boolean = isElectron && electronConfig.isDev;


export function getPathToDownloadsDirectory(filename: string, downloadFolder?: string | null): string {
    let targetPath: string;
    
    if (downloadFolder && downloadFolder.trim() !== '') {
        // Use custom download folder
        targetPath = downloadFolder;
        targetPath = path.join(targetPath, electronConfig.productName);
    } else {
        // Use default downloads path
        const downloadsPath = electronConfig.downloadsPath;
        targetPath = path.join(downloadsPath, electronConfig.productName);
    }

    if (!fs.existsSync(targetPath)) {
        fs.mkdirSync(targetPath, { recursive: true });
    }

    const filePath = path.join(targetPath, filename);

    return filePath;
}

export function getTargetDirectoryPath() {
    if (isElectron) {
        if (isElectronAndDev) {
            if (isRunningInErbDll()) {
                return path.join(__dirname, "../../");
            }
            return __dirname;
        }
        // In Production
        return electronConfig.userDataPath;
    }
    return process.cwd();
}

function isRunningInErbDll() {
    const currentDir = __dirname;
    const dirName = path.basename(currentDir);
    const parentDir = path.basename(path.dirname(currentDir));

    return parentDir === ".erb" && dirName === "dll";
}

export function getReadmePath(): string {
    if (isElectron) {
        if (isElectronAndDev) {
            if (isRunningInErbDll()) {
                return path.join(__dirname, "../", "../", "README.md");
            }
        }
        return path.join(__dirname, "README.md");
    }
    return path.join(process.cwd(), "README.md");
}

export function getInputFilePath(arg1: string): string {
    if (isElectron) {
        if (isElectronAndDev) {
            if (isRunningInErbDll()) {
                const inputFilePath = path.join(
                    __dirname,
                    "../",
                    "../",
                    "inputs",
                    `${arg1}.js`
                );
                return inputFilePath;
            }
        }
        return path.join(__dirname, "inputs", `${arg1}.js`);
    }
    return path.join(process.cwd(), "inputs", `${arg1}.js`);
}
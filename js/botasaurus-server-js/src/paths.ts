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

// A business type alone may be 255 characters, and on Windows the whole path must
// fit in 260, so a task's name can be too long to be a filename: the export then
// always failed. Bytes, because macOS and Linux limit names in bytes.
const MAX_FILENAME_BYTES = 150;

/** A name for a task's export: never empty, and short enough to be written. */
export function taskFilename(kebabName: string, taskId: number) {
    if (!kebabName) {
        return `task-${taskId}`;
    }
    if (Buffer.byteLength(kebabName) <= MAX_FILENAME_BYTES) {
        return kebabName;
    }
    // The id keeps two long names that start alike from overwriting each other
    return `${Buffer.from(kebabName).subarray(0, MAX_FILENAME_BYTES).toString('utf-8').replace(/\uFFFD+$/, '')}-${taskId}`;
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
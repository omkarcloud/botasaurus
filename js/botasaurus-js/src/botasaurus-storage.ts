import fs from 'fs';
import { relativePath } from "./decorators-utils";

function getBotasaurusStoragePath(): string {
    return relativePath('botasaurus_storage.json');
}
function safeWrite(data: string,  filePath: string, tempPath: string,): void {
    fs.writeFileSync(tempPath, data,  { encoding: "utf-8" });
    try {
        fs.renameSync(tempPath, filePath);
    } catch (error) {
        if (fs.existsSync(tempPath)) {
            fs.unlinkSync(tempPath);
        }
        return fs.writeFileSync(filePath, data,  { encoding: "utf-8" });
    }
}


class JSONStorageBackend {
    private jsonPath: string;
    private tempPath: string;
    private jsonData: Record<string, any>;

    constructor(path: string = getBotasaurusStoragePath()) {
        this.jsonPath = path;
        this.tempPath = path + ".temp";
        this.jsonData = {};
        this.refresh();
    }

    refresh(): void {
        if (!fs.existsSync(this.jsonPath)) {
            this.commitToDisk();
        }
        const fileContent = fs.readFileSync(this.jsonPath, 'utf-8');
        try {
            this.jsonData = JSON.parse(fileContent);    
        } catch (error) {
            // file corruption
            this.jsonData = {}
            return
        }
    }

    private commitToDisk(): void {
        safeWrite(JSON.stringify(this.jsonData, null, 4), this.jsonPath, this.tempPath)
    }

    getItem(key: string, defaultValue: any = null): any {
        return key in this.jsonData ? this.jsonData[key] : defaultValue;
    }

    items(): Record<string, any> {
        return { ...this.jsonData };
    }

    setItem(key: string, value: any): void {
        this.jsonData[key] = value;
        this.commitToDisk();
    }
    setStorage(storage: Record<string, any>): void {
        if (!storage || typeof storage !== 'object') {
            throw new Error('Storage must be a valid object');
        }

        this.jsonData = { ...storage }; // Create a copy to prevent reference issues
        this.commitToDisk();
    }
    removeItem(key: string): void {
        if (key in this.jsonData) {
            delete this.jsonData[key];
            this.commitToDisk();
        }
    }

    clear(): void {
        if (fs.existsSync(this.jsonPath)) {
            fs.unlinkSync(this.jsonPath);
        }
        this.jsonData = {};
        this.commitToDisk();
    }
}

class LocalStorage {
    private storageBackendInstance: JSONStorageBackend;

    constructor(path: string = getBotasaurusStoragePath()) {
        this.storageBackendInstance = new JSONStorageBackend(path);
    }

    refresh(): void {
        this.storageBackendInstance.refresh();
    }

    getItem(item: string, defaultValue: any = null): any {
        return this.storageBackendInstance.getItem(item, defaultValue);
    }

    setItem(item: string, value: any): void {
        this.storageBackendInstance.setItem(item, value);
    }
    setStorage(storage: Record<string, any>): void {
        this.storageBackendInstance.setStorage(storage);
    }

    removeItem(item: string): void {
        this.storageBackendInstance.removeItem(item);
    }

    clear(): void {
        this.storageBackendInstance.clear();
    }

    items(): Record<string, any> {
        return this.storageBackendInstance.items();
    }
    resetStorage(): void {
        this.setStorage({});
    }
}

let _storage: LocalStorage | null = null;

function getBotasaurusStorage(): LocalStorage {
    if (!_storage) {
        _storage = new LocalStorage();
    }
    return _storage;
}

export {
    getBotasaurusStoragePath,
    getBotasaurusStorage,
    LocalStorage, 
};
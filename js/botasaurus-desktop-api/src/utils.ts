import fs from 'fs';
import path from 'path';

function removeAfterFirstSlash(inputString: string): string {
    let i = 0;
    const strLen = inputString.length;
    while (true) {
        if (i < strLen) {
            const char = inputString[i];
            if (char === '/') {
                if (i + 1 < inputString.length && inputString[i + 1] === '/') {
                    i += 2;
                    continue;
                } else {
                    return inputString.substring(0, i);
                }
            }
            i++;
        } else {
            break;
        }
    }
    return inputString;
}

function relativePath(targetPath: string, goback: number = 0): string {
    const levels = Array(Math.max(0, goback - 1)).fill('..');
    return path.resolve(process.cwd(), ...levels, targetPath.trim());
}

function createDirectoryIfNotExists(passedPath: string): void {
    const dirPath = relativePath(passedPath, 0);
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

let outputDirectoryCreated = false;
function createOutputDirectoryIfNotExists(): void {
    // Check if output directory exists, if not, create it
    if (!outputDirectoryCreated) {
        createDirectoryIfNotExists("output");
        createDirectoryIfNotExists("output/responses");
        outputDirectoryCreated = true;
    }
}

function writeJsonResponse(filePath: string, data: any, indent: number = 4): void {
    createOutputDirectoryIfNotExists();
    fs.writeFileSync(filePath, JSON.stringify(data, null, indent), { encoding: 'utf-8' });
}

function getFilenameFromResponseHeaders(response: { headers: { get: (header: string) => string | null } }): string {
    const contentDisposition = response.headers.get('Content-Disposition');
    if (!contentDisposition) throw new Error('Content-Disposition header not found');
    const filenamePart = contentDisposition.split('filename=')[1];
    if (!filenamePart) throw new Error('Filename not found in Content-Disposition');
    return filenamePart.trim().replace(/^"|"$/g, '');
}

function writeFileResponse(filePath: string, filename: string, content: Buffer): string {
    createOutputDirectoryIfNotExists();
    const fullPath = path.join(filePath, filename);
    fs.writeFileSync(fullPath, content);
    return fullPath;
}

export {
    removeAfterFirstSlash,
    relativePath,
    createDirectoryIfNotExists,
    createOutputDirectoryIfNotExists,
    writeJsonResponse,
    getFilenameFromResponseHeaders,
    writeFileResponse
};
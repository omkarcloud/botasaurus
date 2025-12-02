import fs from 'fs';
import path from 'path';

/**
 * Removes everything after (and including) the first single slash (/) in a string,
 * but skips over '//' (double slashes), which are used in protocols like 'http://'.
 * This is primarily used to extract the base URL (protocol + host) from a full URL.
 * 
 * Example:
 *   removeAfterFirstSlash("https://example.com/api/v1") // "https://example.com"
 *   removeAfterFirstSlash("http://foo/bar/baz") // "http://foo"
 *   removeAfterFirstSlash("localhost:8000/api/v1") // "localhost:8000"
 *   removeAfterFirstSlash("https://example.com") // "https://example.com"
 */
function removeAfterFirstSlash(inputString: string): string {
    let i = 0;
    const strLen = inputString.length;
    while (i < strLen) {
        const char = inputString[i];
        if (char === '/') {
            // Check for double slash (e.g., 'http://')
            if (i + 1 < strLen && inputString[i + 1] === '/') {
                i += 2;
                continue;
            } else {
                // Single slash: trim here
                return inputString.substring(0, i);
            }
        }
        i++;
    }
    // No single slash found (or only part of protocol), return the whole input
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
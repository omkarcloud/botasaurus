import path from 'path'
import fs from 'fs'
import { getTargetDirectoryPath } from './paths'

function relativePath(filePath:string, goback = 0) {
    const levels = Array(goback ).fill('..');
    return path.resolve(getTargetDirectoryPath(), ...levels, filePath.trim());
}

function createDirectoryIfNotExists(passedPath:string) {
    const dirPath = relativePath(passedPath);

    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}


let outputCheckDone = false;

function createOutputDirectoryIfNotExists() {
    if (!outputCheckDone) {
        outputCheckDone = true;
        createDirectoryIfNotExists('output/');
    }
}

export  {
    relativePath,
    createDirectoryIfNotExists,
    createOutputDirectoryIfNotExists
};
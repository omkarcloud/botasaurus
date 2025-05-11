const fs = require('fs');
const path = require('path');
const UglifyJS = require('uglify-js');

function minifyFile(inputFile) {
    return new Promise((resolve, reject) => {
        fs.readFile(inputFile, 'utf8', (err, data) => {
            if (err) {
                reject(`Error reading file ${inputFile}: ${err}`);
                return;
            }

            const minifiedCode = UglifyJS.minify(data);
            if (minifiedCode.error) {
                reject(`Error minifying code in ${inputFile}: ${minifiedCode.error}`);
                return;
            }

            fs.writeFile(inputFile, minifiedCode.code, err => {
                if (err) {
                    reject(`Error writing minified file ${inputFile}: ${err}`);
                    return;
                }
                resolve(`Minified file: ${inputFile}`);
            });
        });
    });
}

async function getJsFilesRecursively(directory) {
    let jsFiles = [];
    const items = await fs.promises.readdir(directory, { withFileTypes: true });

    for (const item of items) {
        const fullPath = path.join(directory, item.name);
        if (item.isDirectory()) {
            jsFiles = jsFiles.concat(await getJsFilesRecursively(fullPath));
        } else if (path.extname(item.name).toLowerCase() === '.js') {
            jsFiles.push(fullPath);
        }
    }


    return jsFiles;
}

async function getFilesRecursively(directory) {
    let jsFiles = [];
    const items = await fs.promises.readdir(directory, { withFileTypes: true });

    for (const item of items) {
        const fullPath = path.join(directory, item.name);
        if (item.isDirectory()) {
            jsFiles = jsFiles.concat(await getJsFilesRecursively(fullPath));
        } else {
            jsFiles.push(fullPath);
        }
    }


    return jsFiles;
}
async function minifyAllJsFiles(directory) {
    try {
        const jsFiles = await getJsFilesRecursively(directory);
        
        const minifyPromises = jsFiles.map(async (file) => {
            try {
                const result = await minifyFile(file);
                console.log(result);
            } catch (error) {
                console.error(error);
            }
        });

        await Promise.all(minifyPromises);
    } catch (error) {
        console.error(`Error processing directory ${directory}:`, error);
    }
}

function unlinkAsync(filePath) {
    return new Promise((resolve, reject) => {
        fs.unlink(filePath, (err) => {
            if (err) {
                reject(err);
            } else {
                resolve();
            }
        });
    });
}

async function deleteMapFiles(directory) {
    try {
        const jsFiles = await getFilesRecursively(directory);
        const mapFiles = jsFiles.filter(file => file.endsWith('.map'));
        for (const file of mapFiles) {
            const filePath =file;
            await unlinkAsync(filePath);
            console.log(`Deleted: ${filePath}`);
        }
    } catch (error) {
        console.error(`Error processing directory ${directory}:`, error);
    }
}
// Usage
const distDirectory = 'dist';
// deleteMapFiles(distDirectory)
minifyAllJsFiles(distDirectory);

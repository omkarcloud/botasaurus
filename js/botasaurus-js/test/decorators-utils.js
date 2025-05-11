const assert = require('assert');
const path = require('path');
const fs = require('fs');
const {
    relativePath,
    createDirectoryIfNotExists,
    createOutputDirectoryIfNotExists
} = require('../src/decorators-utils'); // Assuming the previous code is saved as path-utils.js

describe('Path Utilities', () => {
    it('relativePath should work correctly', () => {
        const result = relativePath('test', 0);
        assert.strictEqual(result, path.resolve(process.cwd(), 'test'));
    });

    it('createDirectoryIfNotExists should create a directory', () => {
        const testDir = 'output';
        createDirectoryIfNotExists(testDir);
        assert.strictEqual(fs.existsSync(testDir), true);
        fs.rmdirSync(testDir);
    });

    
    it('createOutputDirectoryIfNotExists should create an output directory', () => {
        createOutputDirectoryIfNotExists();
        assert.strictEqual(fs.existsSync('output'), true);
        fs.rmdirSync('output');
    });
});
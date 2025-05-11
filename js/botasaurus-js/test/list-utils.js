const assert = require('assert');
const {
    flatten, flattenDeep
} = require('../src/list-utils'); // Assuming the previous code is saved as path-utils.js

describe('flatten', () => {
    it('should flatten a single level of nested arrays', () => {
        const input = [1, [2, 3], 4];
        const expected = [1, 2, 3, 4];
        assert.deepEqual(flatten(input), expected);
    });

    it('should flatten multiple levels of nested arrays', () => {
        const input = [1, [2, [3, 4]], 5];
        const expected = [1, 2, [3, 4], 5];
        assert.deepEqual(flatten(input), expected);
    });

    it('should handle empty arrays', () => {
        const input = [];
        const expected = [];
        assert.deepEqual(flatten(input), expected);
    });

    it('should handle arrays with no nesting', () => {
        const input = [1, 2, 3];
        const expected = [1, 2, 3];
        assert.deepEqual(flatten(input), expected);
    });
});

describe('flattenDeep', () => {
    it('should deeply flatten nested arrays', () => {
        const input = [1, [2, [3, [4, 5]]], 6];
        const expected = [1, 2, 3, 4, 5, 6];
        assert.deepEqual(flattenDeep(input), expected);
    });

    it('should handle empty arrays', () => {
        const input = [];
        const expected = [];
        assert.deepEqual(flattenDeep(input), expected);
    });

    it('should handle arrays with no nesting', () => {
        const input = [1, 2, 3];
        const expected = [1, 2, 3];
        assert.deepEqual(flattenDeep(input), expected);
    });
});
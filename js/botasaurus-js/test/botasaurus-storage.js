const assert = require('assert').strict;
const fs = require('fs');
const { getBotasaurusStorage } = require('../src/botasaurus-storage'); // Adjust the require path as needed

describe('BotasaurusStorage', () => {
  let storage;
  const testFilePath = 'botasaurus_storage.json';

  beforeEach(() => {
    // Clear any existing storage file
    if (fs.existsSync(testFilePath)) {
      fs.unlinkSync(testFilePath);
    }
    storage = getBotasaurusStorage();
  });

  afterEach(() => {
    // Clean up after each test
    if (fs.existsSync(testFilePath)) {
      fs.unlinkSync(testFilePath);
    }
  });

  describe('getBotasaurusStorage', () => {
    it('should return the same instance on multiple calls', () => {
      const storage1 = getBotasaurusStorage();
      const storage2 = getBotasaurusStorage();
      assert.strictEqual(storage1, storage2);
    });
  });

  describe('setItem and getItem', () => {
    it('should set and get an item correctly', () => {
      storage.setItem('testKey', 'testValue');
      assert.strictEqual(storage.getItem('testKey'), 'testValue');
    });

    it('should return default value for non-existent key', () => {
      assert.strictEqual(storage.getItem('nonExistentKey', 'defaultValue'), 'defaultValue');
    });

    it('should overwrite existing value', () => {
      storage.setItem('testKey', 'initialValue');
      storage.setItem('testKey', 'newValue');
      assert.strictEqual(storage.getItem('testKey'), 'newValue');
    });
  });

  describe('removeItem', () => {
    it('should remove an existing item', () => {
      storage.setItem('testKey', 'testValue');
      storage.removeItem('testKey');
      assert.strictEqual(storage.getItem('testKey'), null);
    });

    it('should not throw error when removing non-existent item', () => {
      assert.doesNotThrow(() => {
        storage.removeItem('nonExistentKey');
      });
    });
  });

  describe('clear', () => {
    it('should remove all items', () => {
      storage.setItem('key1', 'value1');
      storage.setItem('key2', 'value2');
      storage.clear();
      assert.deepStrictEqual(storage.items(), {});
    });
  });

  describe('items', () => {
    it('should return all items', () => {
      storage.setItem('key1', 'value1');
      storage.setItem('key2', 'value2');
      assert.deepStrictEqual(storage.items(), { key1: 'value1', key2: 'value2' });
    });
  });

  describe('refresh', () => {
    it('should reload data from disk', () => {
      storage.setItem('key1', 'value1');
      
      // Simulate external change to the file
      const externalData = { key2: 'value2' };
      fs.writeFileSync(testFilePath, JSON.stringify(externalData));

      storage.refresh();
      assert.deepStrictEqual(storage.items(), externalData);
    });
  });

  describe('File persistence', () => {
    it('should persist data to file', () => {
      storage.setItem('key1', 'value1');
      
      // Create a new instance to force reading from file
      const newStorage = getBotasaurusStorage();
      assert.strictEqual(newStorage.getItem('key1'), 'value1');
    });
  });
});
const assert = require('assert');
const {
  NumericAscendingSort,
  NumericDescendingSort,
  TrueFirstSort,
  FalseFirstSort,
  TruthyFirstSort,
  FalsyFirstSort,
  NullsFirstSort,
  NullsLastSort,
  NewestDateFirstSort,
  OldestDateFirstSort,
  AlphabeticAscendingSort,
  AlphabeticDescendingSort,
} = require('../src/sorts');

describe('Sorting functions', () => {
  const data = () => [
    { name: 'John', age: 30, active: true, date: '2022-01-01' },
    { name: 'Alice', age: 25, active: false, date: '2021-12-31' },
    { name: 'Bob', age: 35, active: null, date: null },
    { name: 'Eve', age: 28, active: true, date: '2022-01-02' },
  ];

  it('should sort numerically in ascending order', () => {
    const sort = new NumericAscendingSort('age');
    const sortedData = sort.apply(data());
    assert.deepStrictEqual(sortedData.map(item => item.age), [25, 28, 30, 35]);
  });

  it('should sort numerically in descending order', () => {
    const sort = new NumericDescendingSort('age');
    const sortedData = sort.apply(data());
    assert.deepStrictEqual(sortedData.map(item => item.age), [35, 30, 28, 25]);
  });

  it('should sort with true values first', () => {
    const sort = new TrueFirstSort('active');
    const sortedData = sort.apply(data());
    assert.deepStrictEqual(sortedData.map(item => item.active), [true, true, false, null]);
  });

  it('should sort with false values first', () => {
    const sort = new FalseFirstSort('active');
    const sortedData = sort.apply(data());
    assert.deepStrictEqual(sortedData.map(item => item.active), [false, true, true, null]);
  });

  it('should sort with truthy values first', () => {
    const sort = new TruthyFirstSort('active');
    const sortedData = sort.apply(data());

    assert.deepStrictEqual(sortedData.map(item => item.active), [true, true, false, null]);
  });

  it('should sort with falsy values first', () => {
    const sort = new FalsyFirstSort('active');
    const sortedData = sort.apply(data());

    assert.deepStrictEqual(sortedData.map(item => item.active), [ false, null, true, true ]);
  });

  it('should sort with null values first', () => {
    const sort = new NullsFirstSort('active');
    const sortedData = sort.apply(data());
    assert.deepStrictEqual(sortedData.map(item => item.active), [null, true, false,true, ]);
  });

  it('should sort with null values last', () => {
    const sort = new NullsLastSort('active');
    const sortedData = sort.apply(data());

    assert.deepStrictEqual(sortedData.map(item => item.active), [true, false,true,  null]);
  });

  it('should sort dates with newest first', () => {
    const sort = new NewestDateFirstSort('date');
    const sortedData = sort.apply(data());
    assert.deepStrictEqual(sortedData.map(item => item.date), ['2022-01-02', '2022-01-01', '2021-12-31', null]);
  });

  it('should sort dates with oldest first', () => {
    const sort = new OldestDateFirstSort('date');
    const sortedData = sort.apply(data());
    assert.deepStrictEqual(sortedData.map(item => item.date), ['2021-12-31', '2022-01-01', '2022-01-02', null]);
  });

  it('should sort alphabetically in ascending order', () => {
    const sort = new AlphabeticAscendingSort('name');
    const sortedData = sort.apply(data());
    assert.deepStrictEqual(sortedData.map(item => item.name), ['Alice', 'Bob', 'Eve', 'John']);
  });

  it('should sort alphabetically in descending order', () => {
    const sort = new AlphabeticDescendingSort('name');
    const sortedData = sort.apply(data());
    assert.deepStrictEqual(sortedData.map(item => item.name), ['John', 'Eve', 'Bob', 'Alice']);
  });
});
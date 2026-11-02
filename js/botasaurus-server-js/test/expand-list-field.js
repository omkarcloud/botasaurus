const assert = require('assert');
const { Field, ExpandListField, transformRecord, transformRecordStream, getFields } = require('../src/views');

const fields = (options) => [new Field('name'), new ExpandListField('leads', [new Field('name', { outputKey: 'lead_name' }), new Field('title')], options), new Field('error')];

describe('expanding a list into rows', () => {
  const place = { name: 'a', leads: [{ name: 'x', title: 't' }, { name: 'y', title: 'u' }], error: null };
  const noLeads = { name: 'b', leads: [], error: 'failed' };

  for (const [label, transform] of [['transformRecord', transformRecord], ['transformRecordStream', (f, r) => [...transformRecordStream(f, r)]]]) {
    it(`${label}: one row per item`, () => {
      assert.deepStrictEqual(transform(fields({ keepWhenEmpty: true }), place).map((r) => r.lead_name), ['x', 'y']);
    });

    it(`${label}: an empty list has no row by default`, () => {
      assert.deepStrictEqual(transform(fields(), noLeads), []);
    });

    it(`${label}: keepWhenEmpty keeps one row, with the other columns filled`, () => {
      const rows = transform(fields({ keepWhenEmpty: true }), noLeads);
      assert.strictEqual(rows.length, 1);
      assert.strictEqual(rows[0].name, 'b');
      assert.strictEqual(rows[0].error, 'failed');
      assert.ok('lead_name' in rows[0]);
    });

    it(`${label}: a missing list counts as empty`, () => {
      assert.strictEqual(transform(fields({ keepWhenEmpty: true }), { name: 'c' }).length, 1);
    });
  }

  it('getFields keeps the option when it rebuilds the field', () => {
    const shown = getFields(fields({ keepWhenEmpty: true, showIf: () => true }), {}, []);
    assert.strictEqual(shown.find((f) => f instanceof ExpandListField).keepWhenEmpty, true);
    const always = getFields(fields({ keepWhenEmpty: true }), {}, []);
    assert.strictEqual(always.find((f) => f instanceof ExpandListField).keepWhenEmpty, true);
  });
});

import { snakeCase } from 'change-case';
import { isNotNullish } from './null-utils';
import { isEmpty, isObject } from './utils'
import { TaskResults } from './task-results'

type MapFunction = (...args: any[]) => any;

class Field {
    key: string;
    outputKey: string;
    showIf?: (data: any) => boolean;
    map?: MapFunction;

    constructor(key: string, options?: { outputKey?: string, map?: MapFunction, showIf?: (data: any) => boolean }) {
        this.key = key;
        this.outputKey = options?.outputKey || key;
        this.showIf = options?.showIf;

        if (options?.map && typeof options.map !== 'function') {
            throw new Error(`map function must be callable for Field '${this.key}'`);
        }
        this.map = options?.map;
    }
}

class CustomField {
    key: string;
    outputKey: string;
    map: MapFunction;
    showIf?: (data: any) => boolean;

    constructor(key: string, map: MapFunction, options?: { showIf?: (data: any) => boolean }) {
        this.key = key;
        if (typeof map !== 'function') {
            throw new Error(`map function must be callable for CustomField '${this.key}'`);
        }
        this.outputKey = key;
        this.map = map;
        this.showIf = options?.showIf;
    }
}

class ExpandDictField {
    key: string;
    fields: (Field | CustomField)[];
    showIf?: (data: any) => boolean;

    constructor(key: string, fields: (Field | CustomField)[], options?: { showIf?: (data: any) => boolean }) {
        this.key = key;
        this.fields = fields;
        this.showIf = options?.showIf;

        for (const field of fields) {
            if (!(field instanceof Field) && !(field instanceof CustomField)) {
                throw new Error(`ExpandDictField '${this.key}' can only contain Field and CustomField`);
            }
        }
    }
}

class ExpandListField {
    key: string;
    fields: (Field | CustomField | ExpandDictField)[];
    showIf?: (data: any) => boolean;

    constructor(key: string, fields: (Field | CustomField | ExpandDictField)[], options?: { showIf?: (data: any) => boolean }) {
        this.key = key;
        this.fields = fields;
        this.showIf = options?.showIf;
        for (const field of fields) {
            if (!(field instanceof Field) && !(field instanceof CustomField) && !(field instanceof ExpandDictField)) {
                throw new Error(`ExpandListField '${this.key}' can only contain Field, CustomField and ExpandDictField`);
            }
        }
    }
}

class View {
    name: string;
    fields: (Field | CustomField | ExpandDictField | ExpandListField)[];
    id: string;
    containsListField: boolean;

    constructor(name: string, fields: (Field | CustomField | ExpandDictField | ExpandListField)[]) {
        this.name = name;
        this.fields = fields;
        this.id = snakeCase(name);
        this.containsListField = false;

        let expandListCount = 0;
        for (const field of this.fields) {
            if (field instanceof ExpandListField) {
                expandListCount++;
            }
        }

        if (expandListCount > 1) {
            throw new Error(`View '${this.name}' can only contain a maximum of one ExpandListField`);
        }

        for (const field of fields) {
            if (field instanceof Field && field.map) {
                if (field.map.length !== 2) {
                    throw new Error(`Field '${field.key}' map function must accept 2 arguments`);
                }
            } else if (field instanceof CustomField && field.map) {
                if (field.map.length !== 1) {
                    throw new Error(`CustomField '${field.key}' map function must accept 1 argument`);
                }
            } else if (field instanceof ExpandDictField) {
                for (const nestedField of field.fields) {
                    if (nestedField instanceof Field && nestedField.map) {
                        if (nestedField.map.length !== 3) {
                            throw new Error(`Field '${nestedField.key}' map function must accept 3 arguments`);
                        }
                    } else if (nestedField instanceof CustomField && nestedField.map) {
                        if (nestedField.map.length !== 2) {
                            throw new Error(`CustomField '${nestedField.key}' map function must accept 2 arguments`);
                        }
                    }
                }
            } else if (field instanceof ExpandListField) {
                this.containsListField = true;
                for (const nestedField of field.fields) {
                    if (nestedField instanceof Field && nestedField.map) {
                        if (nestedField.map.length !== 3) {
                            throw new Error(`Field '${nestedField.key}' map function must accept 3 arguments`);
                        }
                    } else if (nestedField instanceof CustomField && nestedField.map) {
                        if (nestedField.map.length !== 2) {
                            throw new Error(`CustomField '${nestedField.key}' map function must accept 2 arguments`);
                        }
                    } else if (nestedField instanceof ExpandDictField) {
                        for (const deepNestedField of nestedField.fields) {
                            if (deepNestedField instanceof Field && deepNestedField.map) {
                                if (deepNestedField.map.length !== 4) {
                                    throw new Error(`Field '${deepNestedField.key}' map function must accept 4 arguments`);
                                }
                            } else if (deepNestedField instanceof CustomField && deepNestedField.map) {
                                if (deepNestedField.map.length !== 3) {
                                    throw new Error(`CustomField '${deepNestedField.key}' map function must accept 3 arguments`);
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    apply(data: any[]): [any[], string[]] {
        return performApplyView(data, this);
    }

    toJson() {
        const flatFields = this.flattenFields(this.fields);
        return {
            id: this.id,
            label: this.name,
            fields: flatFields
        };
    }

    private flattenFields(fields: (Field | CustomField | ExpandDictField | ExpandListField)[]): { key: string }[] {
        const flatList: { key: string }[] = [];
        for (const field of fields) {
            if (field instanceof Field || field instanceof CustomField) {
                flatList.push({ key: field.outputKey });
            } else if (field instanceof ExpandDictField || field instanceof ExpandListField) {
                flatList.push(...this.flattenFields(field.fields));
            }
        }
        return flatList;
    }
}

function createNestedFieldValues(record: Record<string, any>, field: ExpandDictField): Record<string, any> {
    const nestedDict = record[field.key] || {};
    const nestedFieldValues: Record<string, any> = {};
    for (const nestedField of field.fields) {
        if (isObject(nestedDict)) {
            const value = nestedDict[nestedField.key];
            if (nestedField instanceof Field) {
                const processedValue = nestedField.map
                    ? nestedField.map(value, nestedDict, record)
                    : value;
                nestedFieldValues[nestedField.outputKey] = processedValue;
            } else if (nestedField instanceof CustomField) {
                nestedFieldValues[nestedField.outputKey] = nestedField.map(nestedDict, record);
            }
        } else {
            nestedFieldValues[nestedField.outputKey] = null;
        }
    }
    return nestedFieldValues;
}

function createNestedFieldValuesListed(item: Record<string, any>, field: ExpandDictField, parentRecord: Record<string, any>): Record<string, any> {
    const nestedDict = item[field.key] || {};
    const nestedFieldValues: Record<string, any> = {};
    for (const nestedField of field.fields) {
        const value = nestedDict[nestedField.key];
        if (nestedField instanceof Field) {
            const processedValue = nestedField.map
                ? nestedField.map(value, nestedDict, item, parentRecord)
                : value;
            nestedFieldValues[nestedField.outputKey] = processedValue;
        } else if (nestedField instanceof CustomField) {
            nestedFieldValues[nestedField.outputKey] = nestedField.map(nestedDict, item, parentRecord);
        }
    }
    return nestedFieldValues;
}

function getFields(fields: (Field | CustomField | ExpandDictField | ExpandListField)[], inputData: any, hidden_fields: string[]): (Field | CustomField | ExpandDictField | ExpandListField)[] {
    const result: (Field | CustomField | ExpandDictField | ExpandListField)[] = [];
    for (const f of fields) {
        if (f instanceof Field || f instanceof CustomField) {
            if (f.showIf) {
                if (f.showIf(inputData)) {
                    result.push(f);
                } else {
                    hidden_fields.push(f.outputKey);
                }
            } else {
                result.push(f);
            }
        } else if (f instanceof ExpandDictField) {
            if (f.showIf) {
                if (f.showIf(inputData)) {
                    result.push(new ExpandDictField(f.key, getFields(f.fields, inputData, hidden_fields) as (Field | CustomField)[]));
                } else {
                    for (const i of f.fields) {
                        hidden_fields.push(i.outputKey);
                    }
                }
            } else {
                result.push(new ExpandDictField(f.key, getFields(f.fields, inputData, hidden_fields) as (Field | CustomField)[]));
            }
        } else if (f instanceof ExpandListField) {
            if (f.showIf) {
                if (f.showIf(inputData)) {
                    result.push(new ExpandListField(f.key, getFields(f.fields, inputData, hidden_fields) as (Field | CustomField | ExpandDictField)[]));
                } else {
                    for (const i of f.fields) {
                        if (i instanceof Field || i instanceof CustomField) {
                            hidden_fields.push(i.outputKey);
                        } else {
                            for (const n of i.fields) {
                                hidden_fields.push(n.outputKey);
                            }
                        }
                    }
                }
            } else {
                result.push(new ExpandListField(f.key, getFields(f.fields, inputData, hidden_fields) as (Field | CustomField | ExpandDictField)[]));
            }
        }
    }
    return result;
}


function transformRecords(results: any[], targetFields: (Field | CustomField | ExpandDictField | ExpandListField)[]) {
    const processedResults: any[] = []

    for (const record of results) {
        const expandedRecords: any[] = transformRecord(targetFields, record)
        processedResults.push(...expandedRecords)
    }
    return processedResults
}

function transformRecordsInPlace(results: any[], targetFields: (Field | CustomField | ExpandDictField | ExpandListField)[]) {
    const processedResults: any[] = []

    for (let i = 0; i < results.length; i++) {
        const record = results[i];
        const expandedRecords: any[] = transformRecord(targetFields, record);
        processedResults.push(...expandedRecords);

        // Set the item to null to save space
        results[i] = null;
    }
    return processedResults;
}
function transformRecord(targetFields: (Field | CustomField | ExpandDictField | ExpandListField)[], record: any) {
    let expandedRecords: any[] = [{}]

    for (const field of targetFields) {
        if (field instanceof Field) {
            const value = record[field.key]
            const result = field.map ? field.map(value, record) : value
            for (const expandedRecord of expandedRecords) {
                expandedRecord[field.outputKey] = result
            }
        } else if (field instanceof CustomField) {
            const result = field.map(record)
            for (const expandedRecord of expandedRecords) {
                expandedRecord[field.outputKey] = result
            }
        } else if (field instanceof ExpandDictField) {
            const nestedFieldValues = createNestedFieldValues(record, field)
            for (const expandedRecord of expandedRecords) {
                Object.assign(expandedRecord, nestedFieldValues)
            }
        } else if (field instanceof ExpandListField) {
            const nestedList = record[field.key] || []
            const newExpandedRecords: any[] = []

            for (const item of nestedList) {
                for (const baseExpandedRecord of expandedRecords) {
                    const newRecord = { ...baseExpandedRecord }
                    for (const nestedField of field.fields) {
                        if (nestedField instanceof Field) {
                            const value = item[nestedField.key]
                            if (nestedField.map) {
                                newRecord[nestedField.outputKey] = nestedField.map(value, item, record)
                            } else {
                                newRecord[nestedField.outputKey] = value
                            }
                        } else if (nestedField instanceof CustomField) {
                            newRecord[nestedField.outputKey] = nestedField.map(item, record)
                        } else if (nestedField instanceof ExpandDictField) {
                            const nestedFieldValues = createNestedFieldValuesListed(item, nestedField, record)
                            Object.assign(newRecord, nestedFieldValues)
                        }
                    }
                    newExpandedRecords.push(newRecord)
                }
            }
            expandedRecords = newExpandedRecords
        }
    }
    return expandedRecords
}

function performApplyViewInPlace(results: any[], viewObj: View, inputData?: any): [any[], string[]] {
    const hidden_fields: string[] = [];
    const targetFields: (Field | CustomField | ExpandDictField | ExpandListField)[] = isNotNullish(inputData)?getFields(viewObj.fields, inputData, hidden_fields):viewObj.fields
    const processedResults: any[] = transformRecordsInPlace(results, targetFields)
    return [processedResults, hidden_fields];
}
function performApplyView(results: any[], viewObj: View, inputData?: any): [any[], string[]] {
    const hidden_fields: string[] = [];
    const targetFields: (Field | CustomField | ExpandDictField | ExpandListField)[] = isNotNullish(inputData)?getFields(viewObj.fields, inputData, hidden_fields):viewObj.fields

    const processedResults: any[] = transformRecords(results, targetFields)

    return [processedResults, hidden_fields];
}


function findView(views: View[], view: string): View | undefined {
    return views.find(v => v.id === view);
}

function _applyViewForUi(results: any[], view: string, views: View[], inputData: any): [any[], string[]] {

    const foundView = view && views.find(v => v.id === view);
    if (foundView) {
        return performApplyViewInPlace(results, foundView, inputData);
    }
    return [results, []];
}
async function _applyViewForUiLargeTask(taskId: number, view: string, views: View[], inputData: any, per_page: number, start: number, end: number, containsListField: boolean): Promise<[number, any[], string[]]> {
    const viewObj = view && views.find(v => v.id === view);
    let result: any[] = [];
    const hidden_fields: string[] = [];

    if (viewObj) {
        const targetFields: (Field | CustomField | ExpandDictField | ExpandListField)[] = isNotNullish(inputData) ? getFields(viewObj.fields, inputData, hidden_fields) : viewObj.fields;
        if (containsListField) {
            let items_count = 0
            await TaskResults.streamTask(taskId, (record, index) => {
                const expandedRecords: any[] = transformRecord(targetFields, record);
                items_count+=expandedRecords.length
                
                if (result.length < per_page && index >= start && index < end) {
                    result.push(...expandedRecords);
                }
            });

            // Ensure result is less than per_page
            if (result.length > per_page) {
                result = result.slice(0, per_page);
            }
            return [items_count, result, hidden_fields];
        } else {
            await TaskResults.streamTask(taskId, (record, index) => {
                if (index >= start && index < end) {
                    const expandedRecords: any[] = transformRecord(targetFields, record);
                    result.push(...expandedRecords);
                }
            }, end);
            return [0, result, hidden_fields];
        }
    }

    await TaskResults.streamTask(taskId, (record, index) => {
        if (index >= start && index < end) {
            result.push(record);
        }
    }, end);

    return [0, result, hidden_fields];
}
function applyView(results: any[], view: string, views: View[]): any[] {
    if (isEmpty(view)) {
        return results;
    }
    const foundView = views.find(v => v.id === view);
    if (foundView) {
        return performApplyView(results, foundView)[0];
    }
    return results;
}

export {
    Field,
    CustomField,
    ExpandDictField,
    ExpandListField,
    View,
    performApplyView,
    _applyViewForUiLargeTask,
    findView,
    _applyViewForUi,
    applyView,
    transformRecord,getFields, 
};
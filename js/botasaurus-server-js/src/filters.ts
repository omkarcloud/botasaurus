import { snakeCase, capitalCase as titleCase } from 'change-case';
import { JsonHTTPResponseWithMessage } from './errors';
import { isNotNullish, isNullish } from './null-utils';
import { isEmpty } from './utils';

export abstract class BaseFilter {
  field: string;
  field_keys: string[];
  label: string | null;
  id: string;

  constructor(field: string, options?: { label?: string }) {
    this.field = field;
    this.field_keys = this.field.split(".");
    this.label = options?.label || null;

    const className = snakeCase(this.getClassName());
    this.id = `${field}_${className}`;
  }

  shouldFilter(filterValue: any): boolean {
    return isNotNullish(filterValue);
  }

  mapFilterValue(filterValue: any): any {
    return filterValue;
  }

  // Checks if the field exists in the given record (supports dot notation)
  hasFilterValue(record: Record<string, any>): boolean {

    if (this.field_keys.length == 1) {
      return this.field in record;
    }

    let current = record;

    for (const key of this.field_keys) {
      if (!(key in current)) {
        return false;
      }
      current = current[key];
    }

    return true;
  }

  getFilterValue(record: Record<string, any>): any {
    if (this.field_keys.length == 1) {
      return record[this.field]
    }

    let current = record;

    for (const key of this.field_keys) {
      current = current[key];
    }

    return current;
  }


  abstract filter(filterValue: any, dataValue: any): boolean;

  toJson(): Record<string, any> {
    return {
      id: this.id,
      type: this.getClassName(),
      label: this.label || this.getLabel(),
    };
  }

  abstract getLabel(): string;

  abstract getClassName(): string;
}

abstract class _NumericFilterBase extends BaseFilter {
  override shouldFilter(filterValue: any): boolean {
    return isNotNullish(filterValue) && typeof filterValue === 'number';
  }
}

export class MinNumberInput extends _NumericFilterBase {
  filter(filterValue: number, dataValue: any): boolean {
    if (typeof dataValue === 'number') {
      return dataValue >= filterValue;
    } else {
      return false;
    }
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Min ${titleCasedField}`;
  }

  getClassName(): string {
    return 'MinNumberInput';
  }
}

export class MaxNumberInput extends _NumericFilterBase {
  filter(filterValue: number, dataValue: any): boolean {
    if (typeof dataValue === 'number') {
      return dataValue <= filterValue;
    } else {
      return false;
    }
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Max ${titleCasedField}`;
  }

  getClassName(): string {
    return 'MaxNumberInput';
  }
}

abstract class _Checkbox extends BaseFilter {
  override shouldFilter(filterValue: any): boolean {
    return filterValue === true;
  }
}

export class IsTrueCheckbox extends _Checkbox {
  filter(_: boolean, dataValue: any): boolean {
    return dataValue === true;
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Has ${titleCasedField}`;
  }

  getClassName(): string {
    return 'IsTrueCheckbox';
  }
}

export class IsFalseCheckbox extends _Checkbox {
  filter(_: boolean, dataValue: any): boolean {
    return dataValue === false;
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Does Not Have ${titleCasedField}`;
  }

  getClassName(): string {
    return 'IsFalseCheckbox';
  }
}

export class IsNullCheckbox extends _Checkbox {
  filter(_: boolean, dataValue: any): boolean {
    return isNullish(dataValue);
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Does Not Have ${titleCasedField}`;
  }

  getClassName(): string {
    return 'IsNullCheckbox';
  }
}

export class IsNotNullCheckbox extends _Checkbox {
  filter(_: boolean, dataValue: any): boolean {
    return isNotNullish(dataValue);
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Has ${titleCasedField}`;
  }

  getClassName(): string {
    return 'IsNotNullCheckbox';
  }
}

export class IsTruthyCheckbox extends _Checkbox {
  filter(_: boolean, dataValue: any): boolean {
    return !!dataValue;
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Has ${titleCasedField}`;
  }

  getClassName(): string {
    return 'IsTruthyCheckbox';
  }
}

export class IsFalsyCheckbox extends _Checkbox {
  filter(_: boolean, dataValue: any): boolean {
    return !dataValue;
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Does Not Have ${titleCasedField}`;
  }

  getClassName(): string {
    return 'IsFalsyCheckbox';
  }
}

interface Option {
  value: string;
  label: string;
}

abstract class _DropdownFilterBase extends BaseFilter {
  options: Option[];
  caseInsensitive: boolean;

  constructor(
    field: string,
    options: Option[],
    dropdownOptions?: {
      label?: string;
      caseInsensitive?: boolean;
    }
  ) {
    super(field, { label: dropdownOptions?.label });
    this.options = options || [];
    this.caseInsensitive = dropdownOptions?.caseInsensitive ?? true;
    if (this.options.length) {
      this.validateOptions(this.options);
    }
  }

  validateOptions(options: Option[]): void {
    if (!options.every((option) => 'value' in option && 'label' in option)) {
      throw new Error("Each option must have 'value' and 'label' keys.");
    }
    if (
      !options.every(
        (option) => typeof option.value === 'string' && typeof option.label === 'string'
      )
    ) {
      throw new TypeError("'value' and 'label' must be of type string.");
    }
    if (new Set(options.map((option) => option.value)).size !== options.length) {
      throw new Error("'value' must be unique for each option.");
    }
  }

  override toJson(): Record<string, any> {
    const filterJson = super.toJson();
    filterJson.options = this.options;
    return filterJson;
  }
}

export class SingleSelectDropdown extends _DropdownFilterBase {
  filter(filterValue: string, dataValue: any): boolean {
    if (typeof dataValue === 'string') {
      const comparisonValue = this.caseInsensitive ? dataValue.toLowerCase() : dataValue;
      return comparisonValue === filterValue;
    } else if (Array.isArray(dataValue)) {
      for (const item of dataValue) {
        if (typeof item === 'string') {
          if ((this.caseInsensitive ? item.toLowerCase() : item) === filterValue) {
            return true;
          }
        }
      }
    }
    return false;
  }

  override mapFilterValue(filterValue: string): string {
    return this.caseInsensitive ? filterValue.toLowerCase() : filterValue;
  }

  override shouldFilter(filterValue: any): boolean {
    return typeof filterValue === 'string' && filterValue.trim() !== '';
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `${titleCasedField} Is`;
  }

  getClassName(): string {
    return 'SingleSelectDropdown';
  }
}

export class BoolSelectDropdown extends _DropdownFilterBase {
  invertFilter: boolean;

  constructor(
    field: string,
    boolOptions?: {
      label?: string;
      prioritizeNo?: boolean;
      invertFilter?: boolean;
    }
  ) {
    const options = boolOptions?.prioritizeNo
      ? [
          { value: 'no', label: 'No' },
          { value: 'yes', label: 'Yes' },
        ]
      : [
          { value: 'yes', label: 'Yes' },
          { value: 'no', label: 'No' },
        ];
    super(field, options, { label: boolOptions?.label });
    this.invertFilter = boolOptions?.invertFilter ?? false;
  }

  filter(filterValue: string, dataValue: any): boolean {
    if (this.invertFilter) {
      if (filterValue === 'yes') {
        return !dataValue;
      } else if (filterValue === 'no') {
        return !!dataValue;
      }
    } else {
      if (filterValue === 'yes') {
        return !!dataValue;
      } else if (filterValue === 'no') {
        return !dataValue;
      }
    }
    return false;
  }

  override shouldFilter(filterValue: any): boolean {
    return typeof filterValue === 'string' && filterValue.trim() !== '';
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Has ${titleCasedField}`;
  }

  getClassName(): string {
    return 'BoolSelectDropdown';
  }
}

export class MultiSelectDropdown extends _DropdownFilterBase {
  filter(filterValue: Set<any>, dataValue: any): boolean {
    if (typeof dataValue === 'string') {
      const comparisonValue = this.caseInsensitive ? dataValue.toLowerCase() : dataValue;
      return filterValue.has(comparisonValue);
    } else if (Array.isArray(dataValue)) {
      for (const item of dataValue) {
        if (typeof item === 'string') {
          const comparisonItem = this.caseInsensitive ? item.toLowerCase() : item;
          if (filterValue.has(comparisonItem)) {
            return true;
          }
        }
      }
    }
    return false;
  }

  override mapFilterValue(filterValue: any): Set<string> {
    if (!Array.isArray(filterValue)) {
      throw new JsonHTTPResponseWithMessage('filterValue must be an array');
    }

    if (filterValue.length > 0 && !filterValue.every((val: any) => typeof val === 'string')) {
      throw new JsonHTTPResponseWithMessage('filterValue must only contain strings');
    }

    return new Set(
      this.caseInsensitive ? filterValue.map((val: string) => val.toLowerCase()) : filterValue
    );
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `${titleCasedField} Is One Of`;
  }

  getClassName(): string {
    return 'MultiSelectDropdown';
  }
}

export class SearchTextInput extends BaseFilter {
  filter(filterValue: string, dataValue: any): boolean {
    if (typeof dataValue === 'string') {
      return dataValue.toLowerCase().includes(filterValue);
    }
    return false;
  }

  override shouldFilter(filterValue: any): boolean {
    return typeof filterValue === 'string' && filterValue.trim() !== '';
  }

  override mapFilterValue(filterValue: string): string {
    return filterValue.trim().toLowerCase();
  }

  getLabel(): string {
    const titleCasedField = titleCase(this.field);
    return `Search ${titleCasedField}`;
  }

  getClassName(): string {
    return 'SearchTextInput';
  }
}
export function applyFiltersInPlace(
  dataRecords: any[],
  filtersData: Record<string, any>,
  availableFilters: BaseFilter[]
): Record<string, any>[] {
  if (isEmpty(filtersData)) {
    return dataRecords;
  }
  

  const applicableFilters = availableFilters.filter((filterObj) =>
    filterObj.shouldFilter(filtersData[filterObj.id])
  );

  for (const filterObj of applicableFilters) {
    const originalFilterValue = filtersData[filterObj.id];
    const transformedFilterValue = filterObj.mapFilterValue(originalFilterValue);
    filtersData[filterObj.id] = transformedFilterValue;
  }

  const filteredRecords: Record<string, any>[] = [];
  for (let i = 0; i < dataRecords.length; i++) {
    const record = dataRecords[i];
    let passesAllFilters = true;
    for (const filterObj of applicableFilters) {
      if (!(filterObj.hasFilterValue(record))) {
        const rep = JSON.stringify(record, null, 4);
        throw new JsonHTTPResponseWithMessage(
          `Filter field ${filterObj.field} not found in data record: ${
            rep.length >= 1003 ? rep.slice(0, 1000) + '...' : rep
          }.`
        );
      }
      if (!filterObj.filter(filtersData[filterObj.id], filterObj.getFilterValue(record))) {
        passesAllFilters = false;
        break;
      }
    }

    if (passesAllFilters) {
      filteredRecords.push(record);
    }

    // Set the item to null to save space
    dataRecords[i] = null;
  }

  return filteredRecords;
}
import { transliterate } from 'transliteration';
import { isObject } from './utils'

export function unicodeToAscii(text: string | null): string {
  if (text === null) { 
    return null as any;
  }

  return transliterate(text)
}


function applyTransformer(data: any, transformer: (text: string) => string | null): any {
    /**
     * Apply a transformer function to all strings in a nested data structure.
     *
     * @param data - The data structure (object, array, nested objects) to transform.
     * @param transformer - A function that takes a string and returns a transformed string.
     * @return The transformed data structure.
     */
    
    if (isObject(data)) {
        // If the item is an object, apply the transformer to each value.
        return Object.fromEntries(Object.entries(data).map(([key, value]) => [key, applyTransformer(value, transformer)]));
    } else if (Array.isArray(data)) {
        // If the item is an array, apply the transformer to each element.
        return data.map(element => applyTransformer(element, transformer));
    } else if (typeof data === 'string') {
        // If the item is a string, apply the transformer directly.
        return transformer(data);
    } else {
        // If the item is not an object, array, or string, return it as is.
        return data;
    }
}
export function convertUnicodeDictToAsciiDict(data: any):any {
    /**
     * Convert unicode data to ASCII, replacing special characters.
     */
    return applyTransformer(data, unicodeToAscii);
}
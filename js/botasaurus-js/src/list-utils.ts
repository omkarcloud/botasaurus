function iterFlatten(array: (any[] | any)[], depth: number = -1): any[] {
    const result: any[] = [];
    for (const item of array) {
        if (Array.isArray(item) && depth !== 0) {
            result.push(...iterFlatten(item, depth - 1));
        } else {
            result.push(item);
        }
    }
    return result;
}

function flattenDepth(array: (any[] | any)[], depth: number = 1): any[] {
    return iterFlatten(array, depth);
}

function flatten(array: (any[] | any)[]): any[] {
    return flattenDepth(array, 1);
}

function flattenDeep(array: (any[] | any)[]): any[] {
    return flattenDepth(array, -1);
}

export { flatten, flattenDeep };


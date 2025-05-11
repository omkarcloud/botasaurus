function isNotEmptyString(x: any) {
    return typeof x === 'string' && x.trim().length > 0;
}

export { isNotEmptyString }  
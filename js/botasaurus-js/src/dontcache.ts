export class DontCache {
    data: any;

    constructor(result: any) {
        this.data = result;
    }
}

export function isDontCache(obj: any){
    return obj instanceof DontCache;
}


import {
    _readJsonFiles,
    _has,
    _remove,
    _deleteItems,
    _hash,
} from "botasaurus/cache";
import { stringify } from "csv-stringify/sync";

export class HTTPNDJSONWriteStream {
    raw: any;

    constructor(raw: any) {
        this.raw = raw;
    }

    push(data: any) {
        return this.performWrite(JSON.stringify(data) + "\n");
    }

    performWrite(content: any) {
        return this.raw.write(content);
    }

    end() {
        this.preEnd();
        return this.raw.end();
    }

    preEnd() {
        // Add any necessary pre-end logic here
    }
    preStart() {
        // Add any necessary pre-end logic here
    }
}

export class HTTPJSONWriteStream extends HTTPNDJSONWriteStream {
    private sep: string;

    constructor(raw: any) {
        super(raw);
        this.sep = "";
    }
    override preStart() {
        this.performWrite("[");
    }

    override push(data: any) {
        const content = this.sep + JSON.stringify(data);
        if (!this.sep) {
            this.sep = ",";
        }
        return this.performWrite(content);
    }

    override preEnd() {
        this.performWrite("]");
    }
}

export class HTTPCSVWriteStream extends HTTPNDJSONWriteStream {
    // @ts-ignore
    override preStart(headers: string[]) {
        const headerLine = stringify([headers]);
        this.performWrite(headerLine);
    }

    override push(data: string[]): Promise<void> {
        const content = stringify([data]);
        return this.performWrite(content);
    }
}

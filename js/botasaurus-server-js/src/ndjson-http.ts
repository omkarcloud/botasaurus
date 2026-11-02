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

    // Waits for a slow reader: ignoring it kept the whole output in memory while
    // the rows were read from disk faster than the socket took them
    performWrite(content: any): Promise<void> | void {
        // A closed response never drains: waiting for it hung the export forever
        if (this.raw.destroyed) {
            throw new Error("The client disconnected");
        }
        if (this.raw.write(content)) return;
        return new Promise<void>((resolve) => {
            const done = () => {
                this.raw.off("drain", done);
                this.raw.off("close", done);
                resolve();
            };
            this.raw.on("drain", done);
            this.raw.on("close", done);
        });
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

    override push(data: any[]) {
        const content = stringify([data]);
        return this.performWrite(content);
    }
}

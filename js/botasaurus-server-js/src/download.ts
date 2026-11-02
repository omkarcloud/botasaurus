import {writeExcelStreamed, writeJsonStreamed, writeJson, writeCsvStreamed, writeCsv, writeExcel, writeNdjson } from './writer'; // Fixed import statement
import writterHttp from './writer-http'; // Fixed import statement
import { getPathToDownloadsDirectory } from './paths'
import { TaskResults } from './task-results'

// Handles the download result based on format
export function downloadResults(results: Array<Record<string, any>>, fmt: string, filename: string, taskId: any, is_large: boolean, streamFn: any, downloadFolder?: string | null, inputPath: string = TaskResults.generateTaskFilePath(taskId)) {
    const filePath = getPathToDownloadsDirectory(filename, downloadFolder);

    if (fmt === "json") {
        if (is_large) {
            return writeJsonStreamed(inputPath, filePath, streamFn);
        } else {
            return writeJson(results, filePath);
        }
    }

    if (fmt === "csv") {
        if (is_large) {
            return writeCsvStreamed(inputPath, filePath, streamFn);
        } else {
            return writeCsv(results, filePath);
        }
    } else if (fmt === "excel") {
        if (is_large) {
            return writeExcelStreamed(inputPath, filePath, streamFn);
        } else {
            return writeExcel(results, filePath);
        }        
    } else if (fmt === "ndjson") {
        // Files are already stored as NDJSON, so just copy the file
        return writeNdjson(inputPath, filePath);
    }

    throw new Error("Unsupported format");
}

export async function downloadResultsHttp(reply: any, results: Array<Record<string, any>>, fmt: string, filename: string, taskId: any, is_large: boolean, streamFn: any, inputPath: string = TaskResults.generateTaskFilePath(taskId)) {
    // The response is written directly, so Fastify must not try to send one too:
    // for a failure part way through it did, which threw "headers already sent"
    reply.hijack();
    try {
        return await writeResultsHttp(reply, results, fmt, filename, is_large, streamFn, inputPath);
    } catch (error) {
        // The status has already been sent, so all that can tell the client is
        // closing the connection: left open, it waited for the rest forever
        reply.raw.destroy();
        throw error;
    }
}

// Node refuses a header with characters outside Latin-1, and a task's name can be
// in any language: a download by API of "牙医 in 北京" failed
export function attachmentHeader(filename: string) {
    const ascii = filename.replace(/[^\x20-\x7e]|["\\]/g, '_');
    return ascii === filename
        ? `attachment; filename="${filename}"`
        : `attachment; filename="${ascii}"; filename*=UTF-8''${encodeURIComponent(filename)}`;
}

async function writeResultsHttp(reply: any, results: Array<Record<string, any>>, fmt: string, filename: string, is_large: boolean, streamFn: any, inputPath: string) {
    const headers: Record<string, string> = {};

    if (fmt === "json") {
        headers["Content-Type"] = "application/json";
        headers["Content-Disposition"] = attachmentHeader(`${filename}.json`);
        reply.raw.writeHead(200, headers);
        if (is_large) {
            return writterHttp.writeJsonStreamed(inputPath, reply.raw, streamFn);
        } else {
            return writterHttp.writeJson(results, reply.raw);
        }

    } else if (fmt === "csv") {
        headers["Content-Type"] = "text/csv";
        headers["Content-Disposition"] = attachmentHeader(`${filename}.csv`);
        reply.raw.writeHead(200, headers);
        if (is_large) {
            return writterHttp.writeCsvStreamed(inputPath, reply.raw, streamFn);
        } else {
            return writterHttp.writeCsv(results, reply.raw);
        }
    } else if (fmt === "excel") {
        headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
        headers["Content-Disposition"] = attachmentHeader(`${filename}.xlsx`);
        reply.raw.writeHead(200, headers);
        if (is_large) {
            return writterHttp.writeExcelStreamed(inputPath, reply.raw, streamFn);
        } else {
            return writterHttp.writeExcel(results, reply.raw);
        }     
    } else if (fmt === "ndjson") {
        headers["Content-Type"] = "application/x-ndjson";
        headers["Content-Disposition"] = attachmentHeader(`${filename}.ndjson`);
        reply.raw.writeHead(200, headers);
        // Files are already stored as NDJSON, so stream directly
        return writterHttp.writeNdjson(inputPath, reply.raw);
    } else {
        throw new Error("Unsupported format");
    }
}
import {writeExcelStreamed, writeJsonStreamed, writeJson, writeCsvStreamed, writeCsv, writeExcel } from './writer'; // Fixed import statement
import writterHttp from './writer-http'; // Fixed import statement
import { getPathToDownloadsDirectory } from './paths'
import { TaskResults } from './task-results'

// Handles the download result based on format
export function downloadResults(results: Array<Record<string, any>>, fmt: string, filename: string, taskId: any, is_large: boolean, streamFn: any, downloadFolder?: string | null) {
    const filePath = getPathToDownloadsDirectory(filename, downloadFolder);

    if (fmt === "json") {
        if (is_large) {
            return writeJsonStreamed(TaskResults.generateTaskFilePath(taskId), filePath, streamFn);
        } else {
            return writeJson(results, filePath);
        }
    }

    if (fmt === "csv") {
        if (is_large) {
            return writeCsvStreamed(TaskResults.generateTaskFilePath(taskId), filePath, streamFn);
        } else {
            return writeCsv(results, filePath);
        }
    } else if (fmt === "excel") {
        if (is_large) {
            return writeExcelStreamed(TaskResults.generateTaskFilePath(taskId), filePath, streamFn);
        } else {
            return writeExcel(results, filePath);
        }        
    }

    throw new Error("Unsupported format");
}

export async function downloadResultsHttp(reply: any, results: Array<Record<string, any>>, fmt: string, filename: string, taskId: any, is_large: boolean, streamFn: any) {
    const headers: Record<string, string> = {};

    if (fmt === "json") {
        headers["Content-Type"] = "application/json";
        headers["Content-Disposition"] = `attachment; filename="${filename}.json"`;
        reply.raw.writeHead(200, headers);
        if (is_large) {
            return writterHttp.writeJsonStreamed(TaskResults.generateTaskFilePath(taskId), reply.raw, streamFn);
        } else {
            return writterHttp.writeJson(results, reply.raw);
        }

    } else if (fmt === "csv") {
        headers["Content-Type"] = "text/csv";
        headers["Content-Disposition"] = `attachment; filename="${filename}.csv"`;
        reply.raw.writeHead(200, headers);
        if (is_large) {
            return writterHttp.writeCsvStreamed(TaskResults.generateTaskFilePath(taskId), reply.raw, streamFn);
        } else {
            return writterHttp.writeCsv(results, reply.raw);
        }
    } else if (fmt === "excel") {
        headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
        headers["Content-Disposition"] = `attachment; filename="${filename}.xlsx"`;
        reply.raw.writeHead(200, headers);
        if (is_large) {
            return writterHttp.writeExcelStreamed(TaskResults.generateTaskFilePath(taskId), reply.raw, streamFn);
        } else {
            return writterHttp.writeExcel(results, reply.raw);
        }     
    } else {
        throw new Error("Unsupported format");
    }
}
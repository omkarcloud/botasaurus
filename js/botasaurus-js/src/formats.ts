export const Formats = {
    JSON: 'JSON',
    EXCEL: 'EXCEL',
    CSV: 'CSV',
    JSON_AND_EXCEL: ['JSON', 'EXCEL'] as const,
    JSON_AND_CSV: ['JSON', 'CSV'] as const
} as const;

export type FormatType = 'JSON' | 'EXCEL' | 'CSV';
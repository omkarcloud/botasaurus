import { isNotNullish, isNullish } from "./null-utils";

interface PaginationInfo<T> {
    count: number;
    total_pages: number;
    next: { page: number; per_page: number } | null;
    previous: { page: number; per_page: number } | null;
    results: T[];
    hidden_fields?: Record<string, unknown>;
}

function applyPagination<T>(
    data: T[],
    page: number,
    per_page: any,
    hidden_fields: Record<string, unknown> | null,
    count: number,
    sliceResults: boolean = true
): PaginationInfo<T> {
    // Handle the case where per_page is null - return all items
    if (isNullish(per_page)) {
        per_page = count === 0 ? 1 : count;
        page = 1;
    }

    // Calculate the total number of pages
    const total_pages = Math.max(Math.ceil(count / per_page), 1); // Ensure at least 1 page
    page = Math.max(Math.min(page, total_pages), 1); // Ensure page is within valid range

    // Calculate indices for slicing the data array to get the current page of results
    const start = calculatePageStart(page, per_page);
    const end = Math.min(calculatePageEnd(start, per_page), count);

    // Determine the page numbers for the next and previous pages
    const nextPage = end < count ? page + 1 : null;
    const previousPage = start > 0 ? page - 1 : null;

    // Prepare the paginated results
    const results = sliceResults ? data.slice(start, end) : data;

    // Construct the next and previous page information
    const nextInfo = isNotNullish(nextPage)
        ? { page: nextPage, per_page }
        : null;
    const previousInfo = isNotNullish(previousPage)
        ? { page: previousPage, per_page }
        : null;

    // Construct the response object
    const paginationInfo: any = {
        count,
        total_pages,
        next: nextInfo,
        previous: previousInfo,
        results,
    };

    if (isNotNullish(hidden_fields)) {
        paginationInfo.hidden_fields = hidden_fields;
    }

    return paginationInfo;
}

export { applyPagination };

export function calculatePageEnd(start: number, per_page: any): number {
    return start + per_page;
}

export function calculatePageStart(page: number, per_page: any) {
    return (page - 1) * per_page;
}

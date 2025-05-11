
export const TaskStatus = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
  ABORTED: 'aborted',
}

export function hasViews(views: any) {
  return views.length
}

export function hasFilters(filters: any) {
  return filters.length
}

export function hasSorts(sorts: any) {
  return sorts.length > 1
}

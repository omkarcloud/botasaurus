import { TaskExecutor } from './task-executor';

// Module-level default executor (lazy-initialized)
let _defaultExecutor: TaskExecutor | null = null;

/**
 * Get the executor instance.
 * In K8s mode, returns the globally configured executor (Master or Worker).
 * In standalone mode, returns a lazy-initialized default TaskExecutor.
 */
export function getExecutor(): TaskExecutor {
    // K8s mode: use globally configured executor
    // @ts-ignore
    if (global.executor) {
        // @ts-ignore
        return global.executor;
    }

    // Standalone mode: lazy-initialize default executor
    if (_defaultExecutor === null) {
        _defaultExecutor = new TaskExecutor();
    }

    return _defaultExecutor;
}

export { TaskExecutor };

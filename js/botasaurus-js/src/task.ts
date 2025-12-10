import { isErrorsInstance, NotFoundException,formatExc, printExc,sleep, } from './utils'
import { prompt } from './beep-utils'
import { isDontCache } from './dontcache'
import pLimit from 'p-limit'

import { printRunning, writeOutput, IS_PRODUCTION, saveErrorLogs } from './decorators-common'
import { increment } from './increment'
import { isNotEmptyString } from './string-utils'
import {
    CacheMissException,
    writeJson,
    createCacheDirectoryIfNotExists,
    _getCachePath,
    _has, _get,
    _remove
} from "./cache"
import { flatten } from './list-utils'
import { FormatType } from './formats'

export type TaskRunOptions<I=any> = {
    data: I
    metadata: any
    isAborted: () => boolean
    pushData: (data: Record<string, any> | Record<string, any>[]) => Promise<void> 
}

type TaskOptions<I> = {
    name?: string
    parallel?: number | ((data: any) => number)
    metadata?: any
    cache?: true  | false | "REFRESH"
    // beep?: boolean;
    closeOnCrash?: boolean
    output?: string | ((data: any, result: any) => void) | null
    outputFormats?: FormatType[]
    raiseException?: boolean
    mustRaiseExceptions?: any[]
    run: (options: TaskRunOptions<I>) => any
    maxRetry?: number
    retryWait?: number
    createErrorLogs?: boolean
}



function createTask<I>(options: TaskOptions<I>, is_async_queue: boolean) {
    const performTask = async function (data: any = null, overrideOptions: Omit<TaskOptions<any>, 'run'> = {}) {
        const combined = { ...options, ...overrideOptions }
        printRunning()

        let {
            parallel = 1, name = null, run, metadata = null, cache = null,
            // beep = false,
            closeOnCrash = false, output = 'default', outputFormats = null, raiseException = false, mustRaiseExceptions = null, maxRetry = null, retryWait = null, createErrorLogs = true,
        } = combined

        performTask.__name__ = isNotEmptyString(name) ? name!.trim() : performTask.__name__
        // @ts-ignore
        const returnDontCacheAsIs = combined.returnDontCacheAsIs
        // @ts-ignore
        const isAborted = combined.isAborted ?? (() => false)
        // @ts-ignore 
        const pushData = combined.pushData ?? (() => {})
        const fn_name = performTask.__name__

        if (cache) {
            createCacheDirectoryIfNotExists(fn_name)
        }

        async function runTask(
            data: any,
            retryAttempt: number
        ): Promise<any> {
            let path: string | undefined

            if (cache === true) {
                path = _getCachePath(fn_name, data)
                if (_has(path)) {
                    try {
                        return _get(path)
                    } catch (error) {
                        if (!(error instanceof CacheMissException)) throw error
                    }
                }
            } else if (cache === 'REFRESH') {
                path = _getCachePath(fn_name, data)
            }

            let result: any
            try {
                result = await run({ data, metadata, isAborted, pushData })
                if (result === undefined) {
                    result = null
                }

                if (cache === true || cache === 'REFRESH') {
                    if (isDontCache(result)) {
                        _remove(path!)
                    } else {
                        writeJson(result, path!)
                    }
                }

                if (isDontCache(result)) {
                    if (!returnDontCacheAsIs) {
                        result = result.data
                    }
                }
                return result
            } catch (error) {
                if (error instanceof NotFoundException && !error.raisedOnce) {
                    if (error.raiseMaximum1Time) {
                        error.raisedOnce = true
                    }
                    throw error
                } else if (mustRaiseExceptions &&
                    isErrorsInstance(mustRaiseExceptions, error)[0]) {
                    if (createErrorLogs) {
                        saveErrorLogs(formatExc(error), data)
                    }
                    throw error
                }

                if (maxRetry !== undefined && maxRetry !== null && maxRetry > retryAttempt) {
                    printExc(error)
                    if (retryWait) {
                        console.log(`Waiting for ${retryWait} seconds`)
                        await sleep(retryWait)
                    }
                    return runTask(
                        data,
                        retryAttempt + 1
                    )
                }

                if (!raiseException) {
                    printExc(error)
                }

                console.error('Task failed for input:', data)
                if (createErrorLogs) {
                    saveErrorLogs(formatExc(error), data)
                }

                if (!IS_PRODUCTION) {
                    if (raiseException) {
                        printExc(error)
                    }

                    if (!closeOnCrash) {
                        await prompt(
                            "We've paused the task to help you debug. Press 'Enter' to close."
                        )
                    }
                }

                if (raiseException) {
                    throw error
                }

                return result
            }
        }


        const numberOfWorkers = typeof parallel === 'function' ? parallel(data) : parallel

        if (numberOfWorkers !== undefined && numberOfWorkers !== null && typeof numberOfWorkers !== 'number') {
            throw new Error('parallel Option must be a number')
        }

        let usedData = data === undefined ? null : data

        usedData = typeof usedData === 'function' ? usedData() : usedData
        const originalData = usedData

        let returnFirst = false
        if (!Array.isArray(usedData)) {
            returnFirst = true
            usedData = [usedData]
        }
        // @ts-ignore
        const hasNumberOfWorkers = numberOfWorkers !== undefined && numberOfWorkers !== null && numberOfWorkers !== false
        const n = (!hasNumberOfWorkers || numberOfWorkers <= 1) ? 1 : Math.min(usedData.length, numberOfWorkers)
        let result: any[] = []

        if (n <= 1) {
            for (let index = 0; index < usedData.length; index++) {
                const dataItem = usedData[index]
                const currentResult = await runTask(dataItem, 0)
                result.push(currentResult)
            }
        } else {
            if (typeof parallel === 'function') {
                console.log(`Running ${n} Requests in Parallel`)
            }
            const limit = pLimit(n)
            const promises = usedData.map((dataItem: any) => limit(async () => {
                const currentResult = await runTask(dataItem, 0)
                return currentResult
            })
            )

            result = await Promise.all(promises)
        }

        if (returnFirst) {
            let final = result[0]
            if (!is_async_queue) {
                writeOutput(output, outputFormats, originalData, final, fn_name)
                return final
            }
            return { originalData, result: final }
        } else {
            let final = result

            if (!is_async_queue) {
                writeOutput(output, outputFormats, originalData, final, fn_name)
                return final
            }
            return { originalData, result: final }
        }
    }

    performTask._scraperType = "task"
    const current = increment()
    performTask.__name__ = isNotEmptyString(options.name) ? options.name!.trim() : current
    return performTask
}

export function task<I=any>(options: TaskOptions<I>) {
    return createTask<I>(options, false)
}

export function getItemRepr(item: any): string | number {
    if (Array.isArray(item)) {
        return JSON.stringify(item)
    } else if (item instanceof Set) {
        return JSON.stringify(Array.from(item))
    } else if (typeof item === 'number' || typeof item === 'string') {
        return item
    } else if (item && typeof item === 'object' && !Array.isArray(item)) {
        return JSON.stringify(item)
    } else {
        return JSON.stringify(item)
    }
}

export function removeItemFromSeenItemsSet(items: any, seenItems: Set<any>) {
    if (!Array.isArray(items)) {
        items = [items]
    }
    for (const item of items) {
        const itemRepr = getItemRepr(item)
        seenItems.delete(itemRepr)
    }
}
export function taskQueue<I=any>(options: TaskOptions<I>& { sequential?: boolean }) {
    // Extract parallel from options - it controls queue-level concurrency, not passed to createTask
    const { parallel: parallelOption, ...taskOptions } = options
    const run = createTask<I>(taskOptions as TaskOptions<I>, true)
    const performTask = () => {
        let seenItems = new Set()
        let lastPromise: Promise<any> = Promise.resolve()
        const state = { promises: [] as any[], draining: false }
        let sequential = 'sequential' in options ? options.sequential : false
        
        // Create concurrency limiter for parallel mode
        const maxLimit = determineMaxLimit(parallelOption)

        let limit: pLimit.Limit
        if (maxLimit <=1) {
            sequential = true
        } else {
            limit = pLimit(maxLimit)
        }



        function getUnique(items: any[]) {
            let singleItem = false
            if (!Array.isArray(items)) {
                items = [items]
                singleItem = true
            }

            let newItems = []

            for (let item of items) {
                const itemRepr = getItemRepr(item)

                if (!seenItems.has(itemRepr)) {
                    newItems.push(item)
                    seenItems.add(itemRepr)
                }
            }

            return singleItem && newItems.length ? newItems[0] : newItems
        }

        const cleanup = () => {
            state.promises = []
            state.draining = false
            seenItems.clear()
            lastPromise = Promise.resolve()
        }

        return {
            put: function (data: any, overrideOptions: Omit<TaskOptions<any>, 'run'> = {}) {
                const uniqueData = getUnique(data)
                let promise: Promise<any> 
                if (sequential) {
                    // runs sequentially
                    promise = lastPromise.then(() => run(uniqueData, overrideOptions))
                    lastPromise = promise

                    state.promises.push(promise)
                    return promise.then(x=>x.result)
                } else {
                    if (Array.isArray(uniqueData)) {
                        promise = Promise.all(uniqueData.map(x=> limit(() => run(x, overrideOptions))))
                        state.promises.push(promise.then(results=>({originalData: uniqueData, result: results.map((x: any)=>x.result)})))
                        return promise.then(results=>results.map((x: any)=>x.result))
                    } else {
                        promise = limit(() => run(uniqueData, overrideOptions))
                        
                        state.promises.push(promise)
                        return promise.then(x=>x.result)
                    }
                }
            },
            get: async function (n: number | null = null) {
                return drainQueue(state, cleanup, (items) => removeItemFromSeenItemsSet(items,seenItems), options, run.__name__, n)
            },
            isCompleted: function () {
                return state.promises.length === 0 && !state.draining
            }
        }
    }
    performTask._isQueue = true
    return performTask
}

export function determineMaxLimit(parallelOption: number | ((data: any) => number) | undefined) {
    const parallelCount = typeof parallelOption === 'function' ? parallelOption(null) : (parallelOption ?? 1)

    const maxLimit = Math.max(1, parallelCount)
    return maxLimit
}

export async function drainQueue(
    state: { promises: Promise<any>[], draining: boolean },
    cleanup: () => void,
    removeItemFromSeenItemsSet: (item: any) => void,
    options: { output?: string | ((data: any, result: any) => void) | null, outputFormats?: FormatType[] | null },
    fnName: string,
    n: number | null = null
) {
    if (n !== null && n < 1) {
        throw new Error('n must be >= 1')
    }
    
    if (!state.promises.length){
        return []
    }

    
    const result_list: any[] = []
    const orignal_data: any[] = []
    // Only partial drain if n is specified AND less than current promises count
    const isPartialDrain = n !== null && n < state.promises.length
    
    state.draining = true
    try {
        if (isPartialDrain) {
            // Partial drain - take first n promises
            let remaining = n!
            while (state.promises.length > 0 && remaining > 0) {
                const takeCount = Math.min(remaining, state.promises.length)
                const currentPromises = state.promises.slice(0, takeCount)
                state.promises = state.promises.slice(takeCount)
                remaining -= takeCount
                
                const results = await Promise.all(currentPromises)
                for (let index = 0; index < results.length; index++) {
                    const { originalData, result } = results[index]
                    if (Array.isArray(originalData)) {
                        orignal_data.push(...originalData)
                        result_list.push(...result)
                    } else {
                        orignal_data.push(originalData)
                        result_list.push(result)
                    }
                    removeItemFromSeenItemsSet(originalData)
                }
            }
        } else {
            // Full drain - keep processing until no new promises are added
            while (state.promises.length > 0) {
                const currentPromises = state.promises
                state.promises = []  // Reset before awaiting so new promises can be added
                const results = await Promise.all(currentPromises)
                for (let index = 0; index < results.length; index++) {
                    const { originalData, result } = results[index]
                    if (Array.isArray(originalData)) {
                        orignal_data.push(...originalData)
                        result_list.push(...result)
                    } else {
                        orignal_data.push(originalData)
                        result_list.push(result)
                    }
                }
            }
            cleanup()
        }

        const { output = 'default', outputFormats = null } = options
        const final = flatten(result_list)
        writeOutput(output, outputFormats, orignal_data, final, fnName)
        
        return final
    } catch (error) {
        
        if (!isPartialDrain) {
            cleanup()
        }
        throw error
    } finally {
        state.draining = false
    }
}

import { createDirectoryIfNotExists } from 'botasaurus/decorators-utils'
import { pathTaskResults, pathTaskResultsTasks,pathTaskResultsCacheDirect, pathTaskResultsCache } from './utils'

createDirectoryIfNotExists(pathTaskResults)
createDirectoryIfNotExists(pathTaskResultsTasks)
createDirectoryIfNotExists(pathTaskResultsCache)
createDirectoryIfNotExists(pathTaskResultsCacheDirect)

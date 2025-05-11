const isInKubernetes: boolean = 'KUBERNETES_SERVICE_HOST' in process.env;

const isWorker: boolean = isInKubernetes && process.env.NODE_TYPE === 'WORKER';
const isMaster: boolean = isInKubernetes && process.env.NODE_TYPE === 'MASTER';
const isDev: boolean =
  process.env.NODE_ENV === 'development' || process.env.DEBUG_PROD === 'true';

export { isInKubernetes, isWorker, isMaster, isDev };

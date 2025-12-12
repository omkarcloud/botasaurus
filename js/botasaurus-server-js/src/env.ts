const isInKubernetes: boolean = 'KUBERNETES_SERVICE_HOST' in process.env;

function _isMaster() {
  const args = process.argv;
  return args.includes('--master')
}

function _isWorker() {
  const args = process.argv;
  return args.includes('--worker')
}

const isWorker: boolean = _isWorker();
const isMaster: boolean = _isMaster();
const isDev: boolean =
  process.env.NODE_ENV === 'development' || process.env.DEBUG_PROD === 'true';

export { isInKubernetes, isWorker, isMaster, isDev };
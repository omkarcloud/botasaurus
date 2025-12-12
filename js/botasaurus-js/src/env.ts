import fs from 'fs';

const isInKubernetes: boolean = 'KUBERNETES_SERVICE_HOST' in process.env;

function _isDocker(): boolean {
    const isMac: boolean = process.platform === 'darwin';
    // Early exit
    if (isMac) {
        return false;
    }
    const isWindows: boolean = process.platform === 'win32';
    
    // Early exit
    if (isWindows) {
        return false;
    }
    
    // Expensive Checks
    return fs.existsSync('/.dockerenv') || 
           (fs.existsSync('/proc/self/cgroup') && 
            fs.readFileSync('/proc/self/cgroup', 'utf8').includes('docker')) ||
           isInKubernetes;
}

const isDocker: boolean = _isDocker();

const isVm: boolean = process.env.VM === 'true';
const isGitpodEnvironment: boolean = 'GITPOD_WORKSPACE_ID' in process.env;

const isVmish: boolean = isDocker || isVm || isGitpodEnvironment;

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

const IS_VM_OR_DOCKER = isDocker || isVm;
const IS_PRODUCTION = process.env.ENV === "production";

type OsType = 'windows' | 'mac' | 'linux';
let cachedOs: OsType | null = null;
function detectOs(): OsType {
    const isWindows = process.platform === 'win32';
    // Early exit
    if (isWindows) {
        return 'windows';
    }

    const isMac = process.platform === 'darwin';
    // Early exit
    if (isMac) {
        return 'mac';
    }

    // Expensive Checks
    return 'linux';
}

function getOs(): OsType {
    if (!cachedOs) {
        cachedOs = detectOs();
    }
    return cachedOs;
}


export {
    IS_VM_OR_DOCKER, 
    IS_PRODUCTION, 
    isInKubernetes,
    isDocker,
    isVm,
    isGitpodEnvironment,
    isVmish,
    isWorker,
    isMaster,
    getOs
};
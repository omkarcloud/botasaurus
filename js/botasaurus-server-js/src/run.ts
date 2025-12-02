import { getExecutor } from './executor';
let hasRun = false;

export default function run() {
    if (hasRun) return;
    hasRun = true;
    getExecutor().load();
    return getExecutor().start();
}
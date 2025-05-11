import { executor } from './executor';
let hasRun = false;

export default function run() {
    if (hasRun) return;
    hasRun = true;
    executor.load();
    return executor.start();
}
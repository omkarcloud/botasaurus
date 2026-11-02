import * as ChromeLauncher from 'chrome-launcher'
import { killLaunchedChromes } from './page'
async function closeAllChromes() {
  try {
    killLaunchedChromes()
    return await ChromeLauncher.killAll()
  } catch (error) {
    console.error(error)
    return 
  }
}

export async function onClose() {
  return closeAllChromes()
}
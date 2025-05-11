import * as ChromeLauncher from 'chrome-launcher'
async function closeAllChromes() {
  try {
    return await ChromeLauncher.killAll()
  } catch (error) {
    console.error(error)
    return 
  }
}

export async function onClose() {
  return closeAllChromes()
}
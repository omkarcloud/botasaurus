const assert = require('assert')
const {
    task, taskQueue
} = require('../src/task') // Assuming the previous code is saved as path-utils.js
const { sleep } = require('../src/utils')

describe('task', () => {
    it('should work', async () => {


        const a = taskQueue({
            // key:"a",
            raiseException:true, 
            closeOnCrash:true, 
            outputFormats:['CSV'],
            metadata:"aa",
            run: async ({data}) =>{
                console.log(data)
                const newLocal = await sleep(data)
                // throw new Error()
                return data
            }
        })
        const n = a()
        n.put([1])
        n.put([2])
        // n.put([3])
        // n.put([4])
        // n.put([5])
        // n.put([4])
        const r = await n.get()
        console.log({r})
        // a(null)

        // const b = task({
        //     run: ({ data }) => {
        //         console.log(data)

        //     }
        // })
        // b()
        // b()
    })
})

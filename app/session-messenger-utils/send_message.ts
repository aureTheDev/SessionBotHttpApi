import { Session, ready } from '@session.js/client'
import { SignalService } from '@session.js/types/signal-bindings';
await ready

const mnemonic = process.argv[2]
const name = process.argv[3]
const recipient = process.argv[4]
const text = process.argv[5]


const session = new Session()
session.setMnemonic(mnemonic, name)
const response = await session.sendMessage({
    to: recipient,
    text: text
})
console.log(response)
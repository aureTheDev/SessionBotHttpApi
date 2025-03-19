import { Session, ready } from '@session.js/client'
await ready

const mnemonic = 'afield foamy abrasive goes idols knife bowling saga wildly emotion queen casket idols'
const recipient = process.argv[2]

const session = new Session()
session.setMnemonic(mnemonic, 'test bot')
const response = await session.sendMessage({
    to: recipient,
    text: 'Hello world'
})

console.log('Sent message with id', response.messageHash)
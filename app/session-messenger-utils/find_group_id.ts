import { Session, Poller, ready } from '@session.js/client'
import { SnodeNamespaces, type Message } from '@session.js/types'
await ready

const mnemonic = 'love love love love love love love love love love love love love'

const session = new Session()
session.setMnemonic(mnemonic, 'Display name')

const poller = new Poller() // polls every 2.5 seconds
session.addPoller(poller)

session.on('message', (msg: Message) => {
    console.log('Received new message!',
        'From:', msg.from,
        'Is from closed group:', msg.type === 'group',
        'Group id:', msg.type === 'group' ? msg.groupId : 'Not group',
        'Text:', msg.text ?? 'No text',
    )

    // If you want to access more properties and experiment with them, use getEnvelope and getContent
    msg.getContent() // => SignalService.Content <- useful message payload
    msg.getCnvelope() // => EnvelopePlus <- message metadata

    // If you want to download attachments, use:
    msg.attachments.forEach(async attachment => console.log(await session.getFile(attachment)))
})
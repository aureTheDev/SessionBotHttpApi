import { Session, Poller, ready } from '@session.js/client'
import { SnodeNamespaces, type Message } from '@session.js/types'
await ready

const mnemonic = process.argv[2]
const name = process.argv[3]

const session = new Session();
session.setMnemonic(mnemonic, name);

const poller = new Poller({interval: null});

session.addPoller(poller);

session.on('message', (msg: Message) => {
  console.log(JSON.stringify(msg, null, 2));
});

await poller.poll();
const net = require('net')
const orig = net.Server.prototype.listen
net.Server.prototype.listen = function (...args) {
  if (args[0] && typeof args[0] === 'object' && args[0].host === '::') args[0] = { ...args[0], host: '0.0.0.0' }
  return orig.apply(this, args)
}

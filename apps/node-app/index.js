const fastify = require('fastify')({ logger: true })
const os = require('os')

fastify.get('/', async (request, reply) => {
  return { 
    message: 'Hello from Node.js (Fastify) - Optimized for Firecracker',
    timestamp: new Date().toISOString(),
    host: os.hostname()
  }
})

fastify.get('/health', async (request, reply) => {
  return { status: 'OK' }
})

const start = async () => {
  try {
    const port = process.env.PORT || 8080
    await fastify.listen({ port: port, host: '0.0.0.0' })
  } catch (err) {
    fastify.log.error(err)
    process.exit(1)
  }
}

start()

module.exports = {
  apps: [{
    name: 'Sierra',
    script: 'main.py',
    interpreter: './sierra-venv/bin/python',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
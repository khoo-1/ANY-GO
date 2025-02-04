module.exports = {
  apps: [
    {
      name: 'any-go-server',
      cwd: './server',
      script: 'index.js',
      watch: false,
      env: {
        NODE_ENV: 'development',
        PORT: 5000,
        HOST: '0.0.0.0',
        MONGODB_URI: 'mongodb://127.0.0.1:27017/any-go'
      },
      error_file: './logs/server-error.log',
      out_file: './logs/server-out.log',
      max_memory_restart: '1G',
      autorestart: true,
      exp_backoff_restart_delay: 1000,
      max_restarts: 3,
      min_uptime: '5000',
      kill_timeout: 3000,
      instances: 1,
      exec_mode: 'fork',
      wait_ready: true,
      listen_timeout: 3000,
      windowsHide: true
    },
    {
      name: 'any-go-client',
      cwd: './client',
      script: 'node_modules/react-scripts/scripts/start.js',
      watch: false,
      env: {
        PORT: 3000,
        BROWSER: 'none',
        NODE_OPTIONS: '--max_old_space_size=4096',
        REACT_APP_API_URL: 'http://localhost:5000',
        CI: 'false',
        HOST: '0.0.0.0'
      },
      error_file: './logs/client-error.log',
      out_file: './logs/client-out.log',
      max_memory_restart: '2G',
      autorestart: true,
      exp_backoff_restart_delay: 1000,
      max_restarts: 3,
      min_uptime: '5000',
      kill_timeout: 3000,
      instances: 1,
      exec_mode: 'fork',
      wait_ready: true,
      listen_timeout: 3000,
      windowsHide: true
    }
  ]
}; 
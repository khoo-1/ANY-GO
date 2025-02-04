module.exports = {
  apps: [
    {
      name: 'any-go-server',
      cwd: './server',
      script: 'index.js',
      watch: ['./'],
      ignore_watch: [
        'node_modules',
        'uploads',
        'logs',
        '*.log'
      ],
      watch_options: {
        followSymlinks: false,
        usePolling: true,
        interval: 1000,
        binaryInterval: 1000
      },
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
      exp_backoff_restart_delay: 100,
      max_restarts: 10,
      min_uptime: '5s',
      windowsHide: true,
      silent: true
    },
    {
      name: 'any-go-client',
      cwd: './client',
      script: 'node_modules/react-scripts/scripts/start.js',
      watch: ['src'],
      ignore_watch: [
        'node_modules',
        'build',
        'logs',
        '*.log'
      ],
      watch_options: {
        followSymlinks: false,
        usePolling: true,
        interval: 1000,
        binaryInterval: 1000
      },
      env: {
        PORT: 3000,
        BROWSER: 'none',
        NODE_OPTIONS: '--max-old-space-size=4096',
        REACT_APP_API_URL: 'http://192.168.110.13:5000',
        CI: 'false'
      },
      error_file: './logs/client-error.log',
      out_file: './logs/client-out.log',
      max_memory_restart: '2G',
      autorestart: true,
      exp_backoff_restart_delay: 100,
      max_restarts: 10,
      min_uptime: '5s',
      windowsHide: true,
      silent: true
    }
  ]
}; 
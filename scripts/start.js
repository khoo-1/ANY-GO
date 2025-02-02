const { spawn } = require('child_process');
const path = require('path');

function startServer() {
  const server = spawn('npm', ['start'], {
    cwd: path.join(__dirname, '../server'),
    stdio: 'inherit'
  });

  server.on('error', (err) => {
    console.error('启动服务器失败:', err);
  });
}

function startClient() {
  const client = spawn('npm', ['start'], {
    cwd: path.join(__dirname, '../client'),
    stdio: 'inherit'
  });

  client.on('error', (err) => {
    console.error('启动客户端失败:', err);
  });
}

startServer();
startClient(); 
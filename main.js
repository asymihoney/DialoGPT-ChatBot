const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let backendProcess;

function createWindow () {
  const win = new BrowserWindow({
    width: 500,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
    }
  });

  win.loadFile('index.html');
}

app.whenReady().then(() => {
  
  const backendPath = path.join(__dirname, 'dist', 'app', 'app.exe');
  backendProcess = spawn(backendPath, {
    cwd: path.join(__dirname, 'dist', 'app'),
    detached: true,
    stdio: 'ignore'
  });

  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (backendProcess) backendProcess.kill();
    app.quit();
  }
});

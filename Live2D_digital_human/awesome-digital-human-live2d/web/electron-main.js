const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let backendProcess;

// 获取后端可执行文件路径
function getBackendPath() {
  // 开发环境
  if (process.env.NODE_ENV === 'development') {
    return null; // 开发环境手动启动后端
  }
  
  // 生产环境 - 后端exe在resources目录
  const backendExe = path.join(
    process.resourcesPath,
    'backend',
    'DigitalHuman-Backend.exe'
  );
  
  if (fs.existsSync(backendExe)) {
    return backendExe;
  }
  
  console.error('Backend executable not found:', backendExe);
  return null;
}

// 启动后端服务
function startBackend() {
  const backendPath = getBackendPath();
  
  if (!backendPath) {
    console.log('Development mode - backend should be started manually');
    return;
  }
  
  console.log('Starting backend:', backendPath);
  
  backendProcess = spawn(backendPath, [], {
    cwd: path.dirname(backendPath),
    stdio: 'inherit'
  });
  
  backendProcess.on('error', (err) => {
    console.error('Failed to start backend:', err);
  });
  
  backendProcess.on('exit', (code) => {
    console.log('Backend process exited with code:', code);
  });
}

// 停止后端服务
function stopBackend() {
  if (backendProcess) {
    console.log('Stopping backend...');
    backendProcess.kill();
    backendProcess = null;
  }
}

// 创建主窗口
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'public', 'favicon.ico')
  });

  // 加载应用
  if (process.env.NODE_ENV === 'development') {
    // 开发环境 - 连接到Next.js开发服务器
    mainWindow.loadURL('http://localhost:3001/sentio');
    mainWindow.webContents.openDevTools(); // 打开开发者工具
  } else {
    // 生产环境 - 加载打包后的静态文件
    mainWindow.loadFile(path.join(__dirname, 'out', 'sentio.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 应用准备就绪
app.whenReady().then(() => {
  // 先启动后端
  startBackend();
  
  // 等待2秒让后端启动完成
  setTimeout(() => {
    createWindow();
  }, 2000);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// 所有窗口关闭
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopBackend();
    app.quit();
  }
});

// 应用退出
app.on('before-quit', () => {
  stopBackend();
});

// 处理未捕获的异常
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});

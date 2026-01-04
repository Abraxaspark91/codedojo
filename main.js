const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const http = require('http');

// 전역 변수
let mainWindow = null;
let lmsServerProcess = null;
let gradioProcess = null;
let currentModel = null;

// 상태 업데이트 헬퍼 함수
function sendStatus(message) {
  console.log(message);
  if (mainWindow && mainWindow.webContents) {
    mainWindow.webContents.send('status-update', message);
  }
}

// 에러 전송 헬퍼 함수
function sendError(message) {
  console.error(message);
  if (mainWindow && mainWindow.webContents) {
    mainWindow.webContents.send('error', message);
  }
}

// 범용 명령 실행 헬퍼
function runCommand(command, args) {
  return new Promise((resolve, reject) => {
    const proc = spawn(command, args);
    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('close', (code) => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(new Error(stderr || `Command failed with code ${code}`));
      }
    });

    proc.on('error', (err) => {
      reject(err);
    });
  });
}

// LMS 모델 리스트 가져오기
async function lmsListModels() {
  try {
    sendStatus('● 모델 리스트 불러오는 중...');
    const output = await runCommand('lms', ['ls']);
    // lms ls의 출력을 파싱 (줄 단위로 모델 이름)
    const models = output.trim().split('\n').filter(line => line.trim());
    sendStatus(`✓ ${models.length}개 모델 발견`);
    return models;
  } catch (error) {
    sendError(`모델 리스트 불러오기 실패: ${error.message}`);
    return [];
  }
}

// LMS 서버 중지
async function lmsServerStop() {
  try {
    sendStatus('● LMS 서버 중지 중...');
    await runCommand('lms', ['server', 'stop']);
    sendStatus('✓ LMS 서버 중지 완료');
    return true;
  } catch (error) {
    // 서버가 이미 중지된 경우 무시
    sendStatus('✓ LMS 서버 중지 (이미 중지됨)');
    return true;
  }
}

// LMS 모델 언로드
async function lmsUnloadAll() {
  try {
    sendStatus('● 메모리 초기화 중 (모델 언로드)...');
    await runCommand('lms', ['unload', '--all']);
    sendStatus('✓ 모델 언로드 완료');
    return true;
  } catch (error) {
    // 모델이 없는 경우 무시
    sendStatus('✓ 모델 언로드 (이미 언로드됨)');
    return true;
  }
}

// LMS 서버 시작
async function lmsServerStart() {
  return new Promise((resolve, reject) => {
    sendStatus('● LMS 서버 시작 중...');

    lmsServerProcess = spawn('lms', ['server', 'start']);

    lmsServerProcess.stdout.on('data', (data) => {
      console.log(`LMS: ${data}`);
    });

    lmsServerProcess.stderr.on('data', (data) => {
      console.error(`LMS Error: ${data}`);
    });

    lmsServerProcess.on('error', (err) => {
      sendError(`LMS 서버 시작 실패: ${err.message}`);
      reject(err);
    });

    // Health check로 서버 ready 확인
    waitForServer('http://127.0.0.1:1234/v1/models', 30000)
      .then(() => {
        sendStatus('✓ LMS 서버 시작 완료');
        resolve(true);
      })
      .catch((err) => {
        sendError(`LMS 서버 응답 없음: ${err.message}`);
        reject(err);
      });
  });
}

// LMS 모델 로드
async function lmsLoadModel(modelPath) {
  return new Promise((resolve, reject) => {
    sendStatus(`● 모델 로딩 중: ${modelPath}...`);

    const proc = spawn('lms', ['load', modelPath]);

    proc.stdout.on('data', (data) => {
      const msg = data.toString().trim();
      if (msg) {
        sendStatus(`  ${msg}`);
      }
    });

    proc.stderr.on('data', (data) => {
      console.error(`LMS Load Error: ${data}`);
    });

    proc.on('close', (code) => {
      if (code === 0) {
        currentModel = modelPath;
        sendStatus('✓ 모델 로딩 완료');
        resolve(true);
      } else {
        sendError('모델 로딩 실패');
        reject(new Error('Model loading failed'));
      }
    });

    proc.on('error', (err) => {
      sendError(`모델 로딩 실패: ${err.message}`);
      reject(err);
    });
  });
}

// Gradio 서버 시작
async function startGradio() {
  return new Promise((resolve, reject) => {
    sendStatus('● Gradio 서버 시작 중...');

    gradioProcess = spawn('python', ['app.py']);

    gradioProcess.stdout.on('data', (data) => {
      const msg = data.toString();
      console.log(`Gradio: ${msg}`);

      // "Running on local URL" 감지
      if (msg.includes('Running on')) {
        sendStatus('✓ Gradio 서버 시작 완료');
      }
    });

    gradioProcess.stderr.on('data', (data) => {
      console.error(`Gradio Error: ${data}`);
    });

    gradioProcess.on('error', (err) => {
      sendError(`Gradio 시작 실패: ${err.message}`);
      reject(err);
    });

    // Health check로 Gradio ready 확인
    waitForServer('http://127.0.0.1:7860', 30000)
      .then(() => {
        sendStatus('✓ 모든 준비 완료! UI로 전환합니다...');

        // Gradio UI로 전환
        if (mainWindow) {
          mainWindow.loadURL('http://127.0.0.1:7860');
        }

        resolve(true);
      })
      .catch((err) => {
        sendError(`Gradio 서버 응답 없음: ${err.message}`);
        reject(err);
      });
  });
}

// Health check 헬퍼
function waitForServer(url, timeout = 30000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    function check() {
      http.get(url, (res) => {
        if (res.statusCode === 200) {
          resolve();
        } else if (Date.now() - startTime < timeout) {
          setTimeout(check, 500);
        } else {
          reject(new Error('Timeout waiting for server'));
        }
      }).on('error', (err) => {
        if (Date.now() - startTime < timeout) {
          setTimeout(check, 500);
        } else {
          reject(new Error('Timeout waiting for server'));
        }
      });
    }

    check();
  });
}

// 선택 UI HTML
const selectionHTML = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>CodeDojo - 시작</title>
  <style>
    body {
      margin: 0;
      padding: 20px;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    .container {
      background: rgba(255,255,255,0.1);
      backdrop-filter: blur(10px);
      border-radius: 15px;
      padding: 30px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    h1 { margin-top: 0; text-align: center; }
    select, button {
      width: 100%;
      padding: 12px;
      margin: 10px 0;
      border: none;
      border-radius: 8px;
      font-size: 14px;
    }
    button {
      background: #4CAF50;
      color: white;
      cursor: pointer;
      font-size: 16px;
      font-weight: bold;
    }
    button:hover { background: #45a049; }
    button:disabled { background: #ccc; cursor: not-allowed; }
    #status {
      margin-top: 20px;
      padding: 15px;
      background: rgba(0,0,0,0.3);
      border-radius: 8px;
      min-height: 200px;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.6;
      overflow-y: auto;
      max-height: 250px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🥋 CodeDojo</h1>
    <select id="modelSelect" disabled>
      <option>모델 불러오는 중...</option>
    </select>
    <button id="startBtn" disabled>시작하기</button>
    <div id="status">
      <div>● 초기화 중...</div>
    </div>
  </div>
  <script>
    const { ipcRenderer } = require('electron');

    const modelSelect = document.getElementById('modelSelect');
    const startBtn = document.getElementById('startBtn');
    const statusDiv = document.getElementById('status');

    // 상태 업데이트 수신
    ipcRenderer.on('status-update', (event, message) => {
      const line = document.createElement('div');
      line.textContent = message;
      statusDiv.appendChild(line);
      statusDiv.scrollTop = statusDiv.scrollHeight;
    });

    // 모델 리스트 수신
    ipcRenderer.on('models-loaded', (event, models) => {
      if (models.length === 0) {
        modelSelect.innerHTML = '<option>사용 가능한 모델이 없습니다</option>';
        return;
      }
      modelSelect.innerHTML = models.map(m =>
        '<option value="' + m + '">' + m + '</option>'
      ).join('');
      modelSelect.disabled = false;
      startBtn.disabled = false;
    });

    // 에러 수신
    ipcRenderer.on('error', (event, error) => {
      const line = document.createElement('div');
      line.style.color = '#ff6b6b';
      line.style.fontWeight = 'bold';
      line.textContent = '✗ ' + error;
      statusDiv.appendChild(line);
    });

    // 시작 버튼 클릭
    startBtn.addEventListener('click', () => {
      const selectedModel = modelSelect.value;
      if (!selectedModel) return;

      startBtn.disabled = true;
      startBtn.textContent = '시작 중...';
      modelSelect.disabled = true;

      ipcRenderer.send('start-with-model', selectedModel);
    });
  </script>
</body>
</html>
`;

// 메인 창 생성
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 600,
    height: 500,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // HTML 로드
  mainWindow.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(selectionHTML));

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 초기화 플로우
async function initialize() {
  try {
    // 1. AI 서버 초기화 (기존 프로세스 정리)
    sendStatus('● AI 서버 초기화 중...');
    await lmsServerStop();
    await lmsUnloadAll();

    // 2. LMS 서버 시작
    await lmsServerStart();

    // 3. 모델 리스트 가져오기
    const models = await lmsListModels();

    // 4. 모델 리스트를 UI에 전송
    if (models.length === 0) {
      sendError('사용 가능한 모델이 없습니다. LM Studio에서 모델을 다운로드해주세요.');
      return;
    }

    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('models-loaded', models);
    }

  } catch (error) {
    sendError(`초기화 실패: ${error.message}`);
    if (error.message.includes('command not found') || error.message.includes('not recognized')) {
      sendError('LM Studio가 설치되지 않았거나 PATH에 없습니다.');
    }
  }
}

// IPC 핸들러: 모델 선택 후 시작
ipcMain.on('start-with-model', async (event, modelPath) => {
  try {
    // 1. 모델 로드
    await lmsLoadModel(modelPath);

    // 2. Gradio 시작
    await startGradio();

  } catch (error) {
    sendError(`시작 실패: ${error.message}`);
  }
});

// 앱 라이프사이클
app.on('ready', () => {
  createWindow();

  // 창이 준비되면 초기화 시작
  mainWindow.webContents.on('did-finish-load', () => {
    initialize();
  });
});

// Cleanup 로직
async function cleanup() {
  console.log('Cleanup 시작...');

  try {
    // 1. Gradio 프로세스 종료
    if (gradioProcess) {
      console.log('Gradio 프로세스 종료 중...');
      gradioProcess.kill();
      gradioProcess = null;
    }

    // 2. 모델 언로드
    await lmsUnloadAll();

    // 3. LMS 서버 중지
    await lmsServerStop();

    // 4. LMS 서버 프로세스 종료
    if (lmsServerProcess) {
      console.log('LMS 서버 프로세스 종료 중...');
      lmsServerProcess.kill();
      lmsServerProcess = null;
    }

    console.log('Cleanup 완료');
  } catch (error) {
    console.error('Cleanup 중 에러:', error);
    // 에러가 있어도 종료는 진행
  }
}

app.on('window-all-closed', async () => {
  await cleanup();
  app.quit();
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Ctrl+C 처리
process.on('SIGINT', async () => {
  await cleanup();
  process.exit(0);
});

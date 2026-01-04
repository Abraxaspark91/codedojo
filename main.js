const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');

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
    sendStatus('● AI모델 리스트 불러오는 중...');
    const output = await runCommand('lms', ['ls', '--json', '--llm']);

    // JSON 파싱
    let modelsData;
    try {
      modelsData = JSON.parse(output.trim());
    } catch (parseError) {
      sendError('AI모델 리스트 JSON 파싱 실패');
      console.error('JSON parse error:', output);
      return [];
    }

    // modelKey, displayName, sizeBytes를 추출하여 객체 배열로 변환
    const models = Array.isArray(modelsData)
      ? modelsData.map(m => {
          // modelKey가 lms load에 전달할 identifier
          const modelKey = m.modelKey || m.identifier || m.id || m.name || m.path;
          if (!modelKey) return null;
          
          // sizeBytes를 GB로 변환
          const sizeGB = m.sizeBytes 
            ? (m.sizeBytes / (1024 ** 3)).toFixed(2)
            : 'Unknown';
          
          // displayName (없으면 modelKey 사용)
          const displayName = m.displayName || modelKey;
          
          // Dropdown에 보여줄 텍스트
          const displayText = `${displayName} (${sizeGB}GB)`;
          
          return {
            key: modelKey,      // lms load에 전달
            display: displayText // UI에 표시
          };
        }).filter(Boolean)
      : [];

    sendStatus(`✓ ${models.length}개 AI모델 발견`);
    return models;
  } catch (error) {
    sendError(`AI모델 리스트 불러오기 실패: ${error.message}`);
    return [];
  }
}

// LMS 서버 중지
async function lmsServerStop() {
  try {
    sendStatus('● AI 서버 중지 중...');
    await runCommand('lms', ['server', 'stop']);
    sendStatus('✓ AI 서버 중지 완료');
    return true;
  } catch (error) {
    // 서버가 이미 중지된 경우 무시
    sendStatus('✓ AI 서버가 이미 중지되어 있습니다.');
    return true;
  }
}

// LMS 모델 언로드
async function lmsUnloadAll() {
  try {
    sendStatus('● AI모델 언로드 중(메모리 비우기)...');
    await runCommand('lms', ['unload', '--all']);
    sendStatus('✓ AI모델 언로드 완료');
    return true;
  } catch (error) {
    // 모델이 없는 경우 무시
    sendStatus('✓ 로딩돼있는 AI모델이 없습니다');
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
      const msg = data.toString().trim();
      
      // 소문자로 변환하여 키워드 검사 (대소문자 무시)
      const lowerMsg = msg.toLowerCase();

      // '진짜 에러'라고 판단할 키워드 정의
      const isRealError = lowerMsg.includes('error') || 
                          lowerMsg.includes('failed') || 
                          lowerMsg.includes('exception') ||
                          lowerMsg.includes('fatal');

      if (isRealError) {
        // 진짜 에러인 경우만 Error로 출력
        console.error(`LMS Error: ${msg}`);
        // 필요하다면 UI로도 전송
        // sendError(`LMS: ${msg}`); 
      } else {
        // 그 외(Success, Info, Running 등)는 일반 로그로 출력
        console.log(`LMS Log: ${msg}`);
        
        // (선택사항) 만약 'success'나 'running' 같은 특정 단어가 있으면 상태창에도 띄워줄 수 있음
        // if (lowerMsg.includes('running')) sendStatus('LMS 서버 가동 중...');
      }
    });
    lmsServerProcess.on('error', (err) => {
      sendError(`AI 서버 시작 실패: ${err.message}`);
      reject(err);
    });

    // Health check로 서버 ready 확인
    waitForServer('http://127.0.0.1:1234/v1/models', 30000)
      .then(() => {
        sendStatus('✓ AI 서버 시작 완료');
        resolve(true);
      })
      .catch((err) => {
        sendError(`AI 서버 응답 없음: ${err.message}`);
        reject(err);
      });
  });
}

// 모델 로딩 완료 확인 헬퍼
async function checkModelLoaded(modelIdentifier, maxRetries = 60) {
  return new Promise((resolve, reject) => {
    let attempts = 0;

    const check = () => {
      attempts++;
      // LM Studio는 OpenAI 호환 API를 제공하므로 /v1/models로 확인 가능
      http.get('http://127.0.0.1:1234/v1/models', (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            // data 배열 안에 해당 모델 id가 있는지 확인
            const isLoaded = json.data && json.data.some(m => m.id === modelIdentifier);
            
            if (isLoaded) {
              resolve(true);
            } else {
              if (attempts >= maxRetries) {
                reject(new Error('AI모델 로딩 시간 초과 (API 확인 실패)'));
              } else {
                // 아직 로드 안됨, 1초 후 재시도
                sendStatus(`● 모델 로딩 확인 중... (${attempts}/${maxRetries})`);
                setTimeout(check, 1000); 
              }
            }
          } catch (e) {
            console.error('JSON 파싱 에러:', e);
            setTimeout(check, 1000);
          }
        });
      }).on('error', (err) => {
        console.error('API 연결 에러:', err);
        setTimeout(check, 1000);
      });
    };

    check();
  });
}

// [수정] LMS 모델 로드 함수
async function lmsLoadModel(modelIdentifier) {
  return new Promise(async (resolve, reject) => {
    sendStatus(`● 모델 로딩 명령 전송: ${modelIdentifier}...`);

    // 1. 로드 명령 실행 (결과를 기다리지 않고 프로세스 실행만 함)
    const proc = spawn('lms', ['load', modelIdentifier], { encoding: 'ANSI' });

    proc.stdout.on('data', (data) => {
      const msg = data.toString().trim();
      // 진행률 표시 (UI 업데이트)
      if (msg.includes('%') || msg.includes('[')) {
        process.stdout.write('\r' + msg); 
      } else if (msg) {
        console.log(`LMS CLI: ${msg}`);
      }
    });

    proc.stderr.on('data', (data) => {
      console.log(`LMS CLI(Info): ${data.toString().trim()}`);
    });

    // 프로세스가 닫힐 때(성공이든, "Client disconnected"든 상관없이)
    // 실제 서버 상태를 확인하는 단계로 넘어갑니다.
    proc.on('close', async (code) => {
      console.log(`LMS CLI 프로세스 종료 (Code: ${code}). 서버 상태 확인 시작.`);
      
      try {
        // 2. 프로세스 종료 후, 실제 API를 찔러서 로딩이 완료될 때까지 기다림
        await checkModelLoaded(modelIdentifier);
        
        currentModel = modelIdentifier;
        console.log('✓ API로 AI모델 로딩 최종 확인됨');
        sendStatus('✓ AI모델 로딩 완료');
        resolve(true);
      } catch (error) {
        sendError(`AI모델 로딩 실패: ${error.message}`);
        reject(error);
      }
    });

    proc.on('error', (err) => {
      // spawn 자체가 실패했을 때만 에러 처리
      sendError(`AI모델 로딩 중 에러가 발생했습니다(LMS): ${err.message}`);
      reject(err);
    });
  });
}

// Python 경로 찾기 (.venv 우선)
function getPythonPath() {
  const isWindows = process.platform === 'win32';
  const venvPython = isWindows
    ? path.join(process.cwd(), '.venv', 'Scripts', 'python.exe')
    : path.join(process.cwd(), '.venv', 'bin', 'python');

  // .venv가 있으면 사용
  if (fs.existsSync(venvPython)) {
    return venvPython;
  }

  // .venv가 없으면 시스템 python 사용
  return isWindows ? 'python.exe' : 'python3';
}

// Gradio 서버 시작
async function startGradio() {
  return new Promise((resolve, reject) => {
    sendStatus('● Gradio 서버 시작 중...');

    const pythonPath = getPythonPath();
    const appPath = path.join(process.cwd(), 'app.py');

    // app.py 존재 확인
    if (!fs.existsSync(appPath)) {
      sendError(`app.py를 찾을 수 없습니다: ${appPath}`);
      reject(new Error('app.py not found'));
      return;
    }

    gradioProcess = spawn(pythonPath, [appPath], {
      cwd: process.cwd()
    });

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
        sendStatus('✓ 모든 준비 완료! 코딩 도장으로 진입합니다...');

        // Gradio UI로 전환
        if (mainWindow) {
          mainWindow.loadURL('http://127.0.0.1:7860');
          mainWindow.setResizable(true);
          mainWindow.maximize();
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
    if (Date.now() - startTime >= timeout) {
      reject(new Error('Timeout waiting for server'));
      return;
    }
    
    http.get(url, (res) => {
      if (res.statusCode === 200) {
        resolve();
      } else {
        setTimeout(check, 500);
      }
    }).on('error', (err) => {
      setTimeout(check, 500);
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
        '<option value="' + m.key + '">' + m.display + '</option>'
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
    sendStatus('● AI 서버 상태 확인 중...');
    
    // 1. 서버가 이미 살아있는지 체크 (Health Check)
    let isServerRunning = false;
    try {
      await waitForServer('http://127.0.0.1:1234/v1/models', 2000); // 2초만 대기
      isServerRunning = true;
      sendStatus('✓ 기존 AI 서버가 이미 실행 중입니다.');
    } catch (e) {
      isServerRunning = false;
    }

    // 2. 서버가 안 켜져 있을 때만 시작 절차 수행
    if (!isServerRunning) {
      await lmsServerStart();
    }
    // (서버가 이미 실행 중이면 그대로 사용)

    // 3. 모델 리스트 가져오기 (여기부터는 기존과 동일)
    const models = await lmsListModels();

    // 4. 모델 리스트를 UI에 전송
    if (models.length === 0) {
      sendError('사용 가능한 AI모델이 없습니다. LM Studio에서 모델을 다운로드해주세요.');
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
  mainWindow.webContents.once('did-finish-load', () => {
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
      console.log('AI 서버 프로세스 종료 중...');
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

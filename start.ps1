# 启动服务脚本
# 启动后端服务

# 一键启动前后端服务

# 检查后端环境
$backendPath = Join-Path $PSScriptRoot "backend"
$pythonPath = Join-Path $backendPath "venv\Scripts\python.exe"
$mainPath = Join-Path $backendPath "main.py"

if (-not (Test-Path $pythonPath)) {
    Write-Host "错误: Python 虚拟环境未找到" -ForegroundColor Red
    Write-Host "请先设置虚拟环境:" -ForegroundColor Yellow
    Write-Host "cd backend" -ForegroundColor Yellow
    Write-Host "python -m venv venv" -ForegroundColor Yellow
    Write-Host ".\venv\Scripts\activate" -ForegroundColor Yellow
    Write-Host "pip install -r requirements.txt" -ForegroundColor Yellow
    exit
}

if (-not (Test-Path $mainPath)) {
    Write-Host "错误: 后端主程序 main.py 未找到" -ForegroundColor Red
    exit
}

# 检查前端环境
$clientPath = Join-Path $PSScriptRoot "client"
$packageJsonPath = Join-Path $clientPath "package.json"

if (-not (Test-Path $packageJsonPath)) {
    Write-Host "错误: 前端 package.json 未找到" -ForegroundColor Red
    exit
}

# 启动后端服务
Write-Host "启动后端服务..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$backendPath'; .\venv\Scripts\python.exe main.py`""

# 启动前端服务
Write-Host "启动前端服务..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$clientPath'; npm run dev`""

Write-Host "前后端服务启动成功!" -ForegroundColor Green
Write-Host "- 前端地址: http://localhost:5173" -ForegroundColor Cyan
Write-Host "- 后端地址: http://localhost:8000" -ForegroundColor Cyan

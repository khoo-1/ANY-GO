# 启动服务脚本
# 一键启动前后端服务

# 设置编码为 UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 设置控制台为UTF-8模式
try {
    # 设置控制台代码页为UTF-8 (65001)
    chcp 65001 | Out-Null
    Write-Host "已设置控制台为UTF-8模式" -ForegroundColor Green
} catch {
    Write-Host "无法设置控制台编码: $_" -ForegroundColor Yellow
}

# 检查后端环境
$backendPath = Join-Path $PSScriptRoot "backend"

# 支持两种虚拟环境目录：.venv 和 venv
$venvPaths = @(
    (Join-Path $backendPath ".venv\Scripts\python.exe"),
    (Join-Path $backendPath "venv\Scripts\python.exe")
)

$pythonPath = $null
foreach ($path in $venvPaths) {
    if (Test-Path $path) {
        $pythonPath = $path
        Write-Host "找到Python虚拟环境: $pythonPath" -ForegroundColor Green
        break
    }
}

$mainPath = Join-Path $backendPath "main.py"
$initCombinedPath = Join-Path $backendPath "init_combined.py"
$diagnoseDbPath = Join-Path $backendPath "diagnose_db.py"
$appDbPath = Join-Path $backendPath "app.db"

if ($null -eq $pythonPath) {
    Write-Host "错误: Python 虚拟环境未找到" -ForegroundColor Red
    Write-Host "请先设置虚拟环境:" -ForegroundColor Yellow
    Write-Host "cd backend" -ForegroundColor Yellow
    Write-Host "python -m venv .venv" -ForegroundColor Yellow
    Write-Host ".\.venv\Scripts\activate" -ForegroundColor Yellow
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

# 确保数据库目录存在
$dbDir = Join-Path $backendPath "db_backup"
if (-not (Test-Path $dbDir)) {
    New-Item -Path $dbDir -ItemType Directory | Out-Null
    Write-Host "创建数据库备份目录: $dbDir" -ForegroundColor Green
}

# 备份现有数据库
if (Test-Path $appDbPath) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $dbDir "app.db.backup.$timestamp"
    Write-Host "备份旧数据库: $appDbPath -> $backupPath" -ForegroundColor Yellow
    Copy-Item -Path $appDbPath -Destination $backupPath -Force
    
    # 完全移除旧数据库文件，确保不存在问题
    Remove-Item -Path $appDbPath -Force
    Write-Host "旧数据库已备份并移除" -ForegroundColor Green
    
    # 检查数据库文件是否已被完全移除
    if (Test-Path $appDbPath) {
        Write-Host "警告: 无法完全移除旧数据库文件，可能被其他进程锁定" -ForegroundColor Red
        $continue = Read-Host "是否继续? (y/n)"
        if ($continue -ne "y") {
            exit
        }
    } else {
        Write-Host "旧数据库文件已成功移除" -ForegroundColor Green
    }
}

# 显示启动模式和初始化方式
Write-Host "`n==============================================" -ForegroundColor Cyan
Write-Host "        ANY-GO 系统启动" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# 检查是否存在数据库诊断脚本
if ((Test-Path $diagnoseDbPath) -and (-not (Test-Path $appDbPath))) {
    Write-Host "发现数据库诊断脚本，是否运行诊断? (y/n)" -ForegroundColor Yellow
    $runDiagnose = Read-Host
    
    if ($runDiagnose -eq "y") {
        Write-Host "运行数据库诊断脚本..." -ForegroundColor Yellow
        Push-Location $backendPath
        
        # 创建详细的诊断日志文件
        $diagLogFile = Join-Path $backendPath "db_diagnose_log.txt"
        Write-Host "诊断结果将记录到: $diagLogFile" -ForegroundColor Yellow
        
        # 运行诊断脚本并记录到日志文件
        & $pythonPath diagnose_db.py 2>&1 | Tee-Object -FilePath $diagLogFile
        $diagResult = $?
        Pop-Location
        
        if ($diagResult) {
            Write-Host "诊断完成" -ForegroundColor Green
        } else {
            Write-Host "诊断过程中出现错误" -ForegroundColor Red
            Write-Host "查看详细诊断日志: $diagLogFile" -ForegroundColor Yellow
        }
    }
}

# 使用统一的初始化脚本
if (Test-Path $initCombinedPath) {
    Write-Host "使用统一初始化脚本 init_combined.py 创建数据库..." -ForegroundColor Yellow
    try {
        # 切换到后端目录并运行初始化脚本
        Push-Location $backendPath
        
        # 创建详细的日志文件
        $logFile = Join-Path $backendPath "db_init_log.txt"
        Write-Host "初始化过程将记录到日志文件: $logFile" -ForegroundColor Yellow
        
        # 设置PYTHONIOENCODING环境变量确保Python输出为UTF-8
        $env:PYTHONIOENCODING = "utf-8"
        
        # 运行初始化脚本并记录到日志文件
        & $pythonPath init_combined.py 2>&1 | Tee-Object -FilePath $logFile
        $initResult = $?
        Pop-Location
        
        if ($initResult) {
            Write-Host "数据库初始化成功!" -ForegroundColor Green
        } else {
            Write-Host "数据库初始化失败!" -ForegroundColor Red
            Write-Host "详细错误日志已保存到: $logFile" -ForegroundColor Yellow
            Write-Host "请查看日志文件解决问题" -ForegroundColor Yellow
            
            # 尝试分析错误
            $errorContent = Get-Content -Path $logFile -Tail 20 -Encoding UTF8
            Write-Host "错误日志末尾内容:" -ForegroundColor Red
            $errorContent | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
            
            $continue = Read-Host "数据库初始化失败，是否继续启动服务? (y/n)"
            if ($continue -ne "y") {
                exit
            }
        }
    } catch {
        Write-Host "数据库初始化出错: $_" -ForegroundColor Red
        $continue = Read-Host "是否继续启动服务? (y/n)"
        if ($continue -ne "y") {
            exit
        }
    }
} else {
    Write-Host "警告: 统一初始化脚本 init_combined.py 未找到" -ForegroundColor Yellow
    Write-Host "将尝试使用默认的初始化方式" -ForegroundColor Yellow
    
    # 尝试运行旧的初始化脚本
    $initDbPath = Join-Path $backendPath "init_db.py"
    $initUsersPath = Join-Path $backendPath "init_users.py"
    
    # 运行数据库表初始化脚本
    if (Test-Path $initDbPath) {
        Write-Host "运行数据库表初始化脚本..." -ForegroundColor Yellow
        Push-Location $backendPath
        # 设置PYTHONIOENCODING环境变量确保Python输出为UTF-8
        $env:PYTHONIOENCODING = "utf-8"
        & $pythonPath init_db.py
        $initDbResult = $?
        Pop-Location
        
        if ($initDbResult) {
            Write-Host "数据库表初始化成功!" -ForegroundColor Green
        } else {
            Write-Host "数据库表初始化失败!" -ForegroundColor Red
            $continue = Read-Host "是否继续? (y/n)"
            if ($continue -ne "y") {
                exit
            }
        }
    } else {
        Write-Host "错误: 数据库表初始化脚本 init_db.py 未找到!" -ForegroundColor Red
        $continue = Read-Host "缺少初始化脚本，是否继续? (y/n)"
        if ($continue -ne "y") {
            exit
        }
    }
    
    # 运行用户初始化脚本
    if (Test-Path $initUsersPath) {
        Write-Host "运行用户初始化脚本..." -ForegroundColor Yellow
        Push-Location $backendPath
        # 设置PYTHONIOENCODING环境变量确保Python输出为UTF-8
        $env:PYTHONIOENCODING = "utf-8"
        & $pythonPath init_users.py
        $initUsersResult = $?
        Pop-Location
        
        if ($initUsersResult) {
            Write-Host "用户初始化成功!" -ForegroundColor Green
        } else {
            Write-Host "用户初始化失败!" -ForegroundColor Red
            $continue = Read-Host "是否继续? (y/n)"
            if ($continue -ne "y") {
                exit
            }
        }
    } else {
        Write-Host "警告: 用户初始化脚本 init_users.py 未找到!" -ForegroundColor Yellow
    }
}

# 确认数据库文件是否存在
if (Test-Path $appDbPath) {
    $fileSize = (Get-Item $appDbPath).Length / 1KB
    Write-Host "数据库文件存在: $appDbPath (大小: $fileSize KB)" -ForegroundColor Green
    
    # 如果文件大小异常小，可能表示初始化不完整
    if ($fileSize -lt 1) {
        Write-Host "警告: 数据库文件大小异常小 ($fileSize KB)，可能初始化不完整" -ForegroundColor Red
        $continue = Read-Host "数据库文件大小异常，是否继续启动服务? (y/n)"
        if ($continue -ne "y") {
            exit
        }
    }
} else {
    Write-Host "警告: 数据库文件不存在或创建失败" -ForegroundColor Red
    $continue = Read-Host "数据库文件不存在，是否继续启动服务? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

# 启动后端服务
Write-Host "`n启动后端服务..." -ForegroundColor Green
# 设置环境变量确保Python输出为UTF-8
$env:PYTHONIOENCODING = "utf-8"
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$backendPath'; `$env:PYTHONIOENCODING='utf-8'; & '$pythonPath' main.py`""

# 启动前端服务
Write-Host "启动前端服务..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$clientPath'; npm run dev`""

Write-Host "`n==============================================" -ForegroundColor Cyan
Write-Host "        服务启动成功!" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "- 前端地址: http://localhost:5173" -ForegroundColor Cyan
Write-Host "- 后端地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "- API文档: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`n默认用户信息:" -ForegroundColor Yellow
Write-Host "- 管理员: admin / admin123" -ForegroundColor White
Write-Host "- 普通用户: user / user123" -ForegroundColor White

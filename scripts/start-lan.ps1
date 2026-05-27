# ============================================================
# AiMediaMaker 局域网测试启动脚本
# ============================================================
# 用法: 在项目根目录执行
#   powershell -ExecutionPolicy Bypass -File scripts/start-lan.ps1
# 或右键 → 使用 PowerShell 运行
# ============================================================

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

# 获取本机局域网 IP（排除虚拟网卡/Loopback）
$lanIP = (Get-NetIPAddress -AddressFamily IPv4 | 
    Where-Object { 
        $_.IPAddress -notlike "127.*" -and 
        $_.IPAddress -notlike "169.*" -and
        $_.InterfaceAlias -notlike "*Loopback*" -and
        $_.IPAddress -match "^192\.168\.|^10\.|^172\.(1[6-9]|2[0-9]|3[01])\." 
    } | 
    Select-Object -First 1).IPAddress

if (-not $lanIP) {
    Write-Host "❌ 未能自动检测到局域网 IP，请手动检查网络配置" -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AiMediaMaker 局域网测试环境启动器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "检测到局域网 IP: " -NoNewline
Write-Host "$lanIP" -ForegroundColor Yellow
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Green
Write-Host "  前台页面: http://$($lanIP):5173" -ForegroundColor White
Write-Host "  后台管理: http://$($lanIP):5174" -ForegroundColor White
Write-Host "  API 接口: http://$($lanIP):8000" -ForegroundColor White
Write-Host ""
Write-Host "按 Enter 开始启动三个服务..." -ForegroundColor Gray
$null = Read-Host

# 检查 .env CORS 配置
$envFile = Join-Path $root "backend\.env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    $frontendOrigin = "http://$($lanIP):5173"
    $adminOrigin = "http://$($lanIP):5174"
    
    if (-not ($envContent -match [regex]::Escape($frontendOrigin))) {
        Write-Host ""
        Write-Host "⚠️  警告: backend\.env 的 CORS_ORIGINS 未包含局域网地址" -ForegroundColor Yellow
        Write-Host "   请确保包含以下地址（已自动修改，如未生效请手动检查）:" -ForegroundColor Yellow
        Write-Host "   $frontendOrigin" -ForegroundColor Yellow
        Write-Host "   $adminOrigin" -ForegroundColor Yellow
        Write-Host ""
    }
}

# 启动后端
function Start-Backend {
    $backendPath = Join-Path $root "backend"
    $venvPython = Join-Path $backendPath ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Host "❌ 后端虚拟环境未找到: $venvPython" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🚀 启动后端服务 (port 8000)..." -ForegroundColor Cyan
    $cmd = "cd `"$backendPath`"; & `"$venvPython`" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
}

# 启动前台
function Start-Frontend {
    $frontendPath = Join-Path $root "frontend"
    Write-Host "🚀 启动前台页面 (port 5173)..." -ForegroundColor Cyan
    $cmd = "cd `"$frontendPath`"; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
}

# 启动后台
function Start-Admin {
    $adminPath = Join-Path $root "frontend-admin"
    Write-Host "🚀 启动后台管理 (port 5174)..." -ForegroundColor Cyan
    $cmd = "cd `"$adminPath`"; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
}

Start-Backend
Start-Sleep -Seconds 2
Start-Frontend
Start-Sleep -Seconds 2
Start-Admin

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  所有服务已启动!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📱 局域网内其他设备可访问:" -ForegroundColor White
Write-Host "   前台: http://$($lanIP):5173" -ForegroundColor Yellow
Write-Host "   后台: http://$($lanIP):5174" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  注意: 首次访问后台需要登录" -ForegroundColor Gray
Write-Host "   默认账号: admin / admin123" -ForegroundColor Gray
Write-Host ""

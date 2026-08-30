param(
  [ValidateSet("api", "ui", "all")]
  [string]$Target = "api",
  [switch]$NoOpen
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$results = Join-Path $root "allure-results"
$report = Join-Path $root "allure-report"
$html = Join-Path $root "report.html"

if (Test-Path $results) { Remove-Item -Recurse -Force $results }
if (Test-Path $report) { Remove-Item -Recurse -Force $report }

$pytestArgs = @("-m", "api")
if ($Target -eq "ui") { $pytestArgs = @("-m", "ui") }
if ($Target -eq "all") { $pytestArgs = @() }

python -m pytest (Join-Path $root "tests") @pytestArgs --alluredir=$results --clean-alluredir --html=$html --self-contained-html --headless
if (-not $?) {
  Write-Host "测试执行失败，已停止生成报告。" -ForegroundColor Red
  exit 1
}

$allureCmd = "allure"
if (-not (Get-Command allure -ErrorAction SilentlyContinue)) {
  $fallback = "C:\Users\qing124\allure\allure-2.46.0\bin\allure.bat"
  if (Test-Path $fallback) { $allureCmd = $fallback }
}

& $allureCmd generate $results -o $report --clean
python (Join-Path $root "export_report.py")
Write-Host "Allure 完整报告：$report（用 查看报告.bat 打开）" -ForegroundColor Green
Write-Host "双击即开报告：$html 与 $(Join-Path $report 'index.html')" -ForegroundColor Green
if (-not $NoOpen) { Start-Process (Join-Path $report "index.html") }

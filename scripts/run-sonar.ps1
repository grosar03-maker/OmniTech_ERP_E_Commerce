$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$toolsRoot = Join-Path $repoRoot '.tools'
$scannerRoot = Join-Path $toolsRoot 'sonar-scanner'
$scannerVersion = if ($env:SONAR_SCANNER_VERSION) { $env:SONAR_SCANNER_VERSION } else { '5.0.1.3006' }
$zipName = "sonar-scanner-cli-$scannerVersion-windows.zip"
$scannerUrl = if ($env:SONAR_SCANNER_URL) {
    $env:SONAR_SCANNER_URL
} else {
    "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/$zipName"
}

function Get-LocalScannerExecutable {
    $localScanner = Join-Path $scannerRoot 'bin\sonar-scanner.bat'
    if (Test-Path $localScanner) {
        return $localScanner
    }

    return $null
}

function Get-PathScannerExecutable {
    $pathScanner = Get-Command sonar-scanner -ErrorAction SilentlyContinue
    if ($pathScanner) {
        return $pathScanner.Source
    }

    return $null
}

function Install-LocalScanner {
    New-Item -ItemType Directory -Force -Path $toolsRoot | Out-Null

    $zipPath = Join-Path $toolsRoot $zipName
    Write-Host "Descargando SonarScanner CLI $scannerVersion..."
    Invoke-WebRequest -Uri $scannerUrl -OutFile $zipPath

    $extractPath = Join-Path $toolsRoot "sonar-scanner-$scannerVersion-windows"
    Remove-Item -Recurse -Force $extractPath, $scannerRoot -ErrorAction SilentlyContinue
    Expand-Archive -Path $zipPath -DestinationPath $toolsRoot -Force

    if (-not (Test-Path $extractPath)) {
        $expanded = Get-ChildItem -Path $toolsRoot -Directory |
            Where-Object { $_.Name -like "sonar-scanner-$scannerVersion*" } |
            Select-Object -First 1

        if (-not $expanded) {
            throw 'No se encontro la carpeta extraida de SonarScanner.'
        }

        $extractPath = $expanded.FullName
    }

    Move-Item -Path $extractPath -Destination $scannerRoot
    Remove-Item -Force $zipPath -ErrorAction SilentlyContinue
}

Set-Location $repoRoot

if (-not (Test-Path (Join-Path $repoRoot 'sonar-project.properties'))) {
    throw 'No existe sonar-project.properties en la raiz del proyecto.'
}

if (-not (Test-Path (Join-Path $repoRoot 'coverage.xml'))) {
    throw 'No existe coverage.xml. Ejecuta primero make test-ci.'
}

$scanner = Get-LocalScannerExecutable
if (-not $scanner) {
    try {
        Install-LocalScanner
        $scanner = Get-LocalScannerExecutable
    } catch {
        Write-Warning $_.Exception.Message
        Write-Warning 'No se pudo instalar el scanner local. Se intentara usar sonar-scanner desde PATH.'
        $scanner = Get-PathScannerExecutable
    }
}

if (-not $scanner) {
    throw 'No se pudo instalar ni encontrar sonar-scanner.'
}

$arguments = @()
if ($env:SONAR_TOKEN) {
    $arguments += "-Dsonar.token=$env:SONAR_TOKEN"
} elseif ($env:SONAR_LOGIN) {
    $arguments += "-Dsonar.login=$env:SONAR_LOGIN"
}

Write-Host "Ejecutando SonarScanner desde $scanner"
& $scanner @arguments

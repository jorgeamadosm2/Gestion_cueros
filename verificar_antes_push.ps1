# Script de verificación antes de subir a GitHub
# Ejecutar: .\verificar_antes_push.ps1

Write-Host "🔍 Verificando seguridad antes de subir a GitHub..." -ForegroundColor Cyan
Write-Host ""

$errores = 0
$advertencias = 0

# Verificar que estamos en un repositorio Git
if (-not (Test-Path ".git")) {
    Write-Host "❌ ERROR: No es un repositorio Git" -ForegroundColor Red
    Write-Host "   Ejecuta primero: git init" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Repositorio Git encontrado" -ForegroundColor Green

# Verificar archivos sensibles
Write-Host ""
Write-Host "🔒 Verificando archivos sensibles..." -ForegroundColor Cyan

$archivosSensibles = @(
    "firebase_config.json",
    ".streamlit\secrets.toml",
    ".session.json"
)

foreach ($archivo in $archivosSensibles) {
    if (Test-Path $archivo) {
        # Verificar si está en git
        $enGit = git ls-files $archivo 2>$null
        if ($enGit) {
            Write-Host "❌ ERROR: $archivo está siendo rastreado por Git" -ForegroundColor Red
            $errores++
        } else {
            Write-Host "✅ $archivo existe pero está protegido por .gitignore" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️  $archivo no existe (OK si no lo necesitas)" -ForegroundColor Yellow
    }
}

# Verificar .gitignore
Write-Host ""
Write-Host "📝 Verificando .gitignore..." -ForegroundColor Cyan

if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    
    $patronesNecesarios = @(
        "firebase_config.json",
        "secrets.toml",
        ".session.json",
        "__pycache__",
        ".venv"
    )
    
    foreach ($patron in $patronesNecesarios) {
        if ($gitignoreContent -match [regex]::Escape($patron)) {
            Write-Host "✅ $patron está en .gitignore" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $patron NO está en .gitignore" -ForegroundColor Yellow
            $advertencias++
        }
    }
} else {
    Write-Host "❌ ERROR: .gitignore no existe" -ForegroundColor Red
    $errores++
}

# Verificar requirements.txt
Write-Host ""
Write-Host "📦 Verificando requirements.txt..." -ForegroundColor Cyan

if (Test-Path "requirements.txt") {
    Write-Host "✅ requirements.txt existe" -ForegroundColor Green
    $deps = Get-Content "requirements.txt"
    
    $depsNecesarias = @("streamlit", "pandas", "firebase-admin")
    foreach ($dep in $depsNecesarias) {
        if ($deps -match $dep) {
            Write-Host "  ✅ $dep incluido" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $dep NO incluido" -ForegroundColor Yellow
            $advertencias++
        }
    }
} else {
    Write-Host "❌ ERROR: requirements.txt no existe" -ForegroundColor Red
    $errores++
}

# Verificar archivo principal
Write-Host ""
Write-Host "🎯 Verificando archivo principal..." -ForegroundColor Cyan

if (Test-Path "gestion_cueros.py") {
    Write-Host "✅ gestion_cueros.py existe" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: gestion_cueros.py no existe" -ForegroundColor Red
    $errores++
}

# Verificar estructura .streamlit
Write-Host ""
Write-Host "⚙️  Verificando configuración Streamlit..." -ForegroundColor Cyan

if (Test-Path ".streamlit") {
    Write-Host "✅ Carpeta .streamlit existe" -ForegroundColor Green
    
    if (Test-Path ".streamlit\secrets.toml.example") {
        Write-Host "✅ secrets.toml.example existe" -ForegroundColor Green
    } else {
        Write-Host "⚠️  secrets.toml.example no existe (recomendado para documentación)" -ForegroundColor Yellow
        $advertencias++
    }
} else {
    Write-Host "⚠️  Carpeta .streamlit no existe" -ForegroundColor Yellow
    $advertencias++
}

# Verificar archivos de documentación
Write-Host ""
Write-Host "📚 Verificando documentación..." -ForegroundColor Cyan

$docsRecomendados = @(
    "README.md",
    "DEPLOY_STREAMLIT_CLOUD.md"
)

foreach ($doc in $docsRecomendados) {
    if (Test-Path $doc) {
        Write-Host "✅ $doc existe" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $doc no existe (recomendado)" -ForegroundColor Yellow
        $advertencias++
    }
}

# Ver estado de Git
Write-Host ""
Write-Host "📊 Estado de Git:" -ForegroundColor Cyan
git status --short

# Contar archivos a subir
Write-Host ""
Write-Host "📁 Archivos que se subirán a GitHub:" -ForegroundColor Cyan
$archivos = git ls-files
Write-Host "   Total: $($archivos.Count) archivos" -ForegroundColor White

# Buscar archivos sospechosos
$sospechosos = $archivos | Where-Object { 
    $_ -match "\.db$|\.sqlite|firebase_config\.json|secrets\.toml$|\.env$"
}

if ($sospechosos) {
    Write-Host ""
    Write-Host "🚨 ARCHIVOS SOSPECHOSOS ENCONTRADOS:" -ForegroundColor Red
    foreach ($s in $sospechosos) {
        Write-Host "   ❌ $s" -ForegroundColor Red
    }
    $errores++
}

# Resumen final
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "               RESUMEN FINAL                     " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

if ($errores -eq 0 -and $advertencias -eq 0) {
    Write-Host "🎉 ¡TODO PERFECTO! Puedes hacer push a GitHub" -ForegroundColor Green
    Write-Host ""
    Write-Host "Comandos para continuar:" -ForegroundColor Cyan
    Write-Host "  git add ." -ForegroundColor White
    Write-Host "  git commit -m 'Sistema de Gestión de Cueros'" -ForegroundColor White
    Write-Host "  git push -u origin main" -ForegroundColor White
    exit 0
} elseif ($errores -eq 0) {
    Write-Host "⚠️  $advertencias advertencia(s) encontrada(s)" -ForegroundColor Yellow
    Write-Host "   Puedes continuar, pero revisa las advertencias" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Comandos para continuar:" -ForegroundColor Cyan
    Write-Host "  git add ." -ForegroundColor White
    Write-Host "  git commit -m 'Sistema de Gestión de Cueros'" -ForegroundColor White
    Write-Host "  git push -u origin main" -ForegroundColor White
    exit 0
} else {
    Write-Host "❌ $errores error(es) encontrado(s)" -ForegroundColor Red
    Write-Host "⚠️  $advertencias advertencia(s) encontrada(s)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "❌ NO HAGAS PUSH TODAVÍA" -ForegroundColor Red
    Write-Host "   Corrige los errores antes de continuar" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ver: VERIFICACION_SEGURIDAD.md para más información" -ForegroundColor Cyan
    exit 1
}

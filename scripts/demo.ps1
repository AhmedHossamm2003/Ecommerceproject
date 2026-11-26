[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("help", "start", "open", "test", "status", "stop")]
    [string]$Action = "help"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot

$ExpectedRawFiles = @(
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv"
)

function Invoke-DockerStep {
    param(
        [Parameter(Mandatory)]
        [string]$Title,
        [Parameter(Mandatory)]
        [string[]]$DockerArguments
    )

    Write-Host ""
    Write-Host "==> $Title" -ForegroundColor Cyan
    & docker @DockerArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Title (docker exit code $LASTEXITCODE)"
    }
}

function Assert-DockerReady {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker was not found. Install/open Docker Desktop, then try again."
    }

    & docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Engine is not ready. Open Docker Desktop and wait for Engine running."
    }
}

function Assert-LocalSetup {
    if (-not (Test-Path -LiteralPath ".env" -PathType Leaf)) {
        throw "Missing .env. Run: Copy-Item .env.example .env, then replace the example passwords."
    }

    $missingFiles = @(foreach ($fileName in $ExpectedRawFiles) {
        $filePath = Join-Path -Path "data\raw" -ChildPath $fileName
        if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) {
            $fileName
        }
    })

    if ($missingFiles.Count -gt 0) {
        throw "Missing Olist files in data\raw: $($missingFiles -join ', ')"
    }
}

switch ($Action) {
    "open" {
        Assert-DockerReady

        if (-not (Test-Path -LiteralPath ".env" -PathType Leaf)) {
            throw "Missing .env. Run: Copy-Item .env.example .env, then replace the example passwords."
        }

        Invoke-DockerStep "Open the saved project services" @(
            "compose", "--profile", "orchestration", "up", "-d",
            "postgres", "pgadmin", "kestra-postgres", "kestra"
        )
        Invoke-DockerStep "Show service status" @("compose", "--profile", "orchestration", "ps")

        Write-Host ""
        Write-Host "Saved project is open and ready for presentation." -ForegroundColor Green
        Write-Host "pgAdmin: http://localhost:5050"
        Write-Host "Kestra:  http://localhost:8080"
    }

    "start" {
        Assert-DockerReady
        Assert-LocalSetup

        Invoke-DockerStep "Start PostgreSQL and pgAdmin" @("compose", "up", "-d", "postgres", "pgadmin")
        Invoke-DockerStep "Build the ingestion image" @("compose", "--profile", "ingestion", "build", "ingestion")
        Invoke-DockerStep "Ingest the nine raw CSV files" @("compose", "--profile", "ingestion", "run", "--rm", "ingestion", "--strict-files")
        Invoke-DockerStep "Build the transformation image" @("compose", "--profile", "transformation", "build", "transformation")
        Invoke-DockerStep "Build the clean layer and warehouse" @("compose", "--profile", "transformation", "run", "--rm", "transformation")
        Invoke-DockerStep "Build the quality image" @("compose", "--profile", "quality", "build", "quality")
        Invoke-DockerStep "Run the quality gate" @("compose", "--profile", "quality", "run", "--rm", "quality")
        Invoke-DockerStep "Build the Power BI preparation image" @("compose", "--profile", "bi", "build", "bi-prepare")
        Invoke-DockerStep "Prepare the Power BI views" @("compose", "--profile", "bi", "run", "--rm", "bi-prepare")
        Invoke-DockerStep "Start Kestra" @("compose", "--profile", "orchestration", "up", "-d", "kestra-postgres", "kestra")
        Invoke-DockerStep "Show service status" @("compose", "--profile", "orchestration", "ps")

        Write-Host ""
        Write-Host "Project is ready." -ForegroundColor Green
        Write-Host "pgAdmin: http://localhost:5050"
        Write-Host "Kestra:  http://localhost:8080"
        Write-Host "Credentials are in your local .env file."
    }

    "test" {
        Assert-DockerReady
        Invoke-DockerStep "Build the test image" @("compose", "--profile", "ingestion", "build", "ingestion")
        Invoke-DockerStep "Run all 24 automated tests" @(
            "compose", "--profile", "ingestion", "run", "--rm", "--no-deps",
            "--entrypoint", "python", "ingestion", "-m", "unittest", "discover",
            "-s", "/app/tests", "-v"
        )
        Write-Host "All automated tests passed." -ForegroundColor Green
    }

    "status" {
        Assert-DockerReady
        Invoke-DockerStep "Show service status" @("compose", "--profile", "orchestration", "ps")
    }

    "stop" {
        Assert-DockerReady
        Invoke-DockerStep "Stop services without deleting data" @("compose", "--profile", "orchestration", "stop")
        Write-Host "Services stopped. Docker volumes and database data were preserved." -ForegroundColor Green
    }

    default {
        Write-Host "E-commerce pipeline demo helper" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Run from the repository root:"
        Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 start"
        Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 open"
        Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 test"
        Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 status"
        Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 stop"
        Write-Host ""
        Write-Host "Read docs\BEGINNER_GUIDE_AR.md for the full Arabic walkthrough."
    }
}

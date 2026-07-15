# Complete setup script for Windows PowerShell

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Quiz Bot Setup Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env and add your BOT_TOKEN and ADMIN_IDS" -ForegroundColor Red
    Write-Host "Press any key to open .env in notepad..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    notepad .env
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Docker services" -ForegroundColor Red
    Write-Host "Make sure Docker Desktop is running" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Docker services started" -ForegroundColor Green
Write-Host ""

Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "Running database migrations..." -ForegroundColor Yellow
docker-compose exec -T bot alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migrations complete" -ForegroundColor Green
} else {
    Write-Host "⚠️  Migration may have failed - check logs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Seeding questions..." -ForegroundColor Yellow
docker-compose exec -T bot python scripts/seed_questions.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Questions seeded" -ForegroundColor Green
} else {
    Write-Host "⚠️  Seeding may have failed - check logs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your bot is running!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Find your bot on Telegram" -ForegroundColor White
Write-Host "2. Send /start to begin" -ForegroundColor White
Write-Host "3. Create a room and play!" -ForegroundColor White
Write-Host ""
Write-Host "View logs: docker-compose logs -f bot" -ForegroundColor Cyan
Write-Host "Stop bot: docker-compose down" -ForegroundColor Cyan
Write-Host ""

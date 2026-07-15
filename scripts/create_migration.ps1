# Create initial database migration for PowerShell

Write-Host "Creating initial database migration..." -ForegroundColor Green
alembic revision --autogenerate -m "Initial migration"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration created successfully!" -ForegroundColor Green
    Write-Host "To apply migration, run: alembic upgrade head" -ForegroundColor Yellow
} else {
    Write-Host "Failed to create migration" -ForegroundColor Red
    exit 1
}

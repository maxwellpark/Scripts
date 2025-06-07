$projectRoot = 'C:\Code\'
$mediaRoot = Join-Path $projectRoot 'media'

$mediaFiles = Get-ChildItem -Path $mediaRoot -Recurse -File |
    ForEach-Object { $_.FullName.ToLower() }

$referencedAssets = Get-Content "$projectRoot\asset_references_with_context.txt" |
    ForEach-Object {
        $parts = $_ -split ":", 3
        if ($parts.Count -eq 3) {
            $asset = $parts[2].Trim().ToLower()
            $asset = $asset -replace '^[\\/]*media[\\/]*', ''
            $asset
        }
    } | Sort-Object -Unique

$missingAssets = @()

foreach ($asset in $referencedAssets) {
    if (-not ($mediaFiles | Where-Object { $_ -like "*\$asset" })) {
        $missingAssets += $asset
    }
}

$missingAssets | Sort-Object | Out-File "$projectRoot\missing_assets.txt" -Encoding utf8
Write-Host "written to missing_assets.txt"

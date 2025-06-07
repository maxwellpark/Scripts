$projectRoot = 'C:\Code\'
$mediaRoot = Join-Path $projectRoot 'media'

$mediaFilesSet = @{}
Get-ChildItem -Path $mediaRoot -Recurse -File | ForEach-Object {
    $relative = $_.FullName.Substring($mediaRoot.Length).TrimStart('\', '/')
    $normalized = $relative.Replace('\', '/').ToLower().Trim()
    $mediaFilesSet[$normalized] = $true
}

$referencedAssets = Get-Content "$projectRoot\asset_references_with_context.txt" |
    ForEach-Object {
        $parts = $_ -split ":", 3
        if ($parts.Count -eq 3) {
            $asset = $parts[2].Trim().ToLower()
            $asset = $asset -replace '^[\\/]*media[\\/]*', ''
            $asset.Replace('\', '/').Trim()
        }
    } | Sort-Object -Unique

$missingAssets = @()

foreach ($asset in $referencedAssets) {
    if (-not $mediaFilesSet.ContainsKey($asset)) {
        $missingAssets += $asset
    }
}

$missingAssets | Sort-Object | Out-File "$projectRoot\missing_assets.txt" -Encoding utf8
Write-Host "written to missing_assets.txt"

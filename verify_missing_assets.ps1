$projectRoot = 'C:\Code\'
$mediaRoot = Join-Path $projectRoot 'media'
$missingListPath = "$projectRoot\missing_assets.txt"

$missingAssets = Get-Content $missingListPath | ForEach-Object {
    $_.Replace('\', '/').ToLower().Trim()
}

$mediaFiles = Get-ChildItem -Path $mediaRoot -Recurse -File |
    ForEach-Object {
        $relative = $_.FullName.Substring($mediaRoot.Length).TrimStart('\', '/')
        $relative.Replace('\', '/').ToLower().Trim()
    }

$confirmedMissing = @()
$falsePositives = @()

foreach ($asset in $missingAssets) {
    if ($mediaFiles -contains $asset) {
        $falsePositives += $asset
    } else {
        $confirmedMissing += $asset
    }
}

$confirmedMissing | Sort-Object | Out-File "$projectRoot\confirmed_missing_assets.txt" -Encoding utf8
$falsePositives | Sort-Object | Out-File "$projectRoot\false_positives_in_missing_assets.txt" -Encoding utf8

Write-Host "confirmed missing: $($confirmedMissing.Count)"
Write-Host "false positives removed: $($falsePositives.Count)"

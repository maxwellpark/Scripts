$logPath = "game.log"
$pattern = 'Image load FAILED: (.+)'
$missingFiles = Select-String -Path $logPath -Pattern $pattern | ForEach-Object {
    if ($_ -match $pattern) {
        return $matches[1]
    }
}
$missingFiles | Sort-Object -Unique

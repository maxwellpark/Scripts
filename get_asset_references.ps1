$basePath = "C:\Code\"

Get-ChildItem -Recurse -Include *.lua, *.rml, *.rcss -File -Path $basePath |
    Select-String -Pattern '\b[^"''\s]+\.(png|jpg|jpeg|ogg|mp3|ttf|webp|gif)\b' -AllMatches |
    ForEach-Object {
        $relativePath = $_.Path.Replace($basePath, "")
        foreach ($match in $_.Matches) {
            "${relativePath}:${($_.LineNumber)}:$($match.Value)"
        }
    } | Out-File -Encoding utf8 asset_references_with_context.txt

$basePath = "C:\Code\"

$assetPattern = '\b[^"''\s]+\.(blend|blend1|cam|cfg|cg|dds|exr|fbx|font|fontdef|frag|gcpu|gif|hlsl|htm|html|jpg|jpeg|json|lua|material|mesh|mtl|nav|otf|png|program|rcss|rml|scene|tga|ttf|twk|txt|vert|xcf|xls|xml)\b'
Get-ChildItem -Recurse -Include *.lua, *.rml, *.rcss -File -Path $basePath |
    Select-String -Pattern $assetPattern -AllMatches |
    ForEach-Object {
        $relativePath = $_.Path.Replace($basePath, "")
        foreach ($match in $_.Matches) {
            "${relativePath}:${($_.LineNumber)}:$($match.Value)"
        }
    } | Out-File -Encoding utf8 asset_references_with_context.txt

Write-Host "written to asset_references_with_context.txt"

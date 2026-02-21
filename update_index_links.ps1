$files = Get-ChildItem -Path docs -Recurse -Filter *.md

foreach ($f in $files) {
    if ($f.Name -match "INDEX.md") { continue }
    
    $content = Get-Content -Path $f.FullName -Raw
    if ($content -notmatch "Voltar ao Índice" -and $content -notmatch "Voltar para o Índice") {
        $parts = $f.FullName.Substring($PWD.Path.Length + 1) -split "\\|/"
        $depth = $parts.Count - 2
        $prefix = ""
        if ($depth -gt 0) {
            for ($i = 0; $i -lt $depth; $i++) { $prefix += "../" }
        } else {
            $prefix = "./"
        }
        
        $link = "
---

[ Voltar ao Índice]($($prefix)INDEX.md)
"
        Add-Content -Path $f.FullName -Value $link -Encoding UTF8
        Write-Host "Updated $($f.FullName)"
    }
}

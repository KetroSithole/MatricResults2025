$downloadsPath = "C:\Users\ketro\Downloads"

Get-ChildItem -Path $downloadsPath -File | ForEach-Object {

    if ([string]::IsNullOrWhiteSpace($_.Extension)) {
        return
    }

    $extension = $_.Extension.TrimStart('.').ToUpper()
    $targetFolder = Join-Path $downloadsPath $extension

    if (-not (Test-Path $targetFolder)) {
        New-Item -ItemType Directory -Path $targetFolder | Out-Null
    }

    Move-Item -Path $_.FullName -Destination $targetFolder -Force
}

[CmdletBinding()]
param(
    [ValidateNotNullOrEmpty()]
    [string]$Version = "0.1.14",

    [ValidateNotNullOrEmpty()]
    [string]$ReleaseRoot = "https://azdaja.dev/releases",

    [ValidateNotNullOrEmpty()]
    [string]$InstallDir = (Join-Path $env:LOCALAPPDATA "Programs\Azdaja"),

    [switch]$NoPathUpdate
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Assert-NoReparsePoint {
    param([Parameter(Mandatory = $true)][string]$Path)

    $full = [System.IO.Path]::GetFullPath($Path)
    $root = [System.IO.Path]::GetPathRoot($full)
    if ([string]::IsNullOrEmpty($root)) {
        throw "path has no filesystem root: $Path"
    }

    $current = $root
    $relative = $full.Substring($root.Length)
    foreach ($part in ($relative -split '[\\/]' | Where-Object { $_ -ne "" })) {
        $current = Join-Path $current $part
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "refusing reparse-point install path: $current"
            }
        }
    }
}

function Copy-ReleasePayload {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if ($null -ne $script:LocalVersionRoot) {
        $source = Join-Path $script:LocalVersionRoot $Name
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
            throw "release payload is missing: $source"
        }
        Copy-Item -LiteralPath $source -Destination $Destination
        return
    }

    $uri = "$($script:RemoteVersionRoot)/$Name"
    Invoke-WebRequest -UseBasicParsing -Uri $uri -OutFile $Destination
}

$architecture = $env:PROCESSOR_ARCHITEW6432
if ([string]::IsNullOrEmpty($architecture)) {
    $architecture = $env:PROCESSOR_ARCHITECTURE
}
if ($architecture -ne "AMD64") {
    throw "Azdaja currently supports Windows x86-64 only; detected $architecture"
}

$asset = "azdaja-v$Version-windows-x86_64.exe"
$script:LocalVersionRoot = $null
$script:RemoteVersionRoot = $null
if (Test-Path -LiteralPath $ReleaseRoot -PathType Container) {
    $script:LocalVersionRoot = Join-Path ([System.IO.Path]::GetFullPath($ReleaseRoot)) "v$Version"
    Assert-NoReparsePoint $script:LocalVersionRoot
    if (-not (Test-Path -LiteralPath $script:LocalVersionRoot -PathType Container)) {
        throw "release directory is missing: $script:LocalVersionRoot"
    }
} else {
    $releaseUri = $null
    if (-not [System.Uri]::TryCreate($ReleaseRoot, [System.UriKind]::Absolute, [ref]$releaseUri)) {
        throw "ReleaseRoot must be an existing directory or an absolute URI"
    }
    if ($releaseUri.Scheme -ne "https" -and -not $releaseUri.IsLoopback) {
        throw "remote releases require HTTPS unless the host is loopback"
    }
    $script:RemoteVersionRoot = "$($ReleaseRoot.TrimEnd('/'))/v$Version"
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("azdaja-install-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempRoot | Out-Null
try {
    $sumsPath = Join-Path $tempRoot "SHA256SUMS"
    $binaryPath = Join-Path $tempRoot $asset
    Copy-ReleasePayload "SHA256SUMS" $sumsPath

    $expected = @()
    foreach ($line in [System.IO.File]::ReadAllLines($sumsPath)) {
        if ($line -match '^([0-9a-fA-F]{64})[ \t][ \t]+(.+)$' -and $Matches[2] -ceq $asset) {
            $expected += $Matches[1].ToLowerInvariant()
        }
    }
    if ($expected.Count -ne 1) {
        throw "SHA256SUMS must contain exactly one checksum for $asset"
    }

    Copy-ReleasePayload $asset $binaryPath
    $actual = (Get-FileHash -LiteralPath $binaryPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -cne $expected[0]) {
        throw "checksum mismatch for $asset"
    }

    $bytes = [System.IO.File]::ReadAllBytes($binaryPath)
    if ($bytes.Length -lt 64 -or $bytes[0] -ne 0x4d -or $bytes[1] -ne 0x5a) {
        throw "downloaded payload is not a PE executable"
    }
    $peOffset = [System.BitConverter]::ToInt32($bytes, 0x3c)
    if ($peOffset -lt 0 -or $peOffset + 6 -gt $bytes.Length) {
        throw "downloaded PE header is truncated"
    }
    if ($bytes[$peOffset] -ne 0x50 -or $bytes[$peOffset + 1] -ne 0x45 -or
        $bytes[$peOffset + 2] -ne 0 -or $bytes[$peOffset + 3] -ne 0) {
        throw "downloaded payload has an invalid PE signature"
    }
    if ([System.BitConverter]::ToUInt16($bytes, $peOffset + 4) -ne 0x8664) {
        throw "downloaded payload is not Windows x86-64"
    }

    $probe = (& $binaryPath --version 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $probe -notmatch "^azdaja $([regex]::Escape($Version))(?: |$)") {
        throw "downloaded binary failed the exact version probe: $probe"
    }

    $installFull = [System.IO.Path]::GetFullPath($InstallDir)
    Assert-NoReparsePoint $installFull
    if (Test-Path -LiteralPath $installFull -PathType Leaf) {
        throw "install directory is a file: $installFull"
    }
    New-Item -ItemType Directory -Path $installFull -Force | Out-Null
    Assert-NoReparsePoint $installFull

    $destination = Join-Path $installFull "azdaja.exe"
    Assert-NoReparsePoint $destination
    if (Test-Path -LiteralPath $destination -PathType Container) {
        throw "install destination is a directory: $destination"
    }

    $stage = Join-Path $installFull (".azdaja-stage-" + [guid]::NewGuid().ToString("N") + ".exe")
    $backup = Join-Path $installFull (".azdaja-backup-" + [guid]::NewGuid().ToString("N") + ".exe")
    try {
        Copy-Item -LiteralPath $binaryPath -Destination $stage
        if (Test-Path -LiteralPath $destination -PathType Leaf) {
            [System.IO.File]::Replace($stage, $destination, $backup, $true)
            Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
        } else {
            [System.IO.File]::Move($stage, $destination)
        }
    } finally {
        Remove-Item -LiteralPath $stage -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $backup -Force -ErrorAction SilentlyContinue
    }

    $installedProbe = (& $destination --version 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $installedProbe -notmatch "^azdaja $([regex]::Escape($Version))(?: |$)") {
        throw "installed binary failed the exact version probe: $installedProbe"
    }

    $pathAdded = $false
    if (-not $NoPathUpdate) {
        try {
            $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
            if ($null -eq $userPath) {
                $userPath = ""
            }
            $normalizedInstall = $installFull.TrimEnd('\')
            $alreadyPresent = $false
            foreach ($entry in ($userPath -split ';')) {
                if ($entry.Trim().TrimEnd('\') -ieq $normalizedInstall) {
                    $alreadyPresent = $true
                    break
                }
            }
            if (-not $alreadyPresent) {
                $newPath = $normalizedInstall
                if (-not [string]::IsNullOrWhiteSpace($userPath)) {
                    $newPath = $userPath.TrimEnd(';') + ';' + $normalizedInstall
                }
                [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
                $pathAdded = $true
            }
            if (-not (($env:Path -split ';') | Where-Object { $_.Trim().TrimEnd('\') -ieq $normalizedInstall })) {
                $env:Path = $env:Path.TrimEnd(';') + ';' + $normalizedInstall
            }
        } catch {
            Write-Warning "Installed Azdaja, but could not update the user PATH: $($_.Exception.Message)"
        }
    }

    Write-Output "Installed azdaja $Version to $destination"
    if ($pathAdded) {
        Write-Output "Added $installFull to the user PATH; open a new terminal."
    } elseif ($NoPathUpdate) {
        Write-Output "PATH was not changed; add $installFull manually if needed."
    }
    Write-Output "Run: azdaja --version"
} finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}

param(
  [Parameter(Mandatory=$true)][string]$Seq,
  [Parameter(Mandatory=$true)][string]$Out,
  [int]$delayCs = 5,
  [int]$MaxW = 0,      # 0 = keep original size
  [int]$Stride = 1     # take every Nth frame
)
Add-Type -AssemblyName System.Drawing

$all = Get-ChildItem -Path $Seq -Filter "petal_*.png" | Sort-Object Name
$files = @()
for ($i = 0; $i -lt $all.Count; $i += $Stride) { $files += $all[$i] }
$n = $files.Count
$effDelay = $delayCs * $Stride

function Load-Frame([string]$path) {
  $img = [System.Drawing.Image]::FromFile($path)
  if ($MaxW -gt 0 -and $img.Width -gt $MaxW) {
    $h = [int]($img.Height * $MaxW / $img.Width)
    $bmp = New-Object System.Drawing.Bitmap($MaxW, $h)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.DrawImage($img, 0, 0, $MaxW, $h)
    $g.Dispose(); $img.Dispose()
    return $bmp
  }
  return $img
}

$gif = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/gif' }
$Encoder = [System.Drawing.Imaging.Encoder]::SaveFlag
$EV = [System.Drawing.Imaging.EncoderValue]
$ctor = [System.Drawing.Imaging.PropertyItem].GetConstructor([System.Reflection.BindingFlags]'Instance,NonPublic', $null, @(), $null)

$delayBytes = New-Object byte[] (4 * $n)
for ($i = 0; $i -lt $n; $i++) { $delayBytes[$i * 4] = [byte]$effDelay }
$piDelay = $ctor.Invoke(@()); $piDelay.Id = 0x5100; $piDelay.Type = 4; $piDelay.Len = $delayBytes.Length; $piDelay.Value = $delayBytes
$piLoop = $ctor.Invoke(@()); $piLoop.Id = 0x5101; $piLoop.Type = 3; $piLoop.Len = 2; $piLoop.Value = [byte[]](0, 0)

$first = Load-Frame $files[0].FullName
$first.SetPropertyItem($piDelay); $first.SetPropertyItem($piLoop)
$epMulti = New-Object System.Drawing.Imaging.EncoderParameters(1)
$epMulti.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter($Encoder, [long]$EV::MultiFrame)
$first.Save($Out, $gif, $epMulti)

$epPage = New-Object System.Drawing.Imaging.EncoderParameters(1)
$epPage.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter($Encoder, [long]$EV::FrameDimensionTime)
for ($i = 1; $i -lt $n; $i++) {
  $img = Load-Frame $files[$i].FullName
  $first.SaveAdd($img, $epPage)
  $img.Dispose()
}
$epFlush = New-Object System.Drawing.Imaging.EncoderParameters(1)
$epFlush.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter($Encoder, [long]$EV::Flush)
$first.SaveAdd($epFlush)
$first.Dispose()

$sz = [math]::Round((Get-Item $Out).Length / 1MB, 2)
"GIF: $Out  frames=$n  ${sz}MB"

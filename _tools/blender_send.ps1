param(
  [Parameter(Mandatory=$true)][string]$CodeFile,
  [int]$TimeoutMs = 180000
)
$code = [System.IO.File]::ReadAllText($CodeFile)
$payload = @{ type = "execute_code"; params = @{ code = $code } } | ConvertTo-Json -Depth 6 -Compress
$client = New-Object System.Net.Sockets.TcpClient
$client.Connect('127.0.0.1', 9876)
$stream = $client.GetStream()
$stream.ReadTimeout = $TimeoutMs
$bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
$stream.Write($bytes, 0, $bytes.Length)
$stream.Flush()
$ms = New-Object System.IO.MemoryStream
$buffer = New-Object byte[] 16384
# blocking first read (waits while Blender executes)
$n = $stream.Read($buffer, 0, $buffer.Length)
$ms.Write($buffer, 0, $n)
Start-Sleep -Milliseconds 150
while ($stream.DataAvailable) {
  $n = $stream.Read($buffer, 0, $buffer.Length)
  if ($n -le 0) { break }
  $ms.Write($buffer, 0, $n)
  Start-Sleep -Milliseconds 50
}
$client.Close()
[System.Text.Encoding]::UTF8.GetString($ms.ToArray())

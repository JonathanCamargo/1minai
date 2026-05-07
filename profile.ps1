Write-Output "Loaded functions"
Write-Output "------------------------------------"
Write-Output "q : ask questions to the 1minai api"
function global:q { python C:\git\1minai\scripts\q.py @args }
Write-Output "sum : sumarize files with the 1minai api"
function global:sum { python C:\git\1minai\scripts\sum.py @args }


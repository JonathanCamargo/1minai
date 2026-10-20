Write-Output "Loaded functions"
Write-Output "------------------------------------"
Write-Output "q : ask questions to the 1minai api"
function global:q { python C:\git\1minai\scripts\q.py @args }
Write-Output "sum : sumarize files with the 1minai api"
function global:sum { python C:\git\1minai\scripts\sum.py @args }

Write-Output "paper : analyze scientific papers (pdf/url) with the 1minai api"
function global:paper { python C:\git\1minai\scripts\paper.py @args }
Write-Output "models : list live 1minai chat models with context and price"
function global:models { python C:\git\1minai\scripts\models.py @args }

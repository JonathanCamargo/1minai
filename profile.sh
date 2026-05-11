echo "Loaded functions"
echo "------------------------------------"
echo "q : ask questions to the 1minai api"
q() { "$(dirname "${BASH_SOURCE[0]}")/scripts/q.py" "$@"; }
echo "sum : sumarize files with the 1minai api"
sum() { "$(dirname "${BASH_SOURCE[0]}")/scripts/sum.py" "$@"; }

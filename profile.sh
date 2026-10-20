echo "Loaded functions"
echo "------------------------------------"
echo "q : ask questions to the 1minai api"
_1MINAI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
q() { "$_1MINAI_ROOT/scripts/q.py" "$@"; }
echo "sum : sumarize files with the 1minai api"
sum() { "$_1MINAI_ROOT/scripts/sum.py" "$@"; }

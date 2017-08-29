findall() {
    IFS="|"
    declare -i found=0
    for pat in $f;
    do
        find . -iregex ".*$pat.*"
    done
}
        
grep -v '^$' | while read f
do 
    OIFS="$IFS"
    IFS="|"
    declare -i found=0
    found=$(findall $f | sort -u | wc -l)
    echo "$found $f"
done | sort -rgk 1

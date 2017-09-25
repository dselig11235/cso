grep -v '^$' files | while read f
do 
    found=$(find . -iregex ".*$f.*" | wc -l)
    if test $found -eq 0
    then 
        echo $f
    fi
done

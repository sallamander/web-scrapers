year=$1

if [ -z $year ]; then 
    echo "<Usage>: Input a year to get music data for" >&2
    exit 1
fi

if [ $year -eq 2015 ]; then 
    echo "Year is 2015"
else
    echo "Year is not 2015"
fi 


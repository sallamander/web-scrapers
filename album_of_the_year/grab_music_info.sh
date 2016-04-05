year=$1

if [ -z $year ]; then 
    echo "<Usage>: Input a year to get music data for" >&2
    exit 1
fi

if [ $year -eq 2015 ]; then 
    python albums_of_the_year_lst_ind.py 2015
    python albums_of_the_year_lst_full.py 2015
    python end_year_critic_lists.py 
else
    python albums_of_the_year_lst_ind.py $year
    python albums_of_the_year_lst_full.py $year
fi 


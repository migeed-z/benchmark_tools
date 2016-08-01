qstat -u bengree | awk '{if ($1 == "1661991.m2") print $9;}'



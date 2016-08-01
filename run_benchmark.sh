
# ELAP_TIME=$( qstat -u bengree | awk '{if ($1 == "1661991.m2") print $11;}' )
ELAP_TIME=$( cat 'SAMPLE_QSTAT.txt' | awk '{if ($1 == "1661991.m2") print $11;}' )

echo ${ELAP_TIME}

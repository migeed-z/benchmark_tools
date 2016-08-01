
# ELAP_TIME=$( qstat -u bengree | awk '{if ($1 == "1661991.m2") print $11;}' )
ELAP_TIME=$( cat 'SAMPLE_QSTAT.txt' | awk '{if ($1 == "1661991.m2") print $11;}' )
TIME_TO_STOP="23:00:00"

if [ ${ELAP_TIME} \> ${TIME_TO_STOP} ]; then
  echo "STOP RUNNING CONFIGS"
else
  echo "PICK AND RUN A CONFIG"
fi

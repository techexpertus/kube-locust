#!/bin/bash

LOCUST_CMD="locust"
LOCUST_OPTS="-f $SCENARIO_FILE -H $TARGET_HOST $LOCUSTS"
LOCUST_MODE=${LOCUST_MODE:-standalone}

if [ "$LOCUST_MODE" = "master" ]; then
  LOCUST_OPTS="$LOCUST_OPTS --master"
elif [ "$LOCUST_MODE" = "worker" ]; then
  LOCUST_OPTS="$LOCUST_OPTS --slave --master-host=$LOCUST_MASTER"
fi

echo "=> Starting locust"
echo "$LOCUST_CMD $LOCUST_OPTS"

$LOCUST_CMD $LOCUST_OPTS

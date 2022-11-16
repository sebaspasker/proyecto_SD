#!/bin/bash
KAFKA_HOME=$KAFKA_HOME:../bin
JAVA_HOME=$JAVA_HOME:../bin

./bin/kafka_2.12-3.3.1/bin/zookeeper-server-start.sh ./bin/kafka_2.12-3.3.1/config/zookeeper.properties > ./logs/zookeeper.log 2> logs/error_zookeeper.log &

echo "RUNNING ZOOKEEPER"
echo "WAIT TWO SECONDS..."
sleep 2

./bin/kafka_2.12-3.3.1/bin/kafka-server-start.sh ./bin/kafka_2.12-3.3.1/config/server.properties > ./logs/kafka_server.log 2> logs/error_kafka.log &
sleep 2
echo "RUNNING KAFKA"

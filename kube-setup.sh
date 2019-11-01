#!/usr/bin/env bash

python locust-cluster.py pushlatest --project kube-perf
python locust-cluster.py create --project kube-perf
python locust-cluster.py deploy -f/kubernetes-config/locust-master-controller.yaml -f/kubernetes-config/locust-master-service.yaml -f/kubernetes-config/locust-worker-controller.yaml
#python locust-cluster.py delete -f/kubernetes-config/locust-master-controller.yaml -f/kubernetes-config/locust-master-service.yaml -f/kubernetes-config/locust-worker-controller.yaml --cluster-name kube-locust

##**Debugging locust script on local machine**

Locust scripts can be debug like other python programs in pycharm editor/IntelliJ ultimate edition editor
File debuglocust.py acts as entry point for debugging locust script. In addition, the local computer also needs to have installed all the python package requirements for locust.

####**To install locust on localmachine**
Using pip and the  requirements file, installation is straight forward. Run below pip command
```bash
pip install -r requirements.txt
```
requirements.txt file can be found in root directory 

Once all packages are installed successfully, create run configuration using below paratemers in pycharm/intellij
```text
Script:path to debuglocust.py
Script parameters: -H https://targethost -f locusts.py  RDLocust
```
Place break point and run the configuration. This brings up the locust web running on localhost:8089.
Open the web front end and enter number user/rampup rate as 1/1 and click start. Then the script will stop at the breakpoint for further debugging

##**How to deploy locust onto new kubernetes cluster?**

1. Build image locally and push to project gcr.

```bash
python locust-cluster.py pushlatest --project  kube-perf --container locust 
```

2. Create cluster by providing project name. This will create cluster with default name kube-locust.   

```bash
python locust-cluster.py create --project kube-perf
 
 # If name of cluster needs to be different, then command can accept clustername as below
python locust-cluster.py create --project kube-perf --cluster-name `nameofthecluster` 
```
3. Deploy master node of locust and wait for few minutes so master is up and running. Deploy command also creates firewall rule
```bash
python locust-cluster.py deploy \
    -f/kubernetes-config/locust-master-controller.yaml \
    -f/kubernetes-config/locust-master-service.yaml 
```
4. Deploy worker nodes by running below command
```bash
python locust-cluster.py deploy \
    -f/kubernetes-config/locust-worker-controller.yaml
```
5. Deploy firewall rule so that locust master can be accessed from the machines
```bash
python locust-cluster.py deploy --firewall-rule locustweb
```

##**How to delete the kubernetes cluster?**

Run below command to delete the cluster. Along with cluster,firewall rules also need to be deleted, so the clean up is done
```bash
python locust-cluster.py delete --cluster-name kube-locust --firewall-rule locustweb
```

##**How to push updated script to locust kubernetes cluster?**

Say if the locust script is been modified and this change needs to be reflected in kubernetes cluster. 
To achieve this, the  image needs to be pushed to gcr repo and then the pods need to be restarted

1. Push the latest image by running below command
```bash
python locust-cluster.py pushlatest --project kube-perf --container locust 
```
2. Now image being pushed, does not get updated to kubernetes cluster. For this cluster has to be updated.
 - Delete the kubernetes files.
    Run below command to delete master first and wait for few minutes

    ```bash
    python locust-cluster.py delete \
        -f/kubernetes-config/locust-master-controller.yaml \
        -f/kubernetes-config/locust-master-service.yaml 
    ```
    Next run the command to delete workers and wait for few minutes
    
    ```bash
    python locust-cluster.py delete \
        -f/kubernetes-config/locust-worker-controller.yaml
    ```
- Deploy the files back
    Deploy master controller and service
    ```bash
    python locust-cluster.py deploy \
        -f/kubernetes-config/locust-master-controller.yaml \
        -f/kubernetes-config/locust-master-service.yaml 
    ```
    Deploy workers
        
    ```bash
    python locust-cluster.py deploy \
        -f/kubernetes-config/locust-worker-controller.yaml


##**Resolve issue of number of slaves not appearing as expected?**

Sometime, the number of slaves or worker nodes connected to master do not appear right. This is because locust seem to be doing registration of node at the startup and doesn't continuously check.
For this refresh the master and wait for sometime. then refresh the workers nodes using below commands

```bash
python locust-cluster.py refresh --master
```
Wait for some time so that master is reflected with zero slaves.Next run the below command to refresh workers

```bash
python locust-cluster.py refresh --workers
```

##**How to increase number of worker nodes on kubernetes cluster**
Change the replica values in locust-worker-controller.yaml to the desired number.
Then run the commands mentioned in section `How to push updated script to locust kubernetes cluster`


##**How to run docker-compose cluster locally with additional monitoring?**

Additional monitoring feature helps to capture all response time values into influxdb via statsd. The visualisation of the data can be seen in grafana

1. Build locust image by running below docker-compose command
```bash
docker-compose build

```
2. Bring up the docker-compose environment by running below command
```bash
TARGET_HOST=https://targethost docker-compose up
```
TARGET_HOST is the environment variable containing the environment that is been targeted by locust for load testing
As per the configuration on docker-compose file, this brings up locust with a master and a node. Besides it brings up the containers for influxdb, graphana which capture the data from additional monitoring.

3. Once the docker-compose is up and running, open below urls to open up locust, grafana

http://localhost:8089 # to open to locust web interface and to initiate load test

http://localhost:3000 # to open the grafana ui and view response time values

4. To bring down the environment run below docker-compose command
```bash
docker-compose down
```

##**How to specify which locust class to run**

Locust file has classes that defines a taskset (actions that locust perfom) and wait settings for corresponding tasksets.
At sometimes, it may be required to run one or some of the Locust tasksets, and not all those defined in the locust file. Locust accepts commandline arguments so that it runs particular Locust classes

Example: Locust file has two below taskset
```text
class RDLocust(HttpLocust):
    task_set = RDTask
    min_wait = 50
    max_wait = 100


class STALocust(HttpLocust):
    task_set = STATasks
    min_wait = 5000
    max_wait = 15000

```
the name of class of desired locust should be passed as arguement. 

#### How to pass it to local debugging

Below agruments for a locust debug configuration says it to run only RDLocust
```bash
-H https://targethost -f locusts.py  RDLocust
```
#### How to pass it to distributed execution of locust on kubernetes 
Create below environment variable that get passed onto docker container both master and worker.Startup script of the docker container, uses this to start locust command appropriately

```text
            - name: LOCUSTS
              key: LOCUSTS
              value: RDLocust

```

#### How to pass it in docker compose file
Pass the environment variable in dockercompose master and worker container as below
```text
          LOCUSTS: RDLocust
```


##**How to open locust cluster dashboard and retrieve the locust master web url**

Go to kube-perf project -> Container Engine ->Container Cluster -> kube-locust . Click connect which brings with two commands as below
```bash
gcloud container clusters get-credentials kube-locust --zone europe-west1-d --project kube-perf
kubectl proxy

```
By running open two commands, kubernetes dashboard for this cluster can be accessed using below link
http://localhost:8001/ui

In the dashboard, click on Services.  In the column, external endpoints against row locust master, there will three urls listed.
The url that is accessing port 8089 is the url for accessing the web end of locust

```text
#for example as below
35.187.84.203:8089
```

##**How to deploy locust on kubernetes with extra monitoring**

1. Change the value environment variable EXTRA_MONITORING to "True" in kubernetes files   
            kubernetes-config/locust-master-controller.yaml
            kubernetes-config/locust-worker-controller.yaml
            
2. Push the latest statds container if it has not been already pushed.
```bash
    python locust-cluster.py pushlatest --container statsd --project kube-perf
```
3. Deploy below files and do not deploy worker yet
```bash
python locust-cluster.py deploy \
            -f/kubernetes-config/grafana-deployment.yaml
            -f/kubernetes-config/grafana-service.yaml
            -f/kubernetes-config/influxdb-deployment.yaml
            -f/kubernetes-config/influxdb-service.yaml
            -f/kubernetes-config/locust-master-controller.yaml
            -f/kubernetes-config/locust-master-service.yaml
            -f/kubernetes-config/statsd-deployment.yaml
            -f/kubernetes-config/statsd-service.yaml
```
4. After waiting for a minute, deploy locust worker now

```bash
python locust-cluster.py deploy -f/kubernetes-config/locust-worker-controller.yaml
```

6. Open locust as menitoned in section "How to open locust cluster dashboard and retrieve the locust master web url"

7. To open grafana , run below kubectl portforwarding and open the localhost:3000. User credentials from the locust kubernetes files
```bash
kubectl port-forward <podnameofgrafana> 3000
```

8. To open influxdb , run below kubectl portforwarding and open the localhost:8083. User credentials from the locust kubernetes files
```bash
kubectl port-forward <podnameofgrafana> 8083
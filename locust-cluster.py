import logging
import os

from plumbum import cli, local, TEE,colors

logger = logging.getLogger()
docker = local["docker"]
kubectl = local["kubectl"]
gcloud = local["gcloud"]

info = colors.rgb(100,0,150)

class Cluster(cli.Application):
    def main(self, *args):
        if args:
            print("Unknown command {0!r}".format(args[0]))
            return 1  # error exit code
        if not self.nested_command:  # will be ``None`` if no sub-command follows
            print("No command given")
            return 1  # error exit code


@Cluster.subcommand("pushlatest")
class CreateTag(cli.Application):
    """Pushes the image to google registry"""

    @cli.switch("--project", str, mandatory=True)
    def gce_project(self, gceProject):
        """Set the google cloud project"""
        self.project = gceProject


    @cli.switch("--container", str, mandatory=True)
    def gce_container(self, container):
        """Container to be pushed- Allowed values are locust or statsd
             For locust docker file from root directory is used
             For statsd docker file from additionalmonitoring/statsd is used
        """
        if container == 'locust':
            self.containername = "kube-locust"
            self.buildpath = "."
            return
        if container == 'statsd':
            self.containername = "statsd"
            self.buildpath = "additionalmonitoring/statsd"
            return
        print(info | "invalid container name- Allowed values are locust or statsd")


    def main(self):
        if self.containername:
            self.gcrTag = "eu.gcr.io/" + self.project + "/" + self.containername
            print(info | "Creation of tagged containter image")
            print(info | "Building docker image from path " + self.buildpath )
            docker["build", "-t", "kube/" + self.containername, self.buildpath] & TEE()
            print(info | "Tagging the image")
            docker["tag", "kube/" + self.containername, self.gcrTag] & TEE()
            print(info | "Pushing the image to " + self.gcrTag)
            gcloud["docker", "--project", self.project, "--", "push", self.gcrTag] & TEE()
            print(info | "Done pushing image to gcr")


@Cluster.subcommand("create")
class Create(cli.Application):
    "Creates cluster in the gce project"
    clusterName = "kube-locust"

    @cli.switch("--cluster-name", str)
    def gce_clustername(self, clusterName):
        """Name of the kubernetes cluster"""
        self.clusterName = clusterName

    @cli.switch("--project", str, mandatory=True)
    def gce_project(self, gceProject):
        """Set the google cloud project"""
        self.project = gceProject

    def main(self):
        print(info | "Setting google cloud project...")
        gcloud["config", "set", "project", self.project] & TEE()
        print(info | "Cluster creation " + self.clusterName)
        gcloud["container", "clusters", "create", self.clusterName, "--num-nodes=4"] & TEE()
        print(info | "Creation of cluster done")


@Cluster.subcommand("deploy")
class Deploy(cli.Application):
    "Deployes kubernetes files"

    @cli.switch(["-f", "--files"], str, list=True)
    def kube_deploy(self, files):
        """ kubernetes files that would be deployed.Format to specify a file -f/path-to-file"""
        for file in files:
            path = os.getcwd() + file
            print(info | "Deploying file" + path)
            kubectl["create", "-f", path, "--validate=false"] & TEE()


    @cli.switch("--firewall-rule",str)
    def firewallrule(self,rulename):
        """If given, firewall rule is created. If no value specified, rule name would be defaulted to locustweb"""

        if not rulename:
            rulename = "locustweb"

        #check if the firewall rule exists gcloud compute firewall-rules list | grep locustweb

        print(info | "existinng firewall rules")
        rcode, sout, serr =gcloud["compute","firewall-rules","list"] & TEE()

        for line in sout.splitlines():
            if rulename in line:
                print("Firewall rule already exists")
                return

        print(info | "creating firewall rule")
        gcloud["compute", "firewall-rules", "create", rulename, "--allow=tcp:8089"]()
        print(info | "firewall rule created")

    def main(self):
        print(info | "****")



@Cluster.subcommand("delete")
class Delete(cli.Application):
    "Deletes cluster and kubernetes files"

    @cli.switch(["-f", "--file"], str, list=True)
    def kube_deploy(self, files):
        """  kubernetes files that needs to be deleted. Format to specify a file -f/path-to-file"""
        for file in files:
            path = os.getcwd() + file
            print(info | "Deleting file" + path)
            kubectl["delete", "-f", path] & TEE()

    @cli.switch("--cluster-name", str)
    def gce_clustername(self, clusterName):
        """Name of the kubernetes cluster"""
        self.clusterName = clusterName
        print(info | "deleting cluster")
        gcloud["container", "clusters", "delete", "--quiet", self.clusterName] & TEE()

    @cli.switch("--firewall-rule", str)
    def gce_delete_firewall_rule(self, rulename):
        """ The firewall rule that needs deleting"""
        print(info | "deleting firewall rule")
        gcloud["compute", "firewall-rules", "delete", rulename] & TEE()
        print(info | "firewall rule deleted")

    def main(self):
        print(info | "****")


@Cluster.subcommand("refresh")
class Refresh(cli.Application):
    "refreshed pod and deployes kubernetes files"

    @cli.switch(["-f", "--files"], str, list=True)
    def kube_refresh(self, files):
        """ kubernetes files that would be deployed.Format to specify a file -f/path-to-file
        Note this is not currently working reliablly. Instead run delete and deploy commands to refresh kubernetes
        """
        for file in files:
            path = os.getcwd() + file
            print(info | "Deploying file" + path)
            kubectl["replace", "--force", "-f", path, "--validate=false"] & TEE()

    @cli.switch(["--workers"])
    def refresh_workers(self):
        """deletes pods with label as workers so they get restarted"""
        print(info | " Deleting pods so that they get restarted")
        kubectl["delete","pods","-l","role=worker"] & TEE()

    @cli.switch(["--master"])
    def refresh_master(self):
        """deletes pods with label as masster so they get restarted"""
        print(info | " Deleting pods so that they get restarted")
        kubectl["delete","pods","-l","role=master"] & TEE()

    def main(self):
        print(info | "****")


@Cluster.subcommand("set-cluster")
class SetClusterCredentials(cli.Application):
    """set cluster credentials so that kubectl commands work with the cluster"""
    zone = "europe-west1-d"

    @cli.switch("--cluster-name",str,mandatory=True)
    def cluster_name(self,clusterName):
        """Name of the cluster"""
        self.clusterName = clusterName

    @cli.switch("--project", str,mandatory=True)
    def project(self, project):
        """Name of the google project"""
        self.projectname = project

    @cli.switch("--zone",str)
    def zone_name(self,zone):
        """ Google cloud zone"""
        self.zone = zone

    def main(self):
        print(info | "setting credentials")
        gcloud["container","clusters","get-credentials",self.clusterName,"--zone",self.zone,"--project",self.projectname] & TEE()


if __name__ == "__main__":
    Cluster.run()

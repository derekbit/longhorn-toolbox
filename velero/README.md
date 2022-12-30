# Velero

## Deploy MinIO

1. Deploy MinIO service

2. Navigate to MinIO Console and create a credential

## Deploy Velero Service

1. Download Velero
    ```
    curl -L https://github.com/vmware-tanzu/velero/releases/download/v1.10.0/velero-v1.10.0-linux-amd64.tar.gz | tar zxvf - && cp -a velero-v1.10.0-linux-amd64/velero /usr/local/bin/
    ```

2. Install Velero
    ```
    ./install.sh
    ```

## Run backup
1. Create a PVC
    ```
    kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pvc-with-local-volume/pvc.yaml
    ```
2. Create a Pod using the PVC
    ```
    kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pod-with-local-volume/pod.yaml
    ```
3. Write some data in the volume

4. Back up the Longhorn volume
    ```
    velero backup create volume-backup --include-namespaces default --default-volumesfs-backup
    ```

5. Check backup status by `velero backup describe volume-backup`

## Run restore

1. Remove the Pod and PVC for simulating a disaster recovery

2. Restore from the backup by `velero restore create --from-backup volume-backup`

3. Check restore status by `velero restore get`. If the resotre succeeds, the check the data checksum.

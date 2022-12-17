# Velero

## Deploy MinIO

1. Deploy MinIO service

2. Navigate to MinIO Console and create a credential

## Deploy Velero Service

1. Download Velero
    ```
    curl -L https://github.com/vmware-tanzu/velero/releases/download/v1.9.4/velero-v1.9.4-linux-amd64.tar.gz | tar zxvf - && cp -a velero-v1.9.4-linux-amd64/velero /usr/local/bin/
    ```

2. Install Velero
    ```
    ./install.sh
    ```

## Run backup
1. Deploy Longhorn system

2. Create a Pod with PVC
    ```
    kubectl create -f ./pod_with_pvc.yaml
    ```

3. Back up the Longhorn volume
    ```
    # velero backup create myservice-backup --include-namespaces myservice --default-volumes-to-restic
     ```

4. Check backup status
    ```
    # velero backup describe myservice-backup
    Name:         myservice-backup
    Namespace:    velero
    Labels:       velero.io/storage-location=default
    Annotations:  velero.io/source-cluster-k8s-gitversion=v1.24.1+k3s1
                velero.io/source-cluster-k8s-major-version=1
                velero.io/source-cluster-k8s-minor-version=24

    Phase:  Completed

    Errors:    0
    Warnings:  0

    Namespaces:
    Included:  myservice
    Excluded:  <none>

    Resources:
    Included:        *
    Excluded:        <none>
    Cluster-scoped:  auto

    Label selector:  <none>

    Storage Location:  default

    Velero-Native Snapshot PVs:  auto

    TTL:  720h0m0s

    Hooks:  <none>

    Backup Format Version:  1.1.0

    Started:    2022-12-17 12:45:05 +0000 UTC
    Completed:  2022-12-17 12:45:09 +0000 UTC

    Expiration:  2023-01-16 12:45:05 +0000 UTC

    Total items to be backed up:  16
    Items backed up:              16

    Velero-Native Snapshots: <none included>

    Restic Backups (specify --details for more information):
    Completed:  1
    ```

## Run restore

1. Remove th namespace `myservice` for simulating a disaster recovery
    ```
    # kubectl delete ns myservice
    ```

2. Restore from the backup
    ```
    # velero restore create --from-backup myservice-backup
    Restore request "myservice-backup-20221217125113" submitted successfully.
    Run `velero restore describe myservice-backup-20221217125113` or `velero restore logs myservice-backup-20221217125113` for more details.
    ```

3. Check restore status
    ```
    # velero restore get
    NAME                              BACKUP             STATUS      STARTED                         COMPLETED                       ERRORS   WARNINGS   CREATED                         SELECTOR
    myservice-backup-20221217125113   myservice-backup   Completed   2022-12-17 12:51:13 +0000 UTC   2022-12-17 12:51:38 +0000 UTC   0        0          2022-12-17 12:51:13 +0000 UTC   <none>
    ```

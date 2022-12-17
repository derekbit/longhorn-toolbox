# MinIO

- Deploy MinIO
    ```
    kubectl apply -f ./deploy.yaml
    ```

- Forward API port 9000 and Console port 9090 
    ```
    kubectl port-forward pod/minio 9000 9090 -n minio-system --address='0.0.0.0'
    ```
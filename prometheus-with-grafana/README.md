# **Prometheus and Grafana Installations**

1. Install Prometheus Operator
    
    ```yaml
    k create -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.52.0/bundle.yaml
    ```
    

1. Install Longhorn ServiceManager
    
    ```yaml
    k apply -f prometheus/servicemonitor.yaml
    ```
    

3. Install and configure Prometheus AlertManager

```yaml
k apply -f prometheus/alertmanager.yaml

k create secret generic alertmanager-longhorn --from-file=prometheus/alertmanager_config.yaml -n default

k apply -f prometheus/alertmanager_service.yaml
```

1. Install and configure Prometheus Server
    
    ```yaml
    k apply -f prometheus/prometheus_rule.yaml
    k apply -f prometheus/prometheus_serviceaccount.yaml
    k apply -f prometheus/prometheus_clusterrole.yaml
    k apply -f prometheus/prometheus_clusterrolebinding.yaml
    k apply -f prometheus/prometheus_cr.yaml
    k apply -f prometheus/prometheus_service.yaml
    ```
    

# Install Grafana

1. Create Grafana datasource ConfigMap
    
    ```yaml
    k apply -f grafana/configmap.yaml
    ```
    

1. Create Grafana Deployment
    
    ```yaml
    k apply -f grafana/configmap.yaml
    ```
    

1. Create Grafana Service
    
    ```yaml
    k apply -f grafana/service.yaml
    ```
    

1. Expose Grafana on NodePort `32000`
    
    ```yaml
    kubectl -n default patch svc grafana --type='json' -p '[{"op":"replace","path":"/spec/type","value":"NodePort"},{"op":"replace","path":"/spec/ports/0/nodePort","value":32000}]'
    ```
    

1. Access the Grafana dashboard using any node IP on port `32000`
    ```yaml
    # Default Credential
    User: admin
    Pass: admin
    ```

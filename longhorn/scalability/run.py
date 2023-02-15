import longhorn
import time
import threading
import os

#longhorn_url = 'http://longhorn-frontend.longhorn-system/v1'
#nodes = ["dereksu-lh-pool1-df5ff43a-b27ns", "dereksu-lh-pool1-df5ff43a-tqhm7"]

longhorn_url = 'http://10.20.90.60:80/v1'
nodes = ["rancher60-worker1", "rancher60-worker2"]

num_replicas = 2


TASK = "task"
GROUPS = "groups"
CRON = "cron"
RETAIN = "retain"
SNAPSHOT = "snapshot"
BACKUP = "backup"
CONCURRENCY = "concurrency"
LABELS = "labels"

VOLUME_FRONTEND_BLOCKDEV = "blockdev"
VOLUME_FRONTEND_ISCSI = "iscsi"
DEV_PATH = "/dev/longhorn/"


RETRY_COUNTS = 600
RETRY_INTERVAL = 1
VOLUME_FIELD_STATE = "state"
VOLUME_STATE_ATTACHED = "attached"
VOLUME_STATE_DETACHED = "detached"
VOLUME_FIELD_ROBUSTNESS = "robustness"
VOLUME_ROBUSTNESS_HEALTHY = "healthy"


def get_volume_engine(v):
    engines = v.controllers
    assert len(engines) != 0
    return engines[0]


def check_volume_endpoint(v):
    engine = get_volume_engine(v)
    endpoint = engine.endpoint
    if v.disableFrontend:
        assert endpoint == ""
    else:
        if v.frontend == VOLUME_FRONTEND_BLOCKDEV:
            assert endpoint == os.path.join(DEV_PATH, v.name)
        elif v.frontend == VOLUME_FRONTEND_ISCSI:
            assert endpoint.startswith("iscsi://")
        else:
            raise Exception("Unexpected volume frontend:", v.frontend)
    return endpoint


def wait_for_volume_endpoint(client, name):
    for i in range(RETRY_COUNTS):
        v = client.by_id_volume(name)
        engine = get_volume_engine(v)
        if engine.endpoint != "":
            break
        time.sleep(RETRY_INTERVAL)
    check_volume_endpoint(v)
    return v


def wait_for_volume_creation(client, name):
    for i in range(RETRY_COUNTS):
        volumes = client.list_volume()
        found = False
        for volume in volumes:
            if volume.name == name:
                found = True
                break
        if found:
            break
        time.sleep(RETRY_INTERVAL)
    assert found


def wait_for_volume_status(client, name, key, value,
                           retry_count=RETRY_COUNTS):
    wait_for_volume_creation(client, name)
    for i in range(retry_count):
        volume = client.by_id_volume(name)
        if volume[key] == value:
            break
        time.sleep(RETRY_INTERVAL)
    assert volume[key] == value, f" value={value}\n. \
            volume[key]={volume[key]}\n. volume={volume}"
    return volume


def wait_for_volume_detached(client, name):
    return wait_for_volume_status(client, name,
                                  VOLUME_FIELD_STATE,
                                  VOLUME_STATE_DETACHED)


def wait_for_volume_healthy(client, name, retry_count=RETRY_COUNTS):
    wait_for_volume_status(client, name,
                           VOLUME_FIELD_STATE,
                           VOLUME_STATE_ATTACHED, retry_count)
    wait_for_volume_status(client, name,
                           VOLUME_FIELD_ROBUSTNESS,
                           VOLUME_ROBUSTNESS_HEALTHY, retry_count)
    return wait_for_volume_endpoint(client, name)


def create_recurring_jobs(client, job_name):
    recurring_jobs = {
        job_name: {
            TASK: "snapshot",
            GROUPS: [],
            CRON: "0 */12 * * *",
            RETAIN: 50,
            CONCURRENCY: 1,
            LABELS: {},
        },
    }

    for name, spec in recurring_jobs.items():
        client.create_recurring_job(Name=name,
                                    Task=spec["task"],
                                    Groups=spec["groups"],
                                    Cron=spec["cron"],
                                    Retain=spec["retain"],
                                    Concurrency=spec["concurrency"],
                                    Labels=spec["labels"])

def task_rwo(client, prefix, i, vol_size):
    node_name = nodes[i % len(nodes)]
    vol_name = "volume-rwo-" + prefix + "-" + str(i)

    print("Creating %s..." % (vol_name))

    client.create_volume(name=vol_name,
                         numberOfReplicas=num_replicas,
                         size=str(vol_size),
                         accessMode='rwo')

    vol = wait_for_volume_detached(client, vol_name)

    vol = client.by_id_volume(id=vol_name)
    vol = vol.attach(hostId=node_name)

    vol = wait_for_volume_healthy(client, vol_name)

    for s in range(50):
        vol = client.by_id_volume(id=vol_name)
        snap = vol.snapshotCreate()

        vol.snapshotBackup(name=snap.name)

    job_name = "job-snapshot-rwo-" + prefix + "-" + str(i)
    create_recurring_jobs(client, job_name)
    vol.recurringJobAdd(name=job_name, isGroup=False)


def task_rwx(client, prefix, i, vol_size):
    node_name = nodes[i % len(nodes)]
    vol_name = "volume-rwx-" + prefix + "-" + str(i)

    print("Creating %s..." % (vol_name))

    client.create_volume(name=vol_name,
                         numberOfReplicas=num_replicas,
                         size=str(vol_size),
                         accessMode='rwx')

    vol = wait_for_volume_detached(client, vol_name)


def create_rwo_volumes(client, prefix, num_volumes, vol_size):
    threads = []

    for i in range(num_volumes):
        thread = threading.Thread(target=task_rwo, args=(client, prefix, i, vol_size))
        thread.start()
        threads.append(thread)

    for i in range(num_volumes):
        threads[i].join()
        print("Finished rwo %d" % i)


def create_rwx_volumes(client, prefix, num_volumes, vol_size):
    threads = []

    for i in range(num_volumes):
        thread = threading.Thread(target=task_rwx, args=(client, prefix, i, vol_size))
        thread.start()
        threads.append(thread)

    for i in range(num_volumes):
        threads[i].join()
        print("Finished rwx %d" % i)


prefix = "group1"
client = longhorn.Client(url=longhorn_url)
create_rwo_volumes(client, prefix, 100, 62914560)
create_rwx_volumes(client, prefix, 100, 62914560)

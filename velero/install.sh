#!/bin/bash

BUCKET="backup"
S3URL="http://${MINIO IP}:9000"

velero install \
--provider aws \
--bucket ${BUCKET} \
--image velero/velero:v1.10.0 \
--plugins velero/velero-plugin-for-aws:v1.6.0 \
--namespace velero \
--secret-file ./credential \
--use-volume-snapshots=false \
--use-node-agent \
--default-volumes-to-fs-backup \
--backup-location-config region=minio,s3ForcePathStyle="true",s3Url=${S3URL}

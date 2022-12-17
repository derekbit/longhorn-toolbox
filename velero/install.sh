#!/bin/bash

BUCKET="velero"
S3URL="http://${MINIO IP}:9000"

velero install \
--provider aws \
--bucket ${BUCKET} \
--image velero/velero:v1.9.4 \
--plugins velero/velero-plugin-for-aws:v1.6.0 \
--namespace ${BUCKET} \
--secret-file ./credential \
--use-volume-snapshots=false \
--use-restic \
--backup-location-config region=minio,s3ForcePathStyle="true",s3Url=${S3URL}
#!/bin/sh
# used to unzip csar, replace its YAML and SCRIPTS

echo "The first parameter is: $1";
echo "start unzip csar";

cd $1
unzip nokia*.zip
rm -rf nokia*.zip
cp ne-xxx/deployment/cloud-resource-data.yaml nokia*.csar/scripts/cloud_config/
cp ne-xxx/bulk/* nokia*.csar/bulk-config/

echo "start replace YAML and SCRIPTS"

echo "unzip csar and replace finished"

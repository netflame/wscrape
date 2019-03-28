#!/usr/bin/env sh

target="local"
project="wscrape"

settings_py="${PWD}/wscrape/settings.py"

function help() {
    echo "Help on deploy"
    echo "=============="
    echo "options:"
    echo "  -t:    specified target. (default is 'local') [local, remote]"
    echo "  -p:    specified project belongs to the target. (default is 'wscrape') [wscrape]"
    echo ""
}

if [ $# == 0 ]; then
    help
    exit 0
fi

function toLocal() {
   sed -ir "s#^HTTPPROXY_URL_RANDOM.*#HTTPPROXY_URL_RANDOM = 'http://localhost:6001/random'#" ${settings_py} \
   && sed -ir "s#^REDIS_URL.*#REDIS_URL = 'redis://localhost:6379'#" ${settings_py} \
   && sed -ir "s#^MONGO_URI.*#MONGO_URI = 'mongodb://localhost:27017'#" ${settings_py}
}

function toRemote() {
    sed -ir "s#^HTTPPROXY_URL_RANDOM.*#HTTPPROXY_URL_RANDOM = 'http://uproxy:6001/random'#" ${settings_py} \
    && sed -ir "s#^REDIS_URL.*#REDIS_URL = 'redis://redis:6379'#" ${settings_py} \
    && sed -ir "s#^MONGO_URI.*#MONGO_URI = 'mongodb://mongo:27017'#" ${settings_py}
}

while getopts ":t:p:" opt
do
    case "$opt" in
        t)
            target=${OPTARG}
            case "$target" in
                local*)
                    toLocal
                ;;
                remote*)
                    toRemote
                ;;
                *)
                ;;
            esac
        ;;
        p)
            project=${OPTARG}
        ;;
        *)
        ;;
    esac
done

scrapyd-deploy $target -p $project

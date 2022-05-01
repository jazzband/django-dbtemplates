## Docker Build

~~~bash
docker build -t $APPBASE_IMAGE --platform $PLATFORM --build-arg BASE_IMAGE=$APPBASE_IMAGE --build-arg TAG=$TAG --no-cache -f docker/Dockerfile .
docker build -t $BUILDBASE_IMAGE --platform $PLATFORM --build-arg BASE_IMAGE=$BUILDBASE_IMAGE --build-arg TAG=$TAG --no-cache -f docker/Dockerfile .
~~~


## CodeBuild Test

### Install

~~~bash
$ # docker pull public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:3.0
$ docker pull public.ecr.aws/codebuild/standard:5.0
$ docker pull public.ecr.aws/codebuild/local-builds:latest
~~~

~~~bash
$ wget https://raw.githubusercontent.com/aws/aws-codebuild-docker-images/master/local_builds/codebuild_build.sh
$ chmod +x codebuild_build.sh
~~~


### Exec

~~~bash
export CODEBUILD_RUNNER=public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:3.0
export PLATFORM=linux/amd64
#
./codebuild_build.sh -c -i $CODEBUILD_RUNNER -a /tmp/artifacts -e .env
~~~ 
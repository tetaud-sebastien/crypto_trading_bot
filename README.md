# trading-bot
## Cross building x86_64 on arm64 with buildx and visa versa for Raspberry Pi

note: You can not build 64bit on an non 64bit CPU

### 1 - Set-up Docker buildx

```
export DOCKER_CLI_EXPERIMENTAL=enabled
```
Check the current default:
```
builder docker buildx ls
```

output on arm64:
```
NAME/NODE DRIVER/ENDPOINT STATUS  PLATFORMS
default * docker
default default         running linux/arm64, linux/arm/v7, linux/arm/v6
```
As you see for the default builder only the sub-architectures are available, no cross building. So lets create our own builder.

create a new builder for the architectures you want: 
```
docker buildx create --name mybuilder --platform llinux/arm64*, linux/arm/v7*, linux/arm/v6*, linux/amd64, linux/riscv64, linux/ppc64le, linux/s390x, linux/386
```

Use  buildx builder
```
docker buildx use mybuilder
```

Check the multi arch are enabled

```
docker buildx inspect
```

output:
```
Name:   mybuilder
Driver: docker-container
Nodes:
Name:      mybuilder0
Endpoint:  unix:///var/run/docker.sock
Status:    running
Platforms: linux/arm64*, linux/arm/v7*, linux/arm/v6*, linux/amd64, linux/riscv64, linux/ppc64le, linux/s390x, linux/386``
```

bootstrap the buildkit builder

```
docker buildx inspect --bootstrap
```
output;

```
Name:   mybuilder
Driver: docker-container

Nodes:
Name:      mybuilder0
Endpoint:  unix:///var/run/docker.sock
Status:    running
Platforms: linux/arm64*, linux/arm/v7*, linux/arm/v6*, linux/amd64, linux/riscv64, linux/ppc64le, linux/s390x, linux/386
```

### 2 - Build container

The following CLI build a container for inux/arm/v7 architecture and export the container the current repository.

```
docker buildx build  --platform linux/arm/v7 -o type=docker,dest=- . > batusdt_bot.tar
```
### 3 - Export container to Raspberry Pi

```
scp -r batusdt_bot.tar/ pi@raspberrypi.local:/home/pi
```


### 4 - Load container on Raspberry Pi

```
sudo docker load < batusdt_bot.tar
```
We can check:
```
sudo docker images
```

output:

```
REPOSITORY                TAG       IMAGE ID       CREATED          SIZE
<none>                    <none>    9ee4fcc245b9   20 minutes ago   693MB
```
The container has no name and TAG. We can rename the container:

```
sudo docker tag 9ee4fcc245b9 app/batusdt_bot:latest
```

### 5 - Run containter

```
sudo docker run -d app/batusdt_bot:latest
```

### 6 - Container monitoring

```
sudo docker stats
```

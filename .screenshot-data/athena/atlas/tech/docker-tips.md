# Docker Tips

## Cleanup Commands
```bash
# Remove unused images
docker image prune -a

# Remove all stopped containers
docker container prune

# Nuclear option - remove everything
docker system prune -a --volumes
```

## Debugging
- `docker logs -f container_name` - Follow logs
- `docker exec -it container_name /bin/sh` - Shell into container
- `docker stats` - Resource usage

## Compose
- `docker-compose up -d --build` - Rebuild and start
- `docker-compose logs -f service` - Service logs

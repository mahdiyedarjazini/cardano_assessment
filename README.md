# Cardano Assessment

### Run the Project

1. Start the project:
```bash
docker build .
```

2. In a new terminal, run the image on the container:
```bash
docker run -p 8000:8000 image_name/id
```

The application will be available at http://localhost:8000

To stop the project:
```bash
docker stop container_id/name
```
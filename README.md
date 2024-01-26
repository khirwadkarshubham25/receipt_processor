# Fetch Assessment Receipt Processor

------------------------------------------------

## How to run

1. Open the terminal and clone the git repository.

```bash
git clone https://github.com/khirwadkarshubham25/receipt_processor.git
```

2. Move to the working directory.

```bash
cd receipt_processor
```

3. Build the docker image. I have used the name of the docker image as receipt-processor.

```bash
docker build --no-cache -t receipt-processor .
```

if you wish to use any other name for the image. Please use below command and replace the placeholder with name.
```bash
docker build --no-cache -t <image name> .
```

4. Run the docker image.

```bash
docker-compose up
```
---------------------------------------------------------
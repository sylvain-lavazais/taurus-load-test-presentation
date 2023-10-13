# Taurus-load-test-presentation
Taurus by Blazemeter : How to easily make load tests on your dev project ?

Status: `In progress`
Language: `EN`

## how to present

### pre-requisit

you must have docker installed see [docker docs](https://docs.docker.com/engine/install/) for installation.

### Run

with a linux/macos:
```shell
make presentation
```

without make command
```shell
docker run \
--rm \
-p 1948:1948 \
-p 35729:35729 \
-v $(pwd)/presentation:/slides \
webpronl/reveal-md:latest /slides \
--watch \
--css style/custom.css \
--highlight-theme github-dark
```

hit `CTRL+C` when you're done.

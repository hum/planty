FROM alpine:latest

RUN mkdir /sprout
WORKDIR /sprout

COPY ./build/sprout ./sprout
COPY ./configs/db_config.json ./
COPY ./configs/image.agent ./

RUN chmod +x ./sprout
CMD ["./sprout"]

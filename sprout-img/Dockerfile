FROM alpine:latest

RUN mkdir /sprout-img
WORKDIR /sprout-img

COPY ./build/sprout-img ./sprout-img
COPY ./build/db_config.json ./

RUN chmod +x ./sprout-img
CMD ["./sprout-img"]

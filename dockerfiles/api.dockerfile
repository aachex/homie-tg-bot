FROM golang:1.26.2-alpine3.23
WORKDIR /app

COPY api/go.mod api/go.sum /app/
RUN go mod download && go mod verify

COPY api/. /app/

EXPOSE 8080

RUN go build -o app cmd/homie-api/main.go

CMD [ "./app" ]
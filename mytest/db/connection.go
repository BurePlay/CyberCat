package db

import (
	"context"
	"log"

	"github.com/jackc/pgx/v4"
)

func ConnectDB() *pgx.Conn {
	conn, err := pgx.Connect(context.Background(), "postgres://postgres:1@localhost:5432/tests")
	if err != nil {
		log.Fatalf("Unable to connect to database: %v\n", err)
	}
	return conn
}

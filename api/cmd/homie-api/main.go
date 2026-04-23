package main

import (
	"fmt"
	"os"

	_ "github.com/jackc/pgx/v5/stdlib" // postgres driver
	"github.com/jmoiron/sqlx"
	"github.com/pressly/goose/v3"
)

func main() {
	fmt.Println("START")

	dbUser := os.Getenv("POSTGRES_USER")
	dbPassword := os.Getenv("POSTGRES_PASSWORD")
	dbHost := os.Getenv("POSTGRES_HOST")
	dbPort := os.Getenv("POSTGRES_PORT")
	dbName := os.Getenv("POSTGRES_DB")
	connStr := fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable", dbUser, dbPassword, dbHost, dbPort, dbName)

	mustUpMigrations(connStr)

	fmt.Println("SUCCESS")
}

func mustUpMigrations(connStr string) {
	db, err := sqlx.Connect("pgx", connStr)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	err = goose.SetDialect("postgres")
	if err != nil {
		panic(err)
	}

	const migrationsDir = "db/migrations"
	err = goose.Up(db.DB, migrationsDir)
	if err != nil {
		panic(err)
	}
}

package main

import (
	"context"
	"fmt"
	"homie-api/internal/controller"
	"homie-api/internal/repository/postgres"
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5/pgxpool"
	_ "github.com/jackc/pgx/v5/stdlib" // postgres driver
	"github.com/jmoiron/sqlx"
	"github.com/pressly/goose/v3"
)

func main() {
	// Подключение к БД и накат миграций
	connStr := buildConnStr()

	mustUpMigrations(connStr)

	connPool := mustInitConnPool(connStr)
	defer connPool.Close()

	// Репозитории
	usersRepo := postgres.NewUsersRepo(connPool)

	// Контроллеры
	usersController := controller.NewUsers(usersRepo)

	// Запуск сервера
	r := gin.New()

	v1 := r.Group("/api/v1")
	v1.GET("/user/rand", usersController.GetRandUser)
	v1.POST("/user", usersController.CreateUser)
	v1.PATCH("/user/:id", usersController.EditUser)

	log.Fatal(r.Run(":8080"))
}

func mustInitConnPool(connStr string) *pgxpool.Pool {
	connPool, err := pgxpool.New(context.Background(), connStr)
	if err != nil {
		panic(err)
	}
	return connPool
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

func buildConnStr() string {
	dbUser := os.Getenv("POSTGRES_USER")
	dbPassword := os.Getenv("POSTGRES_PASSWORD")
	dbHost := os.Getenv("POSTGRES_HOST")
	dbPort := os.Getenv("POSTGRES_PORT")
	dbName := os.Getenv("POSTGRES_DB")

	return fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable", dbUser, dbPassword, dbHost, dbPort, dbName)
}

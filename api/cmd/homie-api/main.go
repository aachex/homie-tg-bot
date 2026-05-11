package main

import (
	"context"
	"fmt"
	"homie-api/internal/controller"
	"homie-api/internal/repository/postgres"
	"homie-api/pkg/middleware"
	"log"
	"log/slog"
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

	// Логгер
	opts := slog.HandlerOptions{
		Level: slog.LevelDebug,
	}
	logger := slog.New(slog.NewTextHandler(os.Stdout, &opts))

	// Репозитории
	usersRepo := postgres.NewUsersRepo(connPool)
	offersRepo := postgres.NewOffersRepo(connPool)
	reportsRepo := postgres.NewReportsRepo(connPool)
	statsRepo := postgres.NewStatsRepo(connPool)

	// Контроллеры
	usersController := controller.NewUsers(logger, usersRepo)
	offersController := controller.NewHouseOffers(logger, offersRepo)
	reportsController := controller.NewReports(logger, reportsRepo)
	statsController := controller.NewStats(logger, statsRepo)

	// Конфигурация сервера
	r := gin.New()
	r.GET("/ping", controller.Ping)

	v1 := r.Group("/api/v1")

	// Middleware
	v1.Use(middleware.CheckKey())

	// Routes
	v1.GET("/user/:id", usersController.UserById)
	v1.POST("/user", usersController.CreateUser)
	v1.PATCH("/user/:id", usersController.EditUser)
	v1.GET("/user/:id/offers", offersController.UserOffers)

	v1.GET("/offer/:id", offersController.OfferById)
	v1.GET("/offer/rand", offersController.RandOffer)
	v1.POST("/offer", offersController.CreateOffer)
	v1.DELETE("/offer/:id", offersController.DeleteOffer)
	v1.PATCH("/offer/:id", offersController.SetActiveOffer)
	v1.GET("/offer/:id/likes", offersController.OfferLikes)
	v1.POST("/offer/:id/like", offersController.AddLike)
	v1.DELETE("/offer/:id/like", offersController.DeleteLike)

	v1.GET("/report/pending-reports", reportsController.PendingReports)
	v1.GET("/report/:id", reportsController.ByID)
	v1.GET("/report/count", reportsController.Count)
	v1.POST("/report", reportsController.CreateReport)

	v1.POST("/stats/user-activity", statsController.CreateUserActivity)
	v1.POST("/stats/dau", statsController.DAU)

	// Запуск
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

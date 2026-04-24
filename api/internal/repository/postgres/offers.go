package postgres

import (
	"context"
	"homie-api/internal/model"

	"github.com/jackc/pgx/v5/pgxpool"
)

type OffersRepo struct {
	connPool *pgxpool.Pool
}

func NewOffersRepo(connPool *pgxpool.Pool) *OffersRepo {
	return &OffersRepo{
		connPool: connPool,
	}
}

func (r OffersRepo) RandOffer(ctx context.Context) (offer model.HouseOffer, err error) {
	query := `
		SELECT 
			id,
			is_active,
			owner_id,
			title,
			description,
			city,
			price,
			type,
			media_files
		FROM tg_house_offer 
		WHERE is_active = TRUE 
		ORDER BY RANDOM()`

	row := r.connPool.QueryRow(ctx, query)
	err = row.Scan(&offer.Id, &offer.IsActive, &offer.OwnerId, &offer.Title, &offer.Description, &offer.City, &offer.Price, &offer.Type, &offer.MediaFiles)
	return offer, err
}

func (r OffersRepo) CreateOffer(ctx context.Context, data model.HouseOfferCreate) (id int64, err error) {
	query := `
		INSERT INTO tg_house_offer (
			owner_id,
			title,
			description,
			city,
			price,
			type,
			media_files
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING id`

	row := r.connPool.QueryRow(ctx, query, data.OwnerId, data.Title, data.Description, data.City, data.Price, data.Type, data.MediaFiles)
	err = row.Scan(&id)
	return id, err
}

func (r OffersRepo) DeleteOffer(ctx context.Context, id int64) error {
	query := `DELETE FROM tg_house_offer WHERE id = $1`
	_, err := r.connPool.Exec(ctx, query, id)
	return err
}

func (r OffersRepo) SetActive(ctx context.Context, id int64, active bool) error {
	query := `
		UPDATE tg_house_offer
		SET is_active = $1
		WHERE id = $2`
	_, err := r.connPool.Exec(ctx, query, active, id)
	return err
}

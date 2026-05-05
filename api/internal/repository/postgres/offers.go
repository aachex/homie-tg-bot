package postgres

import (
	"context"
	"errors"
	"fmt"
	"homie-api/internal/model"

	"github.com/jackc/pgx/v5/pgxpool"
)

var (
	ErrLikeAlreadyExists = errors.New("like already exists")
)

type OffersRepo struct {
	connPool *pgxpool.Pool
}

func NewOffersRepo(connPool *pgxpool.Pool) *OffersRepo {
	r := new(OffersRepo)
	r.connPool = connPool
	return r
}

func (r OffersRepo) OfferById(ctx context.Context, id int64) (offer model.HouseOffer, err error) {
	query := `
		SELECT 
			id,
			is_active,
			owner_id,
			title,
			description,
			city,
			district,
			price,
			media_files
		FROM tg_house_offer 
		WHERE id = $1`
	row := r.connPool.QueryRow(ctx, query, id)
	err = row.Scan(&offer.Id, &offer.IsActive, &offer.OwnerId, &offer.Title, &offer.Description, &offer.City, &offer.District, &offer.Price, &offer.MediaFiles)
	return offer, err
}

func (r OffersRepo) OfferLikes(ctx context.Context, offerId int64) (likes []model.HouseOfferLike, err error) {
	likes = []model.HouseOfferLike{}

	query := `
		SELECT
			id,
			offer_id,
			user_id
		FROM offer_like
		WHERE offer_id = $1`
	rows, err := r.connPool.Query(ctx, query, offerId)
	if err != nil {
		return likes, err
	}

	var like model.HouseOfferLike
	for rows.Next() {
		err = rows.Scan(&like.Id, &like.OfferId, &like.UserId)
		if err != nil {
			return likes, err
		}
		likes = append(likes, like)
	}

	err = rows.Err()
	return likes, err
}

func (r *OffersRepo) AddLike(ctx context.Context, offerId int64, userId int64) error {
	query := `
        INSERT INTO offer_like (offer_id, user_id)
        VALUES ($1, $2)
        ON CONFLICT (offer_id, user_id) DO NOTHING
    `
	cmdTag, err := r.connPool.Exec(ctx, query, offerId, userId)
	if err != nil {
		return fmt.Errorf("failed to insert like: %w", err)
	}

	if cmdTag.RowsAffected() == 0 {
		return ErrLikeAlreadyExists
	}
	return nil
}

func (r OffersRepo) RandOffer(ctx context.Context, userId int64, city string) (offer model.HouseOfferVisibleData, err error) {
	query := `
		SELECT
			title,
			description,
			city,
			district,
			price,
			media_files
		FROM tg_house_offer 
		WHERE is_active = TRUE AND owner_id <> $1 and city = $2
		ORDER BY RANDOM()`

	row := r.connPool.QueryRow(ctx, query, userId, city)
	err = row.Scan(&offer.Title, &offer.Description, &offer.City, &offer.District, &offer.Price, &offer.MediaFiles)
	return offer, err
}

func (r OffersRepo) UserOffers(ctx context.Context, userId int64) (offers []model.HouseOfferPreview, err error) {
	offers = []model.HouseOfferPreview{}

	query := `
		SELECT
			tg_house_offer.id,
			tg_house_offer.is_active,
			tg_house_offer.title,
			COUNT(offer_likes.offer_id) as likes_count
		FROM tg_house_offer LEFT JOIN offer_likes ON tg_house_offer.id = offer_likes.offer_id
		WHERE owner_id = $1
		GROUP BY tg_house_offer.id, tg_house_offer.is_active, tg_house_offer.title`

	rows, err := r.connPool.Query(ctx, query, userId)
	if err != nil {
		return offers, err
	}

	var offer model.HouseOfferPreview
	for rows.Next() {
		err = rows.Scan(&offer.Id, &offer.IsActive, &offer.Title, &offer.LikesCount)
		if err != nil {
			return offers, err
		}
		offers = append(offers, offer)
	}

	return offers, rows.Err()
}

func (r OffersRepo) CreateOffer(ctx context.Context, data model.HouseOfferCreate) (id int64, err error) {
	query := `
		INSERT INTO tg_house_offer (
			owner_id,
			title,
			description,
			city,
			district,
			price,
			media_files
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING id`

	row := r.connPool.QueryRow(ctx, query, data.OwnerId, data.Title, data.Description, data.City, data.District, data.Price, data.MediaFiles)
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

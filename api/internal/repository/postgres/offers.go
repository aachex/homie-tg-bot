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
	ErrLikeNotFound      = errors.New("like not found")
)

type OffersRepo struct {
	connPool *pgxpool.Pool
}

func NewOffersRepo(connPool *pgxpool.Pool) *OffersRepo {
	return &OffersRepo{
		connPool: connPool,
	}
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
			media_files,
			flag_processing,
			preferred_smoking,
			preferred_children,
			preferred_pets,
			preferred_occupants_count,
			preferred_noise_lvl,
			preferred_works_from_home,
			preferred_alcohol,
			preferred_age_min,
			preferred_age_max
		FROM tg_house_offer 
		WHERE id = $1`

	row := r.connPool.QueryRow(ctx, query, id)

	err = row.Scan(
		&offer.Id,
		&offer.IsActive,
		&offer.OwnerId,
		&offer.Title,
		&offer.Description,
		&offer.City,
		&offer.District,
		&offer.Price,
		&offer.MediaFiles,
		&offer.FlagProcessing,
		&offer.Preferences.Smoking,
		&offer.Preferences.Children,
		&offer.Preferences.Pets,
		&offer.Preferences.OccupantsCount,
		&offer.Preferences.NoiseLvl,
		&offer.Preferences.WorksFromHome,
		&offer.Preferences.Alcohol,
		&offer.Preferences.AgeMin,
		&offer.Preferences.AgeMax,
	)

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

func (r OffersRepo) AddLike(ctx context.Context, offerId int64, userId int64) error {
	query := `
        INSERT INTO offer_like (offer_id, user_id)
		SELECT $1, $2
		WHERE EXISTS (SELECT 1 FROM tg_house_offer WHERE id = $1)
		ON CONFLICT (offer_id, user_id) DO NOTHING`
	cmdTag, err := r.connPool.Exec(ctx, query, offerId, userId)
	if err != nil {
		return fmt.Errorf("failed to insert like: %w", err)
	}

	if cmdTag.RowsAffected() == 0 {
		return ErrLikeAlreadyExists
	}
	return nil
}

func (r OffersRepo) DeleteLike(ctx context.Context, offerId int64, userId int64) error {
	query := `
        DELETE FROM offer_like
        WHERE offer_id = $1 AND user_id = $2
    `
	cmdTag, err := r.connPool.Exec(ctx, query, offerId, userId)
	if err != nil {
		return fmt.Errorf("failed to delete like: %w", err)
	}

	if cmdTag.RowsAffected() == 0 {
		return ErrLikeNotFound
	}
	return nil
}

func (r OffersRepo) RandOffer(ctx context.Context, userId int64, city string, userFlags model.UserFlags) (offer model.HouseOffer, err error) {
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
			media_files,
			preferred_smoking,
			preferred_children,
			preferred_pets,
			preferred_occupants_count,
			preferred_noise_lvl,
			preferred_works_from_home,
			preferred_alcohol,
			preferred_age_min,
			preferred_age_max
		FROM tg_house_offer 
		WHERE is_active = TRUE AND owner_id <> $1 AND city = $2
	`

	args := []any{userId, city}
	argCounter := 3

	// Курение
	if userFlags.Smoking != nil {
		query += fmt.Sprintf(" AND (preferred_smoking = $%d OR preferred_smoking IS NULL)", argCounter)
		args = append(args, *userFlags.Smoking)
		argCounter++
	}

	// Дети
	if userFlags.Children != nil {
		query += fmt.Sprintf(" AND (preferred_children = $%d OR preferred_children IS NULL)", argCounter)
		args = append(args, *userFlags.Children)
		argCounter++
	}

	// Животные
	if userFlags.Pets != nil {
		query += fmt.Sprintf(" AND (preferred_pets = $%d OR preferred_pets IS NULL)", argCounter)
		args = append(args, *userFlags.Pets)
		argCounter++
	}

	// Количество проживающих
	if userFlags.OccupantsCount != nil {
		query += fmt.Sprintf(" AND (preferred_occupants_count >= $%d OR preferred_occupants_count IS NULL)", argCounter)
		args = append(args, *userFlags.OccupantsCount)
		argCounter++
	}

	// Уровень шума
	if userFlags.NoiseLvl != nil {
		query += fmt.Sprintf(" AND (preferred_noise_lvl = $%d OR preferred_noise_lvl IS NULL)", argCounter)
		args = append(args, *userFlags.NoiseLvl)
		argCounter++
	}

	// Работа из дома
	if userFlags.WorksFromHome != nil {
		query += fmt.Sprintf(" AND (preferred_works_from_home = $%d OR preferred_works_from_home IS NULL)", argCounter)
		args = append(args, *userFlags.WorksFromHome)
		argCounter++
	}

	// Алкоголь
	if userFlags.Alcohol != nil {
		query += fmt.Sprintf(" AND (preferred_alcohol = $%d OR preferred_alcohol IS NULL)", argCounter)
		args = append(args, *userFlags.Alcohol)
		argCounter++
	}

	// Возраст
	if userFlags.AgeMin != nil {
		query += fmt.Sprintf(" AND (preferred_age_max >= $%d OR preferred_age_max IS NULL)", argCounter)
		args = append(args, *userFlags.AgeMin)
		argCounter++
	}
	if userFlags.AgeMax != nil {
		query += fmt.Sprintf(" AND (preferred_age_min <= $%d OR preferred_age_min IS NULL)", argCounter)
		args = append(args, *userFlags.AgeMax)
		argCounter++
	}

	query += " ORDER BY RANDOM() LIMIT 1"

	row := r.connPool.QueryRow(ctx, query, args...)
	err = row.Scan(
		&offer.Id,
		&offer.IsActive,
		&offer.OwnerId,
		&offer.Title,
		&offer.Description,
		&offer.City,
		&offer.District,
		&offer.Price,
		&offer.MediaFiles,
		&offer.Preferences.Smoking,
		&offer.Preferences.Children,
		&offer.Preferences.Pets,
		&offer.Preferences.OccupantsCount,
		&offer.Preferences.NoiseLvl,
		&offer.Preferences.WorksFromHome,
		&offer.Preferences.Alcohol,
		&offer.Preferences.AgeMin,
		&offer.Preferences.AgeMax,
	)
	return offer, err
}

func (r OffersRepo) UserOffers(ctx context.Context, userId int64) (offers []model.HouseOfferPreview, err error) {
	offers = []model.HouseOfferPreview{}

	query := `
		SELECT
			tg_house_offer.id,
			tg_house_offer.is_active,
			tg_house_offer.title,
			COUNT(offer_like.offer_id) as likes_count
		FROM tg_house_offer LEFT JOIN offer_like ON tg_house_offer.id = offer_like.offer_id
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
			media_files,
			flag_processing
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE)
		RETURNING id
	`

	err = r.connPool.QueryRow(
		ctx,
		query,
		data.OwnerId,
		data.Title,
		data.Description,
		data.City,
		data.District,
		data.Price,
		data.MediaFiles,
	).Scan(&id)

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

// UpdateOfferPreferences обновляет предпочтения арендодателя (флаги)
func (r OffersRepo) UpdateOfferPreferences(ctx context.Context, offerId int64, prefs model.OwnerPreferences) error {
	query := `
		UPDATE tg_house_offer SET
			preferred_smoking = $1,
			preferred_children = $2,
			preferred_pets = $3,
			preferred_occupants_count = $4,
			preferred_noise_lvl = $5,
			preferred_works_from_home = $6,
			preferred_alcohol = $7,
			preferred_age_min = $8,
			preferred_age_max = $9,
			flag_processing = FALSE
		WHERE id = $10
	`

	_, err := r.connPool.Exec(ctx, query,
		prefs.Smoking,
		prefs.Children,
		prefs.Pets,
		prefs.OccupantsCount,
		prefs.NoiseLvl,
		prefs.WorksFromHome,
		prefs.Alcohol,
		prefs.AgeMin,
		prefs.AgeMax,
		offerId,
	)

	return err
}

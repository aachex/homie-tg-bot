package postgres

import (
	"context"
	"errors"
	"fmt"
	"homie-api/internal/model"
	"log/slog"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

var (
	ErrLikeAlreadyExists = errors.New("like already exists")
	ErrLikeNotFound      = errors.New("like not found")
)

type OffersRepo struct {
	logger      *slog.Logger
	connPool    *pgxpool.Pool
	premiumRepo *PremiumRepo
}

func NewOffersRepo(logger *slog.Logger, connPool *pgxpool.Pool, premiumRepo *PremiumRepo) *OffersRepo {
	return &OffersRepo{
		logger:      logger,
		connPool:    connPool,
		premiumRepo: premiumRepo,
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
			preferred_age_max,
			preferred_sex
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
		&offer.Preferences.Sex,
	)

	return offer, err
}

func (r OffersRepo) OfferLikes(ctx context.Context, offerId int64) (likes []model.HouseOfferLike, err error) {
	likes = []model.HouseOfferLike{}

	query := `
		SELECT
			id,
			offer_id,
			user_id,
			relevance
		FROM offer_like
		WHERE offer_id = $1`
	rows, err := r.connPool.Query(ctx, query, offerId)
	if err != nil {
		return likes, err
	}

	var like model.HouseOfferLike
	for rows.Next() {
		err = rows.Scan(&like.Id, &like.OfferId, &like.UserId, &like.Relevance)
		if err != nil {
			return likes, err
		}
		likes = append(likes, like)
	}

	err = rows.Err()
	return likes, err
}

func (r OffersRepo) AddLike(ctx context.Context, like model.AddLikeRequest) error {
	query := `
        INSERT INTO offer_like (offer_id, user_id, relevance)
		SELECT $1, $2, $3
		WHERE EXISTS (SELECT 1 FROM tg_house_offer WHERE id = $1)
		ON CONFLICT (offer_id, user_id) DO NOTHING`
	cmdTag, err := r.connPool.Exec(ctx, query, like.OfferId, like.UserId, like.Relevance)
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

func (r OffersRepo) RelevantOffers(ctx context.Context, userId int64, city string, userFlags model.UserFlags, minRelPercent int, limit int) (offers []model.RelevantOffer, err error) {
	const maxRelevanceSum = 200

	err = r.transaction(ctx, func(tx pgx.Tx) error {
		query := `
			WITH user_flags AS (
				SELECT
					COALESCE($3, FALSE)::boolean AS smoking,
					$4::text AS sex,
					COALESCE($5, 'none')::text AS children,
					COALESCE($6, 'none')::text AS pets,
					COALESCE($7, 1)::int AS occupants_count,
					COALESCE($8, 'quiet')::text AS noise_lvl,
					COALESCE($9, FALSE)::boolean AS works_from_home,
					COALESCE($10, 'never')::text AS alcohol,
					COALESCE($11, 0)::int AS age_min,
					COALESCE($12, 150)::int AS age_max
			),
			ranked_offers AS (
				SELECT
					o.*,
					(
						-- Smoking (max 20)
						CASE
							WHEN o.preferred_smoking IS NULL THEN 20
							WHEN u.smoking IS TRUE AND o.preferred_smoking IS TRUE THEN 20
							WHEN u.smoking IS FALSE AND o.preferred_smoking IS FALSE THEN 20
							WHEN u.smoking IS FALSE AND o.preferred_smoking IS TRUE THEN 20
							WHEN u.smoking IS TRUE AND o.preferred_smoking IS FALSE THEN 0
							ELSE 0
						END +
						-- Sex (max 20)
						CASE
							WHEN o.preferred_sex IS NULL OR u.sex IS NULL THEN 20
							WHEN u.sex = 'male' AND o.preferred_sex::text = 'male' THEN 20
							WHEN u.sex = 'female' AND o.preferred_sex::text = 'female' THEN 20
							ELSE 0
						END +
						-- Children (max 20)
						CASE
							WHEN o.preferred_children IS NULL THEN 20
							WHEN o.preferred_children::text = 'none' AND (u.children IS NULL OR u.children = 'none') THEN 20
							WHEN o.preferred_children::text = 'none' AND u.children = 'one' THEN 0
							WHEN o.preferred_children::text = 'none' AND u.children = 'two+' THEN 0
							WHEN o.preferred_children::text = 'none' AND u.children = 'planning' THEN 10
							WHEN o.preferred_children::text = 'one' AND u.children = 'none' THEN 20
							WHEN o.preferred_children::text = 'one' AND u.children = 'one' THEN 20
							WHEN o.preferred_children::text = 'one' AND u.children = 'two+' THEN 0
							WHEN o.preferred_children::text = 'one' AND u.children = 'planning' THEN 10
							WHEN o.preferred_children::text = 'two+' AND u.children = 'none' THEN 20
							WHEN o.preferred_children::text = 'two+' AND u.children = 'one' THEN 20
							WHEN o.preferred_children::text = 'two+' AND u.children = 'two+' THEN 20
							WHEN o.preferred_children::text = 'two+' AND u.children = 'planning' THEN 20
							WHEN o.preferred_children::text = 'planning' AND u.children = 'none' THEN 10
							WHEN o.preferred_children::text = 'planning' AND u.children = 'one' THEN 20
							WHEN o.preferred_children::text = 'planning' AND u.children = 'two+' THEN 20
							WHEN o.preferred_children::text = 'planning' AND u.children = 'planning' THEN 20
							ELSE 0
						END +
						-- Pets (max 20)
						CASE
							WHEN o.preferred_pets IS NULL THEN 20
							WHEN o.preferred_pets::text = 'any' THEN 20
							WHEN o.preferred_pets::text = 'none' AND (u.pets IS NULL OR u.pets = 'none') THEN 20
							WHEN o.preferred_pets::text = 'cats' AND u.pets = 'none' THEN 20
							WHEN o.preferred_pets::text = 'cats' AND u.pets = 'cats' THEN 20
							WHEN o.preferred_pets::text = 'cats' AND u.pets = 'dogs' THEN 10
							WHEN o.preferred_pets::text = 'cats' AND u.pets = 'other' THEN 20
							WHEN o.preferred_pets::text = 'cats' AND u.pets = 'any' THEN 10
							WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'none' THEN 20
							WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'cats' THEN 10
							WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'dogs' THEN 20
							WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'other' THEN 20
							WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'any' THEN 10
							WHEN o.preferred_pets::text = 'other' AND u.pets = 'none' THEN 20
							WHEN o.preferred_pets::text = 'other' AND u.pets = 'cats' THEN 10
							WHEN o.preferred_pets::text = 'other' AND u.pets = 'dogs' THEN 10
							WHEN o.preferred_pets::text = 'other' AND u.pets = 'other' THEN 20
							WHEN o.preferred_pets::text = 'other' AND u.pets = 'any' THEN 10
							ELSE 0
						END +
						-- Occupants count (max 20)
						CASE
							WHEN o.preferred_occupants_count IS NULL THEN 20
							WHEN u.occupants_count <= o.preferred_occupants_count THEN 20
							ELSE 0
						END +
						-- Noise level (max 20)
						CASE
							WHEN o.preferred_noise_lvl IS NULL THEN 20
							WHEN o.preferred_noise_lvl::text = 'quiet' AND u.noise_lvl = 'quiet' THEN 20
							WHEN o.preferred_noise_lvl::text = 'quiet' AND u.noise_lvl = 'normal' THEN 10
							WHEN o.preferred_noise_lvl::text = 'quiet' AND u.noise_lvl = 'loud' THEN 0
							WHEN o.preferred_noise_lvl::text = 'normal' AND u.noise_lvl = 'quiet' THEN 20
							WHEN o.preferred_noise_lvl::text = 'normal' AND u.noise_lvl = 'normal' THEN 20
							WHEN o.preferred_noise_lvl::text = 'normal' AND u.noise_lvl = 'loud' THEN 0
							WHEN o.preferred_noise_lvl::text = 'loud' AND u.noise_lvl = 'quiet' THEN 20
							WHEN o.preferred_noise_lvl::text = 'loud' AND u.noise_lvl = 'normal' THEN 20
							WHEN o.preferred_noise_lvl::text = 'loud' AND u.noise_lvl = 'loud' THEN 20
							ELSE 0
						END +
						-- Works from home (max 20)
						CASE
							WHEN o.preferred_works_from_home IS NULL THEN 20
							WHEN u.works_from_home = o.preferred_works_from_home THEN 20
							ELSE 0
						END +
						-- Alcohol (max 20)
						CASE
							WHEN o.preferred_alcohol IS NULL THEN 20
							WHEN o.preferred_alcohol::text = 'never' AND u.alcohol = 'never' THEN 20
							WHEN o.preferred_alcohol::text = 'never' AND u.alcohol = 'rare' THEN 10
							WHEN o.preferred_alcohol::text = 'never' AND u.alcohol = 'regular' THEN 0
							WHEN o.preferred_alcohol::text = 'rare' AND u.alcohol = 'never' THEN 20
							WHEN o.preferred_alcohol::text = 'rare' AND u.alcohol = 'rare' THEN 20
							WHEN o.preferred_alcohol::text = 'rare' AND u.alcohol = 'regular' THEN 0
							WHEN o.preferred_alcohol::text = 'regular' AND u.alcohol = 'never' THEN 20
							WHEN o.preferred_alcohol::text = 'regular' AND u.alcohol = 'rare' THEN 20
							WHEN o.preferred_alcohol::text = 'regular' AND u.alcohol = 'regular' THEN 20
							ELSE 0
						END +
						-- Age min (max 20)
						CASE
							WHEN o.preferred_age_min IS NULL THEN 20
							WHEN u.age_min >= o.preferred_age_min THEN 20
							WHEN u.age_min < o.preferred_age_min THEN 10
							ELSE 0
						END +
						-- Age max (max 20)
						CASE
							WHEN o.preferred_age_max IS NULL THEN 20
							WHEN u.age_max <= o.preferred_age_max THEN 20
							WHEN u.age_max > o.preferred_age_max THEN 10
							ELSE 0
						END 
					) AS relevance_sum,
					 -- Бонусы за буст
					(
						-- Объявление создано настоящим человеком (не мок)
						CASE
							WHEN o.owner_id != 0 THEN 50
							ELSE 0
						END +
						-- Владелец продвигал своё объявление
						CASE
							WHEN o.boosted_until IS NOT NULL AND NOW() < o.boosted_until THEN 200
							ELSE 0
						END +
						-- Премиум-бонус для владельца (дополнительные очки)
						CASE
							WHEN p_owner.user_id IS NOT NULL THEN 100
							ELSE 0
						END
					) AS boost_sum
				FROM tg_house_offer o
				CROSS JOIN user_flags u
				LEFT JOIN premium p_owner ON p_owner.user_id = o.owner_id AND NOW() < p_owner.until
				LEFT JOIN premium p_user ON p_user.user_id = $1 AND NOW() < p_user.until
				WHERE o.is_active = TRUE 
				AND o.owner_id <> $1 
				AND o.city = $2
				AND (
					p_owner.user_id IS NOT NULL
					OR p_user.user_id IS NOT NULL
					OR (p_owner.user_id IS NULL AND p_user.user_id IS NULL AND o.created_at <= NOW() - INTERVAL '12 hours')
				)
			),
			ranked_with_boost AS (
				SELECT
					*,
					(relevance_sum + boost_sum) AS total_score
				FROM ranked_offers
			)
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
				preferred_age_max,
				preferred_sex,
				relevance_sum,
				((relevance_sum::float / $14) * 100)::int AS relevance_percent
			FROM ranked_with_boost
			WHERE relevance_sum >= $13
			ORDER BY boost_sum DESC, RANDOM()
			LIMIT $15
		`

		minRelevanceSum := minRelPercent * maxRelevanceSum / 100
		args := []any{
			userId,                   // $1
			city,                     // $2
			userFlags.Smoking,        // $3
			userFlags.Sex,            // $4
			userFlags.Children,       // $5
			userFlags.Pets,           // $6
			userFlags.OccupantsCount, // $7
			userFlags.NoiseLvl,       // $8
			userFlags.WorksFromHome,  // $9
			userFlags.Alcohol,        // $10
			userFlags.AgeMin,         // $11
			userFlags.AgeMax,         // $12
			minRelevanceSum,          // $13
			maxRelevanceSum,          // $14
			limit,                    // $15
		}

		rows, err := tx.Query(ctx, query, args...)
		if err != nil {
			return err
		}

		var offer model.RelevantOffer
		for rows.Next() {
			err = rows.Scan(
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
				&offer.Preferences.Sex,
				&offer.RelevanceSum,
				&offer.RelevancePercent,
			)

			if err != nil {
				return err
			}

			offers = append(offers, offer)
		}

		return err
	})

	return offers, err
}

func (r OffersRepo) GetOfferRelevance(ctx context.Context, offerId int64, userFlags model.UserFlags) (relevancePercent int, err error) {
	query := `
		WITH user_flags AS (
			SELECT 
				COALESCE($2, FALSE)::boolean AS smoking,
				$3::text AS sex,
				COALESCE($4, 'none')::text AS children,
				COALESCE($5, 'none')::text AS pets,
				COALESCE($6, 1)::int AS occupants_count,
				COALESCE($7, 'quiet')::text AS noise_lvl,
				COALESCE($8, FALSE)::boolean AS works_from_home,
				COALESCE($9, 'never')::text AS alcohol,
				COALESCE($10, 0)::int AS age_min,
				COALESCE($11, 150)::int AS age_max
		)
		SELECT
			(
				-- Smoking (max 20)
				CASE
					WHEN o.preferred_smoking IS NULL OR u.smoking IS NULL THEN 20
					WHEN u.smoking IS TRUE AND o.preferred_smoking IS TRUE THEN 20
					WHEN u.smoking IS FALSE AND o.preferred_smoking IS FALSE THEN 20
					WHEN u.smoking IS FALSE AND o.preferred_smoking IS TRUE THEN 20
					WHEN u.smoking IS TRUE AND o.preferred_smoking IS FALSE THEN 0
					ELSE 0
				END +
				-- Sex (max 20)
				CASE
					WHEN o.preferred_sex IS NULL OR u.sex IS NULL THEN 20
					WHEN u.sex = 'male' AND o.preferred_sex::text = 'male' THEN 20
					WHEN u.sex = 'female' AND o.preferred_sex::text = 'female' THEN 20
					ELSE 0
				END +
				-- Children (max 20)
				CASE
					WHEN o.preferred_children IS NULL OR u.children IS NULL THEN 20
					WHEN o.preferred_children::text = 'none' AND (u.children IS NULL OR u.children = 'none') THEN 20
					WHEN o.preferred_children::text = 'none' AND u.children = 'one' THEN 0
					WHEN o.preferred_children::text = 'none' AND u.children = 'two+' THEN 0
					WHEN o.preferred_children::text = 'none' AND u.children = 'planning' THEN 10
					WHEN o.preferred_children::text = 'one' AND u.children = 'none' THEN 20
					WHEN o.preferred_children::text = 'one' AND u.children = 'one' THEN 20
					WHEN o.preferred_children::text = 'one' AND u.children = 'two+' THEN 0
					WHEN o.preferred_children::text = 'one' AND u.children = 'planning' THEN 10
					WHEN o.preferred_children::text = 'two+' AND u.children = 'none' THEN 20
					WHEN o.preferred_children::text = 'two+' AND u.children = 'one' THEN 20
					WHEN o.preferred_children::text = 'two+' AND u.children = 'two+' THEN 20
					WHEN o.preferred_children::text = 'two+' AND u.children = 'planning' THEN 20
					WHEN o.preferred_children::text = 'planning' AND u.children = 'none' THEN 10
					WHEN o.preferred_children::text = 'planning' AND u.children = 'one' THEN 20
					WHEN o.preferred_children::text = 'planning' AND u.children = 'two+' THEN 20
					WHEN o.preferred_children::text = 'planning' AND u.children = 'planning' THEN 20
					ELSE 0
				END +
				-- Pets (max 20)
				CASE
					WHEN o.preferred_pets IS NULL OR u.pets IS NULL THEN 20
					WHEN o.preferred_pets::text = 'any' THEN 20
					WHEN o.preferred_pets::text = 'none' AND (u.pets IS NULL OR u.pets = 'none') THEN 20
					WHEN o.preferred_pets::text = 'cats' AND u.pets = 'none' THEN 20
					WHEN o.preferred_pets::text = 'cats' AND u.pets = 'cats' THEN 20
					WHEN o.preferred_pets::text = 'cats' AND u.pets = 'dogs' THEN 10
					WHEN o.preferred_pets::text = 'cats' AND u.pets = 'other' THEN 20
					WHEN o.preferred_pets::text = 'cats' AND u.pets = 'any' THEN 10
					WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'none' THEN 20
					WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'cats' THEN 10
					WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'dogs' THEN 20
					WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'other' THEN 20
					WHEN o.preferred_pets::text = 'dogs' AND u.pets = 'any' THEN 10
					WHEN o.preferred_pets::text = 'other' AND u.pets = 'none' THEN 20
					WHEN o.preferred_pets::text = 'other' AND u.pets = 'cats' THEN 10
					WHEN o.preferred_pets::text = 'other' AND u.pets = 'dogs' THEN 10
					WHEN o.preferred_pets::text = 'other' AND u.pets = 'other' THEN 20
					WHEN o.preferred_pets::text = 'other' AND u.pets = 'any' THEN 10
					ELSE 0
				END +
				-- Occupants count (max 20)
				CASE
					WHEN o.preferred_occupants_count IS NULL OR u.occupants_count IS NULL THEN 20
					WHEN u.occupants_count <= o.preferred_occupants_count THEN 20
					ELSE 0
				END +
				-- Noise level (max 20)
				CASE
					WHEN o.preferred_noise_lvl IS NULL OR u.noise_lvl IS NULL THEN 20
					WHEN o.preferred_noise_lvl::text = 'quiet' AND u.noise_lvl = 'quiet' THEN 20
					WHEN o.preferred_noise_lvl::text = 'quiet' AND u.noise_lvl = 'normal' THEN 10
					WHEN o.preferred_noise_lvl::text = 'quiet' AND u.noise_lvl = 'loud' THEN 0
					WHEN o.preferred_noise_lvl::text = 'normal' AND u.noise_lvl = 'quiet' THEN 20
					WHEN o.preferred_noise_lvl::text = 'normal' AND u.noise_lvl = 'normal' THEN 20
					WHEN o.preferred_noise_lvl::text = 'normal' AND u.noise_lvl = 'loud' THEN 0
					WHEN o.preferred_noise_lvl::text = 'loud' AND u.noise_lvl = 'quiet' THEN 20
					WHEN o.preferred_noise_lvl::text = 'loud' AND u.noise_lvl = 'normal' THEN 20
					WHEN o.preferred_noise_lvl::text = 'loud' AND u.noise_lvl = 'loud' THEN 20
					ELSE 0
				END +
				-- Works from home (max 20)
				CASE
					WHEN o.preferred_works_from_home IS NULL OR u.works_from_home IS NULL THEN 20
					WHEN u.works_from_home = o.preferred_works_from_home THEN 20
					ELSE 0
				END +
				-- Alcohol (max 20)
				CASE
					WHEN o.preferred_alcohol IS NULL OR u.alcohol IS NULL THEN 20
					WHEN o.preferred_alcohol::text = 'never' AND u.alcohol = 'never' THEN 20
					WHEN o.preferred_alcohol::text = 'never' AND u.alcohol = 'rare' THEN 10
					WHEN o.preferred_alcohol::text = 'never' AND u.alcohol = 'regular' THEN 0
					WHEN o.preferred_alcohol::text = 'rare' AND u.alcohol = 'never' THEN 20
					WHEN o.preferred_alcohol::text = 'rare' AND u.alcohol = 'rare' THEN 20
					WHEN o.preferred_alcohol::text = 'rare' AND u.alcohol = 'regular' THEN 0
					WHEN o.preferred_alcohol::text = 'regular' AND u.alcohol = 'never' THEN 20
					WHEN o.preferred_alcohol::text = 'regular' AND u.alcohol = 'rare' THEN 20
					WHEN o.preferred_alcohol::text = 'regular' AND u.alcohol = 'regular' THEN 20
					ELSE 0
				END +
				-- Age min (max 20)
				CASE
					WHEN o.preferred_age_min IS NULL OR u.age_min IS NULL THEN 20
					WHEN u.age_min >= o.preferred_age_min THEN 20
					WHEN u.age_min < o.preferred_age_min THEN 10
					ELSE 0
				END +
				-- Age max (max 20)
				CASE
					WHEN o.preferred_age_max IS NULL OR u.age_max IS NULL THEN 20
					WHEN u.age_max <= o.preferred_age_max THEN 20
					WHEN u.age_max > o.preferred_age_max THEN 10
					ELSE 0
				END
			) AS relevance_sum
		FROM tg_house_offer o
		CROSS JOIN user_flags u
		WHERE o.id = $1::bigint
	`

	args := []any{
		offerId,                  // $1
		userFlags.Smoking,        // $2
		userFlags.Sex,            // $3
		userFlags.Children,       // $4
		userFlags.Pets,           // $5
		userFlags.OccupantsCount, // $6
		userFlags.NoiseLvl,       // $7
		userFlags.WorksFromHome,  // $8
		userFlags.Alcohol,        // $9
		userFlags.AgeMin,         // $10
		userFlags.AgeMax,         // $11
	}

	var relevanceSum int
	err = r.connPool.QueryRow(ctx, query, args...).Scan(&relevanceSum)
	if err != nil {
		return 0, err
	}

	relevancePercent = (relevanceSum * 100) / 200
	return relevancePercent, nil
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

func (r OffersRepo) CreateOffer(ctx context.Context, offer model.HouseOfferCreate) (id int64, err error) {
	const maxOffersCount = 1
	const maxOffersCountPremium = 10

	err = r.transaction(ctx, func(tx pgx.Tx) error {
		// Проверяем, есть ли у пользователя премиум, чтобы определить лимит объявлений
		hasPremium, err := r.premiumRepo.checkPremiumTx(ctx, tx, offer.OwnerId)
		if err != nil {
			return err
		}

		// Если есть премиум, то повышаем лимит объявлений до 10
		offersLimit := maxOffersCount
		if hasPremium {
			offersLimit = maxOffersCountPremium
		}

		// Получаем текущее количество объявлений
		offersCount, err := r.countOffersTx(ctx, tx, offer.OwnerId)
		if err != nil {
			return err
		}

		// Проверяем, не превысили ли лимит имеющихся объявлений
		if offersCount == offersLimit {
			return errors.New("failed to create offer: max offers count exceeded")
		}

		// Всё ок - создаём объявление
		id, err = r.createOfferTx(ctx, tx, offer)
		return err
	})

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
			preferred_sex = $10,
			flag_processing = FALSE
		WHERE id = $11
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
		prefs.Sex,
		offerId,
	)

	return err
}

func (r OffersRepo) transaction(ctx context.Context, f func(tx pgx.Tx) error) error {
	tx, err := r.connPool.Begin(ctx)
	if err != nil {
		return err
	}

	// Rollback
	defer func() {
		rbErr := tx.Rollback(ctx)
		if rbErr != nil {
			r.logger.Error("failed to rollback transaction", "error", rbErr)
		}
	}()

	err = f(tx)
	if err != nil {
		return err
	}

	return tx.Commit(ctx)
}

func (r OffersRepo) countOffersTx(ctx context.Context, tx pgx.Tx, userId int64) (count int, err error) {
	query := `
		SELECT COUNT(*)
		FROM tg_house_offer
		WHERE owner_id = $1
	`
	row := tx.QueryRow(ctx, query, userId)
	err = row.Scan(&count)
	return count, err
}

func (r OffersRepo) createOfferTx(ctx context.Context, tx pgx.Tx, offer model.HouseOfferCreate) (id int64, err error) {
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

	err = tx.QueryRow(
		ctx,
		query,
		offer.OwnerId,
		offer.Title,
		offer.Description,
		offer.City,
		offer.District,
		offer.Price,
		offer.MediaFiles,
	).Scan(&id)

	return id, err
}

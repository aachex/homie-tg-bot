package premium

import (
	"context"
	"homie-api/internal/model"
	"homie-api/internal/repository/postgres"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

const Unlimited = -1

type Repository struct {
	connPool *pgxpool.Pool
}

func NewRepository(connPool *pgxpool.Pool) *Repository {
	return &Repository{
		connPool: connPool,
	}
}

func (r Repository) UserLimits(ctx context.Context, userId int64) (limits model.UserLimits, err error) {
	return r.UserLimitsTx(ctx, r.connPool, userId)
}

func (r Repository) PremiumData(ctx context.Context, userId int64) (premData model.PremiumData, err error) {
	return r.PremiumDataTx(ctx, r.connPool, userId)
}

func (r *Repository) RenewPremium(ctx context.Context, userId int64, daysCount int) (premData model.PremiumData, err error) {
	query := `
		INSERT INTO premium (user_id, until)
		VALUES ($1, NOW() + $2 * INTERVAL '1 day')
		ON CONFLICT (user_id) DO
		UPDATE SET
			until = premium.until + $2 * INTERVAL '1 day'
		WHERE premium.user_id = $1
		RETURNING until
	`

	row := r.connPool.QueryRow(ctx, query, userId, daysCount)
	err = row.Scan(&premData.Until)
	if err != nil {
		return model.PremiumData{}, err
	}
	premData.IsPremium = true

	return premData, err
}

func (r Repository) UserLimitsTx(ctx context.Context, tx postgres.RowQueryer, userId int64) (limits model.UserLimits, err error) {
	// userId = 1 это специальный юзер, который создаёт мок-объявления.
	// Поэтому их у него может быть бесконечно, но лайкать он ничего не может.
	if userId == 1 {
		return model.UserLimits{
			PremiumData: model.PremiumData{
				IsPremium: true,
				Until:     time.Now().Add(time.Hour * 100),
			},
			MaxOffersCount: Unlimited,
			MaxLikesPerDay: 0,
		}, nil
	}

	limits.PremiumData, err = r.PremiumDataTx(ctx, tx, userId)
	if err != nil {
		return model.UserLimits{}, err
	}

	// Максимальное количество объявлений
	limits.MaxOffersCount = 1
	// Максимальное количество лайков в день
	limits.MaxLikesPerDay = 10

	// Повышаем лимиты если есть премиум
	if limits.IsPremium {
		limits.MaxOffersCount = 10
		limits.MaxLikesPerDay = Unlimited
	}

	return limits, nil
}

func (r Repository) PremiumDataTx(ctx context.Context, tx postgres.RowQueryer, userId int64) (premiumData model.PremiumData, err error) {
	if tx == nil {
		tx = r.connPool
	}

	query := `
		SELECT
			now() < until as is_premium,
			until
		FROM premium
		WHERE user_id = $1
	`
	row := tx.QueryRow(ctx, query, userId)
	err = row.Scan(&premiumData.IsPremium, &premiumData.Until)
	return premiumData, err
}

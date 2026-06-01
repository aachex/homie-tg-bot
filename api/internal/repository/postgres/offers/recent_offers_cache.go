package offers

import (
	"log/slog"
	"slices"
	"sync"
	"time"
)

// recentOffersCache хранит ID объявлений, которые недавно были показаны пользователю.
// Нужен для того, чтобы одинаковые объявления не попадались слишком часто.
type recentOffersCache struct {
	logger        *slog.Logger
	mu            sync.RWMutex
	recent        map[int64][]int64 // user_id -> []offer_id
	limit         int
	ttl           time.Duration
	stopCleanupCh chan struct{}
}

func newRecentOffersCache(logger *slog.Logger, limit int, ttl time.Duration) *recentOffersCache {
	cache := recentOffersCache{
		logger: logger,
		recent: map[int64][]int64{},
		limit:  limit,
		ttl:    ttl,
	}

	if ttl != 0 {
		go cache.startCleanup()
	}

	return &cache
}

func (c *recentOffersCache) Add(userID, offerID int64) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if _, ok := c.recent[userID]; !ok {
		c.recent[userID] = []int64{}
	}

	c.recent[userID] = append(c.recent[userID], offerID)
	if len(c.recent[userID]) > c.limit {
		c.recent[userID] = c.recent[userID][1:]
	}
}

func (c *recentOffersCache) Contains(userID, offerID int64) bool {
	c.mu.Lock()
	defer c.mu.Unlock()

	return slices.Contains(c.recent[userID], offerID)
}

func (c *recentOffersCache) Get(userID int64) []int64 {
	c.mu.RLock()
	defer c.mu.RUnlock()

	recentOffers, ok := c.recent[userID]
	if !ok {
		return []int64{}
	}

	return recentOffers
}

func (c *recentOffersCache) Stop() {
	close(c.stopCleanupCh)
}

func (c *recentOffersCache) startCleanup() {
	ticker := time.NewTicker(c.ttl)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			c.cleanup()
			c.logger.Info("cache cleanup completed")
		case <-c.stopCleanupCh:
			c.logger.Info("cache cleanup stopped")
			return
		}
	}
}

func (c *recentOffersCache) cleanup() {
	c.mu.Lock()
	defer c.mu.Unlock()

	// TODO: дописать
	for k := range c.recent {
		delete(c.recent, k)
	}
}

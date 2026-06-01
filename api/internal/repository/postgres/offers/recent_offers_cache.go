package offers

import (
	"slices"
	"sync"
	"time"
)

type recentOffersCache struct {
	mu     sync.RWMutex
	recent map[int64][]int64 // user_id -> []offer_id
	limit  int
	ttl    time.Duration
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

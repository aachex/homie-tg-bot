package cors

import (
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

// CheckKeyMiddleware проверяет API ключ из заголовка.
func CheckKeyMiddleware() gin.HandlerFunc {
	validKey := os.Getenv("VALID_KEY")

	return func(ctx *gin.Context) {
		providedKey := ctx.GetHeader("X-API-Key")

		if providedKey != validKey {
			ctx.AbortWithStatusJSON(http.StatusForbidden, gin.H{
				"error": "invalid api key",
			})
			return
		}

		ctx.Next()
	}
}

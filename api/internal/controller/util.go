package controller

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type defaultResp struct {
	StatusCode int    `json:"status_code"`
	Message    string `json:"message"`
}

func controllerError(ctx *gin.Context, err error, code int) {
	ctx.AbortWithStatusJSON(code, defaultResp{
		StatusCode: code,
		Message:    err.Error(),
	})
}

func Ping(ctx *gin.Context) {
	ctx.JSON(http.StatusOK, defaultResp{
		StatusCode: http.StatusOK,
		Message:    "pong",
	})
}

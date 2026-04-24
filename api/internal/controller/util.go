package controller

import "github.com/gin-gonic/gin"

type defaultResp struct {
	StatusCode int    `json:"statusCode"`
	Message    string `json:"message"`
}

func controllerError(ctx *gin.Context, err error, code int) {
	ctx.AbortWithStatusJSON(code, defaultResp{
		StatusCode: code,
		Message:    err.Error(),
	})
}

package llm

import (
	"context"
	"encoding/json"
	"fmt"
	"homie-api/internal/model"
	"io"
	"log/slog"
	"os"
	"strings"

	openai "github.com/sashabaranov/go-openai"
)

// Client клиент для взаимодействия с OpenRouter через go-openai
type Client struct {
	client *openai.Client
	logger *slog.Logger
	model  string
}

// NewClient создаёт новый клиент OpenRouter
func NewClient(logger *slog.Logger, apiKey string, model string) *Client {
	config := openai.DefaultConfig(apiKey)
	config.BaseURL = "https://openrouter.ai/api/v1"

	return &Client{
		client: openai.NewClientWithConfig(config),
		logger: logger,
		model:  model,
	}
}

// ExtractUserFlags извлекает флаги пользователя из текста
func (c *Client) ExtractUserFlags(ctx context.Context, text string) (model.UserFlags, error) {
	if text == "" {
		c.logger.Warn("empty text provided for flag extraction")
		return model.UserFlags{}, nil
	}

	systemPrompt, err := readSystemPrompt()
	if err != nil {
		return model.UserFlags{}, err
	}

	userPrompt := "Текст пользователя: " + text

	resp, err := c.client.CreateChatCompletion(ctx, openai.ChatCompletionRequest{
		Model: c.model,
		Messages: []openai.ChatCompletionMessage{
			{Role: openai.ChatMessageRoleSystem, Content: systemPrompt},
			{Role: openai.ChatMessageRoleUser, Content: userPrompt},
		},
		ResponseFormat: &openai.ChatCompletionResponseFormat{
			Type: openai.ChatCompletionResponseFormatTypeJSONObject,
		},
		Temperature: 0.1,
	})
	if err != nil {
		c.logger.Error("LLM request failed", "error", err)
		return model.UserFlags{}, err
	}

	if len(resp.Choices) == 0 {
		return model.UserFlags{}, fmt.Errorf("no choices in response")
	}

	content := resp.Choices[0].Message.Content
	content = cleanJSONResponse(content)

	c.logger.Info("successfully fetched LLM reponse", "text", content)

	var flags model.UserFlags
	if err := json.Unmarshal([]byte(content), &flags); err != nil {
		c.logger.Error("failed to parse JSON", "content", content, "error", err)
		return model.UserFlags{}, err
	}

	c.logger.Info("flags extracted", "flags", flags)
	return flags, nil
}

func readSystemPrompt() (string, error) {
	file, err := os.Open("internal/llm/system_prompt.txt")
	if err != nil {
		return "", err
	}

	b, err := io.ReadAll(file)
	if err != nil {
		return "", err
	}

	return string(b), nil
}

func cleanJSONResponse(content string) string {
	// Ищем первый '{' и последний '}'
	start := strings.Index(content, "{")
	end := strings.LastIndex(content, "}")
	if start != -1 && end != -1 && end > start {
		return content[start : end+1]
	}
	return content
}

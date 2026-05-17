package llm

import (
	"context"
	"encoding/json"
	"fmt"
	"homie-api/internal/model"
	"log/slog"

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
func (c *Client) ExtractUserFlags(ctx context.Context, text string) (*model.UserFlags, error) {
	if text == "" {
		c.logger.Warn("empty text provided for flag extraction")
		return &model.UserFlags{}, nil
	}

	systemPrompt := `Ты — система извлечения информации. Твоя задача — вернуть ТОЛЬКО JSON. Никакого текста до или после JSON.

Извлеки из текста пользователя следующие поля:

- smoking: true/false (null если не указано)
- pets: "none" | "cats" | "dogs" | "other" | null
- children: "none" | "one" | "two+" | "planning" | null
- occupants_count: число (null если не указано)
- noise_lvl: "quiet" | "normal" | "loud" | null
- works_from_home: true/false | null
- alcohol: "never" | "rare" | "regular" | null
- age_min: число (минимальный возраст) | null
- age_max: число (максимальный возраст) | null

Правила:
1. Если информация явно не указана — ставь null
2. "двое детей" → children: "two+"
3. "один ребёнок" → children: "one"
4. "планируем ребёнка" → children: "planning"
5. "живу один" → occupants_count: 1
6. "снимаем вдвоём с девушкой" → occupants_count: 2
7. "тихий" → noise_lvl: "quiet"
8. "работаю из дома" → works_from_home: true
9. "не пью" → alcohol: "never"
10. "мне 25 лет" → age_min: 25, age_max: 25

Пример ответа:
{"smoking": false, "pets": "cats", "children": null, "occupants_count": 1, "noise_lvl": "quiet", "works_from_home": true, "alcohol": "never", "age_min": 25, "age_max": 30}`

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
		return nil, err
	}

	if len(resp.Choices) == 0 {
		return nil, fmt.Errorf("no choices in response")
	}

	content := resp.Choices[0].Message.Content

	var flags model.UserFlags
	if err := json.Unmarshal([]byte(content), &flags); err != nil {
		c.logger.Error("failed to parse JSON", "content", content, "error", err)
		return nil, err
	}

	c.logger.Info("flags extracted", "flags", flags)
	return &flags, nil
}

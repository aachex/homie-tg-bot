-- +goose Up
-- +goose StatementBegin

-- Вставка 1: Семейная пара с ребёнком, без животных, тихие
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Светлая 2-комнатная квартира', 'Рядом с парком и школой', 45000, 5297482606, 
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Новогиреево',
    FALSE, 'one', 'none', 3,
    'quiet', FALSE, 'never',
    25, 40, NULL, TRUE
);

-- Вставка 2: Одинокая девушка, работающая в офисе
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Уютная студия в центре', 'Всё необходимое для комфортной жизни', 55000, 5297482606,
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Центральный',
    FALSE, 'none', 'none', 1,
    'quiet', FALSE, 'never',
    25, 35, 'female', TRUE
);

-- Вставка 3: Два IT-шника, работающих из дома
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Просторная трёшка', 'Отличный интернет и зоны для работы', 70000, 5297482606,
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Дмитровский',
    NULL, 'none', 'none', 2,
    'normal', TRUE, 'rare',
    25, 35, 'male', TRUE
);

-- Вставка 4: Семья с двумя детьми и собакой
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Большая квартира для семьи', 'Детский сад и школа рядом', 80000, 5297482606,
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Ясенево',
    FALSE, 'two+', 'dogs', 4,
    'normal', NULL, 'rare',
    30, 45, NULL, TRUE
);

-- Вставка 5: Одинокий мужчина, работающий вахтой
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Студия с современным ремонтом', 'Рядом ТЦ и транспорт', 35000, 5297482606,
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Медведково',
    FALSE, 'none', 'none', 1,
    'loud', NULL, 'regular',
    25, 50, 'male', TRUE
);

-- Вставка 6: Молодая пара, планирующая ребёнка
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Уютная однушка с балконом', 'Рядом метро и магазины', 40000, 5297482606,
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Кузьминки',
    FALSE, 'planning', 'cats', 2,
    'quiet', TRUE, 'never',
    25, 30, NULL, TRUE
);

-- Вставка 7: Женщина с кошкой, работающая удалённо
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Стильная студия с видом на парк', 'Для комфортной жизни и работы', 50000, 5297482606,
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Сокол',
    FALSE, 'none', 'cats', 1,
    'quiet', TRUE, 'never',
    30, 45, 'female', TRUE
);

-- Вставка 8: Двое мужчин, работающих в офисе
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Двушка с раздельными комнатами', 'Идеально для друзей или коллег', 48000, 5297482606,
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Аэропорт',
    TRUE, 'none', 'none', 2,
    'normal', FALSE, 'regular',
    25, 35, 'male', TRUE
);

-- Вставка 9: Пара с собакой, без детей
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Просторная двушка с выходом во двор', 'Для семьи с питомцем', 52000, 5297482606,
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Бабушкинский',
    FALSE, 'none', 'dogs', 2,
    'normal', FALSE, 'rare',
    30, 40, NULL, TRUE
);

-- Вставка 10: Мужчина с хомяком, шумный, работает в офисе
INSERT INTO tg_house_offer (
    title, description, price, owner_id, media_files, city, district,
    preferred_smoking, preferred_children, preferred_pets, preferred_occupants_count,
    preferred_noise_lvl, preferred_works_from_home, preferred_alcohol,
    preferred_age_min, preferred_age_max, preferred_sex, is_active
) VALUES (
    'Удобная однушка', 'Неподалёку транспортная развязка', 38000, 5297482606,
    ARRAY['AgACAgIAAxkDAAIu4Gn8okuf0gJ4yB7fm1Xx0dwEaImkAAKnGWsb3NjoS9Z_M379BUrBAQADAgADeAADOwQ'],
    'Москва', 'Кунцево',
    TRUE, 'none', 'other', 1,
    'loud', FALSE, 'regular',
    25, 35, 'male', TRUE
);

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

DELETE FROM tg_house_offer WHERE owner_id = 5297482606;

-- +goose StatementEnd
-- Удаляем существующую базу данных (для чистой установки)
DROP DATABASE IF EXISTS metal_quality_control;
CREATE DATABASE metal_quality_control
    ENCODING 'UTF8'
    LC_COLLATE 'ru_RU.UTF-8'
    LC_CTYPE 'ru_RU.UTF-8'
    TEMPLATE template0;

\c metal_quality_control;

-- ============================================
-- 1. ТАБЛИЦЫ ДЛЯ АДМИНИСТРИРОВАНИЯ (Задание 2c)
-- ============================================

-- Таблица ролей пользователей
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{"read": true, "write": false, "delete": false, "admin": false}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    hashed_password VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. ОСНОВНЫЕ ТАБЛИЦЫ ПРЕДМЕТНОЙ ОБЛАСТИ
-- ============================================

-- Виды металлопроката
CREATE TABLE product_types (
    id SERIAL PRIMARY KEY,
    type_code VARCHAR(50) UNIQUE NOT NULL,
    type_name VARCHAR(200) NOT NULL,
    standard VARCHAR(100), -- ГОСТ, ТУ, ISO
    thickness_range VARCHAR(100), -- диапазон толщин
    width_range VARCHAR(100), -- диапазон ширины
    material_grade VARCHAR(100), -- марка стали
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Производственные партии
CREATE TABLE production_batches (
    id SERIAL PRIMARY KEY,
    batch_number VARCHAR(100) UNIQUE NOT NULL,
    product_type_id INTEGER REFERENCES product_types(id) ON DELETE RESTRICT,
    production_date DATE NOT NULL,
    furnace_number VARCHAR(50),
    shift_number INTEGER,
    total_weight_kg DECIMAL(10, 2),
    total_length_m DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'в производстве', -- в производстве, произведено, отгружено
    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
    metadata JSONB, -- дополнительные данные
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Типы дефектов
CREATE TABLE defect_types (
    id SERIAL PRIMARY KEY,
    defect_code VARCHAR(50) UNIQUE NOT NULL,
    defect_name VARCHAR(200) NOT NULL,
    category VARCHAR(100), -- поверхностные, внутренние, геометрические
    severity_level VARCHAR(50), -- критический, значительный, незначительный
    description TEXT,
    measurement_unit VARCHAR(50), -- мм, %, ед.
    threshold_value DECIMAL(10, 4), -- пороговое значение
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Контрольные точки/зоны контроля
CREATE TABLE inspection_points (
    id SERIAL PRIMARY KEY,
    point_name VARCHAR(200) NOT NULL,
    point_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    equipment_type VARCHAR(100), -- тип оборудования контроля
    location_in_line VARCHAR(100), -- расположение на линии
    coordinates JSONB, -- координаты на схеме линии
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Результаты контроля (основная таблица)
CREATE TABLE inspection_results (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER REFERENCES production_batches(id) ON DELETE CASCADE,
    inspection_point_id INTEGER REFERENCES inspection_points(id),
    inspection_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    inspector_id INTEGER REFERENCES users(id), -- кто провел контроль
    inspector_name VARCHAR(200), -- или имя системы
    measurement_data JSONB NOT NULL, -- основные данные измерений
    -- Пример measurement_data:
    -- {
    --   "thickness_mm": 5.2,
    --   "width_mm": 1250.5,
    --   "temperature_c": 850,
    --   "hardness_hb": 220,
    --   "roughness_ra": 1.2,
    --   "sensor_readings": [0.1, 0.15, 0.12]
    -- }
    is_defect_detected BOOLEAN DEFAULT FALSE,
    defect_count INTEGER DEFAULT 0,
    overall_verdict VARCHAR(50) DEFAULT 'соответствует', -- соответствует, условно соответствует, не соответствует
    status VARCHAR(50) DEFAULT 'обработка', -- обработка, проверено, утверждено
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Детализация дефектов
CREATE TABLE defect_details (
    id SERIAL PRIMARY KEY,
    inspection_result_id INTEGER REFERENCES inspection_results(id) ON DELETE CASCADE,
    defect_type_id INTEGER REFERENCES defect_types(id),
    defect_location JSONB, -- координаты дефекта
    -- Пример: {"x_mm": 150.5, "y_mm": 45.0, "length_mm": 2.3, "width_mm": 0.5}
    severity DECIMAL(5, 2) CHECK (severity >= 0 AND severity <= 10),
    size_mm DECIMAL(10, 2), -- размер дефекта
    image_path VARCHAR(500), -- путь к изображению
    is_repaired BOOLEAN DEFAULT FALSE,
    repair_method VARCHAR(200),
    repair_date TIMESTAMPTZ,
    repair_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. ИНДЕКСЫ
-- ============================================

-- Индексы для таблицы production_batches
CREATE INDEX idx_batch_number ON production_batches(batch_number);
CREATE INDEX idx_batch_production_date ON production_batches(production_date);
CREATE INDEX idx_batch_status ON production_batches(status);

-- Индексы для таблицы inspection_results
CREATE INDEX idx_inspection_batch_id ON inspection_results(batch_id);
CREATE INDEX idx_inspection_time ON inspection_results(inspection_time);
CREATE INDEX idx_inspection_verdict ON inspection_results(overall_verdict);
CREATE INDEX idx_inspection_status ON inspection_results(status);
CREATE INDEX idx_inspection_defect_detected ON inspection_results(is_defect_detected);

-- Индексы для таблицы defect_details
CREATE INDEX idx_defect_inspection_id ON defect_details(inspection_result_id);
CREATE INDEX idx_defect_type_id ON defect_details(defect_type_id);
CREATE INDEX idx_defect_severity ON defect_details(severity);

-- Индекс для JSONB поля (если часто фильтруем по thickness)
CREATE INDEX idx_measurement_thickness ON inspection_results USING gin ((measurement_data->'thickness_mm'));

-- Индекс для пользователей
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_role ON users(role_id);

-- ============================================
-- 4. НАЧАЛЬНЫЕ ДАННЫЕ (seed data)
-- ============================================

-- Вставляем роли
INSERT INTO roles (role_name, description, permissions) VALUES
('admin', 'Администратор системы', '{"read": true, "write": true, "delete": true, "admin": true}'),
('quality_manager', 'Менеджер по качеству', '{"read": true, "write": true, "delete": true, "admin": false}'),
('operator', 'Оператор контроля', '{"read": true, "write": true, "delete": false, "admin": false}'),
('viewer', 'Наблюдатель', '{"read": true, "write": false, "delete": false, "admin": false}');

-- Тестовые пользователи (пароли: password123 - нужно захешировать в приложении)
INSERT INTO users (username, email, full_name, hashed_password, role_id, is_active) VALUES
('admin_user', 'admin@factory.ru', 'Иванов Иван Иванович', 'hashed_password_here', 1, TRUE),
('quality1', 'quality@factory.ru', 'Петрова Мария Сергеевна', 'hashed_password_here', 2, TRUE),
('operator1', 'operator@factory.ru', 'Сидоров Алексей Петрович', 'hashed_password_here', 3, TRUE);

-- Виды продукции
INSERT INTO product_types (type_code, type_name, standard, thickness_range, width_range, material_grade, description) VALUES
('HRC-01', 'Лист горячекатаный', 'ГОСТ 19903-2015', '1.5-12 мм', '1000-2000 мм', 'Ст3сп', 'Горячекатаный лист общего назначения'),
('CRC-02', 'Лист холоднокатаный', 'ГОСТ 19904-2015', '0.5-3 мм', '1000-1500 мм', '08пс', 'Холоднокатаный лист для штамповки'),
('PIPE-03', 'Труба профильная', 'ГОСТ 8645-68', '1.5-8 мм', '20x20-100x100 мм', 'Ст20', 'Квадратная профильная труба'),
('BEAM-04', 'Балка двутавровая', 'ГОСТ 8239-89', '8-40 мм', '100-600 мм', 'Ст3пс', 'Двутавровая балка для строительства');

-- Типы дефектов
INSERT INTO defect_types (defect_code, defect_name, category, severity_level, description, measurement_unit, threshold_value) VALUES
('SCRATCH', 'Царапина', 'поверхностные', 'незначительный', 'Поверхностная царапина', 'мм', 0.1),
('CRACK', 'Трещина', 'поверхностные', 'критический', 'Поверхностная или сквозная трещина', 'мм', 0.01),
('INCLUSION', 'Включение', 'внутренние', 'значительный', 'Инородное включение в материале', 'мм', 0.5),
('WARP', 'Коробление', 'геометрические', 'значительный', 'Отклонение от плоскостности', 'мм/м', 3.0),
('PIT', 'Раковина', 'поверхностные', 'значительный', 'Поверхностная раковина', 'мм', 1.0),
('SCALE', 'Окалина', 'поверхностные', 'незначительный', 'Неудаленная окалина', 'ед.', 5);

-- Контрольные точки
INSERT INTO inspection_points (point_name, point_code, description, equipment_type, location_in_line) VALUES
('Входной контроль', 'IPC-01', 'Контроль сырья и заготовок', 'Ультразвуковой дефектоскоп', 'начало линии'),
('Контроль толщины', 'IPC-02', 'Измерение толщины проката', 'Лазерный толщиномер', 'после клети'),
('Контроль поверхности', 'IPC-03', 'Визуальный и оптический контроль поверхности', 'Система машинного зрения', 'выход линии'),
('Контроль геометрии', 'IPC-04', 'Измерение плоскостности и размеров', 'Лазерный сканер', 'конец линии');

-- Тестовые производственные партии
INSERT INTO production_batches (batch_number, product_type_id, production_date, furnace_number, shift_number, total_weight_kg, total_length_m, status, quality_rating) VALUES
('BATCH-2024-05-001', 1, '2024-05-15', 'FURNACE-3', 1, 25000.00, 500.00, 'произведено', 4),
('BATCH-2024-05-002', 2, '2024-05-16', 'FURNACE-1', 2, 18000.00, 1200.00, 'в производстве', 3),
('BATCH-2024-05-003', 3, '2024-05-17', 'FURNACE-2', 1, 8000.00, 800.00, 'отгружено', 5);

-- Тестовые результаты контроля
INSERT INTO inspection_results (batch_id, inspection_point_id, inspector_id, inspector_name, measurement_data, is_defect_detected, defect_count, overall_verdict, status) VALUES
(1, 2, 3, 'Автоматическая система', '{"thickness_mm": 5.2, "width_mm": 1250.5, "temperature_c": 850, "hardness_hb": 220, "roughness_ra": 1.2}', FALSE, 0, 'соответствует', 'утверждено'),
(1, 3, 3, 'Автоматическая система', '{"surface_quality": "good", "gloss_level": 85, "color_uniformity": 92}', TRUE, 2, 'условно соответствует', 'проверено'),
(2, 2, 3, 'Сидоров А.П.', '{"thickness_mm": 2.1, "width_mm": 1200.0, "temperature_c": 720, "hardness_hb": 180}', FALSE, 0, 'соответствует', 'обработка');

-- Тестовые дефекты
INSERT INTO defect_details (inspection_result_id, defect_type_id, defect_location, severity, size_mm) VALUES
(2, 1, '{"x_mm": 150.5, "y_mm": 45.0, "length_mm": 2.3, "width_mm": 0.05}', 2.5, 2.3),
(2, 6, '{"x_mm": 320.0, "y_mm": 120.5, "length_mm": 5.0, "width_mm": 3.0}', 1.0, 5.0);

-- ============================================
-- 5. ТРИГГЕРЫ И ФУНКЦИИ
-- ============================================

-- Автоматическое обновление updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Применяем триггеры к таблицам
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_types_updated_at BEFORE UPDATE ON product_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_production_batches_updated_at BEFORE UPDATE ON production_batches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inspection_results_updated_at BEFORE UPDATE ON inspection_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Функция для автоматического подсчета дефектов
CREATE OR REPLACE FUNCTION update_defect_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'DELETE' THEN
        UPDATE inspection_results
        SET defect_count = (
            SELECT COUNT(*) 
            FROM defect_details 
            WHERE inspection_result_id = COALESCE(NEW.inspection_result_id, OLD.inspection_result_id)
        ),
        is_defect_detected = (
            SELECT COUNT(*) > 0
            FROM defect_details 
            WHERE inspection_result_id = COALESCE(NEW.inspection_result_id, OLD.inspection_result_id)
        )
        WHERE id = COALESCE(NEW.inspection_result_id, OLD.inspection_result_id);
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_defect_count_trigger
AFTER INSERT OR DELETE ON defect_details
FOR EACH ROW EXECUTE FUNCTION update_defect_count();

-- ============================================
-- 6. ПРАВА ДОСТУПА
-- ============================================

-- Создаем отдельного пользователя для приложения (для безопасности)
CREATE USER app_user WITH PASSWORD 'secure_password_123';
GRANT CONNECT ON DATABASE metal_quality_control TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- ============================================
-- СООБЩЕНИЕ ОБ УСПЕШНОМ СОЗДАНИИ
-- ============================================
DO $$
BEGIN
    RAISE NOTICE 'База данных "metal_quality_control" успешно создана!';
    RAISE NOTICE 'Таблиц создано: 8';
    RAISE NOTICE 'Тестовых записей добавлено:';
    RAISE NOTICE '  - Ролей: 4';
    RAISE NOTICE '  - Пользователей: 3';
    RAISE NOTICE '  - Типов продукции: 4';
    RAISE NOTICE '  - Типов дефектов: 6';
    RAISE NOTICE '  - Контрольных точек: 4';
    RAISE NOTICE '  - Производственных партий: 3';
    RAISE NOTICE '  - Результатов контроля: 3';
    RAISE NOTICE '  - Дефектов: 2';
END $$;
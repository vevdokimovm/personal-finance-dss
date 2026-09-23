"""Обнаружение смены режима дохода — как ТРИГГЕР ВОПРОСА, а не как переключатель
(WORK_QUEUE P2, M-108).

Замер Г43 на 500 портретах, история 12 месяцев: когда смена уровня действительно была,
байесовское онлайн-обнаружение находит её в 99,6 % случаев и снижает ошибку суммы за полгода
**с 0,186 до 0,019 — в десять раз**. Это самый большой одиночный выигрыш во всём файле.

🔴 И ровно у него самая высокая цена ошибки в другую сторону: чувствительный детектор
принимает декабрьскую премию за «новую жизнь» у **92–93 %** зарплатников и портит им прогноз
(0,233 против 0,076). Защита «новый режим не короче двух месяцев И медиана сдвинулась больше
чем на 15 %» снижает ложные тревоги до 29 %, но не до нуля — одной настройки, хорошей для
всех, на двенадцати точках не существует.

Отсюда контракт: детектор **не переключает** прогноз молча. Он возвращает подозрение,
продукт задаёт вопрос человеку, и только подтверждённый ответ меняет расчёт.
"""
from app.core.regime import detect_regime_change


class TestFindsRealShifts:
    def test_level_drop_is_detected(self):
        """Потеря дохода: девять месяцев по 100 000, затем четыре по 55 000."""
        history = [100_000.0] * 9 + [55_000.0] * 4
        found = detect_regime_change(history)
        assert found is not None
        assert found["changed_at"] >= 8
        assert found["direction"] == "down"
        assert found["new_level"] < found["old_level"]

    def test_level_rise_is_detected(self):
        history = [60_000.0] * 8 + [95_000.0] * 4
        found = detect_regime_change(history)
        assert found is not None
        assert found["direction"] == "up"


class TestDoesNotCryWolf:
    def test_december_bonus_is_not_a_new_life(self):
        """Один всплеск в конце ряда — премия, а не смена режима."""
        history = [80_000.0] * 11 + [160_000.0]
        assert detect_regime_change(history) is None

    def test_plain_noise_is_not_a_shift(self):
        history = [100_000.0, 96_000.0, 104_000.0, 99_000.0, 101_000.0,
                   97_000.0, 103_000.0, 100_000.0, 98_000.0, 102_000.0]
        assert detect_regime_change(history) is None

    def test_small_drift_below_threshold_is_ignored(self):
        """Сдвиг медианы меньше 15 % — не повод объявлять новую жизнь."""
        history = [100_000.0] * 7 + [92_000.0] * 5
        assert detect_regime_change(history) is None

    def test_short_history_gives_nothing(self):
        assert detect_regime_change([100_000.0, 50_000.0]) is None

    def test_one_month_regime_is_too_short_to_believe(self):
        """Новый режим короче двух месяцев не считается режимом."""
        history = [100_000.0] * 11 + [40_000.0]
        assert detect_regime_change(history) is None


class TestItIsAQuestionNotADecision:
    def test_result_carries_a_question_for_the_human(self):
        history = [100_000.0] * 9 + [55_000.0] * 4
        found = detect_regime_change(history)
        assert found is not None
        assert found["question"]
        assert "?" in found["question"]

    def test_confidence_is_reported_and_bounded(self):
        history = [100_000.0] * 9 + [55_000.0] * 4
        found = detect_regime_change(history)
        assert found is not None
        assert 0.0 < found["confidence"] <= 1.0

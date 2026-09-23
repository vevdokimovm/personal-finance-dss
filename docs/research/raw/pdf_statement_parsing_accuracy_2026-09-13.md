# Г20 — Точность парсера банковских PDF-выписок без машинного обучения

> Сырьё исследования. Снято 16.09.2026. Первичный материал дословно, выжимка — после.
> Каждый источник: URL, HTTP-код, размер, дата снятия. «Не добыто» — только с точной причиной.
> Канон модели, формулировку новизны и код продукта этот файл НЕ правит.

**Классификация запроса:** breadth-first — семь слабо связанных под-вопросов
(технический разбор PDF · открытые парсеры РФ · приёмы точности без ML · поведение
при нераспознанном · дедупликация · тестирование · право). Основной канал — GitHub API
(исходники открытых парсеров), вспомогательные — WebSearch/WebFetch/r.jina.ai, научные API.

**Вход (не переоткрывается, взято из Г5 и Г17):** у Сбера 20 форматов выписок
в открытом конвертере Sberbank2Excel, из них 5 новых только за 2026 год; состав колонок
зависит от типа счёта; у Райффайзена нет колонки «Категория», знак стоит внутри суммы,
в ячейке с датой встречается статус «В обработке»; у Сбера нет идентификатора операции —
повторный импорт не отличит дубли.

---

## 0. Что уже есть у нас в коде (исходная точка, снято с рабочего дерева 16.09.2026)

Файлы: `app/services/statement_parser.py` (934 строки), `app/services/statement_reconcile.py`
(385 строк), шаблоны-образцы `app/data/statement_templates/{sber,tinkoff,vtb,raiffeisen}.pdf`
плюс `.md`-расшифровки к каждому, `app/data/statement_templates/MANIFEST.md`.

Точки входа PDF: `parse_tinkoff_pdf`, `parse_vtb_pdf`, `parse_sber_pdf`,
`parse_raiffeisen_pdf`, диспетчер `parse_bank_pdf`, определение банка `detect_pdf_bank`,
отсев не-выписок `pdf_non_statement_reason` / `classify_non_statement`.

Библиотека одна: `pdfplumber`, импорт мягкий (`try/except ImportError`) — «без него
работает всё, кроме импорта PDF».

Учёт пропусков уже есть и осмыслен, дословно из шапки `statement_parser.py`:

```
# ── Учёт пропущенных строк ────────────────────────────────────────────────
# CSV не несёт контрольных сумм, поэтому сверить его с банком нечем. Но главный риск CSV —
# не неверная сумма, а МОЛЧАЛИВАЯ ПОТЕРЯ строки: на реальном файле в 12 788 строк пропажа
# полусотни незаметна. Поэтому каждая точка `continue` обязана назвать причину, а
# `statement_reconcile` отделяет законные пропуски (банк сам отклонил операцию) от наших
# промахов (сумму не разобрали).
SKIP_STATUS = 'операция отклонена банком'
SKIP_NO_AMOUNT = 'сумма не указана'
SKIP_BAD_AMOUNT = 'сумма не распознана'
SKIP_NO_DATE = 'дата не распознана'
SKIP_ZERO = 'нулевая сумма'
SKIP_SERVICE = 'служебная строка (не операция)'
SKIP_UNPARSED = 'строка не разобрана'
```

Сверка сальдо уже существует отдельным модулем `statement_reconcile.py`:
`_sber_declared`, `_vtb_declared`, `_tinkoff_declared`, `_raif_declared`,
`_raif_declared_count`, `_balance_delta`, `completeness_verdict`, `reconcile_statement`.
То есть слой самопроверки в продукте заложен — вопрос темы в том, полон ли он.

---

## П2. Открытые парсеры выписок российских банков — исходники и приёмы

### 2.1 Sberbank2Excel (Ev2geny) — разбор КОДА

Реквизиты снятия (16.09.2026, `curl -sk --http1.1` к `api.github.com` и
`raw.githubusercontent.com`, все ответы 200):

| Файл | URL (raw, ветка master) | Код | Байт |
|---|---|---|---|
| дерево репозитория | `api.github.com/repos/Ev2geny/Sberbank2Excel/git/trees/master?recursive=1` | 200 | — |
| `src/Sberbank2Excel/extractor.py` | `raw.githubusercontent.com/Ev2geny/Sberbank2Excel/master/...` | 200 | 4 314 |
| `extractors.py` | там же | 200 | 2 670 |
| `extractors_generic.py` | там же | 200 | 9 093 |
| `pdf2txtev.py` | там же | 200 | 7 510 |
| `utils.py` | там же | 200 | 5 380 |
| `sberbankPDFtext2Excel.py` | там же | 200 | 9 911 |
| `extractor_SBER_DEBIT_2603.py` | там же | 200 | 13 215 |
| `exceptions.py` | там же | 200 | 321 |
| `tests/sberbankPDF2Excel_test.py` | там же | 200 | 9 592 |
| `CONTRIBUTING.md` | там же | 200 | 11 152 |
| `README.md` | там же | 200 | 30 873 |

Репозиторий один (`search/repositories?q=Sberbank2Excel` → `total_count: 1`),
описание: «конвертация различных вариантов выписок сбербанка из формата PDF в формат Excel».

🔴 **Поправка к входной фактуре: форматов не 20, а 21.** В `extractors.py` на 16.09.2026
зарегистрирован 21 экстрактор, в таблице README — 21 строка. Из них с кодом года 26
(то есть 2026): `SBER_DEBIT_2603`, `SBER_PAYMENT_2604`, `SBER_SAVING_2604`,
`SBER_PAYMENT_DEBIT_2604b`, `SBER_CREDIT_2605` — **пять новых форматов за первые пять
месяцев 2026 года**. Цифра «5 новых за 2026» подтверждается, «20» устарела на один.

#### Архитектура: три слоя, разделённые жёстко

**Слой 1 — PDF → текст, собственный, не библиотечный.** Модуль `pdf2txtev.py`, дословно
из его docstring:

```
This module provides approximately the same functionality as pdfminer.six => pdfminer.high_level
But it allows to provide conversion of Sberbank statement without mixing lines.
The issue it works around is described here: https://github.com/pdfminer/pdfminer.six/issues/466
```

То есть автор **не смог** пользоваться готовым `pdfminer.high_level.extract_text` и переписал
его. Ключевой приём — сборка «виртуальных строк» по координатам и разделение колонок
**табуляцией**:

```python
def _PDFpage2txt(page:PDFPage, laparams = None) -> str:
    if laparams is None:
        laparams = LAParams(char_margin=0.001, line_margin=0.001, boxes_flow=None)
```

```python
    # Sorting input list in reverse order by bottom Y coordinate of the horizontal text box
    list_LTTextBoxHorizontal = sorted(list_LTTextBoxHorizontal, key=lambda box: box.y0, reverse=True)
    ...
    """ 
    If the LTTextBoxHorizontal top side (y1) is higher then the vertical middle of the previous 
    LTTextBoxHorizontal ([i-1]), then both current and previous LTTextBoxHorizontal are considered to be on the same 
    line/ row. In this case current LTTextBoxHorizontal element is added as the next element of the current row
    Otherwise current LTTextBoxHorizontal is added to a new line / row of the matrix
    """
    for i in range(1, len(list_LTTextBoxHorizontal)):
        vert_middle_prev_box = (list_LTTextBoxHorizontal[i-1].y0 + list_LTTextBoxHorizontal[i-1].y1)/2
        if list_LTTextBoxHorizontal[i].y1 > vert_middle_prev_box:
            matrix[-1].append(list_LTTextBoxHorizontal[i])
        else:
            matrix.append([list_LTTextBoxHorizontal[i]])

    matrix = [sorted(row, key=lambda box:box.x0) for row in matrix]
```

и затем `_matrix_2_txt(matrix, separator="\t")`. **Это ровно тот приём, о котором спрашивал
п.1 задания: кластеризация по координатам, но по Y — в строки, по X — только сортировка
внутри строки.** Порог склейки в строку: верх текущего бокса выше вертикальной середины
предыдущего. `char_margin=0.001, line_margin=0.001, boxes_flow=None` — то есть автор
**намеренно выключил** собственную группировку pdfminer и делает её сам.

Дальше весь разбор идёт по тексту с `\t`-разделителями:

```python
def split_Sberbank_line(line:str)->List[str]:
    """
    Разделяем Сбербанковсую строчку на кусочки данных. Разделяем используя symbol TAB
    """
    line_parts=re.split(r'\t',line)
    line_parts=list(filter(None,line_parts))
    return line_parts
```

🔴 **Ограничение приёма названо самим автором в CONTRIBUTING.md, дословно:**

> «Следует отметить, что т.к. Sberbank2Excel сначала преобразует PDF файл в промежуточный
> текстовый файл, то создавать новый модуль имеет практический смысл только для PDF формата,
> информация в котором представлена в виде виртульных строк. Это условие пока что выполняется
> для всех известных вариантов выписок Сбера, но может не выполняться для других банков,
> например похоже не выполняется для [ВТБ](https://github.com/Ev2geny/Sberbank2Excel/issues/37)»

То есть **текстовая нормализация Сбера на ВТБ не переносится** — и это прямо про наш
`parse_vtb_pdf`, который у нас сделан через табличный экстрактор `pdfplumber`, а не через текст.

**Слой 2 — абстрактный `Extractor` (ABC) с шестью обязательными методами.** Дословно
сигнатуры из `extractor.py`:

```python
class Extractor(ABC):
    def __init__(self, bank_text: str):
        self.bank_text = bank_text 

    @abstractmethod
    def check_specific_signatures(self):
        """Function is not expected to return any result, but is expected to raise 
        exceptions.InputFileStructureError() if the text is not supported"""

    @abstractmethod
    def get_period_balance(self) -> Decimal: ...
    @abstractmethod
    def split_text_on_entries(self)->list[str]: ...
    @abstractmethod
    def decompose_entry_to_dict(self, entry: str) -> dict | list[dict]: ...
    @abstractmethod
    def get_column_name_for_balance_calculation(self) -> str: ...
    @abstractmethod
    def get_columns_info(self)->dict: ...
```

🔴 Два метода из шести существуют **только ради самопроверки**: `get_period_balance()`
и `get_column_name_for_balance_calculation()`. Проверка сальдо тут не опция, а часть
контракта формата: каждый экстрактор обязан уметь сказать, какую колонку складывать и с
каким числом из шапки сравнивать.

Общий для всех формат-детектор — `check_support()`, конъюнкция трёх условий:

```python
    def check_support(self)->bool:
        try:
            self.check_specific_signatures()
            result = isinstance(self.get_period_balance(), Decimal) and len(self.split_text_on_entries()) > 0
            return result
        except exceptions.InputFileStructureError:
            return False
```

То есть формат считается «своим», только если (а) сработал отпечаток шапки, (б) баланс
периода извлёкся числом, (в) нашлась хотя бы одна транзакция. **Определение формата
совмещено с пробным разбором** — самый сильный приём во всём репозитории.

**Слой 3 — выбор экстрактора перебором, с запретом неоднозначности.** `extractors_generic.py`:

```python
def determine_extractor_auto(pdf_text:str) -> type:
    supported_extractors = [extractor for extractor in extractors_list if extractor(pdf_text).check_support()]

    if len(supported_extractors) == 0:
        raise exceptions.InputFileStructureError("Неизвecтный формат выписки, ни один из экстракторов не подходят")

    if len(supported_extractors) > 1 :
        raise exceptions.InputFileStructureError(f"Непонятный формат выписки. Больше чем один экстрактор говорят, "
                                                 f"что понимают его \n {[extractor.__name__ for extractor in supported_extractors]}")
    return supported_extractors[0]
```

🔴 **Ноль подходящих — отказ. Больше одного подходящего — тоже отказ.** Никакого
«возьмём первый подходящий» или «возьмём самый новый». Это прямой ответ на вопрос п.3
задания «как получают 100 % без ML»: не угадывать при неоднозначности.

#### Отпечаток формата: как выглядит `check_specific_signatures` на практике

Из `extractor_SBER_DEBIT_2603.py` (формат марта 2026), дословно:

```python
    def check_specific_signatures(self):
        test_sberbank = re.search(r'сбербанк', self.bank_text, re.IGNORECASE)
        test_vipiska_po_schetu = re.search(r'Выписка по счёту дебетовой карты', self.bank_text, re.IGNORECASE)
        test_data_formirovania = re.search(r'Дата формирования', self.bank_text, re.IGNORECASE)
        test_dergunova_k_a = re.search(r'Дергунова К\. А\.', self.bank_text, re.IGNORECASE)
        test_dya_proverki_podlinnosti = re.search(r'Для проверки подлинности документа', self.bank_text, re.IGNORECASE)
        test_ostatok_po_schetu = re.search(r'ОСТАТОК ПО СЧЁТУ', self.bank_text, re.IGNORECASE)

        if (not (test_sberbank  and
                test_vipiska_po_schetu and 
                test_dya_proverki_podlinnosti and 
                test_data_formirovania) 
            or 
            test_ostatok_po_schetu or test_dergunova_k_a
            ):
            raise exceptions.InputFileStructureError("Не найдены паттерны, соответствующие выписке")
```

🔴 Отпечаток **двусторонний**: есть обязательные маркеры (И) и есть **запрещающие**
(`ОСТАТОК ПО СЧЁТУ`, `Дергунова К. А.` — подпись должностного лица, отличающая соседний
формат). Именно запрещающие маркеры разводят близкие форматы и не дают
`determine_extractor_auto` упасть в «больше одного экстрактора». Это приём, которого у нас
в `detect_pdf_bank` нет вовсе.

Разрезание на записи — одна многострочная регулярка с `re.VERBOSE`, lookahead на начало
следующей транзакции и явным вычищением межстраничных разделителей:

```python
        # Удаляем куски текста, которые являются разделами между страницами PDF, не несущими информации
        cleaned_text = re.sub(r'Продолжение на следующей странице[\s\S]*?операции²\n', '', self.bank_text)
        
        individual_entries = re.findall(r"""
            \d\d\.\d\d\.\d\d\d\d\s{1}\d\d:\d\d\s{1}        # Date and time like '06.07.2021 15:46' and one space
            (?=\d{3,8}|-|0)                                # код авторизации, либо "-", либо 0 (issue 33). 
                                                           # Код авторизациии который я видел всегда состоит и 6 цифр,
                                                           # но на всякий случай укажем с 3 до 8
            .*?\n                                          # Anything till end of the line including a line break
            \d\d\.\d\d\.\d\d\d\d\s{1}                      # дата обработки
            [\s\S]*?                                       # any character, including new line. !!None-greedy!!
            (?=\d\d\.\d\d\.\d\d\d\d\s{1}\d\d:\d\d|         # lookahead до начала новой трансакции
            Дата\sформирования)                            # Либо да конца выписки
            """, cleaned_text, re.VERBOSE)

        if len(individual_entries) == 0:
            raise exceptions.InputFileStructureError(
                "Не обнаружена ожидаемая структора данных: не найдено ни одной трасакции")
```

Приёмы, которые тут стоит забрать целиком: (1) **перенос страницы удаляется регуляркой
до разбора**, а не обрабатывается в цикле; (2) **запись определяется по якорю «дата+время
в начале» и заканчивается lookahead-ом на следующий якорь либо на маркер конца документа** —
это и есть решение проблемы многострочного назначения платежа без всяких координат;
(3) многострочность ограничена явной проверкой:

```python
        if len(lines) < 2 or len(lines) > 4:
            raise exceptions.InputFileStructureError(
                "entry is expected to have from 2 to 4 lines\n" + str(entry))
```

то есть «запись из 5 строк» — не молча разобранная как попало, а **отказ**.

#### Деньги — только `Decimal`, знак выводится из отсутствия плюса

```python
def get_decimal_from_money(money_str: str, process_no_sign_as_negative=False) -> Decimal:
    """
    Converts string, representing money to a Decimal.
    If process_no_sign_as_negative is set to True, then a number will be negative in case no leading sign is available
    Example: get_decimal_from_money('1 189,40', True) -> -1189.4
    """
    money_str = unidecode.unidecode(money_str)
    money_str = money_str.replace(' ','')
    money_str = money_str.replace(',','.')
    leading_plus = False
    if money_str[0] == '+':
        leading_plus = True
    money_decimal = Decimal(money_str)
    if (process_no_sign_as_negative and not leading_plus):
        money_decimal = -1 * money_decimal
    return money_decimal
```

🔴 Три вещи разом: `unidecode` убивает неразрывные пробелы и прочую типографику **до**
парсинга; тип `Decimal`, не `float`; правило «нет плюса — значит расход» — это ровно
описанный во входной фактуре случай Райффайзена, где знак живёт внутри суммы.
У нас в `statement_parser._num` результат — `float`.

#### Самопроверка сальдо: одна функция, порог — одна копейка

```python
def check_transactions_balance(input_pd: pd.DataFrame, balance: Decimal, column_name_for_balance_calculation:str)->None:
    """
    сравниваем вычисленный баланс периода (get_period_balance) и баланс периода, полученный сложением всех трансакций в
    pandas dataframe.
    Если разница одна копейка или больше, то выдаётся ошибка
    """
    calculated_balance = input_pd[column_name_for_balance_calculation].sum()
    if balance-calculated_balance:
        raise exceptions.BalanceVerificationError(f"""
            Ошибка проверки балланса по трансакциям: 
                Вычисленный баланс по информации в шапке выписки = {balance}
                Вычисленный баланс по всем трансакциям = {calculated_balance}
        """)
```

Формула шапки, дословно из README: `баланс_по_шапке = СУММА ПОПОЛНЕНИЙ - СУММА СПИСАНИЙ -
СУММА СПИСАНИЙ БАНКА`. В формате 2603 это:

```python
        res_popolneniy = re.search(r'Пополнение\t(.+)', self.bank_text)
        if not res_popolneniy:
            raise exceptions.InputFileStructureError('Не найдена структура с пополнениями')
        res_spisaniy = re.search(r'Списание\t(.+)', self.bank_text)
        ...
        return summa_popolneniy - summa_spisaniy
```

🔴 Допуск **нулевой** (`if balance - calculated_balance:` — любая ненулевая разница
в `Decimal` считается ошибкой). Это возможно только потому, что арифметика в `Decimal`.
На `float` нулевой допуск дал бы ложные срабатывания — и это прямое следствие для нас.

Поведение при несходимости в продукте: по умолчанию **исключение и никакого файла**,
отключается только явным флагом `-b/--balcheck` («Игнорировать результаты сверки баланса»),
и тогда текст ошибки записывается на служебный лист `Info` выходного Excel:

```python
            info_worksheet.write('A6', f'Ошибки при конвертации: "{errors}"')
```

🔴 Ошибка **уезжает вместе с данными** в артефакт — её нельзя потерять, открыв файл позже.

Ошибка на отдельной транзакции — тоже не тихая: `get_entries()` оборачивает исключение
и **печатает сам текст записи**, на которой споткнулся:

```python
            except Exception as e:
                raise RuntimeError("Ошибка при обработке трансакции\n" + "-"*20 + "\n" + entry + "\n" + "-"*20) from e
```

Это буквально то, что просит п.4 задания: «явный отказ с показом строки».

#### Корпус образцов и тестирование

- Публичный корпус — **один** файл: `tests/test_data/_SBER_DEBIT_2107_anonymized_reduced.txt`
  (1 218 байт). Всё остальное приватно, дословно из теста:

```python
"""
no_github_module.py contains information, which is not shared via github due to confidential nature
Its structure is following:
SBER_DEBIT_old_not_supported_pdf = r"Path to some file on the drive"
...
"""
```

- Все приватные тесты помечены `@pytest.mark.private`, запуск без них: `python -m pytest -m "not private"`.
  Из CONTRIBUTING дословно: «Режим "not private" избегает запускать тесты, промаркированные как
  `private`. Это те тесты, для работы которых требуется приватные варианты выписок, недоступные
  в исходном коде (**а таких - большинство**)».
- 🔴 Тесты проверяют не значения полей, а **отсутствие исключения** — то есть фактически
  проверяют сходимость сальдо, потому что несходимость и есть исключение. Плюс два
  негативных теста, которые проверяют, что ошибка ЕСТЬ:

```python
def test_correctly_balance_error_SBER_DEBIT_2107_pdf():
    with pytest.raises(exceptions.BalanceVerificationError):
        sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_2107_wrong_balance_txt)

def test_correctly_does_not_convert_SBER_DEBIT_old_not_supported():
    with pytest.raises(exceptions.InputFileStructureError):
        sberbankPDF2Excel(no_github_module.path2_SBER_DEBIT_old_not_supported_pdf)
```

- Имена тестов привязаны к номерам issue: `..._issue_31_simulation_txt`, `..._issue_33_txt`,
  `..._issue_35_txt`, `..._issue_36_txt`, `..._issue_39`, а также
  `..._issue_36_theoretical_case_txt` — **синтетический случай, руками сконструированный
  под гипотезу, которая в жизни не встречалась**. То есть корпус растёт по одному файлу
  на каждый баг, и это задокументированная практика.
- Отдельный «самотест» экстрактора — `extractors_generic.debug_extractor(...)`: гоняет новый
  экстрактор на правильном тексте и на **заведомо неправильном** (`wrong_text = "Some wrong
  text, which cannot be correct"`), требуя от каждого метода исключения на неправильном.
  Плюс сверяет множества полей:

```python
    undefined_fiels_set = all_actually_returned_fields_set - set(columns_info_dic.keys())
    if len(undefined_fiels_set)>0:
        raise ValueError(...)
```

#### Сколько стоит формат: измеримые числа

- Эталонный коммит добавления одного формата (`0f6c85e4`, 20.03.2023,
  «Format SBER_DEBIT_2303_CHELYABINSK is added», API `commits/0f6c85e4...`, 200):
  **`{'total': 199, 'additions': 199, 'deletions': 0}`**, пять файлов —
  `extractor_..._CHELYABINSK.py` (+191), `extractors.py` (+3), тест (+4), README (+1),
  скриншот формата.
  🔴 **Ноль удалений: новый формат не трогает старый код вообще.** Модульность здесь
  не декларация, а измеримое свойство.
- Релизов всего 37 (`releases?per_page=100`, 200), первый 24.01.2020, последний
  **v5.4.0 от 01.06.2026**. За период янв–июн 2026 — пять релизов (5.1.1, 5.2.0, 5.3.0,
  5.3.1, 5.4.0).
- Из них релизы v4.4.0 (20.03.2023) и v3.1.0 («Добавлен новый формат выписки 2107_Stavropol»,
  11.07.2021) прямо привязаны к добавлению формата.

### 2.2 ofxstatement и `ofxstatement-russian` — конечный автомат и синтетический id

Реквизиты (16.09.2026, `curl -sk --http1.1`, все 200):
`api.github.com/search/repositories?q=ofxstatement&sort=stars` → `kedder/ofxstatement`
(364 звезды, последний push 22.08.2026); `gerasiov/ofxstatement-russian` (28 звёзд,
🔴 **последний push 07.01.2021 — проект мёртв пять лет**); `partizand/ofxstatement-vtb24`
(1 звезда, push 17.11.2016 — мёртв).
Дерево `ofxstatement-russian` (`git/trees/master?recursive=1`, 200): плагины
`alfabank.py` (4 289 б), `avangard.py` (5 025 б), `sberbank_csv.py` (3 046 б),
`sberbank_txt.py` (6 917 б), `tinkoff.py` (4 741 б), `vtb.py` (6 230 б).
Скачаны: `sberbank_txt.py` (200, 6 917 б), `tinkoff.py` (200, 4 741 б),
`README.rst` (200, 3 814 б), ядро `kedder/ofxstatement` → `src/ofxstatement/statement.py`
(200, 15 959 б).

🔴 **Ответ на вопрос «что они делают при смене формата»: ничего. Проект заброшен.**
Плагины написаны под текстовые/CSV-выгрузки 2013–2016 годов (`sb_encoding = 'cp1251'`,
формат даты `'%d.%m.%Y %H:%M:%S'`, поля Тинькофф из 13 колонок). Это и есть измеренная
цена отказа от сопровождения: парсер не ломается громко — он просто перестаёт существовать
вместе с автором. Для нас это аргумент к тому, что поддержка формата — статья постоянных
расходов, а не разовая задача.

**Корпус образцов у них есть и он публичный** (в отличие от Sberbank2Excel):
`tests/samples/alfabank.csv` (592 б), `sberbank.csv` (1 821 б), `sberbank_maestro.txt`
(2 770 б), `sberbank_visa.txt` (10 266 б), `vtb.csv` (816 б), `vtb_user_date.csv` (492 б),
плюс по тесту на банк (`test_alfabank.py` 1 764 б, `test_sberbank_csv.py` 1 903 б,
`test_sberbank_txt.py` 1 853 б, `test_vtb.py` 1 757 б) и `util.py` (259 б).
🔴 Отдельный образец `vtb_user_date.csv` — вариант того же банка с другой датой; то есть
корпус устроен «файл на каждый обнаруженный вариант», ровно как в Sberbank2Excel, но здесь
файлы маленькие (0,5–10 КБ) и анонимные, поэтому лежат в открытом репозитории.

#### Приём 1: разбор текста конечным автоматом по строкам (`sberbank_txt.py`)

Это прямая иллюстрация к п.3 задания «конечные автоматы по строкам». Машина состояний
собрана декларативно, дословно:

```python
class ParserState:
    def __init__(self, name, parser):
        self.name = name
        self.matchers = list()
        parser.append(self)

    def addMatcher(self, reString, nextState=None, function=None):
        self.matchers.append([re.compile(reString), nextState, function])

    def run(self, line):
        for (matcher, nextState, function) in self.matchers:
            match = matcher.match(line)
            if match:
                if function:
                    function(match)
                return nextState
        return None
```

и описание конкретного формата — это описание переходов:

```python
        self.currentState = 'init'
        state = ParserState('init', self)
        state.addMatcher(r"^.*ВАЛЮТА СЧЕТА.*$", 'currency')

        state = ParserState('currency', self)
        state.addMatcher(r"^\s*(\w{3})\s*$", 'begin_balance', self.extractCurrency)

        state = ParserState('begin_balance', self)
        state.addMatcher(r"^ОСТАТОК НА НАЧАЛО ПЕРИОДА:\s*(\d+\.\d{2})(\+)?\s*$",
                         'table_header', self.extractBeginBalance)

        state = ParserState('table_header', self)
        state.addMatcher(r"^[-+]{80,}$", 'table_header2')

        state = ParserState('table_header2', self)
        state.addMatcher(r"^[-+]{80,}$", 'transaction')

        state = ParserState('transaction', self)
        state.addMatcher(r"^[-+]{80,}$", 'end_balance')
        state.addMatcher(
            r"^(.*)\s*(\d{2}[А-Я]{3})\s+(\d{2}[А-Я]{3}\d{2})\s+\d{6}\s+(.*)\s\w{3}\s+\d*\.\d{2}\s+(\d*\.\d{2})(CR)?\s*$",
            None, self.extractTransaction)
        ...
        state.addMatcher(r".*ИТОГО ПО.*")
        state.addMatcher(r"^(.+)\s*$", None, self.extractTransactionAppend)

        state = ParserState('end_balance', self)
        state.addMatcher(r"^ОСТАТОК НА КОНЕЦ ПЕРИОДА:\s*(\d+\.\d{2})\+?\s*$",
                         'table_header', self.extractEndBalance)
```

Что тут важно перенять:
1. **Многострочное описание решается состоянием, а не регуляркой через всю запись**:
   последний матчер состояния `transaction` — `^(.+)\s*$` → `extractTransactionAppend`,
   то есть «любая строка, не похожая на новую операцию, дописывается к текущей».
   Это второй (после lookahead-приёма Sberbank2Excel) рабочий способ обработать
   многострочное назначение платежа.
2. **Строка-итог гасится явно**: `state.addMatcher(r".*ИТОГО ПО.*")` — без функции и без
   перехода, то есть «распознано и намеренно проигнорировано». Служебные строки не
   попадают в «не разобрано» — это разные категории.
3. **Разделитель таблицы служит якорем переходов**: `^[-+]{80,}$` — рамка из 80+ символов
   открывает и закрывает таблицу. Границы таблицы читаются из самого документа, а не
   задаются координатами.
4. **Остатки на начало и конец периода извлекаются машиной как отдельные состояния** —
   то есть сходимость сальдо обеспечена конструкцией, а не отдельной проверкой.
5. 🔴 **Слабое место, которое повторять не надо**: `float(match.group(1))` в
   `extractBeginBalance` / `extractEndBalance` и `float(...)` в сумме операции. Деньги
   во `float` — у Sberbank2Excel в том же месте `Decimal`. Это прямая развилка, и она
   определяет, можно ли ставить нулевой допуск при сверке.

#### Приём 2: синтетический идентификатор операции — канонический ответ на п.5

Ядро `ofxstatement/statement.py`, дословно:

```python
def generate_transaction_id(stmt_line: StatementLine) -> str:
    """Generate pseudo-unique id for given statement line.

    This function can be used in statement parsers when real transaction id is
    not available in source statement.
    """
    h = sha1()
    assert stmt_line.date is not None
    h.update(stmt_line.date.strftime("%Y-%m-%d %H:%M:%S").encode("utf8"))
    if stmt_line.memo is not None:
        h.update(stmt_line.memo.encode("utf8"))
    if stmt_line.amount is not None:
        h.update(str(stmt_line.amount).encode("utf8"))
    return h.hexdigest()
```

Ключ — **sha1 от тройки (дата со временем, memo, сумма)**. И сразу же — честное признание,
что тройка не уникальна, с решением коллизии, дословно:

```python
def generate_unique_transaction_id(stmt_line: StatementLine, unique_id_set: set) -> str:
    """
    Generate a unique transaction id.

    A bit of background: the problem with these transaction id's is that
    they do do not only have to be unique, they also have to stay the same
    for the same transaction every time you generate the statement.  So
    generating random ids will not work, even though they will be unique,
    GnuCash or beancount will recognize these transaction as "new" if you
    happen to generate and import the same statement twice or import two
    statements with overlapping periods.

    The function generate_transaction_id() is deterministic, but does not
    necesserily generate an unique id.
    ...
    """
    id = initial_id = generate_transaction_id(stmt_line)
    counter = 0
    while id in unique_id_set:
        counter += 1
        id = initial_id + str(counter)

    unique_id_set.add(id)
    return id + ("" if counter == 0 else "-" + str(counter))
```

🔴 **Здесь дословно назван наш сценарий:** «if you happen to generate and import the same
statement twice **or import two statements with overlapping periods**». Требование
сформулировано точно: id обязан быть не просто уникальным, а **одинаковым для одной и той
же операции при каждой генерации**. Отсюда следствия для нашей дедупликации:
- хеш считается **только от полей, которые банк печатает стабильно**; любое наше
  обогащение (категория, нормализация описания, MCC) в хеш входить не должно, иначе
  смена нашего же кода породит дубли задним числом;
- две идентичные операции в один день (два одинаковых кофе) — **законный случай**,
  и он решается счётчиком повторов внутри партии, а не слиянием;
- счётчик обязан быть **позиционно устойчивым**: при повторном импорте того же периода
  порядок строк должен совпасть, иначе `-1` и `-2` поменяются местами. Это требование
  к нашей сортировке перед хешированием, которого в коде ofxstatement нет — там порядок
  берётся из файла.

Плагин Тинькофф применяет это буквально, с комментарием, который и есть ответ на вопрос
«а что делать, если банк id не даёт»:

```python
        # as csv file does not contain explicit id of transaction, generating artificial one
        transaction.id = statement.generate_transaction_id(transaction)
```

Инвариант OFX, который заставляет это делать, — в `StatementLine.assert_valid()`:

```python
        assert self.id or self.check_no or self.refnum
```

то есть **строка без идентификатора вообще не является валидной** и не может быть записана.
Это архитектурный приём: невозможность существования операции без ключа проверяется типом,
а не дисциплиной.

Ещё две вещи из `tinkoff.py`, применимые к нам дословно:

```python
        if not line['status'] == 'OK':
            print("Notice: Skipping line %d: Transaction time %s status is %s." % (
                self.cur_record, line['op_time'], line['status']))
            return None
```
— пропуск по статусу **называет номер строки и её время**, то есть пропуск наблюдаем
(у нас это уже есть в виде `SKIP_STATUS`, но без номера строки);

```python
        if not line['currency'] == self.statement.currency:
            print("Transaction %s currency '%s' differ from account currency '%s'." % (...))
            return None
```
— операция в чужой валюте **не пересчитывается и не глотается**, а откладывается с явным
сообщением. У нас валютная операция сейчас просто попадёт в сумму счёта.

И отдельно — резервный расчёт баланса, когда банк его не печатает:

```python
def recalculate_balance(stmt: Statement) -> None:
    """Recalculate statement starting and ending dates and balances.
    When starting balance is not available, it will be assumed to be 0.
    This function can be used in statement parsers when balance information is
    not available in source statement.
    """
    total_amount = sum([sl.amount for sl in stmt.lines if sl.amount is not None], D(0))
    stmt.start_balance = stmt.start_balance or D(0)
    stmt.end_balance = stmt.start_balance + total_amount
    stmt.start_date = min(sl.date for sl in stmt.lines if sl.date is not None)
    stmt.end_date = max(sl.date for sl in stmt.lines if sl.date is not None)
```

🔴 Обратить внимание: это **НЕ самопроверка**, а подмена. Если сальдо считать по своим же
разобранным строкам, сходимость будет тождественной и не поймает ничего. Различать эти два
режима обязательно: «банк объявил итог» → проверка имеет силу; «итога нет, посчитали сами» →
проверки нет вовсе, и это надо показывать пользователю как пониженную гарантию.

---

## П4 и П5. Поведение продуктов при нераспознанном и дедупликация при регулярном импорте

> Материал добыт субагентом 16.09.2026 (бюджет 12 действий израсходован полностью:
> 2 WebSearch + 10 Bash/curl). Ниже — его находки с реквизитами и дословными цитатами.
> Проверял ли лид каждую ссылку повторно: нет; реквизиты приводятся как сняты субагентом.

### 4.1 Дзен-мани — прямой ответ на вопрос задания

**Источник:** `https://jonny3d.userecho.com/knowledge-bases/2/articles/4-kak-rabotaet-sinhronizatsiya-s-bankami`
(зеркало официальной базы знаний Дзен-мани на UserEcho), HTTP 200, 66 189 байт, 16.09.2026,
`curl -sk --http1.1` с браузерным UA. Статья создана 9 лет назад.

🔴 Ключевая цитата, дословно:

> «При получении операций от банка Дзен-мани ищет их среди операций у себя.
> При этом сравниваются операции по внутренним идентификаторам операции от
> банка (если есть) или по комбинациям дата, получатель, сумма. Если операция
> не находится, тогда она создаётся. После импорта всех операций может быть
> создана операция корректировки, если после импорта операций остаток на счету
> стал отличаться от остатка по счёту в банке.»

> «При подключении к счёту синхронизации с банком на этом счету нужно отключить
> обработку СМС, если этого не произошло автоматически. Иначе операции будут
> создаваться как при синхронизации с банком, так и при обработке входящих СМС
> от банков, из-за чего возможно дублирование операций и создание операций
> корректировок.»

Схема, стало быть, двухуровневая: **id банка, если есть → иначе тройка (дата, получатель,
сумма) → остаточное расхождение закрывается служебной операцией «Корректировка»**.
Окна по дате в справке нет: сравнение описано как совпадение комбинации.

**Пороги (единственные явные числа).** Источник:
`https://support.zenmoney.ru/ru/knowledge-bases/2/articles/17-obrabotka-operatsij-posle-sinhronizatsii-s-bankami`,
HTTP 200, 51 079 байт, «Последнее изменение: 7 лет назад». Дословно:

> «Условия, по которым операции объединяются в перевод: если у расходной и
> доходной операции не указаны категории, совпадает дата платежа, разные счета
> и сумма снятия и поступления отличается в пределах 3%.»

> «Условия, по которым вносится планируемая операция: если у фактической и
> планируемой операции совпадают счета, сумма отличается в пределах 3%, дата
> планируемой операции не более чем, фактическая дата +1 день.»

> «ВАЖНО: Правила обработки работают только если в операции определился
> уникальный получатель платежа.»

> «Категории определяются в зависимости от распознанного имени получателя…
> Если выбор категории вам оказался не по нраву, вы можете его изменить. Тогда
> в следующей раз покупки в этом же магазине получат указанную вами ранее
> категорию. Вы можете переименовать имя получателя платежа, тогда все следующие
> операции у этого же получателя будут получать наименование, указанное вами
> последним.»

🔴 То есть **правка пользователя превращается в правило** — и по категории, и по имени
получателя. Это ровно то, что у нас заложено в `UserCategoryRule`, и подтверждение, что
механизм отраслевой, а не наша выдумка. И отдельно: при нераспознанном получателе
автоматика не отказывает, а **отключается** — операция создаётся, правила к ней не
применяются.

🔴 **Самое важное расхождение для нас.** Источник:
`https://support.zenmoney.ru/knowledge-bases/2/articles/157-zagruzka-dannyih-iz-drugih-servisov`,
HTTP 200, 65 802 байта, «Последнее изменение: 2 года назад». Дословно:

> «ВАЖНО: Убедитесь, что в файле только те операции, которые действительно
> отсутствуют в Дзен-мани, чтобы не загрузить их повторно.»

**При файловом импорте дедупликации у Дзен-мани НЕТ ВООБЩЕ** — ответственность переложена
на пользователя текстом. Дедуп по тройке работает только на канале прямой банковской
синхронизации. 🔴 Это значит, что разобранный во входной фактуре «приём Дзен-мани» **к
нашему сценарию (импорт PDF-файла) напрямую не относится** — его придётся переносить
на файловый канал самим, чего у первоисточника нет.

Там же — поведение при нераспознанном в файле, дословно:

> «Каждая строка файла - это одна загружаемая операция. Важно, чтобы в
> комментариях операций не было переноса строк, иначе каждая новая строка будет
> расцениваться как новая операция. […] Необходимо правильно указать все
> необходимые типы данных в колонках импортируемых данных, иначе импорт не
> запустится или пройдёт не корректно. Возможно, понадобится разбить
> импортируемый файл на несколько небольших файлов по 2 тыс строк… Если ошибок
> не много, то они будут указаны списком и их можно будет поправить или
> пропустить.»

Числа: дробление файла по **2 000 строк**; ошибки — **построчным списком с выбором
«поправить или пропустить»**, файл целиком не отвергается (отвергается только при неверной
разметке типов колонок).

**Корректировка как индикатор сбоя.** Источник:
`https://support.zenmoney.ru/ru/knowledge-bases/2/articles/3-operatsii-korrektirovka-i-chto-s-nimi-delat`,
HTTP 200, 59 664 байта, «Последнее изменение: 6 лет назад». Дословно:

> «Операция с категорией "Корректировка" создается автоматически при
> распознавании СМС и при подключении к банку, если остаток на счету в банке не
> совпадает c остатком на счету в Дзен-мани.»

> «При синхронизации с банком напрямую создание корректировок отключить невозможно.»

> «Если удалить корректировку, остаток на счету изменится на сумму удалённой
> операции. При следующей синхронизации Дзен-мани снова увидит расхождение
> остатков и создаст необходимую корректировку заново.»

🔴 Дословно задокументированный отказ их собственного алгоритма — готовый тест-кейс для нас:

> «Некоторые магазины замораживают суммы на карте (HOLD-операции) не так, как мы
> ожидали. Они не размораживают сумму, чтобы отметить её как исполненную.
> Вместо этого они отменяют её и проводят заново как новую покупку. Мы этого не
> ожидали, к сожалению. Поэтому покупки в Яндекс.Такси, Gett и, возможно,
> где-то ещё могут создавать дубли покупок и провоцировать создание
> корректировок. ☹»

Перечисленные ими причины корректировок (то есть готовый список наших рисков):
одновременная синхронизация одного счёта с двух телефонов; неуказанный или неверный
кредитный лимит/овердрафт; СМС, пришедшие не по порядку; неверное распознавание СМС;
ручная операция с ошибочным счётом; неверный номер карты в настройках. Плюс дословно:
«Многие банки "тихо" обновляют остаток кредитных (ипотечных) счетов и не добавляют
операций… Так делает Сбербанк, например, ежедневно увеличивая долг на сумму дневной
комиссии».

**Открытый код `zenmoney/ZenPlugins`** (API `api.github.com/repos/zenmoney/ZenPlugins` 200,
дерево `git/trees/master` 200; файлы через `raw.githubusercontent.com`, все 200):
`src/common/transactionGroupHandler.js` (4 608 б, тест 13 182 б),
`src/common/mergeTransfers.js` (1 429 б, тест 3 585 б),
`src/common/handleGroups.js` (1 649 б, тест 1 546 б), `src/common/adapters.js` (18 277 б).
🔴 **Дедупликации входящих операций против уже сохранённых в открытом коде НЕТ** — она
серверная. В плагинном слое есть только (а) группировка по массиву ключей убывающей
строгости и (б) парная склейка расход+приход в перевод с жёсткими предусловиями:

```js
export function mergeTransfersHandler (transactions, {...} = {}) {
    if (transactions.length < 2 ||
      transactions.length % 2 !== 0 ||
      transactions.some(transaction => transaction.movements.filter(isMainMovement).length > 1)) {
      return null
    }
    const incomes = transactions.filter(t => getMovementSign(t.movements.find(isMainMovement)) > 0)
    const outcomes = transactions.filter(t => getMovementSign(t.movements.find(isMainMovement)) < 0)
    if (outcomes.length !== incomes.length) { return null }
    if (areQuiteDifferentTransactions(incomes) || areQuiteDifferentTransactions(outcomes)) { return null }
    if (incomes[0].movements.find(isMainMovement).account.id === outcomes[0].movements.find(isMainMovement).account.id) { return null }
    ...
        date: new Date(Math.min(outcome.transaction.date.getTime(), income.transaction.date.getTime())),
```

```js
export function handleGroups ({ items, makeGroupKeys, handleGroup }) {
    ...
    for (let i = 0; i < n; i++) {   // проход по уровням ключей: сначала строгий, потом слабее
```

🔴 Приём «массив ключей убывающей строгости, проход по уровням» — это то, чего нам не
хватает: сначала пытаться сматчить по самому строгому ключу, и только затем ослаблять.
Заметить: **окна по дате в коде нет вообще**, есть сортировка и выбор `Math.min` двух дат.

Ограничение канала, названное субагентом: `api.github.com/search/code` без токена отдаёт
**HTTP 401 «Requires authentication»**, поэтому файлы отбирались по дереву, а не поиском
по коду.

### 4.2 Lunch Money — единственный полностью формализованный критерий

**Источник:** `https://raw.githubusercontent.com/lunch-money/support/master/importing-transactions/import-via-csv.md`
(исходник их официальной базы знаний; веб-зеркало `support.lunchmoney.app/guides/import-via-csv`),
HTTP 200, 8 678 байт, 16.09.2026.

> «You can choose to Apply Rules and Skip Duplicates. Both of these settings are
> recommended, so they are on by default. […] Skip Duplicates will ensure that the
> same transaction will not be imported twice. **We determine two transactions to be
> the same if the date, payee name, and amount all match exact.**»

> «This list of transactions has run through your rules and been de-duplicated per
> your settings. **Duplicated transactions are shown at the bottom for your personal
> debugging.** […] To prevent some transactions from being imported, de-select them.»

> «You'll also see a list of **malformed lines** from your CSV. These represent lines
> in your CSV that we determined to be missing required data, such as a date, payee
> name, or amount. If you believe any of these were done in error, you can always go
> back to Step 2 and fix your column matches.»

> «Format preferred: YYYY/MM/DD or YYYY-MM-DD. All other formats are possible, but we
> may have a hard time parsing them. (It should still work, as there is an opportunity
> to **teach our system which date format you're using**…)»

> «Configurations can be saved during Step 3, so next time you upload CSVs to the same
> asset, you get to choose whether or not to use the saved configuration…»

> «There is a file size restriction of **200kb**. We recommend you upload at most a few
> months' worth of transactions at a time.»

> «We did a **best guess** as to what your updated balance should be, but if we were off,
> you can enter the correct balance on this page.»

> «Because there isn't a standard format for transactions in a CSV file, every bank
> exports transactions differently and we may sometimes encounter a CSV that we're not
> able to parse. […] Please contact us at support@lunchmoney.app with a snippet of your
> file and we'll work on getting it supported.»

Мастер из пяти шагов: Upload CSV → Match CSV columns → Review CSV settings → Review
Transactions → Import Transactions. Импортируемых полей всего четыре.

Выжимка: критерий дубля — **точное совпадение тройки (дата, payee, сумма), без окна
и без нечёткого сравнения**. Нераспознанное отбраковывается **построчно**, сами строки
показываются, и предусмотрен возврат на шаг разметки колонок. Нераспознанный формат
даты — обучаемая настройка, сохраняемая конфигурация импорта на счёт.
🔴 Пометка о надёжности обещания: формулировка «ensure that the same transaction will not
be imported twice» — **маркетинговая абсолютизация**: тут же назван критерий точного
совпадения payee, а их changelog фиксирует поломку на payee со звёздочкой
(«CSV/PDF duplicate detection failed for payee names with asterisks»,
`feedback.lunchmoney.app/changelog` — дословно не снят, бюджет субагента кончился).

### 4.3 Tiller — происхождение строки хранится в самих данных

**Источник:** `https://help.tiller.com/en/articles/12159768-automatically-import-bank-csvs-into-tiller`
(«Automatically import bank CSVs into Tiller», Heather Phillips, 24.07.2026), HTTP 200,
53 219 байт, снято через текстовый прокси `r.jina.ai` (прямой `curl` к старому URL
`help.tillerhq.com/.../2871811` вернул 404).

> «You can import CSVs on the Tiller Console to add transaction data directly into a
> Tiller-managed account. […] or it could be an account you want to track 100% manually.
> You can also use this workflow to add transactions if a bank connection is down.
> **See more about how to handle duplicates when the connection comes back up.**»

> «Confirm or add the **Import Tag** column to your spreadsheet (optional but recommended)»

Выжимка: Tiller прямо признаёт, что ручной импорт в автоматический счёт порождает дубли
при восстановлении связи, и решает это **колонкой происхождения строки («Import Tag»)
прямо в данных**. Само правило сверки полей у Tiller не добыто.

### 4.4 Что по этому пункту НЕ добыто и почему

- **CoinKeeper** (импорт, дубли) — не добыто. Причина: бюджет субагента (12 действий)
  исчерпан на объектах 1/3/4, **ни одной попытки по домену не сделано**. Это нехватка
  бюджета, а не отказ источника. Косвенно известно, что CSV-экспорт у CoinKeeper есть:
  Дзен-мани держит для него внешний Excel-конвертер.
- **MoneyWiz** — не добыто, та же причина. Косвенно: Дзен-мани рекомендует для MoneyWiz
  «конвертер на python 3 jupyter notebook».
- **Tiller, статья про дубли** — не добыта целиком: старый URL
  `help.tillerhq.com/en/articles/2871811-duplicate-transactions-in-the-transactions-sheet`
  через `r.jina.ai` дал HTTP 200 у прокси, но тело содержит «Target URL returned error 404»;
  по адресу `help.tiller.com/en/articles/432693-duplicate-transactions` теперь лежит другая
  статья (ID переиспользован). Нужный раздел живёт якорем `#h_9ce19151d0` внутри статьи
  12159768 и в снятый фрагмент не попал.
- **`api.github.com/search/code`** — HTTP 401 «Requires authentication» без токена.
  Обход: `git/trees` + `raw.githubusercontent.com`.
- `support.zenmoney.ru` без префикса `/ru/` отдаёт **301 с нулевым телом**; рабочая
  форма — с `/ru/` либо зеркало на `userecho.com`.
- Свежесть источников Дзен-мани: пометки «последнее изменение 6–7 лет назад» и «2 года
  назад» — правила могли измениться без обновления справки. Код ZenPlugins снят с master
  на 16.09.2026 (последний push 11.09.2026) и актуален.

---

## П1. Как устроены PDF банков технически — СОБСТВЕННЫЕ ЗАМЕРЫ, не реклама

> Все числа ниже получены запуском инструментов на этой машине 16.09.2026, а не взяты
> из статей. Окружение: `pdftotext version 26.04.0` (poppler, `/usr/local/bin/pdftotext`),
> `pdfplumber 0.11.9` (венв проекта, Python 3.13), `pymupdf 1.28.2` (отдельный венв
> в скрэтчпаде, поставлен `uv pip install`, системный Python блокирует `pip` по PEP 668).
> 🔴 **Честная оговорка о материале:** замеры сделаны на наших синтетических шаблонах
> `app/data/statement_templates/*.pdf` (по 2 операции, 25–27 КБ) и на специально
> сконструированном стресс-файле. Реальных выписок банков в работе не использовалось
> (правило 7 проекта). Поэтому выводы о ПОРЯДКЕ инструментов переносимы, а абсолютные
> проценты точности на реальных файлах этими замерами НЕ установлены.
> `camelot` и `tabula` не замерялись: в окружении их нет, `camelot` требует ghostscript,
> `tabula` — JVM; ставить их ради замера на двухстрочных синтетических таблицах смысла
> не имеет, и это названо ограничением, а не результатом.

### 1.1 Замер: три режима `pdftotext` на четырёх шаблонах

| Файл | `pdftotext` (умолчание) | `-layout` | `-raw` |
|---|---|---|---|
| sber.pdf | 281 б / 107 мс | 281 б / 61 мс | 279 б / 64 мс |
| tinkoff.pdf | 174 б / 61 мс | 174 б / 60 мс | 172 б / 57 мс |
| vtb.pdf | 551 б / 65 мс | **703 б** / 61 мс | 531 б / 62 мс |
| raiffeisen.pdf | 434 б / 63 мс | **609 б** / 66 мс | 414 б / 59 мс |

Время у всех режимов одинаковое в пределах разброса (~60 мс, первый запуск 107 мс —
прогрев). Разница не во времени, а в структуре.

🔴 **Главный результат замера: режим по умолчанию РАЗРУШАЕТ строку таблицы.**
`pdftotext vtb.pdf -` (без флагов), дословный вывод:

```
Дата

Дата обр.

Сумма

12.01.2026 10:00

12.01.2026

-1 500,00

13.01.2026 11:00

13.01.2026

25 000,00

Приход

25 000,00

Расход

Комиссия

Описание

1 500,00

0,00

Ozon

0,00

Перевод
```

Колонки выданы **по-колоночно**: сначала все даты, потом все суммы, потом все описания.
Связь «сумма ↔ операция» потеряна безвозвратно, восстановить её из этого текста нельзя
в принципе. Тот же файл с `-layout`:

```
                            Дата               Дата обр.    Сумма       Приход      Расход     Комиссия   Описание
                            12.01.2026 10:00   12.01.2026   -1 500,00               1 500,00   0,00       Ozon
                            13.01.2026 11:00   13.01.2026   25 000,00   25 000,00              0,00       Перевод
```

Строки целы, колонки выровнены пробелами, **пустая ячейка видна как пропуск нужной ширины**
(в первой строке пусто под «Приход», во второй — под «Расход»).

**Вывод замера №1:** `pdftotext` без `-layout` для выписок непригоден, причём отказывает
он МОЛЧА — текст извлёкся, ошибок нет, данные бессмысленны. Это худший из возможных
режимов отказа, и он ровно тот, что описан в задании как «тихая ошибка».

### 1.2 Замер: `pdfplumber` — таблицы находятся только там, где нарисованы линии

`pdfplumber 0.11.9`, `extract_text()` + `extract_tables()` на странице:

| Файл | знаков текста | найдено таблиц | строк в таблицах | мс |
|---|---|---|---|---|
| sber.pdf | 200 | **0** | 0 | 21 |
| tinkoff.pdf | 117 | **0** | 0 | 14 |
| vtb.pdf | 373 | 1 | 3 | 57 |
| raiffeisen.pdf | 266 | 1 | 4 | 34 |

Там, где линии есть, результат идеальный (дословный вывод):

```
ROW: ['Дата', 'Дата обр.', 'Сумма', 'Приход', 'Расход', 'Комиссия', 'Описание']
ROW: ['12.01.2026 10:00', '12.01.2026', '-1 500,00', '', '1 500,00', '0,00', 'Ozon']
ROW: ['13.01.2026 11:00', '13.01.2026', '25 000,00', '25 000,00', '', '0,00', 'Перевод']
```

```
ROW: ['№ П/П', 'Дата операции', 'Номер документа', 'Поступления', 'Расходы', 'Детали операции', 'Номер карты']
ROW: ['', 'Выполнена банком', '', '', '', '', '']
ROW: ['1', '14.01.2026 08:00', 'DOC1', '', '- 780,00 ₽', 'Аптека Ригла', '*5678']
ROW: ['2', '15.01.2026 09:00', 'DOC2', '+ 3 000,00 ₽', '', 'Кэшбэк', '*5678']
```

🔴 Два наблюдения, прямо бьющие в тему:
1. **`extract_tables()` вернул 0 таблиц на sber.pdf и tinkoff.pdf** — там таблица без
   линий. То есть стратегия «дай pdfplumber найти таблицу» работает ровно на тех банках,
   которые рисуют рамку, и **не работает** на тех, кто верстает пробелами. У Сбера
   (по разбору Sberbank2Excel, раздел 2.1) рамок нет вовсе.
2. Вторая строка райффайзеновской таблицы — `['', 'Выполнена банком', '', '', '', '', '']` —
   **это не операция, а вторая строка шапки, попавшая в выдачу как строка данных**.
   Ровно тот класс, что во входной фактуре описан как «в ячейке с датой встречается
   статус "В обработке"»: под колонкой даты живёт чужой текст. Парсер, слепо берущий
   каждую строку таблицы за операцию, съест её и либо упадёт, либо создаст пустую операцию.

### 1.3 Замер: `pymupdf` — скорость

| Файл | знаков | мс |
|---|---|---|
| sber.pdf | 201 | 14,5 |
| tinkoff.pdf | 118 | 3,5 |
| vtb.pdf | 374 | 4,4 |
| raiffeisen.pdf | 267 | 4,3 |

🔴 **`pymupdf` быстрее `pdfplumber` в 4–8 раз и быстрее `pdftotext` (процесс) на порядок**
(3,5–14,5 мс против 14–57 мс и ~60 мс). На 12 788 строках, о которых говорит комментарий
в нашем `statement_parser.py`, эта разница из косметической становится заметной.

### 1.4 🔴 Замер, опровергающий наивную кластеризацию x-координат

Задание предполагает «кластеризацию x-координат в колонки». Проверено буквально:
взяты все слова страницы (`page.get_text("words")`), собраны их `x0`, сделана одномерная
кластеризация с порогом разрыва 5 pt. Дословный вывод:

```
x0 values (raiffeisen p1): [78.0, 78.0, 94.1, 122.6, 131.2, 165.5, 181.2, 181.2, 181.2, 192.0, 193.0,
 218.8, 218.8, 218.8, 218.8, 236.8, 242.0, 251.0, 267.1, 267.1, 268.7, 311.5, 311.5, 311.5, 341.0,
 398.7, 398.7, 408.0, 415.6, 446.1, 465.9, 465.9, 471.3, 501.9, 519.0, 519.0, 519.0, 551.5, 552.6,
 605.4, 605.4, 605.4, 634.9]
clusters (gap>5pt): [(78.0,78.0,2), (94.1,94.1,1), (122.6,122.6,1), (131.2,131.2,1), (165.5,165.5,1),
 (181.2,181.2,3), (192.0,193.0,2), (218.8,218.8,4), (236.8,236.8,1), (242.0,242.0,1), (251.0,251.0,1),
 (267.1,268.7,3), (311.5,311.5,3), (341.0,341.0,1), (398.7,398.7,2), (408.0,408.0,1), (415.6,415.6,1),
 (446.1,446.1,1), (465.9,465.9,2), (471.3,471.3,1), (501.9,501.9,1), (519.0,519.0,3), (551.5,552.6,2),
 (605.4,605.4,3), (634.9,634.9,1)]
```

**25 «колонок» для таблицы из 7 колонок.** Причина очевидна задним числом: второе и третье
слово внутри ячейки («операции» после «Дата», «Ригла» после «Аптека») начинаются со своих
x0 и порождают ложные колонки. **Наивная кластеризация всех x0 не работает и работать
не может.**

Рабочий вариант — **якоря из строки шапки**: сгруппировать слова в строки по y (допуск 3 pt),
взять x0 слов ПЕРВОЙ строки таблицы как границы колонок, каждое слово отнести к последнему
якорю ≤ x0. Дословный вывод группировки по y для того же файла:

```
80.2  АО@78 | «Райффайзенбанк».@94 | Выписка@193 | по@237 | счёту@251
93.2  Обороты@78 | 3@123 | 000,00@131 | 780,00@166
120.9 №@181 | П/П@192 | Дата@219 | операции@242 | Номер@311 | документа@341 | Поступления@399 | Расходы@466 | Детали@519 | операции@553 | Номер@605 | карты@635
136.5 Выполнена@219 | банком@269
152.1 1@181 | 14.01.2026@219 | 08:00@267 | DOC1@311 | -@466 | 780,00@471 | ₽@502 | Аптека@519 | Ригла@552 | *5678@605
167.7 2@181 | 15.01.2026@219 | 09:00@267 | DOC2@311 | +@399 | 3@408 | 000,00@416 | ₽@446 | Кэшбэк@519 | *5678@605
```

🔴 Три вещи видны прямо в числах:
1. **Якоря колонок: 181, 219, 311, 399, 466, 519, 605.** Данные попадают на них точно
   (`14.01.2026@219`, `DOC1@311`, `Аптека@519`, `*5678@605`) — разброс нулевой.
2. **Знак операции определяется КОЛОНКОЙ, а не символом:** в первой строке минус стоит
   на 466 («Расходы»), во второй плюс на 399 («Поступления»). То есть при координатном
   разборе «знак внутри суммы» (фактура по Райффайзену) перестаёт быть проблемой вовсе —
   колонка сама и есть знак, а символ `-`/`+` избыточен и служит перекрёстной проверкой.
3. **Строка `Выполнена@219 | банком@269` стоит ровно на якоре колонки даты** — вот
   механика того, как «В обработке» оказывается в ячейке даты. Значит, правило отсечения
   должно быть не «ячейка даты непустая», а «содержимое ячейки даты сопоставилось
   с шаблоном даты», иначе служебная строка пройдёт как операция.

### 1.5 🔴 Стресс-замер: «съезжающие колонки при длинном тексте» — воспроизведено

Сконструирован PDF (`pymupdf`, A4, четыре колонки на x = 60/150/430/500), где описание
второй операции заведомо длиннее своей колонки и заезжает в колонку суммы.
Три инструмента на одном и том же файле:

**`pdftotext -layout` — строка разваливается на четыре, число рвётся пополам:**

```
Data         Opisanie                                                        Summa           Ostatok

12.01.2026   Oplata OZON                                                     1 500,00        33 500,00

13.01.2026   Perevod ot Ivanova Ivana Ivanovicha po dogovoru N 1234567890 ot 25
                                                                            01.01.2026
                                                                                000,00 za uslugi
                                                                                              58 500,00

14.01.2026   Kofe                                                            150,00          58 350,00
```

Сумма `25 000,00` превратилась в «25» в конце одной строки и «000,00» в начале другой.
🔴 Построчная регулярка возьмёт отсюда **25** и запишет операцию на двадцать пять рублей
вместо двадцати пяти тысяч. Файл при этом разберётся «успешно»: ни исключения, ни
пропущенной строки. Это и есть та самая тихая ошибка, ради которой заведена тема.

**`pdfplumber.extract_text()` — хуже: посимвольное перемешивание.** Дословно
(`repr` строки, третья операция):

```
'13.01.2026 Perevod ot Ivanova Ivana Ivanovicha po dogovoru N 1234567890 ot 012.50 10.0200,2060 za uslu5g8i 500,00'
```

Символы даты обработки, суммы и остатка вбиты друг в друга («012.50 10.0200,2060»,
«uslu5g8i»). `extract_tables()` на этом файле вернул `[]` — линий нет.

**Координатный разбор с якорями шапки — единственный, кто выжил.** Дословный вывод
(та же логика, что в 1.4: строки по y, колонка по последнему якорю ≤ x0):

```
anchors: [60, 150, 430, 500]
['Data', 'Opisanie', 'Summa', 'Ostatok']
['12.01.2026', 'Oplata OZON', '1 500,00', '33 500,00']
['13.01.2026', 'Perevod ot Ivanova Ivana Ivanovicha po dogovoru N 1234567890 ot 01.01.2026', '25 000,00 za uslugi', '58 500,00']
['14.01.2026', 'Kofe', '150,00', '58 350,00']
```

Структура строки цела, **сумма `25 000,00` и остаток `58 500,00` извлечены верно**,
дата обработки уехала в хвост описания, а хвост описания («za uslugi») — в колонку суммы.
То есть загрязнение осталось, но оно (а) **локализовано в текстовых полях**, (б) ловится
тривиальной проверкой «ячейка суммы после удаления числа должна быть пустой».
🔴 Это и есть главный аргумент за координатный слой: он превращает катастрофу молчаливого
неверного числа в наблюдаемую аномалию.

**Вывод по П1, по замерам:**
`pdftotext` без `-layout` — непригоден (разрушает строки). `pdftotext -layout` — годится
как быстрый текстовый слой и как источник «отпечатка» формата, но ломается на переполнении
колонки, ломается **тихо** и рвёт числа. `pdfplumber.extract_tables()` — точен, но только
при нарисованных линиях. `pdfplumber.extract_text()` на переполнении даёт худший результат
из трёх. `pymupdf` — самый быстрый и единственный, кто дал удобный доступ к словам
с координатами. Правильная единица извлечения — **слово с координатами, а не строка
текста**; колонки задаются **якорями шапки**, а не кластеризацией всех x0.

---

## П3. Как добиваются высокой точности БЕЗ ML

### 3.1 `invoice2data` — декларативный шаблон как отдельный артефакт

Смежная область из задания — разбор счетов-фактур. Живой эталон:
`github.com/invoice-x/invoice2data` (снято 16.09.2026, `api.github.com/.../git/trees/master`
200; файлы через `raw.githubusercontent.com`):
`docs/recommended-template-fields.md` (200, 10 155 б),
`src/invoice2data/extract/invoice_template.py` (200, 25 496 б),
`src/invoice2data/extract/templates/au/au.com.opal.yml` (200, 1 420 б).

🔴 **Главная идея: формат описан данными (YAML), а не кодом.** Дословно весь шаблон
транспортной выписки Opal — обратить внимание, что это именно выписка по карте с
построчными операциями, то есть наш класс документа:

```yaml
issuer: Opal Customer Care
keywords:
  - Opal Customer Care
  - Your activity statement
  - or visit opal.com.au
fields:
  opal_card_number: 'Opal card number\s+(\d{4}\s\d{4}\s\d{4}\s\d{4})'
  amount: 'Total fares \(incl. GST\)\s+-\$(\d{1,10}.\d\d)'
  total_top_ups: 'Total top ups\s+(-?\$\d{1,10}.\d\d)'
  total_adjustments: 'Total adjustments\s+(-?\$\d{1,10}.\d\d)'
  activity_statement_balance: 'Activity statement\s+(-?\$\d{1,10}.\d\d)'
  date: 'Printed (\d\d:\d\d \d\d \w\w\w \d{4})'
  from_date: 'top ups from (\d\d \w+ \d\d\d\d) to'
  to_date: 'to (\d\d \w+ \d\d\d\d)'
lines:
  start: '\s*Always remember to tap on and tap off'
  end: "Understanding your activity statement"
  first_line: '^(?P<tx_number>\d{1,10})[ ]{10,22}(?P<day_of_week>(Mon|Tue|Wed|Thu|Fri|Sat|Sun))[ ]{6}(?P<timestamp>\d\d:\d\d)[ ]{18}(?P<details>\S+( \S+)*)[ ]{6,32}(?P<journey_number>(\d{1,3})?)[ ]+(?P<fare>(Travel Reward|Off-peak|Default fare|Day Cap)?)[ ][ ]+(?P<full_fare>(\d{1,3}.\d\d)?)[ ]+(?P<discount>(\d{1,3}.\d\d)?)[ ]+(?P<amount>-?\d{1,3}.\d\d)$'
  line: '^[ ]{18,24}(?P<datestamp>(\d\d/\d\d/\d\d)?)[ ]{,32}(?P<details>\S+( \S+)*)?$'
  last_line: "^$"
options:
  date_formats:
    - '%H:%M %d %b %Y'
  currency: AUD
  remove_whitespace: false
```

Что отсюда переносится дословно:
1. **`keywords` = отпечаток формата**, как `check_specific_signatures` у Sberbank2Excel,
   но данными. Плюс есть `exclude_keywords` — тот самый «запрещающий маркер».
2. **`lines: start / end / first_line / line / last_line`** — каноническое решение задачи
   «таблица операций внутри документа + многострочная запись»: границы блока операций
   задаются якорными строками, `first_line` ловит начало записи, `line` — её продолжения.
   Это третий независимо изобретённый вариант того же приёма (после lookahead Sberbank2Excel
   и состояния-аккумулятора ofxstatement).
3. 🔴 **Слабость, которую видно прямо в регулярке:** `[ ]{10,22}`, `[ ]{6,32}`,
   `[ ]{18,24}` — ширина колонки закодирована количеством пробелов, то есть шаблон завязан
   на `-layout`-раскладку. Это ровно то, что разваливается на переполнении колонки
   (замер 1.5). Декларативность шаблона хороша, а вот привязка к пробелам — нет.

Логика выбора шаблона, дословно из `invoice_template.py`:

```python
    def matches_input(self, extracted_str: str) -> bool:
        if all(_keyword_matches(k, extracted_str) for k in self["keywords"]):
            # All keywords found
            if self["exclude_keywords"] and any(
                _keyword_matches(k, extracted_str) for k in self["exclude_keywords"]
            ):
                # At least one exclude_keyword found
                return False
            # No exclude_keywords or none found, template is good
            return True
        return False
```

то есть **все ключевые слова И ни одного запрещающего**. Комментарий в коде отмечает, что
ключевые слова — это регулярки, с откатом на подстроку: «Any keyword that does not compile
as a valid regex falls back to a plain substring check».

**Обязательные поля — жёсткий отказ, а не пустое значение:**

```python
def _check_required_fields(self, output):
    if "required_fields" not in self.keys():
        required_fields = ["date", "amount", "invoice_number", "issuer"]
    ...
    if set(required_fields).issubset(output.keys()):
        ...
        return output
    logger.error(
        "Unable to match all required fields. "
        f"The required fields are: {required_fields}. "
        f"Output contains the following fields: {fields}.")
    missing = set(required_fields) - set(fields)
    raise RequiredFieldsMissingError(missing, self.get("template_name"))
```

**А сверка итогов — наоборот, мягкая, и это явно задокументировано:**

```python
def _validate_tax_total(output, template_name) -> None:
    """Warn if the per-rate tax amounts don't add up to ``amount_tax``.

    Purely advisory (a tolerance-based warning); never raises or alters output.
    """
    ...
    if total and abs(total - amount_tax) > 0.02:
        logger.warning(
            "tax_lines total (%.2f) does not match amount_tax (%.2f) in %s", ...)
```

🔴 **Два разных режима строгости в одном продукте, и это осознанно:** отсутствие
обязательного поля = исключение; несходимость суммы по строкам с объявленным итогом =
предупреждение с допуском 0.02. Плюс третий режим — `strict_fields: true` как опция шаблона,
превращающая предупреждение о неизвестном поле в `ValueError`. **Строгость сделана
настройкой формата, а не свойством парсера.** Это прямо применимо к нам: по одним банкам
мы знаем итоги точно, по другим — нет.

Отдельно стоит зафиксировать: в актуальном дереве проекта есть `src/invoice2data/ai/`
(`fallback.py` 3 183 б, `template_generator.py` 5 327 б, `providers/openai_compatible.py`).
🔴 То есть **живой отраслевой эталон правил-без-ML в 2026 году добавил ML именно как
fallback и как генератор шаблона**, оставив правила основным путём. Это не аргумент
против требования владельца «чисто правилами» — это указание, где ML в принципе
появляется у тех, кто начинал с правил: не в разборе, а в подсказке шаблона.

### 3.2 Грамматики (`lark`, `parsimonious`) — отрицательный результат

Целенаправленно искался открытый разбор банковских выписок на формальной грамматике.
🔴 **Не найдено ни одного проекта.** Поиск по GitHub (`search/repositories`) по запросам
«invoice parser template regex», «выписка банка парсер pdf», «alfabank statement parser
python» вернул либо пустые выдачи, либо уже разобранные выше репозитории.
Все четыре изученных зрелых парсера (Sberbank2Excel, ofxstatement-russian, ofxstatement,
invoice2data) построены на **регулярках плюс состоянии**, ни один — на грамматике.
Это отрицательный результат и его стоит принять как ответ: на выписках грамматика
отраслевой практикой не является. Объяснение видно из материала: документ не имеет
устойчивой грамматики — у него есть якоря и координаты, а «синтаксис» ломается на каждом
переносе строки и переполнении колонки.

### 3.3 🔴 Каталог самопроверок, ловящих ошибку БЕЗ эталона

Собрано из разобранных источников; помечено, где приём наблюдался, а где выведен.

| # | Проверка | Формула / условие | Где наблюдалась | Что ловит |
|---|---|---|---|---|
| 1 | Сходимость оборотов | `Σ приходов − Σ расходов == объявленный баланс периода` | Sberbank2Excel `check_transactions_balance`, допуск **0** на `Decimal` | потерянную строку, неверный знак, неверно прочитанное число |
| 2 | Сходимость остатков | `входящий остаток + приход − расход == исходящий остаток` | наш `_balance_delta`; у Sberbank2Excel формула шапки | то же, плюс операции вне периода |
| 3 | Совпадение числа строк с объявленным | `len(операции) == заявленное число` | наш `_raif_declared_count`; у Sberbank2Excel `len(split_text_on_entries()) > 0` | молчаливую потерю строк |
| 4 | Полнота разбора (все строки файла объяснены) | каждая пропущенная строка имеет НАЗВАННУЮ причину, причины делятся на законные и наши | наш `completeness_verdict` + `SKIP_*` | наш промах, замаскированный под «в файле так было» |
| 5 | Обязательные поля записи | отсутствие любого из `date/amount/...` → исключение | invoice2data `_check_required_fields` | пустую операцию вместо отказа |
| 6 | Ограничение формы записи | «запись состоит из 2–4 строк, иначе отказ» | Sberbank2Excel `decompose_entry_to_dict` | склейку двух операций в одну |
| 7 | Однозначность формата | ровно один экстрактор подтвердил формат, иначе отказ | Sberbank2Excel `determine_extractor_auto` | разбор новым форматом по правилам старого |
| 8 | Отпечаток + запрещающие маркеры | все обязательные И ни одного запрещающего | Sberbank2Excel, invoice2data `exclude_keywords` | соседний формат того же банка |
| 9 | Даты внутри объявленного периода | `период.начало ≤ дата операции ≤ период.конец` | 🔴 **выведено**, в изученных парсерах не наблюдалось | сдвиг года, перепутанные ДД/ММ, чужие строки |
| 10 | Соответствие знака колонке | сумма из колонки «Расходы» отрицательна, из «Поступления» — положительна; символ `+`/`-` совпадает с колонкой | 🔴 **выведено из замера 1.4** | перепутанные колонки при съезде раскладки |
| 11 | Чистота числовой ячейки | после изъятия числа в ячейке суммы не осталось букв | 🔴 **выведено из замера 1.5** | переполнение соседней колонки (единственный способ заметить «25» вместо «25 000,00») |
| 12 | Монотонность колонки остатка | если банк печатает остаток после операции: `остаток[i] − остаток[i−1] == сумма[i]` | 🔴 **выведено**; данные для этого есть у Сбера (`balance_account_currency`) и ВТБ | **построчную** проверку каждой операции, а не только итога — самая сильная из всех |
| 13 | Валюта операции == валюта счёта | иначе операция откладывается с сообщением | ofxstatement `tinkoff.py` | тихое смешение валют в одной сумме |
| 14 | Сверка итогов по правильной дате | итоги банк считает по дате ОБРАБОТКИ, а не операции | наш `_vtb_parsed_by_processing_date` | ложную тревогу сверки (важно: проверка должна быть верной, иначе её отключат) |

🔴 **Про «100 % точности», которых просит владелец.** Ни один из четырёх изученных
проектов не заявляет точности вообще. Sberbank2Excel вместо точности обещает **отказ**:
формат не распознан → исключение; сальдо не сошлось → исключение; запись странной формы →
исключение. Проверка №12 (монотонность остатка) — единственная из каталога, которая
проверяет **каждую операцию по отдельности**, а не агрегат; все остальные агрегатные
проверки принципиально не ловят **компенсирующиеся** ошибки (две операции перепутаны
местами; сумма перенесена с одной операции на другую; описание не от той операции).
Поэтому честная формулировка цели не «100 % точности чтения», а:
**«ни одна ошибка чтения не проходит молча»** — и это достижимо, в отличие от первого.

---

## П6. Тестирование парсера

### 6.1 Что уже есть у нас (снято с дерева 16.09.2026)

`tests/`: `test_pdf_parsers.py`, `test_statement_parser.py` (63 стр.),
`test_statement_parser_multibank.py` (119), `test_statement_parser_real_formats.py` (476),
`test_statement_property.py` (191), `test_statement_reconcile.py` (301),
`test_statement_templates.py` (172), `test_import_dedup.py`, `test_bulk_import.py`,
`test_statement_import.py` (35). `hypothesis==6.155.7` уже в `requirements-dev.txt`.

Property-тесты есть и, главное, **их границы честно названы в самом файле**, дословно:

```
**Границы метода.** Генератор знает ровно те шаблоны, что и парсер, поэтому зелёный прогон
здесь НЕ доказывает, что читаются двести банков — это замкнутый круг. Что он доказывает:
устойчивость ВНУТРИ известного формата к вариациям, которые встречаются в живых выписках
(неразрывные пробелы, разделители тысяч и их отсутствие, запятая против точки, суффиксы
валюты, перенос описания внутри ячейки, копеечные суммы, длинные описания). Реальных файлов
на руках одиннадцать — фаззинг закрывает пространство между ними.
```

🔴 Это ровно то ограничение, о котором предупреждает и обзор Chen et al. (см. ниже):
генератор и парсер разделяют одну модель формата, поэтому такой тест проверяет
устойчивость, а не правильность.

### 6.2 Метаморфическое тестирование применительно к ПАРСЕРУ

Первоисточник добыт в Г18 и лежит в `docs/research/raw/closed_forever_retry_2026-09-16.md`:
Chen T.Y., Kuo F.-C., Liu H., Poon P.-L., Towey D., Tse T.H., Zhou Z.Q. «Metamorphic Testing:
A Review of Challenges and Opportunities», *ACM Comput. Surv.* **51, 1, Article 4 (January
2018), 27 pages**, DOI 10.1145/3143561. Дословно оттуда:

> **Definition 1 (Metamorphic Relation).** Let f be a target function or algorithm.
> A metamorphic relation is a necessary property of f over a sequence of two or more
> inputs x₁, x₂, …, xₙ, where n ⩾ 2, and their corresponding outputs f(x₁), …, f(xₙ).

> With MT, it is not necessary to investigate whether P(xᵢ) = f(xᵢ) for any individual test
> case xᵢ — which would require a test oracle. MT therefore alleviates the oracle problem
> in testing.

🔴 **Для парсера оракульная проблема стоит ОСТРЕЕ, чем для матмодели**, и именно поэтому
метод сюда ложится лучше: реальную выписку пользователя мы никогда не увидим, эталона
к ней нет ни у кого, а проверять надо именно её. Метаморфические отношения парсера
(формулируются впервые здесь, в изученных проектах не встречались):

| MR | Преобразование входа | Ожидаемое отношение выходов |
|---|---|---|
| MR-1 (перестановка) | поменять местами две операции в файле | множество операций то же, итоги те же |
| MR-2 (масштаб) | умножить все суммы на 10 | все суммы выхода ×10, число операций неизменно |
| MR-3 (удлинение описания) | удлинить описание одной операции до переполнения колонки | 🔴 **числа НЕ меняются** — прямой тест на дефект из замера 1.5 |
| MR-4 (разрез страницы) | вставить перенос страницы с повтором шапки между двумя операциями | выход неизменен |
| MR-5 (удаление строки) | убрать одну операцию из файла, не трогая итоги шапки | сверка сальдо ОБЯЗАНА дать расхождение ровно на её сумму |
| MR-6 (добавление шума) | заменить обычные пробелы на неразрывные, запятую на точку | выход неизменен |
| MR-7 (дубль) | продублировать операцию в файле | число операций +1, сумма +сумма операции (а НЕ схлопывание в одну) |
| MR-8 (конкатенация) | склеить выписку за январь и за февраль | множество операций = объединение двух разборов |

🔴 MR-5 и MR-7 — самые ценные: первый проверяет, что **самопроверка работает** (тест на
тест), второй — что дедупликация не съедает законные повторы.

Предупреждение обзора, которое обязано попасть в план, дословно:

> **Challenge 2: Systematic MR identification and selection.** … most of these
> identifications were conducted in an ad hoc and arbitrary way.

> … the effectiveness of MRs … **has not been conclusively determined.**

То есть MT для парсера — дополнение к золотым файлам и сверке сальдо, а не замена.

### 6.3 Корпус: чему учит практика двух проектов

- Sberbank2Excel: публичный корпус — **один** анонимизированный файл (1 218 б), остальное
  приватно за `@pytest.mark.private`; растёт по файлу на каждый issue; есть **синтетический
  «теоретический случай»**, руками сконструированный под гипотезу, не встречавшуюся в жизни.
- ofxstatement-russian: корпус **публичный**, 6 файлов по 0,5–10 КБ, включая два варианта
  одного банка (`vtb.csv` и `vtb_user_date.csv`).
- У нас: 10 синтетических шаблонов в `app/data/statement_templates/` + «одиннадцать реальных
  файлов на руках» (по тексту `test_statement_property.py`), регенерация —
  `python -m tools.statement_templates.build_templates`.

🔴 Вывод: **корпус обязан быть двухслойным** — публичные синтетические файлы (в репозитории,
регенерируемые, годятся для CI) и приватные анонимизированные реальные тексты (вне
репозитория, помеченные маркером, пропускаемые в чужом окружении). Оба проекта пришли
к этому независимо. У нас первый слой есть, второго как оформленного механизма нет.

Приём анонимизации у Sberbank2Excel формализован и стоит копирования, дословно из README:

> «Задача состоит в том чтобы удалить неиспользуемую конфиденциальную информацию либо
> заменить используемую конфиденциальную информацию, но сделать это таким образом чтобы
> конвертер всё еще распознавал бы структуру файла **и смог бы выполнить проверку вычисления
> сумм транзакций**.»

То есть анонимизация обязана **сохранять сходимость сальдо** — иначе анонимизированный файл
бесполезен как тест.

### 6.4 Как честно измерять точность

Из материала следует четыре разных числа, которые нельзя смешивать:
1. **Доля разобранных строк** = `parsed / rows`. Это то, что считает наш
   `completeness_verdict`. Не говорит ничего о правильности сумм.
2. **Доля строк с верными суммами** — требует эталона, то есть измеряется только
   на золотых файлах, не на файле пользователя.
3. **Доля файлов, прошедших сверку сальдо** — единственная метрика, измеримая
   на живом потоке без эталона. 🔴 Её и надо объявлять пользователю.
4. **Доля файлов, по которым формат вообще распознан** — отдельная метрика; её падение
   есть индикатор «банк сменил формат», и мониторить надо именно её, а не жалобы.

Ловушка, которую надо назвать явно: `recalculate_balance` из ofxstatement (раздел 2.2)
показывает, как метрика №3 превращается в тождество, если «объявленный» итог мы посчитали
сами. Считать файл проверенным можно **только когда итог напечатан банком**.

---

## П8. Расхождения с тем, как парсер устроен у нас сейчас

> Только фиксация. Код не правился (правило задания). Читалось:
> `app/services/statement_parser.py`, `app/services/statement_reconcile.py`,
> `app/api/routes_banks.py`, `tests/test_statement_property.py`, `tests/test_import_dedup.py`.
> 🔴 Сразу отмечу честно: код зрелее, чем предполагала постановка темы. Колонки по ролям
> шапки, знак из семантики колонки, отсев справок, учёт пропусков с названной причиной,
> отдельный модуль сверки — всё это уже есть, и часть «находок» исследования в нём
> реализована раньше. Ниже — именно расхождения, а не список недостающего.

**Р1. Один парсер на банк против версии формата.** У нас `BANK_PARSERS` отображает
`bank_id → функция`: один `parse_sber_pdf` на Сбер. У Sberbank2Excel на тот же Сбер —
**21 экстрактор**, и выбор между ними построен на пробном разборе. Наш `detect_bank`
возвращает **первое совпадение** маркера:

```python
def detect_bank(text: str) -> str | None:
    low = _norm(text)
    for bank, markers in _BANK_MARKERS:
        if any(marker in low for marker in markers):
            return bank
    return None
```

— то есть (а) нет запрещающих маркеров, (б) нет правила «ровно один кандидат, иначе отказ»,
(в) нет самого понятия версии формата внутри банка. Новый формат Сбера для нас неотличим
от старого: определится как «Сбер», уйдёт в `parse_sber_pdf` и разберётся по правилам
старого формата. Это и есть главный структурный зазор.

**Р2. `float` против `Decimal`, допуск 0.01 против нуля.** У нас `_num()` возвращает
`float`, сверка в `statement_reconcile` идёт с `TOLERANCE = 0.01`. У Sberbank2Excel деньги —
`Decimal`, а условие ошибки — `if balance - calculated_balance:` (любая ненулевая разница).
🔴 Связь прямая: допуск в копейку существует у нас **потому**, что арифметика на `float`;
на `Decimal` он не нужен. Копеечный допуск — это ровно та щель, в которую проходит
компенсирующаяся ошибка округления на большом файле.

**Р3. Сбер разбирается из `page.extract_text()`.** `parse_sber_pdf` собирает строки через
`pdfplumber → extract_text()` и матчит их регуляркой `_SBER_OP`. Замер 1.5 показывает, что
именно `extract_text()` на переполнении колонки даёт посимвольное перемешивание
(`'…ot 012.50 10.0200,2060 za uslu5g8i 500,00'`). Координатного слоя (слова с x/y) в нашем
коде нет вовсе — ни `pdfplumber.extract_words()`, ни `pymupdf`. Для табличных банков (ВТБ,
Райффайзен) роль координат играет `extract_tables()`, что работает, **пока банк рисует
линии**; для Сбера, который их не рисует, страховки нет.

**Р4. Ключ дедупликации — множество, а не мультимножество.** `app/api/routes_banks.py`:

```python
    existing_keys = {
        (row.date, row.amount, row.type, row.description)
        for row in db.query(...)
    }
    ...
        key = (t_date, to_money(t['amount']), t['type'], t.get('description'))
        if key in existing_keys:
            skipped_duplicates += 1
            continue
        existing_keys.add(key)
```

Из этого следуют три расхождения:
1. 🔴 **Две настоящие одинаковые операции в один день схлопываются в одну.** Это не
   предположение — это закреплено тестом `tests/test_import_dedup.py`:
   ```python
    def test_duplicates_within_file_skipped(self, client: TestClient) -> None:
        dup = "Дата;Сумма;Описание\n01.06.2026;-1000;Кофе\n01.06.2026;-1000;Кофе\n"
        body = _upload(client, dup).json()
        assert body["added_count"] == 1
        assert body["skipped_duplicates"] == 1
   ```
   Два одинаковых кофе за день — законный случай, и он теряется. ofxstatement решает
   ровно это счётчиком повторов (`id = initial_id + str(counter)`), Lunch Money — показом
   отфильтрованных дублей отдельным списком с возможностью вернуть.
2. **В ключ входит `description` — НАШЕ производное поле**, а не то, что напечатал банк:
   оно склеено (`merchant = description or category or 'Операция'`) и обрезано до 255.
   Любая будущая правка нормализации описания **задним числом породит дубли** по всей
   истории. У ofxstatement в хеш идут только сырые дата/memo/сумма, и в докстринге прямо
   сказано, что id обязан «stay the same for the same transaction every time you generate».
3. **Ключ живёт в памяти и в запросе, а не в БД как поле операции.** Проверить,
   «та ли это операция», можно только сравнением по всем полям; ни хранимого
   `external_id`, ни его происхождения нет.

**Р5. Тихий пропуск строки прямо в импорте.** Там же, в `routes_banks.py`:

```python
        try:
            t_date = datetime.fromisoformat(t['date']) if isinstance(t['date'], str) else t['date']
        except (ValueError, TypeError):
            continue
```

🔴 `continue` **без счётчика и без причины** — операция исчезает молча. Это прямо
противоречит дисциплине `SKIP_*`, выстроенной в `statement_parser.py` («каждая точка
`continue` обязана назвать причину»), и живёт этажом выше неё, уже после всех сверок:
`completeness_verdict` считает строки на уровне парсера и этой потери не увидит.

**Р6. Политика при расхождении: предупредить, не блокировать.** Наш `statement_reconcile`,
дословно из докстринга: «Политика при расхождении (решение владельца): **предупредить,
но не блокировать**… Блокировка опаснее: наш собственный промах в чтении итогов оставил
бы человека вообще без импорта». У Sberbank2Excel — противоположное: исключение и никакого
выходного файла, обход только явным флагом `-b`. **Это названное решение владельца, а не
дефект**; фиксирую как расхождение с отраслевым образцом и отмечаю средний путь из
invoice2data: строгость сделана **свойством формата** (`required_fields` → исключение,
сверка итога → предупреждение с допуском, `strict_fields` → опция). То есть можно
блокировать там, где мы формату доверяем, и предупреждать там, где нет, не выбирая
одно на всё.

**Р7. Проверок из каталога 3.3 у нас нет четырёх:** №9 (даты внутри объявленного периода),
№10 (соответствие знака колонке как перекрёстная проверка — знак из колонки берётся,
но с символом `+`/`-` не сверяется), №11 (чистота числовой ячейки), №12 (монотонность
колонки остатка). 🔴 Последняя — единственная построчная проверка из всего каталога,
и данные для неё у нас уже извлекаются (`balance_account_currency` у Сбера, колонка
остатка у ВТБ).

**Р8. Тестовый корпус односложен.** Есть 10 синтетических шаблонов и property-тесты
(с честно названной границей «генератор знает те же шаблоны, что и парсер»), но нет
(а) оформленного приватного слоя реальных анонимизированных текстов с маркером пропуска
(`@pytest.mark.private` у Sberbank2Excel), (б) требования «анонимизация сохраняет
сходимость сальдо», (в) метаморфических тестов (MR-1…MR-8 из 6.2), (г) регрессионного
файла на каждый найденный дефект формата (у Sberbank2Excel — `..._issue_31_...`,
`..._issue_33_...`, `..._issue_36_theoretical_case_...`).

---

## П2.3. Сколько стоит поддерживать формат одного банка в год — по журналу issue

Источник: `api.github.com/repos/Ev2geny/Sberbank2Excel/issues?state=all&per_page=100`
(200, снято 16.09.2026), 85 записей, из них отобраны не-PR.

**Обращений в год (всего / из них про слом формата)** — отбор по заголовку
(«перестал», «поменял», «не работает», «новый формат», «не конверт», «новая форма»):

| Год | Всего issue | Про слом формата |
|---|---|---|
| 2020 | 5 | 1 |
| 2021 | 9 | 3 |
| 2022 | 7 | 1 |
| 2023 | 6 | 0 |
| 2024 | 23 | **8** |
| 2025 | 14 | 3 |
| 2026 (до 16.09) | 9 | **7** |

**Лаг «сообщили → закрыли» по этим же issue, в днях** (отсортировано):
`0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 4, 6, 6, 11, 12, 12, 14, 19, 23, 58, 81, 84`.
Медиана — **6 дней**, среднее ≈ 15, максимум 84 дня
(`#57 SBER_DEBIT_2408 не работает, если транзакция разнесена…`, 23.12.2024 → 17.03.2025).

Конкретные эпизоды 2026 года, дословно из заголовков:
`#80 «Сбербанк поменял форму выписки дебетовой карты»` (16.03 → 08.04, **23 дня**);
`#81 «Сбербанк поменял форму выписки по платёжному счёту»` (05.04, в тот же день);
`#82 «Сбербанк поменял форму выписки по счёту "Накопительный счёт"»` (05.04, в тот же день);
`#83 «Выписка по платёжному счёту всё еще не работает на релизе 5.2.0»` (08.04 — то есть
**первая починка не сработала**); `#84 «Выписка по счёту дебетовой карты перестала
работать»` (17.04); `#87 «Опять перестали конвертиться выписки, кредитная и дебетовая»`
(28.05 → 01.06); `#88 fix(DEBIT_2604b)` (31.05 → 01.06).

🔴 **Оценка трудозатрат (это ОЦЕНКА, а не замер — так и называю).**
Замеренная часть: объём одного формата — **199 строк в пяти файлах, 0 удалений**
(коммит `0f6c85e4`); частота событий — **7 сломов за 8,5 месяцев 2026 года на одном банке**;
медианный лаг — 6 дней. Не замерено: сколько часов автор реально тратит (в журнале
нет учёта времени).
Исходя из объёма (≈200 строк по готовому шаблону + прогон `debug_extractor` + проверка
сходимости сальдо) и из того, что половина issue закрывается в день обращения, разумная
вилка — **4–8 часов на один формат при готовом каркасе**, плюс 1–2 часа на триаж и переписку
с пользователем (получить анонимизированный текст). Эпизод `#83` показывает, что с
вероятностью, которую тут видно как 1 из 7, потребуется **второй заход**, то есть надо
закладывать множитель ≈1,2.
**Итого на один банк уровня Сбера: 5–7 событий в год × (5–10 ч) ≈ 30–70 часов в год.**
На четырёх банках (Сбер, Т-Банк, ВТБ, Райффайзен) при том же характере поведения —
🔴 **порядка 100–250 часов в год, то есть от полумесяца до полутора месяцев чистой работы
одного человека, только на поддержание чтения файлов.** Это ответ на вопрос итога
и одновременно аргумент за то, чтобы вся вариативность формата жила в данных (шаблон),
а не в коде.

🔴 **Отдельная находка из того же журнала, прямо подтверждающая расхождение Р2.**
Три issue подряд, дословно по заголовкам:
`#71 «Не использовать float при подсчете денежных значений»` (16.10.2025 → 02.12.2025),
`#72 «Replace get_float_from_money with get_decimal_from_money»` (16.10.2025 → 03.11.2025),
`#76 «Replace get_float_from_money with get_decimal_from_money»` (03.11.2025 → 09.11.2025).
То есть проект **осознанно мигрировал с `float` на `Decimal` в конце 2025 года** — это
не стилистический выбор автора, а исправленный дефект. У нас в `statement_parser._num`
сейчас `float`, и допуск `TOLERANCE = 0.01` в сверке — прямое следствие того же класса.

Ещё два заголовка из журнала, описывающие классы дефектов, которых у нас в тестах нет:
`#57 «SBER_DEBIT_2408 не работает, если транзакция разнесена…»` (перенос записи),
`#79 «SBER_CREDIT_2511 не работает при многострочной трансакции»`,
`#11 «Не конвертируется выписка с большим расстоянием между с…»` (разрядка/интервалы),
`#39 «Формат типа SBER_DEBIT_2212 перестал работать в случае ст…»`,
`#34 «SBER_SAVING_2303 не работает если "Пополнение" или "Спи…"»` (отсутствующий итог
в шапке — то есть отказ самой самопроверки).
🔴 Последний класс важен отдельно: **самопроверка сама является источником отказов**, когда
банк перестаёт печатать итог. Значит, отсутствие объявленного итога надо трактовать
не как ошибку файла, а как понижение гарантии (см. метрику №3 в 6.4).

---

## П7. Юридическая рамка: приём и хранение исходных PDF

> Материал добыт вторым субагентом 16.09.2026, бюджет 12 действий израсходован полностью.
> 🔴 Замечание по каналу, полезное на будущее: `consultant.ru` через `curl -sk --http1.1`
> с браузерным UA отдавал **HTTP 200 на всех запросах, 403 не было ни разу**. Ограничение
> не антибот, а расписание некоммерческой версии для ПОДЗАКОННЫХ актов («по рабочим дням
> с 20-00 до 24-00 МСК»); кодексы и федеральные законы отдаются круглосуточно.

### 7.1 Приём выписки на почту сервиса

Прямого запрета в нормах нет; запрет заменён обязанностями. ФЗ от 27.07.2006 № 152-ФЗ,
ст. 7 (`consultant.ru/document/cons_doc_LAW_61801/a15bab60.../`, 200, 38 846 б):

```
Статья 7. Конфиденциальность персональных данных
Операторы и иные лица, получившие доступ к персональным данным, обязаны не
раскрывать третьим лицам и не распространять персональные данные без согласия
субъекта персональных данных, если иное не предусмотрено федеральным законом.
```

Ст. 19 (там же, `ca9e5658.../`, 200, 92 474 б), выборочно дословно:

```
1. Оператор при обработке персональных данных обязан принимать необходимые
правовые, организационные и технические меры или обеспечивать их принятие для
защиты персональных данных от неправомерного или случайного доступа к ним,
уничтожения, изменения, блокирования, копирования, предоставления,
распространения персональных данных, а также от иных неправомерных действий...
2. Обеспечение безопасности персональных данных достигается, в частности:
...
3) применением прошедших в установленном порядке процедуру оценки соответствия
средств защиты информации;
3.1) применением для уничтожения персональных данных прошедших в установленном
порядке процедуру оценки соответствия средств защиты информации, в составе
которых реализована функция уничтожения информации;
(п. 3.1 введен Федеральным законом от 08.08.2024 N 233-ФЗ)
...
8) установлением правил доступа к персональным данным, обрабатываемым в
информационной системе персональных данных, а также обеспечением регистрации
и учета всех действий, совершаемых с персональными данными в информационной
системе персональных данных;
```

🔴 Вывод (вывод, не норма): почтовый ящик не даёт **регистрации и учёта всех действий**
(п. 8 ч. 2 ст. 19) и делает почтового провайдера фактическим третьим лицом, у которого
копия остаётся вне контроля оператора. Позиция Роскомнадзора дословно **не добыта**;
во вторичном источнике (ГАРАНТ.РУ) она передаётся как «сама по себе передача персональных
данных по незащищённым каналам связи Законом N 152-ФЗ не запрещена» — **пересказ, не цитата**.

### 7.2 Банковская тайна: ст. 26 ФЗ от 02.12.1990 № 395-1 (ред. от 04.08.2026)

`consultant.ru/document/cons_doc_LAW_5842/5583e2ca.../`, 200, 250 437 б. Дословно:

```
Кредитная организация, Банк России, организация, осуществляющая функции по
обязательному страхованию вкладов, гарантируют тайну об операциях, о счетах и
вкладах своих клиентов и корреспондентов. Все служащие кредитной организации
обязаны хранить тайну об операциях, о счетах и вкладах ее клиентов и
корреспондентов...
```

```
Справки по счетам и вкладам физических лиц выдаются кредитной организацией им
самим, законным представителям несовершеннолетних... судам, органам
принудительного исполнения... (в ред. Федеральных законов от 03.08.2018 N 322-ФЗ,
от 24.06.2025 N 163-ФЗ)
```

Абзац об ответственности перечисляет субъектов закрытым списком (Банк России,
госорганы, «кредитные, аудиторские и иные организации», уполномоченный орган по ПОД/ФТ
и т. д.).

🔴 Вывод субагента (вывод, не норма): перечень построен по субъектному признаку и рассчитан
на тех, кто получает сведения **от банка**. Сервис, получающий выписку **от самого клиента**,
в нём прямо не назван; единственная растяжимая зацепка — «иные организации», её судебное
толкование не проверялось (`kad.arbitr.ru` отдаёт 451). Клиент — первый в перечне лиц,
которым справка выдаётся законно, то есть он ею распоряжается правомерно. Режим 152-ФЗ
при этом сохраняется полностью.

### 7.3 Сроки хранения и уничтожение

ФЗ № 152-ФЗ, ст. 5 ч. 7 (`cons_doc_LAW_61801/96fbc469.../`, 200, 52 516 б):

```
7. Хранение персональных данных должно осуществляться в форме, позволяющей
определить субъекта персональных данных, не дольше, чем этого требуют цели
обработки персональных данных, если срок хранения персональных данных не
установлен федеральным законом, договором... Обрабатываемые персональные данные
подлежат уничтожению либо обезличиванию по достижении целей обработки или в
случае утраты необходимости в достижении этих целей, если иное не предусмотрено
федеральным законом.
```

Ст. 21 (`d3fe43a7.../`, 200, 73 806 б), ключевые части дословно:

```
2. ...обязан уточнить персональные данные... в течение семи рабочих дней...
3. В случае выявления неправомерной обработки... в срок, не превышающий трех
рабочих дней с даты этого выявления, обязан прекратить неправомерную обработку...
В случае, если обеспечить правомерность обработки... невозможно, оператор в срок,
не превышающий десяти рабочих дней с даты выявления... обязан уничтожить...
3.1. ...уведомить уполномоченный орган... 1) в течение двадцати четырех часов о
произошедшем инциденте... 2) в течение семидесяти двух часов о результатах
внутреннего расследования... (часть 3.1 введена Федеральным законом от 14.07.2022 N 266-ФЗ)
4. В случае достижения цели обработки... уничтожить персональные данные... в срок,
не превышающий тридцати дней с даты достижения цели обработки...
5. В случае отзыва субъектом... согласия... в срок, не превышающий тридцати дней
с даты поступления указанного отзыва...
```

🔴 **Точность, которую надо унести в юрблок:** «7 рабочих дней» — это срок **уточнения**
неточных ПДн (ч. 2), а **не** срок уничтожения. Сроки уничтожения: **30 дней** (ч. 4 —
достижение цели; ч. 5 — отзыв согласия) и **10 рабочих дней** (ч. 3, при невозможности
сделать обработку правомерной, плюс 3 рабочих дня на её прекращение). Формулировка
«30 дней / 7 рабочих дней» в постановке темы смешивает два разных института.

**Приказ Роскомнадзора от 28.10.2022 № 179** «Об утверждении Требований к подтверждению
уничтожения персональных данных» (Минюст 28.11.2022, № 71167). Текст добыт с
`rulaws.ru/acts/Prikaz-Roskomnadzora-ot-28.10.2022-N-179/` (200, 54 074 б); на
`consultant.ru` — заглушка расписания (200, 29 306 б). Дословно:

```
2. Настоящий приказ вступает в силу с 1 марта 2023 г. и действует до 1 марта 2029 г.

2. В случае если обработка персональных данных осуществляется оператором с
использованием средств автоматизации, документами, подтверждающими уничтожение
персональных данных субъектов персональных данных, являются акт об уничтожении
персональных данных... и выгрузка из журнала регистрации событий в информационной
системе персональных данных (далее - выгрузка из журнала).

5. Выгрузка из журнала должна содержать:
а) фамилию, имя, отчество (при наличии) субъекта (субъектов)...;
б) перечень категорий уничтоженных персональных данных...;
в) наименование информационной системы персональных данных, из которой были
уничтожены персональные данные...;
г) причину уничтожения персональных данных;
д) дату уничтожения персональных данных субъекта (субъектов) персональных данных.

8. Акт об уничтожении персональных данных и выгрузка из журнала подлежат
хранению в течение 3 лет с момента уничтожения персональных данных.
```

🔴 Для нас это **техническое** требование, а не бумажное: журнал обязан по каждому
удалению логировать субъекта, категории ПДн, имя ИСПДн, причину и дату. Подтверждающие
документы хранятся 3 года — дольше, чем сами данные.

### 7.4 Уровень защищённости и шифрование

ПП РФ от 01.11.2012 № 1119 (`cons_doc_LAW_137356/8c86cf63.../`, 200, 73 100 б),
искомый пункт дословно:

```
12. Необходимость обеспечения 4-го уровня защищенности персональных данных при
их обработке в информационной системе устанавливается при наличии хотя бы одного
из следующих условий:
а) для информационной системы актуальны угрозы 3-го типа и информационная система
обрабатывает общедоступные персональные данные;
б) для информационной системы актуальны угрозы 3-го типа и информационная система
обрабатывает иные категории персональных данных сотрудников оператора или иные
категории персональных данных менее чем 100000 субъектов персональных данных,
не являющихся сотрудниками оператора.
```

```
11. ...д) для информационной системы актуальны угрозы 3-го типа и информационная
система обрабатывает иные категории персональных данных более чем 100000 субъектов
персональных данных, не являющихся сотрудниками оператора.
```

```
4. Выбор средств защиты информации для системы защиты персональных данных
осуществляется оператором в соответствии с нормативными правовыми актами,
принятыми Федеральной службой безопасности Российской Федерации и Федеральной
службой по техническому и экспортному контролю...
```

🔴 Итог: при наших исходных (иные категории ПДн, субъекты — не сотрудники, менее
100 000, угрозы 3-го типа) — **4-й, низший уровень защищённости** по п. 12 «б».
**Обязанности шифровать хранимые файлы ПП 1119 не устанавливает** — оно задаёт уровень,
а состав мер отнесён к актам ФСТЭК и ФСБ (п. 4). Порог **100 000 субъектов** — это порог
перехода на УЗ-3 (п. 11 «д»): рост продукта сам по себе поднимает требования, и это
архитектурный риск, а не разовая констатация.

### 7.5 Избыточные данные в выписке

ФЗ № 152-ФЗ, ст. 5 (тот же URL, 200, 52 516 б), дословно:

```
4. Обработке подлежат только персональные данные, которые отвечают целям их обработки.
5. Содержание и объем обрабатываемых персональных данных должны соответствовать
заявленным целям обработки. Обрабатываемые персональные данные не должны быть
избыточными по отношению к заявленным целям их обработки.
```

🔴 Вывод (вывод, не норма): после разбора файла цель «извлечь операции» достигнута,
а исходный PDF несёт номер счёта, ФИО, адрес, номер карты — данные, модели не нужные.
По ч. 5 они избыточны, по ч. 7 утратили необходимость. **Нормы, буквально предписывающей
«удалить исходный PDF», нет**; вывод следует из связки ч. 5 + ч. 7 ст. 5 и ч. 4 ст. 21
(30 дней). Прямая альтернатива уничтожению, названная в самой норме, — **обезличивание**.

### 7.6 Что по праву НЕ добыто

1. **Дословная позиция Роскомнадзора** о пересылке ПДн по e-mail — страницы
   `77.rkn.gov.ru/p3852/p13239/p13309/` и `garant.ru/consult/business/1793028/`
   не открывались, бюджет ушёл на первоисточники норм. Имеющееся — пересказ.
2. **Ст. 9 152-ФЗ (условия согласия)** — не запрашивалась; URL известен.
3. **Ст. 21, части 6 и далее** — извлечение оборвалось на ч. 5 по ограничению длины вывода.
4. 🔴 **Приказ ФСТЭК России от 18.02.2013 № 21** — не запрашивался. Именно он задаёт
   конкретный набор мер для УЗ-4 и отвечает на вопрос, обязательно ли шифрование хранимых
   файлов. **Это главная незакрытая дыра пункта 7.**
5. 🔴 **Приказ ФСБ России от 10.07.2014 № 378** — не запрашивался; отвечает на вопрос,
   когда требуется сертифицированное СКЗИ.
6. **Официальное опубликование Приказа РКН № 179** не сверено: `publication.pravo.gov.ru`
   по номеру `0001202211290004` (200, 22 790 б) вернул **соседний** документ — Приказ РКН
   от 27.10.2022 № 178 (Минюст № 71166). Для сверки нужен поиск по реестру Минюста № 71167.
7. **Судебная практика** по вопросу, тянется ли режим ст. 26 № 395-1 на небанковского
   получателя выписки от самого клиента («иные организации») — не проверялась,
   `kad.arbitr.ru` отдаёт 451.

---

# ИТОГ Г20

## И1. Главный вывод, к которому свёлся весь материал

🔴 **Цель «100 % точности чтения» недостижима и, что важнее, непроверяема: у файла
пользователя нет эталона ни у нас, ни у кого-либо.** Достижима и проверяема другая цель —
**«ни одна ошибка чтения не проходит молча»**. Все четыре изученных зрелых парсера
(Sberbank2Excel, ofxstatement, ofxstatement-russian, invoice2data) не обещают точности
вообще; вместо этого они обещают **отказ**: формат не распознан — исключение, сальдо
не сошлось — исключение, запись странной формы — исключение, обязательное поле
отсутствует — исключение. Точность у них — не свойство алгоритма, а следствие того,
что неточность не может пройти незамеченной.

Второй вывод того же веса: **вариативность формата обязана жить в данных, а не в коде.**
Замер по журналу Sberbank2Excel: 21 формат одного банка, 5 из них за первые пять месяцев
2026 года, 7 обращений «банк поменял форму» за 8,5 месяцев 2026 года. При одном парсере
на банк это означает переписывание кода 5–7 раз в год на каждый банк.

## И2. Архитектура парсера, которую стоит принять (пять слоёв, каждый с обоснованием)

**Слой 0. Приём файла и классификация документа.**
Отсев «это не выписка операций» (справка об остатке, реквизиты) — до всего остального.
*Обоснование:* у нас уже реализовано (`classify_non_statement`, `pdf_non_statement_reason`),
и это правильный порядок: иначе «0 операций» будет истолковано как пустая выписка.
Добавить сюда же различение «текстовый слой есть / это скан»: при отсутствии текстового
слоя — **немедленный отказ с объяснением**, а не пустой результат. (OCR темой исключён.)

**Слой 1. PDF → слова с координатами (а не → текст).**
Единица извлечения — слово с `(x0, y0, x1, y1)`. Строки собираются группировкой по y
с допуском ~3 pt; колонки задаются **якорями x0 слов строки-шапки**; каждое слово
относится к последнему якорю ≤ x0.
*Обоснование — замеры 1.1–1.5, а не мнение:* `pdftotext` без `-layout` перемешивает
колонки по-колоночно и теряет связь «сумма ↔ операция» безвозвратно; `pdftotext -layout`
на переполнении колонки рвёт число `25 000,00` на «25» и «000,00»; `pdfplumber.extract_text()`
на том же файле выдаёт посимвольную кашу `'…ot 012.50 10.0200,2060 za uslu5g8i 500,00'`;
координатный разбор с якорями на том же файле **вернул сумму и остаток верно**.
Наивная кластеризация всех x0 проверена и **отвергнута замером**: 25 «колонок» на таблицу
из 7. Инструмент — `pymupdf` (в 4–8 раз быстрее `pdfplumber` на тех же файлах) либо
`pdfplumber.extract_words()`; `extract_tables()` оставить как **быстрый путь только для
банков, рисующих линии** (на файлах без линий он вернул 0 таблиц).

**Слой 2. Отпечаток формата и выбор обработчика.**
Отпечаток двусторонний: набор обязательных маркеров (конъюнкция) + набор **запрещающих**.
Выбор формата — **пробным разбором**: кандидат считается подходящим, только если отпечаток
сошёлся, контрольный итог периода извлёкся числом и нашлась хотя бы одна операция.
Ноль кандидатов — отказ. **Больше одного кандидата — тоже отказ.**
*Обоснование:* это буквально `check_support()` + `determine_extractor_auto()` Sberbank2Excel
и `matches_input()` + `exclude_keywords` invoice2data — два независимых проекта пришли
к одному. Запрещающие маркеры — единственное, что разводит близкие форматы одного банка
(`SBER_DEBIT_2603` отличается от соседа отсутствием `ОСТАТОК ПО СЧЁТУ` и подписи
`Дергунова К. А.`).

**Слой 3. Описание формата ДАННЫМИ.**
Формат — запись (YAML/JSON), а не функция: `keywords`, `exclude_keywords`, `columns`
(роль → подпись в шапке), `totals` (как достать объявленные итоги), `record` (якорь
начала записи, признак строки-продолжения, признак конца блока), `strictness` (блокировать
или предупреждать).
*Обоснование:* invoice2data (`lines: start/end/first_line/line/last_line`) показывает, что
класс «таблица операций с многострочными записями» описывается декларативно целиком.
При этом 🔴 **не копировать их привязку к числу пробелов** (`[ ]{10,22}`) — она и есть то,
что ломается при переполнении колонки; у нас место пробелов занимают координатные якоря.
Цена вопроса измерена: новый формат у Sberbank2Excel — 199 строк кода и 0 удалений;
в декларативной схеме это ~40 строк данных и 0 строк кода.

**Слой 4. Нормализация значений.**
Деньги — **`Decimal`** от строки, без промежуточного `float`. Нормализация типографики
(`unidecode`-подобная свёртка неразрывных пробелов) — **до** разбора числа. Знак берётся
из **колонки**, символ `+`/`-` используется как перекрёстная проверка, а не как источник.
Даты — по списку допустимых форматов формата, а не угадыванием.
*Обоснование:* `get_decimal_from_money` Sberbank2Excel; их же issue `#71 «Не использовать
float при подсчете денежных значений»` и `#72/#76 «Replace get_float_from_money with
get_decimal_from_money»` (окт.–дек. 2025) — то есть проект **прошёл эту ошибку и исправил
её**; замер 1.4 показывает, что знак однозначно читается из колонки.

**Слой 5. Самопроверки и вердикт.**
См. И3. Вердикт — объект, а не булево: `status`, какие проверки выполнены, какие
недоступны, расхождение с числами. Пользователю показывается, **что именно проверено**,
и это же число (доля файлов, прошедших сверку сальдо) — единственная честная метрика
качества на живом потоке.

**Чего в архитектуре НЕТ и почему.** Грамматик (`lark`, `parsimonious`) — ни один из
четырёх зрелых проектов их не применяет, и целевой поиск открытого парсера выписок
на грамматике не нашёл ничего; у документа нет устойчивого синтаксиса, у него есть якоря
и координаты. ML — по требованию владельца; отмечено, что invoice2data в 2026 году держит
ML **только как fallback и генератор шаблона**, то есть даже там правила остаются основным
путём.

## И3. Самопроверки, дающие ОТКАЗ вместо тихой ошибки

Порядок — от дешёвых к дорогим; первая несработавшая останавливает разбор.

| Уровень | Проверка | Реакция |
|---|---|---|
| Документ | текстовый слой есть | 🔴 отказ: «это скан, операции прочитать нельзя» |
| Документ | это выписка операций, а не справка | 🔴 отказ с названной причиной (есть) |
| Формат | отпечаток сошёлся ровно у одного обработчика | 🔴 отказ: 0 — «формат неизвестен», >1 — «формат неоднозначен» |
| Формат | объявленный итог периода извлёкся числом | отказ формата-кандидата (часть пробного разбора) |
| Запись | форма записи в допустимых границах (N строк, обязательные поля) | 🔴 отказ **с показом самой записи** |
| Запись | ячейка суммы после изъятия числа пуста | 🔴 отказ: переполнение соседней колонки (единственный способ поймать «25» вместо «25 000,00») |
| Запись | знак в ячейке не противоречит колонке | 🔴 отказ: колонки съехали |
| Запись | дата внутри объявленного периода | 🔴 отказ: сдвиг года / перепутаны ДД-ММ |
| Запись | валюта операции = валюте счёта | операция откладывается с сообщением, не пересчитывается |
| Файл | **монотонность остатка**: `остаток[i] − остаток[i−1] == сумма[i]` | 🔴 **самая сильная проверка: единственная построчная**; отказ с указанием номера строки |
| Файл | сходимость оборотов: `Σприход − Σрасход == объявленный баланс` | отказ / предупреждение по `strictness` формата |
| Файл | сходимость остатков: `вход + приход − расход == выход` | то же |
| Файл | число операций == объявленному | то же |
| Файл | полнота разбора: каждая пропущенная строка имеет НАЗВАННУЮ причину | 🔴 отказ, если есть пропуски по нашей вине (есть) |

**Три правила, без которых этот список не работает.**
1. 🔴 **Проверка агрегата не ловит компенсирующиеся ошибки** (две операции поменялись
   местами; сумма перенесена с одной на другую; описание не от той операции). Единственная
   защита от них в списке — монотонность остатка. Если банк остаток не печатает,
   **гарантия принципиально ниже, и это надо говорить пользователю, а не умалчивать**.
2. 🔴 **Итог, посчитанный нами самими, проверкой не является.** `recalculate_balance`
   из ofxstatement — иллюстрация вырождения: сверять разобранное с суммой разобранного
   бессмысленно. Проверенным файл считается, только когда итог **напечатан банком**.
3. 🔴 **Самопроверка сама становится источником ложных отказов**, когда банк перестаёт
   печатать итог (`#34 SBER_SAVING_2303 не работает если "Пополнение" или "Спи…"`) или
   считает его по другой дате (наш случай с ВТБ: итоги по дате обработки). Поэтому строгость
   — свойство формата (`strictness`), а не глобальная политика, и «итога нет» трактуется
   как **понижение гарантии**, а не как ошибка файла.

## И4. План тестового корпуса

**Слой А — публичный синтетический** (в репозитории, регенерируемый, идёт в CI).
Есть: 10 шаблонов + `tools.statement_templates.build_templates`. Добавить генерацию
патологий, по одному файлу на класс: переполнение колонки (замер 1.5); перенос страницы
с повтором шапки; многострочное описание в 2, 3 и 4 строки; вторая строка шапки под
колонкой даты («Выполнена банком», «В обработке»); операция в чужой валюте; нулевая
сумма; отклонённая банком операция; две **идентичные** операции в один день; отсутствующий
итог в шапке; итог, посчитанный по дате обработки.

**Слой Б — приватный реальный** (вне репозитория). Анонимизированные **текстовые**
представления реальных выписок, помеченные маркером пропуска (`@pytest.mark.private`
по образцу Sberbank2Excel), чтобы CI и чужое окружение проходили без них.
🔴 Требование к анонимизации, дословно перенимаемое: заменять данные так, **чтобы парсер
всё ещё мог выполнить проверку сходимости сумм** — иначе анонимизированный файл бесполезен.

**Слой В — регрессия по дефектам.** Файл на каждый найденный дефект, имя содержит его
идентификатор (образец: `..._issue_33_...`, `..._issue_36_theoretical_case_...`, где
последний — **синтетический случай под гипотезу, в жизни не встречавшуюся**).

**Слой Г — property-based.** Есть (`test_statement_property.py`) с честно названной
границей «генератор знает те же шаблоны, что и парсер».

**Слой Д — метаморфический** (нет, добавить). MR-1…MR-8 из раздела 6.2; приоритет —
MR-3 (удлинение описания: числа не меняются), MR-5 (удаление строки: сверка ОБЯЗАНА
сработать — тест на тест) и MR-7 (дубль: число операций +1, а не схлопывание).
Оговорка обзора Chen et al. держится в уме: «the effectiveness of MRs … has not been
conclusively determined», метод дополняет золотые файлы, а не заменяет их.

**Четыре метрики, которые нельзя смешивать:** доля разобранных строк · доля строк
с верными суммами (только на золотых файлах) · **доля файлов, прошедших сверку сальдо**
(единственная измеримая на живом потоке — её и объявлять) · доля файлов с распознанным
форматом (её падение = «банк сменил формат», это и есть сигнал мониторинга).

## И5. Сколько стоит поддерживать формат одного банка в год

Замерено (журнал issue Sberbank2Excel, раздел П2.3): **7 обращений «формат сломался»
за 8,5 месяцев 2026 года** на одном банке (2024 — 8, 2025 — 3); медианный лаг «сообщили →
закрыли» **6 дней**, максимум 84; объём одного формата — **199 строк в 5 файлах, 0 удалений**;
в 1 случае из 7 потребовался **второй заход** (`#83 «…всё еще не работает на релизе 5.2.0»`).
Оценено (не замерено, часы в журнале не учитываются): **5–10 ч на событие**, включая
триаж и переписку ради анонимизированного образца.

🔴 **Один банк уровня Сбера: 5–7 событий × 5–10 ч ≈ 30–70 часов в год.
Четыре банка (Сбер, Т-Банк, ВТБ, Райффайзен): порядка 100–250 часов в год** — от полумесяца
до полутора месяцев чистой работы одного человека **только на поддержание чтения файлов**.
Это и есть экономическое обоснование слоя 3 (формат данными): при декларативном описании
событие стоит правки записи, а не написания функции, и — главное — может быть отдано
пользователю/поддержке без релиза кода.

## И6. 🔴 Что противоречит тому, как парсер устроен у нас сейчас

Полностью — в разделе П8; здесь — сжатый перечень, **код не правился**:

1. **Один парсер на банк** (`BANK_PARSERS: bank_id → функция`), тогда как у одного Сбера
   21 версия формата. `detect_bank` возвращает **первое совпадение** маркера, без
   запрещающих маркеров и без правила «ровно один кандидат, иначе отказ». Новый формат
   Сбера будет разобран правилами старого. **Главный структурный зазор.**
2. **Деньги во `float`** (`_num`) и допуск `TOLERANCE = 0.01` в сверке — как следствие.
   Эталонный проект прошёл ровно этот путь и исправил его на `Decimal` в конце 2025 года.
3. **Сбер разбирается из `page.extract_text()`** — режим, давший в замере 1.5 худший
   результат из трёх. Координатного слоя в коде нет вовсе; для табличных банков его роль
   играет `extract_tables()`, работающий, **пока банк рисует линии**.
4. **Ключ дедупликации — множество `(date, amount, type, description)`**: две настоящие
   одинаковые операции в один день схлопываются в одну (закреплено тестом
   `test_duplicates_within_file_skipped`); в ключ входит НАШЕ производное `description`
   (склеенное, обрезанное до 255) — правка нормализации задним числом породит дубли;
   идентификатор нигде не хранится. Эталон (ofxstatement): детерминированный sha1 от сырых
   (дата, memo, сумма) + счётчик повторов, с явным требованием «stay the same for the same
   transaction every time you generate».
5. **Тихий `continue` в `routes_banks.py`** при неразобранной дате — без счётчика и без
   причины, этажом выше дисциплины `SKIP_*` и после всех сверок; `completeness_verdict`
   этой потери не видит.
6. **Политика «предупредить, не блокировать»** против отказа у эталона. Это **решение
   владельца**, а не дефект; средний путь из invoice2data — сделать строгость свойством
   формата, а не глобальной политикой.
7. **Нет четырёх проверок** из И3: даты внутри периода, сверка знака с колонкой,
   чистота числовой ячейки, **монотонность остатка** (единственная построчная; данные
   для неё у Сбера и ВТБ уже извлекаются).
8. **Дедупликация файлового импорта — наша зона ответственности целиком.** Разобранный
   «приём Дзен-мани» (дата–получатель–сумма + корректировка остатка) работает у них
   **только на прямой синхронизации с банком**; при файловом импорте они прямо пишут
   «Убедитесь, что в файле только те операции, которые действительно отсутствуют».
   Переносить его на наш канал придётся самим, первоисточника для этого нет.

## И7. Что осталось неизвестным

- **`camelot` и `tabula` не замерялись** — их нет в окружении (нужны ghostscript и JVM),
  а на двухстрочных синтетических таблицах замер был бы бессмысленным. Сравнение с ними
  остаётся непроведённым; выводы И2 на них не опираются.
- **Замеры сделаны на синтетике.** Реальных банковских выписок в работе не было (правило 7
  проекта). Порядок инструментов переносим, абсолютные проценты точности — нет.
- **CoinKeeper и MoneyWiz** (поведение при нераспознанном, дедупликация) — не добыты:
  бюджет субагента кончился раньше, ни одной попытки по доменам не сделано.
- **Правило сверки полей у Tiller** — не добыто: старый URL 404, ID статьи переиспользован,
  нужный раздел живёт якорем внутри другой статьи.
- **Приказ ФСТЭК № 21 и Приказ ФСБ № 378** — не запрашивались; именно они отвечают на
  вопрос, обязательно ли шифрование хранимых PDF и когда нужно сертифицированное СКЗИ.
  🔴 Главная незакрытая дыра по праву.
- **Дословная позиция Роскомнадзора** о пересылке ПДн по e-mail — только пересказ из
  вторичного источника.
- **Официальное опубликование Приказа РКН № 179** не сверено (по указанному номеру
  публикации лежит соседний приказ № 178).
- **Судебное толкование «иных организаций»** в ст. 26 № 395-1 применительно к
  небанковскому получателю выписки — не проверялось (`kad.arbitr.ru` отдаёт 451).
- **Точная трудоёмкость формата в часах** — не замерена нигде: в журнале Sberbank2Excel
  учёта времени нет, вилка 5–10 ч выведена из объёма кода и доли задач, закрытых в день
  обращения.


---

## ДОБОР Г22 (16.09.2026) — технический контур 152-ФЗ

**Заказ:** COVERAGE_AUDIT_3.md, раздел «→ Г22». Главная дыра Г20: Приказ ФСТЭК № 21
и Приказ ФСБ № 378 не запрашивались ни разу, а именно они отвечают, обязательно ли
шифровать хранимые PDF-выписки.

**Классификация запроса:** breadth-first — восемь независимых нормативных под-вопросов,
каждый отвечается своим первоисточником. Depth-first не подходит: это не «разные школы
мысли об одном», а разные акты. Straightforward тоже нет: восемь актов, часть за
антиботом. Рассмотренные и отвергнутые способы: (а) идти через обзорные статьи
интеграторов (отвергнут — Г20 уже дал пересказ, заказ требует дословного текста);
(б) один агент на весь батч (отвергнут — бюджет одного агента кончился в Г20 на
половине); (в) **выбран:** нормативное ядро (пп. 1–3, 7) вахта снимает сама прямым
`curl` с сайтов регуляторов, а рассеянные по источникам пункты (4–6, 8) отдаются
двум последовательным подагентам.

**Время попыток:** 12:38–13:05 МСК (по mtime снятых файлов) 16.09.2026. Это ВНЕ окна 20–24 МСК, в котором
некоммерческая версия `consultant.ru` отдаёт подзаконные акты, — поэтому приказы
брались с сайтов ведомств и с `pravo.gov.ru`, а не с «Консультанта». Отсутствие
приказа в выдаче «Консультанта» в этом батче ничего не означает.

---

### 1. Приказ ФСТЭК России от 18.02.2013 № 21 — состав мер для 4-го уровня защищённости

**Источник:** https://fstec.ru/dokumenty/vse-dokumenty/prikazy/prikaz-fstek-rossii-ot-18-fevralya-2013-g-n-21
— `curl -sk --http1.1` с браузерным UA, **HTTP 200, 224 926 байт**, снято 16.09.2026 12:39 МСК.
Текст в редакции **приказов ФСТЭК России от 23.03.2017 № 49 и от 14.05.2020 № 68**
(строка «Список изменяющих документов» на самой странице).

#### 1.1. 🔴 Главное — криптография прямо ВЫВЕДЕНА за рамки этого приказа

Дословно, п. 1, абзац третий:

> «В настоящем документе не рассматриваются вопросы обеспечения безопасности
> персональных данных, отнесенных в установленном порядке к сведениям, составляющим
> государственную тайну, а также **меры, связанные с применением шифровальных
> (криптографических) средств защиты информации**.»

То есть Приказ № 21 **не содержит и не может содержать требования шифровать хранимые
данные**: криптография в нём вынесена в отдельный предмет (он регулируется Приказом
ФСБ № 378, см. п. 2 ниже).

#### 1.2. Дословно — рамка выбора мер

П. 1, абзац первый:

> «Настоящий документ разработан в соответствии с частью 4 статьи 19 Федерального
> закона от 27 июля 2006 г. N 152-ФЗ "О персональных данных" … и устанавливает состав
> и содержание организационных и технических мер по обеспечению безопасности
> персональных данных при их обработке в информационных системах персональных данных …
> для каждого из уровней защищенности персональных данных, установленных в Требованиях …
> утвержденных постановлением Правительства Российской Федерации от 1 ноября 2012 г. N 1119».

П. 2, абзац второй (кто может делать работы):

> «Для выполнения работ по обеспечению безопасности персональных данных при их обработке
> в информационной системе … могут привлекаться на договорной основе юридическое лицо
> или индивидуальный предприниматель, имеющие лицензию на деятельность по технической
> защите конфиденциальной информации.»

П. 4 — 🔴 сертифицированные СЗИ требуются **не всегда, а по необходимости**:

> «Меры по обеспечению безопасности персональных данных реализуются в том числе
> посредством применения в информационной системе средств защиты информации, прошедших
> в установленном порядке процедуру оценки соответствия, **в случаях, когда применение
> таких средств необходимо для нейтрализации актуальных угроз** безопасности
> персональных данных.»

П. 6 — периодичность оценки эффективности:

> «Оценка эффективности реализованных в рамках системы защиты персональных данных мер …
> проводится оператором **самостоятельно** или с привлечением на договорной основе
> юридических лиц и индивидуальных предпринимателей, имеющих лицензию … **не реже
> одного раза в 3 года**.»

П. 9 — четырёхшаговая процедура выбора мер: определение базового набора по приложению →
**адаптация** (в т.ч. «исключение из базового набора мер, непосредственно связанных
с информационными технологиями, не используемыми в информационной системе») →
**уточнение** адаптированного набора под все актуальные угрозы → **дополнение** мерами
из иных НПА.

П. 10 — компенсирующие меры:

> «При **невозможности технической реализации** отдельных выбранных мер …, а также
> **с учетом экономической целесообразности** на этапах адаптации базового набора мер
> и (или) уточнения адаптированного базового набора мер **могут разрабатываться иные
> (компенсирующие) меры**, направленные на нейтрализацию актуальных угроз … В этом
> случае в ходе разработки системы защиты персональных данных должно быть проведено
> **обоснование применения компенсирующих мер**.»

П. 11 — дополнительные меры **только при угрозах 1-го и 2-го типов** (проверка ПО на НДВ,
тестирование на проникновение, защищённое программирование). Для нас (3-й тип, см. п. 3
ниже) они не обязательны.

П. 12 (в ред. приказа № 68 от 14.05.2020):

> «Технические меры защиты персональных данных реализуются посредством применения средств
> защиты информации, в том числе программных (программно-аппаратных) средств, в которых
> они реализованы, **имеющих необходимые функции безопасности**. … При использовании
> в информационных системах средств защиты информации, **сертифицированных** по требованиям
> безопасности информации, указанные средства должны быть сертифицированы на соответствие
> обязательным требованиям …».

Классы средств по уровням (п. 12, абзацы о классах):

> «в информационных системах **4 уровня** защищенности персональных данных применяются
> средства защиты информации **6 класса и 6 уровня доверия**, а также средства
> вычислительной техники не ниже **6 класса**.»

(Уровни доверия — по приказу ФСТЭК России от 30.07.2018 № 131.)

#### 1.3. Базовый набор мер для УЗ-4 — приложение, снято таблицей построчно

Шапка приложения: колонки «Уровни защищенности персональных данных: **4 | 3 | 2 | 1**»
(именно в таком порядке — первая колонка это наш уровень). Примечание под таблицей:

> «"+" - мера по обеспечению безопасности персональных данных включена в базовый набор мер
> для соответствующего уровня защищенности персональных данных. Меры …, не обозначенные
> знаком "+", применяются при адаптации базового набора мер и уточнении адаптированного
> базового набора мер, а также при разработке компенсирующих мер …».

**Базовый набор для УЗ-4 — ровно 32 меры из 15 групп. Дословный перечень:**

*I. Идентификация и аутентификация (ИАФ) — 5 мер:*
ИАФ.1 идентификация и аутентификация пользователей-работников оператора;
ИАФ.3 управление идентификаторами (создание, присвоение, уничтожение);
ИАФ.4 управление средствами аутентификации (хранение, выдача, инициализация,
блокирование, меры при утрате/компрометации);
ИАФ.5 защита обратной связи при вводе аутентификационной информации;
ИАФ.6 идентификация и аутентификация **внешних пользователей** (не работников оператора).

*II. Управление доступом (УПД) — 10 мер:*
УПД.1 управление учётными записями, в том числе внешних пользователей;
УПД.2 методы, типы и правила разграничения доступа (дискреционный/мандатный/ролевой);
УПД.3 управление информационными потоками между устройствами, сегментами и системами;
УПД.4 разделение полномочий (ролей) пользователей, администраторов и обслуживающих лиц;
УПД.5 минимально необходимые права и привилегии;
УПД.6 ограничение неуспешных попыток входа;
УПД.13 **защищённый удалённый доступ через внешние сети**;
УПД.14 регламентация и контроль беспроводного доступа;
УПД.15 регламентация и контроль мобильных технических средств;
УПД.16 управление взаимодействием с внешними информационными системами сторонних организаций.

*III. Ограничение программной среды (ОПС) — в базовом наборе УЗ-4 НЕТ ни одной меры.*
*IV. Защита машинных носителей (ЗНИ) — 🔴 в базовом наборе УЗ-4 НЕТ ни одной меры.*
*(Это прямо относится к вопросу о шифровании файлов на носителе: мер группы ЗНИ,
включая уничтожение/затирание и контроль носителей, базовый набор УЗ-4 не требует.)*

*V. Регистрация событий безопасности (РСБ) — 4 меры:* РСБ.1 определение событий
и сроков хранения; РСБ.2 состав и содержание информации о событиях; РСБ.3 сбор, запись
и хранение в течение установленного времени; РСБ.7 защита информации о событиях.

*VI. Антивирусная защита (АВЗ) — 2 меры:* АВЗ.1 реализация антивирусной защиты;
АВЗ.2 обновление базы признаков вредоносных программ.

*VII. Обнаружение вторжений (СОВ) — НЕТ.*

*VIII. Контроль защищённости (АНЗ) — 1 мера:* АНЗ.2 контроль установки обновлений ПО,
включая обновление ПО средств защиты информации.

*IX. Целостность (ОЦЛ) — НЕТ. X. Доступность (ОДТ) — НЕТ.*

*XI. Защита среды виртуализации (ЗСВ) — 2 меры:* ЗСВ.1 идентификация и аутентификация
в виртуальной инфраструктуре, в т.ч. администраторов средств виртуализации;
ЗСВ.2 управление доступом к объектам внутри виртуальных машин.
*(Релевантно нам: продукт живёт на арендованных виртуальных мощностях.)*

*XII. Защита технических средств (ЗТС) — 2 меры:* ЗТС.3 контроль и управление физическим
доступом в помещения; ЗТС.4 размещение устройств вывода, исключающее несанкционированный
просмотр.

*XIII. Защита системы и каналов связи (ЗИС) — 1 мера, и она единственная «про канал»:*

> «**ЗИС.3** Обеспечение защиты персональных данных от раскрытия, модификации
> и навязывания (ввода ложной информации) **при ее передаче (подготовке к передаче)
> по каналам связи, имеющим выход за пределы контролируемой зоны**, в том числе
> беспроводным каналам связи»

*XIV. Инциденты (ИНЦ) — НЕТ. XV. Управление конфигурацией (УКФ) — НЕТ.*

#### 1.4. Вывод по п. 1 (прямой ответ)

**Приказ ФСТЭК № 21 НЕ требует шифрования персональных данных при хранении для УЗ-4.**
Основания три, каждое дословное: (а) п. 1 выводит криптографические меры за рамки
документа целиком; (б) в базовом наборе УЗ-4 группа ЗНИ (защита машинных носителей)
пуста; (в) единственная мера ЗИС.3 касается **передачи** по каналам за пределы
контролируемой зоны, а не хранения. Требуемое для УЗ-4 — это разграничение доступа
(ИАФ + УПД, 15 мер из 32), журналирование, антивирус, обновления, физический доступ
и защита канала передачи.

---

### 2. Приказ ФСБ России от 10.07.2014 № 378 — когда обязательны сертифицированные СКЗИ

**Полное название:** «Об утверждении Состава и содержания организационных и технических мер
по обеспечению безопасности персональных данных при их обработке в информационных системах
персональных данных **с использованием средств криптографической защиты информации**,
необходимых для выполнения установленных Правительством Российской Федерации требований
к защите персональных данных для каждого из уровней защищенности».
Зарегистрирован в Минюсте России **18.08.2014, регистрационный № 33620**. Подписал директор
ФСБ А. Бортников.

**Источник полного текста:** https://rppa.pro/npa/fsb378_10.07.2014 (Regional Privacy
Professionals Association) — `curl -sk --http1.1`, **HTTP 200, 84 581 байт**, снято
16.09.2026 12:41 МСК. Сверочные каналы: `regulhub.kaspersky.ru/decrees/prikaz-378`
(200, 105 345 б — обзор, не текст), `consultant.ru/document/cons_doc_LAW_167862/...`
(200, 30 560 б — **заглушка без текста**, попытка в 12:41 МСК, то есть вне окна 20–24 МСК
для подзаконных актов), `base.garant.ru/70727118/` и `docs.cntd.ru` — **403 даже через
`r.jina.ai`** (тело ответа: Cloudflare «Just a moment…», то есть прокси отдал чужой
антибот, а не страницу).

#### 2.1. 🔴 Главное — область применения приказа, дословно

> **«2.** Настоящий документ **предназначен для операторов, использующих СКЗИ** для
> обеспечения безопасности персональных данных при их обработке в информационных системах.»

> **«1.** Настоящий документ определяет состав и содержание организационных и технических мер
> по обеспечению безопасности персональных данных при их обработке в информационных системах
> персональных данных … **с использованием средств криптографической защиты информации**
> (далее - СКЗИ), необходимых для выполнения установленных Правительством Российской
> Федерации требований к защите персональных данных для каждого из уровней защищенности.»

**Вывод по гипотезе из заказа — ПОДТВЕРЖДЕНА текстом.** Приказ № 378 адресован операторам,
которые СКЗИ **уже применяют**. Он не создаёт обязанности применять криптографию; он
описывает, что делать, **если** оператор избрал криптографический способ защиты. Обязанность
применить СКЗИ возникает не из № 378, а из п. 13 «г» ПП 1119 / п. 4 Приказа ФСТЭК № 21 —
и только «в случае, когда применение таких средств необходимо для нейтрализации актуальных
угроз», то есть по итогам собственной модели угроз оператора.

#### 2.2. Что приказ требует для 4-го уровня защищённости (раздел II, пп. 5–15)

П. 5 дословно воспроизводит п. 13 ПП 1119 (режим помещений; сохранность носителей;
утверждённый перечень допущенных лиц; СЗИ, прошедшие оценку соответствия, — «в случае,
когда применение таких средств необходимо для нейтрализации актуальных угроз»).

П. 6 — режим помещений, **где размещены и хранятся СКЗИ и носители ключевой,
аутентифицирующей и парольной информации** (входные двери с замками, опечатывание
по окончании рабочего дня либо сигнализация о вскрытии; правила доступа в рабочее
и нерабочее время; утверждённый перечень лиц).

🔴 П. 7 «а» — **единственное место во всём контуре, где шифрование даёт послабление,
а не создаёт обязанность**:

> «осуществлять хранение **съемных машинных носителей** персональных данных в сейфах
> (металлических шкафах), оборудованных внутренними замками с двумя или более дубликатами
> ключей и приспособлениями для опечатывания замочных скважин или кодовыми замками.
> **В случае если на съемном машинном носителе персональных данных хранятся только
> персональные данные в зашифрованном с использованием СКЗИ виде, допускается хранение
> таких носителей вне сейфов** (металлических шкафов)».

П. 7 «б» — поэкземплярный учёт машинных носителей через журнал с регистрационными
(заводскими) номерами.

П. 9 — порядок определения требуемого класса СКЗИ: получение исходных данных → формирование
и **утверждение руководителем оператора совокупности предположений о возможностях
нарушителя** → и далее, п. 9 «в»:

> «использования для обеспечения требуемого уровня защищенности персональных данных при их
> обработке в информационной системе **СКЗИ класса КС1 и выше**.»

То есть для УЗ-4 минимальный класс — **КС1** (самый низкий из пяти: КС1 < КС2 < КС3 < КВ < КА).

#### 2.3. Классы КС1 / КС2 / КС3 — по какому признаку различаются (дословно)

- **КС1** (п. 10) — нейтрализует атаки, создаваемые **без привлечения специалистов в области
  разработки и анализа СКЗИ**, проводимые **вне контролируемой зоны**, в том числе «проведение
  на этапе эксплуатации атаки из информационно-телекоммуникационных сетей, доступ к которым
  не ограничен определенным кругом лиц, если информационные системы, в которых используются
  СКЗИ, имеют выход в эти сети» (п. 10 «и») — это ровно модель «атакующий из интернета».
- **КС2** (п. 11) — возможности п. 10 **плюс не менее одной** дополнительной, первая из которых:
  «а) проведение атаки **при нахождении в пределах контролируемой зоны**».
- **КС3** (п. 12) — возможности пп. 10 и 11 **плюс** «а) **физический доступ к СВТ**, на которых
  реализованы СКЗИ и СФ; б) возможность располагать аппаратными компонентами СКЗИ и СФ …».
- **КВ** (п. 13) — дополнительно привлечение специалистов по анализу сигналов и НДВ прикладного
  ПО, лабораторные исследования СКЗИ, работа профильных НИЦ.
- **КА** (п. 14) — всё перечисленное и выше.

П. 15: «дополнительные возможности, не входящие в число перечисленных в пунктах 10–14 …
**не влияют** на порядок определения требуемого класса СКЗИ».

Для сопоставления (п. 18, раздел III): при переходе на **3-й УЗ** класс зависит от типа угроз —
«СКЗИ класса КВ и выше в случаях, когда … актуальны **угрозы 2 типа**; СКЗИ класса **КС1 и выше**
в случаях, когда … актуальны **угрозы 3 типа**». Это прямо показывает, почему тип угроз (см. п. 3)
для нас дороже уровня защищённости: он двигает класс СКЗИ на два разряда.

#### 2.4. Вывод по п. 2 (прямой ответ)

**Обязанности применять сертифицированные СКЗИ у нас не возникает автоматически.**
Приказ № 378 применяется только к оператору, который СКЗИ использует (п. 2). Если продукт
защищает выписки организационными мерами и разграничением доступа, а криптографию как
средство защиты ПДн по модели угроз не заявляет, требования № 378 к нему не обращены.
Если же криптография заявлена как мера нейтрализации актуальной угрозы, то при УЗ-4
достаточно **класса КС1** (п. 9 «в»), и вместе с ним приезжает весь режимный «хвост»:
помещения с опечатыванием (п. 6), сейфы или шифрование для съёмных носителей (п. 7 «а»),
поэкземплярный журнал носителей (п. 7 «б»), утверждённая руководителем модель нарушителя
(п. 9 «б»). 🔴 Практический вывод для продукта: **заявлять СКЗИ как меру защиты ПДн —
дороже, чем не заявлять**; TLS как транспорт при этом никуда не девается, но обосновывается
через ЗИС.3 Приказа № 21, а не через № 378.

---

### 3. ПП РФ от 01.11.2012 № 1119 — уровни защищённости и типы угроз

**Источник:** PDF-копия полного текста —
https://ncagp.ru/upload/files/nor_docs/2025/5_3-Постановление%20Правительства%20РФ%20от%2001.11.2012%20N%201119.pdf
— `curl -sk --http1.1`, **HTTP 200, 155 206 байт, `application/pdf`**, снято 16.09.2026
12:41 МСК, разобрано `pdftotext` (25 404 байта текста). Заголовочная плашка — выгрузка
КонсультантПлюс, то есть текст сверен с той же базой, которая в рабочее время отдаёт
только заглушку.

#### 3.1. П. 6 — типы актуальных угроз, дословно

> «Угрозы **1-го типа** актуальны для информационной системы, если для нее в том числе
> актуальны угрозы, связанные с наличием недокументированных (недекларированных)
> возможностей **в системном программном обеспечении**, используемом в информационной системе.
> Угрозы **2-го типа** актуальны …, если … актуальны угрозы, связанные с наличием
> недокументированных (недекларированных) возможностей **в прикладном программном
> обеспечении** … Угрозы **3-го типа** актуальны …, если для нее актуальны угрозы,
> **не связанные** с наличием недокументированных (недекларированных) возможностей
> в системном и прикладном программном обеспечении …».

> «**7.** Определение типа угроз безопасности персональных данных, актуальных для
> информационной системы, **производится оператором** с учетом оценки возможного вреда,
> проведенной во исполнение пункта 5 части 1 статьи 18.1 Федерального закона
> "О персональных данных", и в соответствии с нормативными правовыми актами, принятыми
> во исполнение части 5 статьи 19 Федерального закона "О персональных данных".»

🔴 **От чего зависит наш тип угроз.** Тип определяет **сам оператор** (п. 7), и зависит он
не от чувствительности данных, а от того, включает ли оператор в модель угроз НДВ
в системном (1-й тип) или прикладном (2-й тип) ПО. Для продукта на обычном стеке
(Linux, PostgreSQL, FastAPI) стандартная и защитимая позиция — **3-й тип**: НДВ в системном
и прикладном ПО из модели исключены. Цена ошибки здесь выше, чем кажется: объявив 2-й тип,
оператор по п. 11 «б» ПП 1119 уезжает на 3-й УЗ, а по п. 18 Приказа ФСБ № 378 — на класс
СКЗИ **КВ и выше**, плюс включаются меры п. 11 Приказа ФСТЭК № 21 (проверка на НДВ,
пентесты, защищённое программирование).

#### 3.2. П. 12 — основание нашего 4-го уровня, дословно

> «**12.** Необходимость обеспечения 4-го уровня защищенности персональных данных при их
> обработке в информационной системе устанавливается при наличии хотя бы одного из следующих
> условий:
> а) для информационной системы актуальны угрозы 3-го типа и информационная система
> обрабатывает **общедоступные** персональные данные;
> **б) для информационной системы актуальны угрозы 3-го типа и информационная система
> обрабатывает иные категории персональных данных сотрудников оператора или иные категории
> персональных данных менее чем 100000 субъектов персональных данных, не являющихся
> сотрудниками оператора.**»

**Сверка с выводом Г20 — подтверждается построчно.** Мы попадаем в п. 12 «б»: угрозы 3-го
типа + «иные категории» ПДн (финансовые сведения к специальным категориям по п. 5
не относятся — там закрытый перечень: раса, национальность, политические взгляды,
религиозные или философские убеждения, состояние здоровья, интимная жизнь) + менее
100 000 субъектов, не являющихся сотрудниками.

🔴 **Порог перехода 100 000 — уточнение, которого в Г20 не было.** При превышении 100 000
субъектов при угрозах 3-го типа и «иных категориях» включается **не** п. 11 «б» (он про
угрозы 2-го типа), а п. 11 «д»: «для информационной системы актуальны угрозы 3-го типа
и информационная система обрабатывает иные категории персональных данных **более чем
100000 субъектов** … не являющихся сотрудниками оператора» → **3-й уровень защищённости**.
То есть вывод Г20 верен, но точная норма перехода — **п. 11 «д»**, а не п. 11 «б».

#### 3.3. П. 13 — что требуется для 4-го УЗ, дословно (полный список, всего четыре пункта)

> «**13.** Для обеспечения 4-го уровня защищенности персональных данных при их обработке
> в информационных системах необходимо выполнение следующих требований:
> а) организация режима обеспечения безопасности помещений, в которых размещена
> информационная система, препятствующего возможности неконтролируемого проникновения
> или пребывания в этих помещениях лиц, не имеющих права доступа в эти помещения;
> б) обеспечение **сохранности носителей** персональных данных;
> в) утверждение руководителем оператора документа, определяющего **перечень лиц**, доступ
> которых к персональным данным, обрабатываемым в информационной системе, необходим
> для выполнения ими служебных (трудовых) обязанностей;
> г) использование средств защиты информации, прошедших процедуру **оценки соответствия**
> требованиям законодательства Российской Федерации в области обеспечения безопасности
> информации, **в случае, когда применение таких средств необходимо для нейтрализации
> актуальных угроз**.»

П. 14 — для 3-го УЗ ко всему этому добавляется назначение **ответственного должностного лица**
за безопасность ПДн. У нас такой обязанности по ПП 1119 нет (но см. ст. 18.1 152-ФЗ, где
ответственный за организацию обработки ПДн — отдельная и безусловная обязанность).

**Вывод по п. 3:** в ПП 1119 **слова «шифрование» применительно к хранению нет вовсе**.
Требование п. 13 «б» — «сохранность носителей», а не «шифрование носителей». Требование
п. 13 «г» — условное («в случае, когда … необходимо»), и условие проверяется собственной
моделью угроз оператора.


---

> **Перерыв в работе.** Сессия оборвалась после записи п. 3 (лимит аккаунта, HTTP 429),
> аккаунт сменён, работа продолжена с того же места 16.09.2026. Пункты 1–3 выше
> не переписывались; скрэтчпад со снятыми страницами пережил смену аккаунта.

### 5. Приказ РКН № 179 против № 178 — сверка опубликования (закрыто)

**Как найдено.** Поиск по тексту в API `publication.pravo.gov.ru/api/Documents` параметр
`SearchText` **молча игнорирует** (HTTP 200, `itemsTotalCount` 1 699 767 — вся база, первой
строкой протокол с Марокко от 16.09.2026), поэтому поиск по реквизитам через API не работает.
Сделан прямой перебор номеров опубликования `0001YYYYMMDDNNNN` за 29.11–02.12.2022
(номера 0001–0070 каждого дня) с фильтром по слову «связи» в заголовке. Найдено три
документа, из них два — Роскомнадзора.

| Номер опубликования | Что там лежит (дословно заголовок карточки) | Рег. Минюста |
|---|---|---|
| **0001202211290004** | Приказ Федеральной службы по надзору в сфере связи, информационных технологий и массовых коммуникаций **от 27.10.2022 № 178** «Об утверждении Требований к оценке вреда, который может быть причинен субъектам персональных данных в случае нарушения Федерального закона "О персональных данных"» | 28.11.2022 № 71166 |
| **0001202211290008** | Приказ Федеральной службы по надзору в сфере связи, информационных технологий и массовых коммуникаций **от 28.10.2022 № 179** «Об утверждении Требований к подтверждению уничтожения персональных данных» | 28.11.2022 № 71167 |

Источники: http://publication.pravo.gov.ru/Document/View/0001202211290008 — **HTTP 200,
22 098 байт**; http://publication.pravo.gov.ru/Document/View/0001202211290004 — **HTTP 200,
22 790 байт**; оба сняты 16.09.2026 12:50 МСК. Дата опубликования обоих — **29.11.2022**.
Текст каждого — 4 страницы в просмотрщике.

**Вывод.** Номер приказа в юрблоке **верный — № 179 от 28.10.2022** (он и регулирует
подтверждение уничтожения ПДн). Ошибочным был **номер опубликования**, приписанный ему в Г20:
`0001202211290004` принадлежит № 178. Правильная ссылка —
**`0001202211290008`**. Попутно: № 178 (оценка вреда) нам тоже нужен — на него прямо
опирается п. 7 ПП 1119 (тип угроз определяется «с учетом оценки возможного вреда,
проведенной во исполнение пункта 5 части 1 статьи 18.1» 152-ФЗ).

---

### 6. Ст. 22 152-ФЗ — уведомление Роскомнадзора о начале обработки

**Источник:** https://www.consultant.ru/document/cons_doc_LAW_61801/d996966e22e1320c9de1ab82d9f6be12c3d9d765/
— `curl -sk --http1.1`, **HTTP 200, 93 944 байта**, снято 16.09.2026 12:43 МСК,
**редакция от 26.07.2026** (на странице отметка «Подготовлена редакция документа
с изменениями, не вступившими в силу» — сами изменения в выдаче не раскрыты, см. «не добыто»).
Законы в некоммерческой версии отдаются круглосуточно — замер подтверждён.

#### 6.1. Дословно

> «**1.** Оператор **до начала обработки** персональных данных обязан уведомить уполномоченный
> орган по защите прав субъектов персональных данных о своем намерении осуществлять обработку
> персональных данных, за исключением случаев, предусмотренных частью 2 настоящей статьи.»

> «**2.** Оператор вправе осуществлять без уведомления уполномоченного органа … обработку
> персональных данных:
> **1) - 6) утратили силу с 1 сентября 2022 года. - Федеральный закон от 14.07.2022 N 266-ФЗ;**
> 7) включенных в государственные информационные системы персональных данных, созданные
> в целях защиты безопасности государства и общественного порядка;
> 8) в случае, если оператор осуществляет деятельность по обработке персональных данных
> **исключительно без использования средств автоматизации**;
> 9) обрабатываемых в случаях, предусмотренных законодательством Российской Федерации
> о транспортной безопасности …»

> «**3.** Уведомление … направляется в виде документа на бумажном носителе или в форме
> электронного документа и подписывается уполномоченным лицом. Уведомление должно содержать
> следующие сведения: 1) наименование …, адрес оператора; 2) цель обработки …;
> **7) описание мер, предусмотренных статьями 18.1 и 19 настоящего Федерального закона,
> в том числе сведения о наличии шифровальных (криптографических) средств и наименования
> этих средств;** 7.1) … ответственных за организацию обработки персональных данных, и номера
> их контактных телефонов, почтовые адреса и адреса электронной почты; 8) дата начала обработки
> …; 9) срок или условие прекращения обработки …; 10) сведения о наличии или об отсутствии
> трансграничной передачи …; **10.1) сведения о месте нахождения базы данных информации,
> содержащей персональные данные граждан Российской Федерации;** 10.2) …; 11) сведения
> об обеспечении безопасности персональных данных в соответствии с требованиями к защите
> персональных данных, установленными Правительством Российской Федерации.»

> «**3.1.** При предоставлении сведений … оператор **для каждой цели** обработки персональных
> данных указывает категории персональных данных, категории субъектов …, правовое основание
> обработки …, перечень действий с персональными данными, способы обработки …»
> (введена 266-ФЗ).

> «**4.** Уполномоченный орган … в течение **тридцати дней** с даты поступления уведомления …
> вносит сведения … в реестр операторов. Сведения, содержащиеся в реестре операторов,
> **за исключением сведений о средствах обеспечения безопасности** персональных данных …,
> являются общедоступными.»

> «**7.** В случае изменения сведений … оператор **не позднее 15-го числа месяца, следующего
> за месяцем**, в котором возникли такие изменения, обязан уведомить уполномоченный орган …
> В случае прекращения обработки … — в течение **десяти рабочих дней** с даты прекращения
> обработки.»

> «**8.** Формы уведомлений, предусмотренных частями 1, 4.1 и 7 настоящей статьи,
> устанавливаются уполномоченным органом …» (введена 266-ФЗ).

#### 6.2. Ответственность за неподачу — 🔴 это НЕ ст. 19.7 КоАП

Заказ предполагал ст. 19.7 КоАП. Текущая редакция ст. 13.11 КоАП (снята в п. 8 ниже)
содержит **специальный состав** — ч. 10, введённая ФЗ от 30.11.2024 № 420-ФЗ:

> «**10.** Невыполнение или несвоевременное выполнение оператором предусмотренной
> законодательством Российской Федерации в области персональных данных обязанности
> по уведомлению уполномоченного органа по защите прав субъектов персональных данных
> о намерении осуществлять обработку персональных данных -
> влечет наложение административного штрафа на граждан в размере от пяти тысяч до десяти
> тысяч рублей; на должностных лиц - от тридцати тысяч до пятидесяти тысяч рублей;
> **на юридических лиц - от ста тысяч до трехсот тысяч рублей.**»

Примечание 1 к ст. 13.11: по чч. 1.1, **8–18** «индивидуальные предприниматели несут
административную ответственность **как юридические лица**». Специальная норма вытесняет
общую ст. 19.7 (непредставление сведений в госорган) — это вывод по правилу lex specialis,
не цитата; текст ст. 19.7 в этом батче не снимался.

#### 6.3. Вывод по п. 6

**Обязаны.** Исключения ч. 2 для нас не работают: пп. 1–6 (в т.ч. прежнее исключение
«в связи с заключением договора» и «ПДн, полученные при заключении договора») **отменены
с 01.09.2022**, а оставшиеся пп. 7–9 (госсистемы безопасности, обработка без автоматизации,
транспортная безопасность) к сервису не относятся. Срок — **до начала обработки**, то есть
до первого реального пользователя, а не до запуска рекламы. После подачи — изменения
сведений не позднее 15-го числа следующего месяца. Важная связка с п. 2: в уведомлении
по ч. 3 п. 7 **указываются сведения о наличии СКЗИ и их наименования** — то, что продукт
заявит о шифровании, становится публично-реестровым фактом (кроме самих средств, ч. 4),
а значит, заявленная криптография будет проверяема на соответствие Приказу ФСБ № 378.
Место базы данных (ч. 3 п. 10.1) тоже указывается — прямая связка с п. 7 ниже.

---

### 7. Хранение исходных PDF — срок, уничтожение, банковская тайна, локализация

**Что уже снято в Г20 и не переоткрывается** (см. разделы 7.2 и 7.3 этого файла выше):
ст. 5 ч. 4, 5, 7 152-ФЗ (хранение не дольше цели, запрет избыточности, уничтожение или
обезличивание по достижении цели); ст. 21 чч. 2–5 (7 раб. дней — уточнение; 10 раб. дней —
ч. 3; 30 дней — чч. 4 и 5; 24 ч / 72 ч — уведомление об инциденте, ч. 3.1); ст. 26
№ 395-1 (обязанность хранить тайну адресована кредитной организации и перечню лиц,
получающих сведения **от банка**; клиент — законный получатель справки и ею распоряжается).
Судебная практика по «иным организациям» в ст. 26 по-прежнему не проверена
(`kad.arbitr.ru` 451, в Г22 не пробовалась — не входила в пункты заказа).

#### 7.1. Новое — локализация, ч. 5 ст. 18 152-ФЗ, в редакции 2025 года

**Источник:** https://www.consultant.ru/document/cons_doc_LAW_61801/cbf4e15b7c330f9372e876cdf2bc928bad7950ef/
— **HTTP 200, 56 528 байт**, редакция от 26.07.2026, снято 16.09.2026 12:43 МСК.

> «**5.** При сборе персональных данных, в том числе посредством информационно-
> телекоммуникационной сети "Интернет", запись, систематизация, накопление, хранение,
> уточнение (обновление, изменение), извлечение персональных данных граждан Российской
> Федерации **с использованием баз данных, находящихся за пределами территории Российской
> Федерации, не допускаются**, за исключением случаев, указанных в пунктах 2, 3, 4, 8
> части 1 статьи 6 настоящего Федерального закона.»

Формулировка **запретительная** («не допускаются»), а не прежняя позитивная («оператор
обязан обеспечить … с использованием баз данных, находящихся на территории РФ»). Какой
именно закон её ввёл и с какой даты — в этой выдаче строки «в ред.» при ч. 5 не видно;
по памяти это ФЗ от 28.02.2025 № 23-ФЗ со вступлением с 01.07.2025, **но это не сверено**
и в выжимку как факт не идёт.

**Применимость к нам.** Исключения ч. 5 — пп. 2, 3, 4, 8 ч. 1 ст. 6 (международный договор
и закон; правосудие; госуслуги; профессиональная деятельность журналиста/СМИ, научная,
литературная и иная творческая). **П. 5 ч. 1 ст. 6 (исполнение договора с субъектом)
в перечень исключений НЕ входит** — значит, основание «договор с пользователем» от локализации
не освобождает. Исходные PDF-выписки — это «хранение» ПДн граждан РФ в «базе данных»
в смысле ч. 5, файловое хранилище тут не отличается от СУБД. **Хостинг первичной записи
и хранения — только на территории РФ**, включая объектное хранилище под PDF и резервные копии.
Ответственность — ч. 8 ст. 13.11 КоАП (юрлица **1–6 млн ₽**), повтор — ч. 9 (**6–18 млн ₽**),
см. п. 8.

#### 7.2. Вывод по п. 7

1. **Срок хранения исходного PDF** федеральным законом **не установлен** → действует ч. 7
   ст. 5: не дольше цели. Цель «извлечь операции» достигается в момент разбора, после чего
   PDF (номер счёта, ФИО, адрес, номер карты) избыточен по ч. 5 ст. 5 → уничтожение
   или обезличивание в пределах **30 дней** (ч. 4 ст. 21). Если продукт хранит PDF дольше
   (например, для повторного разбора при обновлении парсера), эта цель должна быть **прямо
   названа** в политике и в согласии, иначе хранение превращается в обработку, «несовместимую
   с целями сбора» (ч. 1 ст. 13.11 КоАП, юрлица **150–300 тыс. ₽**).
2. **Уничтожение по запросу субъекта** — 30 дней при отзыве согласия (ч. 5 ст. 21);
   подтверждение уничтожения — по форме Приказа РКН **№ 179** (п. 5 выше, опубликование
   `0001202211290008`).
3. **Банковская тайна у небанковского получателя** — прямой обязанности по ст. 26 № 395-1
   текст не создаёт (см. Г20 §7.2); режим защиты для нас — полностью 152-ФЗ.
4. **Локализация** — обязательна, в запретительной редакции, договорное основание
   не освобождает.

---

### 8. Ответственность — ст. 13.11 КоАП после 30.11.2024 № 420-ФЗ

**Источник:** https://www.consultant.ru/document/cons_doc_LAW_34661/1f421640c6775ff67079ebde06a7d2f6d17b96db/
— `curl -sk --http1.1`, **HTTP 200, 115 000 байт**, **редакция КоАП от 26.07.2026**,
снято 16.09.2026 12:43 МСК. Все суммы ниже — дословно из санкций, для **юридических лиц**
(ИП по чч. 1.1, 8–18 — как юрлица, примечание 1).

#### 8.1. Составы, относящиеся к продукту

| Ч. | Состав (сокращённо, ключевые слова дословно) | Юрлицо | Ред. |
|---|---|---|---|
| 1 | обработка «в случаях, не предусмотренных законодательством» либо «несовместимая с целями сбора» | 150 000 – 300 000 ₽ | 420-ФЗ |
| 1.1 | повтор ч. 1 | 300 000 – 500 000 ₽ | 420-ФЗ |
| 2 | обработка без письменного согласия, когда оно обязательно, или с нарушением требований к составу согласия | 300 000 – 700 000 ₽ | 589-ФЗ от 12.12.2023 |
| 2.1 | повтор ч. 2 | 1 000 000 – 1 500 000 ₽ | 589-ФЗ |
| 3 | неопубликование политики обработки ПДн | 30 000 – 60 000 ₽ | 19-ФЗ от 24.02.2021 |
| 4 | непредоставление субъекту информации об обработке | 40 000 – 80 000 ₽ | 19-ФЗ |
| 5 | невыполнение в срок требования субъекта или РКН об уточнении, блокировании, **уничтожении** | 50 000 – 90 000 ₽ | 19-ФЗ |
| 5.1 | повтор ч. 5 | 300 000 – 500 000 ₽ | 19-ФЗ |
| 6 | несохранность **материальных носителей при обработке без средств автоматизации**, повлёкшая доступ | 50 000 – 100 000 ₽ | 19-ФЗ |
| 8 | нарушение **локализации** при сборе, в т.ч. через интернет | 1 000 000 – 6 000 000 ₽ | 405-ФЗ от 02.12.2019 |
| 9 | повтор ч. 8 | 6 000 000 – 18 000 000 ₽ | 405-ФЗ |
| 10 | **неподача / несвоевременная подача уведомления** о намерении обрабатывать ПДн | 100 000 – 300 000 ₽ | 420-ФЗ |
| 11 | неуведомление / несвоевременное уведомление РКН об **инциденте** (неправомерной передаче) | 1 000 000 – 3 000 000 ₽ | 420-ФЗ |
| 12 | «неправомерную передачу (предоставление, распространение, доступ)» ПДн **1 000 – 10 000 субъектов** и (или) 10 000 – 100 000 идентификаторов | 3 000 000 – 5 000 000 ₽ | 420-ФЗ |
| 13 | то же, **10 000 – 100 000 субъектов** и (или) 100 000 – 1 000 000 идентификаторов | 5 000 000 – 10 000 000 ₽ | 420-ФЗ |
| 14 | то же, **более 100 000 субъектов** и (или) более 1 000 000 идентификаторов | 10 000 000 – 15 000 000 ₽ | 420-ФЗ |
| 15 | **повтор** чч. 12–14 | 🔴 **от 1 до 3 % выручки** за предшествующий календарный год, «но не менее двадцати миллионов рублей и не более пятисот миллионов рублей» | 420-ФЗ |
| 16 | утечка **специальной категории** ПДн | 10 000 000 – 15 000 000 ₽ | 420-ФЗ |
| 17 | утечка **биометрических** ПДн | 15 000 000 – 20 000 000 ₽ | 420-ФЗ |
| 18 | повтор чч. 16–17 | 🔴 **от 1 до 3 % выручки**, «но не менее двадцати пяти миллионов рублей и не более пятисот миллионов рублей» | 420-ФЗ |

(Ч. 7 — только госорганы, неприменима.)

#### 8.2. Что квалифицируется как «утечка» — дословно

Диспозиция чч. 12–14: «**Действия (бездействие) оператора, повлекшие неправомерную передачу
(предоставление, распространение, доступ) информации, включающей персональные данные** …,
если эти действия (бездействие) не содержат признаков уголовно наказуемого деяния».

Примечание 4: «В целях настоящей статьи **под идентификатором понимается уникальное
обозначение сведений о физическом лице, содержащееся в информационной системе персональных
данных оператора и относящееся к такому лицу**.»

Примечания 2 и 3: в чч. 10–18 «должностное лицо» — только должностное лицо госоргана,
муниципального органа **или некоммерческой организации**; «юридическое лицо» — оператор,
**не являющийся** государственным, муниципальным органом или НКО. То есть у коммерческого
оператора по чч. 10–18 штрафуется **только организация**, не её директор.

Примечание 5: при назначении наказания по чч. 15 и 18 отягчающим учитывается, что лицо
на момент нарушения считалось подвергнутым наказанию по **чч. 1–11** ст. 13.11 и (или)
ст. 13.6, 13.12 КоАП — то есть прежние «бумажные» штрафы (политика, уведомление, согласие)
утяжеляют будущий оборотный.

#### 8.3. Выводы по п. 8

1. **Оборотный штраф — только за ПОВТОРНУЮ утечку** (чч. 15, 18), не за первую.
   Первая утечка у нас (УЗ-4, < 100 000 субъектов) — это ч. 12 или ч. 13: **3–5 млн ₽**
   при 1 000–10 000 субъектов, **5–10 млн ₽** при 10 000–100 000.
2. 🔴 **Ниже порога 1 000 субъектов И 10 000 идентификаторов состав чч. 12–14 не наступает**.
   Но идентификаторы считаются отдельно и «и (или)» — одна выписка несёт много идентификаторов
   (номер счёта, номер карты, ФИО, адрес, каждая операция с контрагентом-физлицом). Малая
   база пользователей не гарантирует ухода ниже порога: 10 000 идентификаторов набираются
   на порядок быстрее, чем 1 000 субъектов. Это вывод из текста примечания 4, судебного
   толкования «идентификатора» в батче нет.
3. **Отдельного состава «не зашифровал» / «не выполнил меры ПП 1119 или Приказа ФСТЭК № 21»
   в ст. 13.11 нет.** Невыполнение технических мер наказуемо через последствие — утечку
   (чч. 12–14) — и через ч. 11, если об утечке не уведомили. Ч. 6 (сохранность носителей)
   относится только к обработке **без** средств автоматизации.
4. **Самые вероятные для раннего продукта** санкции — не оборотные, а «бумажные» и
   инфраструктурные: ч. 10 (уведомление, 100–300 тыс.), ч. 8 (локализация, 1–6 млн),
   ч. 2 (согласие, 300–700 тыс.), ч. 11 (неуведомление об инциденте, 1–3 млн).


#### 6.4. Дополнение к п. 6 — как подаётся уведомление (позиция Управления РКН по ЦФО, дословно)

**Источник:** https://77.rkn.gov.ru/p3852/p13239/p13309/ (раздел вопросов и ответов Управления
Роскомнадзора по ЦФО) — `curl -sk --http1.1`, **HTTP 200, 33 891 байт, кодировка cp1251**
(перекодирована `iconv`), снято 16.09.2026 12:51 МСК. Это та самая страница, которую Г20
числил за «позицией РКН об e-mail»; **по содержанию она не про e-mail как канал передачи ПДн**,
а про подачу уведомления и сайты школ.

> «Для внесения оператора в реестр персональных данных на территории **Москвы и Московской**,
> Владимирской, Ивановской, Калужской, Костромской, Орловской, Смоленской, Тульской областей
> необходимо подать уведомление в **Управление Роскомнадзора по Центральному федеральному
> округу**. **Формы подачи уведомлений утверждены приказом Роскомнадзора от 28.10.2022 № 180.**
> Оператор обязан уведомить уполномоченный орган до начала обработки персональных данных. …
> Документы могут быть направлены в регистрирующий орган почтовым отправлением, в форме
> электронных документов, подписанных **усиленной квалифицированной электронной подписью**
> заявителя, или через аутенфикацию **ЕСИА**.»

> «На Портале персональных данных Роскомнадзора https://pd.rkn.gov.ru/ сформировать
> и отправить уведомление в территориальный орган Роскомнадзора одним из следующих способов:
> в бумажном виде; в электронном виде с использованием усиленной квалифицированной
> электронной подписи; или через аутенфикацию на портале Госуслуг.»

**Следствие для юрблока:** формы уведомления — **Приказ РКН от 28.10.2022 № 180** (соседний
с № 179 по дате; опубликование № 180 в этом батче не сверялось). Орган для московского
оператора — **Управление РКН по ЦФО**. Каналы — бумага, УКЭП или Госуслуги через pd.rkn.gov.ru.

`https://www.garant.ru/consult/business/1793028/` (вторая страница из Г20) — **HTTP 403, 902 б**
прямым `curl`; через `r.jina.ai` **HTTP 200, но 360 байт** (тело — ошибка прокси, текста нет).


> **Поправка времени снятия.** В пп. 1–8 выше время снятия первоначально проставлялось
> на глаз и в части пунктов было завышено на 1–1,5 часа. Исправлено 16.09.2026 по mtime
> файлов в скрэтчпаде: все первоисточники Г22 сняты между **12:38 и 12:57 МСК**.

---

### 4. Позиция регулятора о приёме ПДн по электронной почте

**Кто искал:** один подагент (general-purpose), запуск после записи пп. 1–3 и 5–8.
Потолок ему был 15 действий, фактически сделано **26 вызовов инструментов** — перерасход
отмечен. Дословные цитаты ниже **сверены вахтой** grep-ом по сохранённому подагентом
тексту (`scratchpad/g22/sub4/rppa.txt`) — совпадают.

#### 4.1. Первоисточник, который удалось добыть — разъяснения Минкомсвязи России от 25.08.2015

**Автор — Минкомсвязь (ныне Минцифры), не Роскомнадзор.** Документ: «Обработка и хранение
персональных данных в РФ. Изменения с 1 сентября 2015 года согласно положениям 242-ФЗ».
Номера письма нет — это опубликованные разъяснения. Оригинал на `digital.gov.ru/ru/personaldata/`
по данным поисковой выдачи **снят** (самостоятельно не проверялось).

**Источник:** https://rppa.pro/npa/minkomsvyaz_25.08.2015 — полный текст на сайте ассоциации
RPPA, `curl`, **HTTP 200, 167 932 байта**, снято 16.09.2026 12:53 МСК. Категория: полный
текст официального документа на сайте третьего лица (не пересказ, но и не сайт ведомства).

Раздел «Понятие сбора персональных данных», дословно:

> «под сбором персональных данных можно понимать **документально оформленную процедуру
> получения оператором от субъекта его персональных данных**, для их последующей обработки
> в соответствии с заявленными целями сбора».

> «**локализации подлежат только те персональные данные, которые были получены оператором
> в результате осуществляемой им целенаправленной деятельности по организации сбора таких
> данных, а не в результате случайного (незапрошенного) попадания к нему персональных данных,
> например, вследствие получения писем по электронной или иной почте, в которых содержатся
> персональные данные.** Аналогичным образом, не является сбором получение одним юридическим
> лицом персональных данных от другого юридического лица, если такие данные представляют собой
> контактную информацию работников или представителей такого юридического лица, переданную
> в ходе осуществления ими своей законной деятельности.»

> «… при осуществлении субъектом сбора информации, содержащей персональные данные, и ее
> последующей обработки **с использованием вычислительных мощностей, предоставленных иным
> лицом**, ответственность за соблюдение требований ч. 5 ст. 18 … **лежит на указанном
> субъекте**, учитывая целенаправленный характер его деятельности по сбору».

Раздел «Ответы пользователям и представителям организаций», вопрос дословно:

> «Организация пользуется сервисом электронной почты, чья серверная инфраструктура
> расположена за рубежом. На электронные почтовые ящики могут приходить электронные письма,
> содержащие персональные данные в неструктурированном виде. После получения письма работник
> осуществляет извлечение и внесение полученных персональных данных в базу данных,
> расположенную в России… Подпадает ли инфраструктура почтового сервиса под требования
> 242-ФЗ?»

Ответ (концовка, дословно): «Учитывая изложенное, **в случае, если на территории Российской
Федерации происходит сбор персональных данных гражданина Российской Федерации**, за исключением
вышеуказанных случаев, **оператор персональных данных должен будет соблюдать требования
Федерального закона №242-ФЗ**». Прямого «да/нет» про почтовые серверы ответ не даёт —
отсылает к общей норме.

#### 4.2. Не добыто — с каналами

- **Прямая позиция Роскомнадзора (письмо с номером и датой) о e-mail как канале приёма ПДн,
  о защищённости канала или шифровании писем — не найдена.** Поисковая выдача дала только
  блоги, интеграторов ИБ, консультации юристов и пересказ интервью представителя РКН о том,
  что адрес e-mail сам является ПДн — всё это не первоисточник.
- `https://77.rkn.gov.ru/p3852/p13239/p13309/` — **вахта**: HTTP 200, 33 891 б в 12:51 МСК
  (см. п. 6.4; страница про уведомления, не про e-mail). **Подагент** в 12:53 МСК на тот же
  адрес, а также `34.rkn.gov.ru/p8959/p15053/` и `25.rkn.gov.ru/p17348/p32646/` получил
  **код 000, 0 байт** (соединение не установилось). 🔴 **Противоречие между вахтой
  и подагентом по доступности `*.rkn.gov.ru`:** у вахты отдалось за две минуты до того.
  Вероятная причина — нестабильность соединения или разный сетевой путь процесса подагента;
  вывод подагента «РКН не пускает зарубежные адреса» **не подтверждён** и в выжимку не идёт.
- `r.jina.ai` на `77.rkn.gov.ru/...` и `74.rkn.gov.ru/social/questions/spd/` — HTTP 422,
  ~705 б, `TimeoutError: page.goto`.
- `https://pd.rkn.gov.ru/faq/` — HTTP 200, 9 682 б, но оболочка без вопросов (текста 1 054 символа,
  подгружается скриптом).
- `https://rkn.gov.ru/news/rsoc/news52266.htm` — `WebFetch`: «Socket is closed».
- Exa — у подагента ошибка «Server not found» (404), канал не проверен.
- `garant.ru/consult/business/1793028/` — 403 прямым `curl`, через `r.jina.ai` 200 / 360 б
  с телом «Checking your browser» (антибот Garant).

#### 4.3. Вывод по п. 4

1. **Прямого запрета принимать ПДн на e-mail нет ни в законе, ни в найденных разъяснениях.**
   Прямого разрешения — тоже. Требований к шифрованию писем в официальных текстах не найдено.
2. 🔴 **Исключение «случайно пришедших писем» для FINPILOT не работает.** Если сервис сам
   предлагает пользователю переслать выписку на свой адрес — это «целенаправленная
   деятельность по организации сбора», а не «случайное (незапрошенное) попадание».
   Значит, почтовый ящик сервиса — место **сбора** ПДн, и на него действует ч. 5 ст. 18
   (п. 7.1 выше, запретительная редакция).
3. 🔴 **Почтовый ящик на иностранном сервисе (Gmail, Outlook, Proton и т. п.) при таком
   сборе = нарушение локализации** (ч. 8 ст. 13.11 КоАП, 1–6 млн ₽). Ответственность
   за чужие вычислительные мощности разъяснения прямо возлагают на оператора. Вывод
   логический из текста 2015 года и текущей ч. 5 ст. 18, не цитата РКН.
4. **Канал передачи письма** от почтового сервера пользователя до сервера сервиса
   оператор не контролирует; для входящей почты мера ЗИС.3 Приказа ФСТЭК № 21 выполняется
   тем, что оператор может обеспечить сам: приём только по TLS (STARTTLS/MTA-STS) на своём
   российском почтовом сервере. Это инженерная экстраполяция, не норма.

---

## ИТОГ Г22

**Процесс, честно.** Классификация — breadth-first. Субагентов — **один** (п. 4), остальное
(пп. 1–3, 5–8) вахта сняла сама прямым `curl`, потому что это получение дословных текстов
актов, а не исследование мнений; второй подагент не понадобился. Поисков `WebSearch`
у вахты — 2. Сессия прерывалась лимитом аккаунта (HTTP 429) после п. 3, продолжена
на другом аккаунте без потерь: пп. 1–3 к тому моменту уже были в файле.

### Таблица требований

| Требование | Норма (точная ссылка) | К нам? | Что сделать в продукте |
|---|---|---|---|
| Уровень защищённости | ПП 1119 п. 12 «б» (угрозы 3-го типа + иные категории + < 100 000 субъектов) | **Да, УЗ-4** | Зафиксировать в модели угроз; следить за счётчиком субъектов |
| Порог перехода на УЗ-3 | ПП 1119 **п. 11 «д»** (> 100 000 субъектов, 3-й тип) — не п. 11 «б», как было в Г20 | При росте | Метрика числа субъектов; при 100 000 — назначить ответственного за безопасность в ИС (п. 14) |
| Тип угроз | ПП 1119 пп. 6–7; определяет сам оператор с учётом оценки вреда (Приказ РКН № 178) | **Да** | Модель угроз с обоснованием 3-го типа (НДВ в системном и прикладном ПО не актуальны); оценка вреда по № 178 |
| Режим помещений | ПП 1119 п. 13 «а»; ФСТЭК № 21 ЗТС.3 | Да | Для облака — договор с ЦОД/хостером в РФ с физической охраной; свой офис — не хранить ПДн на рабочих ноутбуках |
| Сохранность носителей | ПП 1119 п. 13 «б» (без слова «шифрование») | Да | Хранилище в РФ, резервные копии там же; без выгрузок PDF на съёмные носители |
| Перечень допущенных лиц | ПП 1119 п. 13 «в» | Да | Приказ руководителя со списком; совпадает с ролями в УПД |
| Сертифицированные СЗИ | ПП 1119 п. 13 «г»; ФСТЭК № 21 п. 4 — **только если необходимы для нейтрализации актуальных угроз** | Условно | Обосновать в модели угроз; если применяются — 6 класс, 6 уровень доверия, СВТ не ниже 6 класса (ФСТЭК № 21 п. 12) |
| 32 базовые меры УЗ-4 | ФСТЭК № 21, приложение: ИАФ.1,3–6; УПД.1–6,13–16; РСБ.1–3,7; АВЗ.1–2; АНЗ.2; ЗСВ.1–2; ЗТС.3–4; ЗИС.3 | **Да** | Аутентификация и управление учётками (вкл. пользователей), RBAC и минимум прав, блокировка после неудачных входов, защищённый удалённый админ-доступ, журнал событий безопасности с защитой, антивирус и обновления, контроль доступа к гипервизору/облачной консоли, **TLS на всех внешних каналах** |
| Компенсирующие меры | ФСТЭК № 21 п. 10 | Да | Если мера невыполнима или экономически нецелесообразна — письменно обосновать замену |
| Оценка эффективности | ФСТЭК № 21 п. 6 — не реже 1 раза в 3 года, можно самостоятельно | Да | Внутренний аудит раз в ≤ 3 года |
| Криптография для ПДн | ФСБ № 378 **п. 2** — «для операторов, использующих СКЗИ» | **Только если заявим** | Не заявлять шифрование как меру защиты ПДн без необходимости; если заявить — КС1 и режимный хвост (пп. 6, 7, 9) |
| Уведомление РКН | 152-ФЗ ст. 22 ч. 1; исключения пп. 1–6 ч. 2 отменены 266-ФЗ с 01.09.2022 | **Да** | Подать через pd.rkn.gov.ru (УКЭП или Госуслуги) в Управление РКН по ЦФО **до первого реального пользователя**; формы — Приказ РКН № 180; изменения — до 15-го числа следующего месяца (ч. 7) |
| Сведения о СКЗИ в уведомлении | ст. 22 ч. 3 п. 7 | Да | Указать фактически применяемые средства — не больше и не меньше, чем реально используется |
| Место базы данных | ст. 22 ч. 3 п. 10.1; ст. 18 **ч. 5** (запретительная редакция) | **Да** | Сбор, запись и хранение ПДн граждан РФ, **включая PDF, почтовый ящик приёма и бэкапы** — только в РФ; договор (п. 5 ч. 1 ст. 6) от локализации не освобождает |
| Срок хранения PDF | 152-ФЗ ст. 5 чч. 5, 7; ст. 21 ч. 4 | Да | Удалять или обезличивать исходный PDF после разбора, максимум 30 дней; иную цель хранения прямо назвать в политике и согласии |
| Уничтожение по отзыву согласия | ст. 21 ч. 5 (30 дней); подтверждение — **Приказ РКН № 179** от 28.10.2022, опубл. **0001202211290008** | Да | Функция удаления с актом/выгрузкой журнала по форме № 179 |
| Инцидент | ст. 21 ч. 3.1 (24 ч / 72 ч); КоАП 13.11 ч. 11 (1–3 млн ₽) | Да | Регламент реагирования, контакт с РКН, журнал для расследования |
| Утечка | КоАП 13.11 чч. 12–14 (3–15 млн ₽ по числу субъектов и идентификаторов); **оборотный 1–3 % — только повторная** (ч. 15, мин. 20 млн ₽) | Да | Считать идентификаторы, а не только субъектов: порог 10 000 идентификаторов достигается раньше, чем 1 000 субъектов |
| Банковская тайна у получателя | 395-1 ст. 26 — адресована банкам и получающим сведения от банка | **Прямо нет** (вывод Г20, практика не проверена) | Режим защиты — 152-ФЗ целиком |

### 🔴 Прямые ответы

**1. Обязаны ли мы шифровать хранимые PDF-выписки? — НЕТ, нормативной обязанности нет.**
Три независимых текстовых основания: (а) Приказ ФСТЭК № 21, п. 1 — меры, «связанные
с применением шифровальных (криптографических) средств», **выведены из документа**;
в базовом наборе УЗ-4 группа ЗНИ (защита носителей) **пуста**, единственная мера про канал
(ЗИС.3) касается **передачи**, а не хранения; (б) ПП 1119, п. 13 для УЗ-4 требует
«сохранности носителей», а не шифрования; сертифицированные СЗИ — только «когда применение
таких средств необходимо для нейтрализации актуальных угроз»; (в) Приказ ФСБ № 378, п. 2 —
«предназначен для операторов, **использующих** СКЗИ», обязанности применять криптографию
не создаёт.

**Чем, если всё-таки шифровать:**
- **Как инженерную меру сверх требований** (AES на уровне хранилища, ключи в KMS) — **любым
  средством**, без сертификации, но тогда **не заявлять** это в модели угроз и уведомлении
  как средство защиты ПДн, нейтрализующее актуальную угрозу. Иначе включается № 378.
- **Если заявить криптографию мерой нейтрализации актуальной угрозы** — только
  **сертифицированным ФСБ СКЗИ класса не ниже КС1** (№ 378 п. 9 «в»), с утверждённой
  руководителем моделью нарушителя, журналом носителей и режимом помещений хранения ключей;
  при этом сведения о СКЗИ идут в уведомление РКН (ст. 22 ч. 3 п. 7).
- ⚠️ Оговорка: граница «применяю как инженерную меру, но не заявляю» — это вывод из текста
  п. 2 № 378 и п. 4 № 21, а не цитата регулятора; проверочной практики РКН/ФСБ по этому
  разграничению в батче нет. Это самое слабое место итога.

**2. Нужно ли уведомление в РКН и когда? — ДА, до начала обработки.** Все исключения,
под которые мог бы попасть сервис (пп. 1–6 ч. 2 ст. 22), отменены с 01.09.2022. Подача
через pd.rkn.gov.ru (УКЭП или Госуслуги) в Управление РКН по ЦФО, формы — Приказ РКН № 180.
Неподача — **ч. 10 ст. 13.11 КоАП** (юрлица 100–300 тыс. ₽), а не ст. 19.7, как предполагал
заказ. Изменения сведений — не позднее 15-го числа следующего месяца.

**3. Можно ли принимать выписки на e-mail? — МОЖНО, но только на почтовый сервер в РФ.**
Запрета на e-mail как канал нет ни в законе, ни в найденных разъяснениях. Однако когда
сервис сам просит прислать выписку на свой адрес, это **целенаправленный сбор** (разъяснения
Минкомсвязи от 25.08.2015), а не «случайное письмо», поэтому ящик приёма подпадает под
ч. 5 ст. 18 152-ФЗ: **Gmail/Outlook/любой зарубежный хостинг почты исключён**
(риск ч. 8 ст. 13.11 КоАП, 1–6 млн ₽). Письмо после разбора — такой же исходный документ,
как загруженный PDF: удалять из ящика по тем же 30 дням. Канал от пользователя до сервера
оператор не контролирует; со своей стороны — приём только по TLS. Прямой позиции РКН с номером
письма по этому вопросу **не найдено**, вывод держится на разъяснениях Минкомсвязи 2015 года
и тексте закона.

### Осталось неизвестным

1. **Прямое письмо РКН** о приёме ПДн на e-mail, о защищённом канале и о зарубежной почте —
   не найдено; `*.rkn.gov.ru` отдавались нестабильно (200 у вахты, 000 у подагента через
   две минуты), `pd.rkn.gov.ru/faq/` грузит вопросы скриптом.
2. **Какой закон и с какой даты ввёл запретительную редакцию ч. 5 ст. 18** — строка «в ред.»
   в выдаче не видна; предположение «23-ФЗ от 28.02.2025, с 01.07.2025» не сверено.
3. **Не вступившие в силу изменения к 152-ФЗ** (отметка «Подготовлена редакция» на странице
   ст. 22, ред. от 26.07.2026) — содержание не раскрыто.
4. **Практика РКН/ФСБ** по разграничению «шифрование как инженерная мера» и «СКЗИ как средство
   защиты ПДн» — не искалась.
5. **Опубликование Приказа РКН № 180** (формы уведомления) — не сверялось.
6. **Судебная практика** по ст. 26 № 395-1 для небанковского получателя — вне пунктов заказа,
   осталась открытой с Г20.
7. **Толкование «идентификатора»** (примечание 4 к ст. 13.11) в практике — не искалось.


## ДОБОР Г24 (16.09.2026)

Контекст: хвосты Г20 (CoinKeeper, MoneyWiz — «ни одной попытки по доменам»; правило сверки полей Tiller).
Каналы на 16.09.2026: `WebSearch`, `curl -sk --http1.1` с браузерным UA, `r.jina.ai`. **Wayback — лежит**
(`archive.org/wayback/available` → HTTP 429, CDX → HTTP 503 «Internet Archive: Temporarily Offline», проверено
в начале захода). Exa в сессии отключена.

### Г24.1а CoinKeeper — импорта ФАЙЛОВ нет вовсе; импорт только из банка (iOS) и из СМС (Android)

**Источник 1.** `https://ruhelp.coinkeeper.me/d0eb732d6e2e49bcb29ef9550b31e4ee` («Как экспортировать свои данные в файл?»,
справочный центр CoinKeeper на Notion-подобном движке) через `r.jina.ai` → **HTTP 200, 3 596 байт**, снято 16.09.2026.
Первая строка статьи, дословно:

> «Возможности импорта файлов в приложение CoinKeeper пока, к сожалению, нет.
> CoinKeeper позволяет экспортировать свои данные (списки операций и остатки в кошельках) в формате .csv.»

**Источник 2.** `https://roadmap.coinkeeper.me/` (публичная доска идей продукта) через `r.jina.ai` → **HTTP 200, 9 897 байт**,
16.09.2026. Идея в статусе «Открыта», дословно:

> «[Импорт из Excel/CSV] Когда нужно восстановить учёт за период приходится очень много и долго заносить операции.
> Гораздо проще было бы подготовить файл на основе выгрузки из банка и импортировать — Открыта iOS Android Веб Telegram 5 комм.»

и отзыв пользователя в другой идее («внесение расходов по сканированию чеков»), дословно:

> «…в сравнении с ужасным импортом, непонятным задваиванием сумм одних и тех же операций, отнесе…» (обрезано самой доской)

**Источник 3.** `http://ck3help.me/page6703845.html` («Импорт банковских операций — Помощь по CoinKeeper 3»), `curl`+UA →
**HTTP 200, 62 101 байт**, 16.09.2026. Дословно:

> «Чтобы подгрузить новых операций нужно нажимать кнопку Обновить под карточкой счета. Импортированные операции появятся
> в истории счета. Баланс счета в Coinkeeper всегда совпадает с балансом карты в интернет-банке.
> Операцию, загруженную через импорт, можно при желании удалить, при этом она не повлияет на баланс счета.»
> «В целях безопасности нет возможности использовать на одном устройстве импорт банковских операций и распознавание СМС.»

**Источник 4.** `https://about.coinkeeper.me/page24017104.html` (рассылка «Настраиваем импорт из банков»), `curl`+UA →
**HTTP 200, 89 659 байт**, 16.09.2026. Дословно:

> «на Apple - вы подключаете импорт напрямую, персональные данные из интернет-банка. Так подключаются Сбербанк, ВТБ,
> Альфа-Банк и Тинькофф Банк.» · «для Android: … выберите «Импорт из SMS» … При каждом новом открытии приложения,
> не импортированные операции из SMS будут автоматически добавляться в ленту.»
> «Мы не даем пользователям одновременно подключить импорт из банков и импорт из СМС, исключая ситуацию, в которой
> у нас будет доступ к обоим факторам безопасности.» · «Импорт из банков на Apple отслеживает переводы между счетами.»

**Источник 5.** `https://about.coinkeeper.me/faq`, `curl`+UA → **HTTP 200, 159 706 байт**: «Не видите кнопку "Импорт"?
Проверьте, что в вашем телефоне стоит локация "Россия". На данный момент импорт доступен только в России.»

**Выжимка.**
- Вопрос «что делает CoinKeeper с нераспознанной строкой файла» **снимается**: файлового импорта нет (первоисточник,
  справка продукта). Идея «Импорт из Excel/CSV» висит открытой на доске.
- **Дедупликация.** Документированного правила нет ни в одной из 5 страниц. Механизм защиты от дублей — **архитектурный**:
  (а) запрет одновременно включать банк и СМС на одном устройстве (мотивирован безопасностью, но попутно убирает главный
  источник двойного счёта); (б) «баланс счёта всегда совпадает с балансом карты в интернет-банке» и удаление
  импортированной операции «не повлияет на баланс» — то есть баланс берётся из банка, а не суммируется из операций,
  и дубль в ленте не портит остаток. Жалоба пользователя на «непонятное задваивание сумм одних и тех же операций» на
  публичной доске показывает, что дубли в ленте всё же возникают, и чистятся руками (свайп → удалить).
- **Для нас:** CoinKeeper — не образец для файлового импорта; полезный приём — **баланс счёта как внешний якорь**,
  не зависящий от полноты ленты (у нас аналог — сверка итогов выписки, `И3`).

Каналы, пройденные сверх перечисленного: `WebSearch` ×3 («CoinKeeper импорт выписки дубли», «CoinKeeper задвоились
операции импорт», «CoinKeeper импорт из файла CSV Excel»). Отдельной статьи про дубли в справке поиск не нашёл.

### Г24.1б MoneyWiz — дубли при файловом импорте спрашиваются у человека; правило совпадения — «сумма точно + дата ±3 дня» (для банковской синхронизации)

**Источник 1 — MoneyWiz 2022 offline guide** (официальный PDF, «Last updated: Dec 14, 2021»),
`https://assets.wiz.money/MoneyWiz_Guide.pdf`, `curl`+UA → **HTTP 200, 2 584 863 байта**, 16.09.2026, `pdftotext`.
🟡 Документ датирован декабрём 2021; онлайн-статья с тем же разделом (`help.wiz.money/en/articles/4440666-…`) сегодня
отдаёт **404** (и по `curl`, и через `r.jina.ai`; новый шаблон адреса `/a/…-4440666` — тоже 404), в текущем справочном
центре раздела «Importing» в списке коллекций нет. Поиск (`WebSearch`) при этом ещё показывает сниппет статьи с тем же
текстом — формулировка переходила из версии в версию.

Chapter 10, Section 10.6 «Transaction duplicates detection», дословно:

> «MoneyWiz checks all transactions you wish to import against already existing transactions and in case it finds
> possible duplicates it will ask you what to do. This can happen for a number of reasons, for example:
> • you are trying to import the same bank statement file for the second time or,
> • you have imported all transactions for September and you are trying to import a bank statement which includes
>   transaction from 25 Sep to 25 Oct for example. In this case transactions that appear between 25 and 30 Sep can be
>   duplicated or you can skip them or,
> • you are importing the two accounts which participate in the same transfer transaction.
> These phases will not appear if MoneyWiz can recognize the format of the dates and there are no duplicate transactions.»

Section 10.2 «Select Date format», дословно:

> «MoneyWiz recognizes many date formats but sometimes it might need some help. For example, with dates like 6/6/2019,
> is this mm/dd/yyyy or dd/mm/yyyy? If MoneyWiz cannot figure out the date format without your help, it'll show you a
> couple of transactions and ask you to select the correct date format used throughout the file.»

Section 10.3 — два режима: «Quick import – quickly import your file, selecting default values for all remaining stages.
For example, if no match was found for your payee, MoneyWiz will create new payee.» · «Advanced import – manually proceed
through each stage and review default settings.»

Section 2.14 (ручная операция против банковской синхронизации), дословно — **единственное явно выписанное правило
совпадения полей**:

> «When downloading transactions from Online Banking, MoneyWiz looks for possible duplicates. It does that by searching
> for transactions that meet both of the following conditions:
> 1. transaction amount is exactly the same,
> 2. transaction date is within 3 days range (either way, to account for weekends).
> If MoneyWiz finds a match, it will not download the transaction from Online Banking but instead update the existing
> transaction with missing information (it there is any).»

Section 4.7 (auto-skip запланированных операций) повторяет то же правило и честно называет его провал:
«Therefore the only way a duplicate might appear as a result of this is if your date is not within 3 days period or the
amount is not exactly the same.»

**Источник 2 — «How do I format CSV file before importing?»** `https://help.wiz.money/a/how-do-i-format-csv-file-before-importing-4440549`
через `r.jina.ai` → **HTTP 200, 14 135 байт**, 16.09.2026 (прямой `curl` на старый адрес `/en/articles/4440549-…` → 404).
Дословно — поведение на «неожиданных» строках и колонках:

> «At minimum, your CSV file needs to contain: Date · Description · Amount»
> «If MoneyWiz cannot guess what the column contains, it'll default to "Don't import".»
> «What MoneyWiz might not like is additional information stored like this: ACCOUNT BALANCE: 3312.50 … Thank you for
> using our services. … Most of the time, MoneyWiz won't mind this data and import your file just fine. However, there
> is a chance that it would confuse the importing algorithm…»
> «An important rule is not to include time in the same column as the date – it's the single most common reason why date
> format is not recognised. MoneyWiz cannot parse the date if time is stored in the same column. At the moment, MoneyWiz
> does not import time of transactions for CSV files and will import all transactions as 12:00.»
> «If MoneyWiz seems not to recognise your amounts properly, check if the thousands and decimal separators from the file
> are the same as in your device's regional settings.»
> «Japanese, Buddhist, Persian and Islamic calendars are not supported.»

**Выжимка.**
- **Дедупликация при файловом импорте — есть**, и это отличие от Дзен-мани (там только при прямой синхронизации).
  Решение о подозрительном дубле **возвращается человеку** («it will ask you what to do»), как у Lunch Money (отдельный
  список), а не молча отбрасывается. Явно названы три сценария: повтор того же файла, **перекрытие периодов** выписок,
  две стороны одного перевода — ровно наш набор случаев.
- **Правило совпадения полей** выписано только для банковской синхронизации и auto-skip: **сумма точно + дата в окне ±3 дня**,
  описание и контрагент в правило НЕ входят. Для файлового импорта поля сравнения не раскрыты (🟡 разумно предположить
  то же правило, но первоисточником не подтверждено). Правило **заведомо размыто**: две одинаковые покупки кофе за 150 ₽
  в соседние дни оно назовёт дублем — поэтому и спрашивает человека.
- **Нераспознанное** — отказ ведётся по **колонкам и формату**, не по строкам: неопознанная колонка → «Don't import»;
  неопознанный формат даты → вопрос с примерами строк; мусор над заголовком и в подвале «чаще всего» терпится, но «может
  запутать алгоритм». **Поведения на отдельной битой строке** (пропуск/отказ файла/отчёт) справка не описывает — не добыто
  ни в гайде, ни в статье о формате.
- **Для нас:** (1) окно ±N дней + точная сумма — индустриальный минимум, но без описания и без счётчика повторов в окне он
  даёт ложные дубли; наш ключ должен быть строже и спорные случаи — отдавать человеку, как делают и MoneyWiz, и Lunch Money;
  (2) CSV-время MoneyWiz выбрасывает (всё в 12:00) — подтверждает, что время операции нельзя класть в ключ дедупликации
  между форматами.

### Г24.2 Tiller — правило сверки полей при поиске дублей

**Источник 1 — актуальная статья справки** (ID не переиспользован, это другой адрес, чем в Г20):
`https://help.tiller.com/en/articles/883554-what-should-i-do-if-i-see-duplicate-transactions-in-my-sheet`
(«What Should I Do if I See Duplicate Transactions in my Sheet?», Heather Phillips, **May 21, 2026**), `curl`+UA →
**HTTP 200, 205 582 байта**; `r.jina.ai` → **HTTP 200, 42 647 байт**; 16.09.2026. Ссылку дал `WebSearch`
(«Tiller duplicate transactions help»). Дословно:

> «To get started troubleshooting duplicates, first review the transaction IDs for the duplicates.»
> «## Identical Transaction IDs — If the pairs of duplicates have identical transaction IDs these are likely due to a fill
> issue and should be reported to the support team immediately.»
> «## Unique Transaction IDs — If the pairs of duplicates have unique Transaction IDs then the cause is likely due to one of
> the issues detailed below.»
> «# Re-added with a backup data provider … review the Source column (to the far right) in your Transactions sheet to see if
> the sources are different (Yodlee, Plaid, Manual).»
> «# Manual Data Entry — If you manually added transaction data from Mint, Personal Capital or your bank you might have added
> some that overlapped with the data Tiller was able to automatically pull from your institution. Be sure to check the date
> range before manually adding data so that you don't introduce duplicates.»
> «# Data provider mistake — Sometimes our data provider will pull in duplicate transactions. This can happen when the
> transaction was in a pending state and then was later posted. Most of the time duplicates caused by our data provider
> will resolve on their own … usually within a week.»
> «Existing duplicates will remain in your sheet even after the data feed issue is addressed by our data provider. You can
> remove duplicates manually or by using the experimental Tiller Community Solutions add-on Manage Duplicates workflow.»

**Источник 2 — само правило сверки полей.** Статья выше ссылается на документацию инструмента:
`https://community.tiller.com/t/how-to-use-the-manage-duplicates-workflow-in-the-tiller-labs-add-on/2971`,
снято через Discourse JSON API `https://community.tiller.com/t/2971.json`, `curl`+UA → **HTTP 200, 23 512 байт**,
16.09.2026. Заголовок «Docs: Manage Duplicates workflow», создан 2020-02-29, **последняя правка первого поста 2022-04-15**.
Дословно:

> «How Manage Duplicates works
> The workflow identifies transactions that have a date of within 3 days of each with the same amount and other data
> including description, institution, and account number. The Manage Duplicates workflow highlights a suspected duplicate
> row with an orange fill. You'll have an opportunity to flag additional transactions that should have been highlighted and
> also to remove the flag for transactions that are not actually duplicates. Once you're ready, the workflow can delete all
> flagged duplicate transactions.
> The duplicate flagging analysis will usually preserve the oldest/original transaction from a set of duplicate transactions.
> If only one transaction within a set of duplicates has been categorized, the duplicate flagging analysis will preserve the
> categorized transaction (even if it is the newest).
> To identify a match, the duplicate flagging analysis requires an exact match for all of the following fields (if present)
> across the set of duplicates:
> Amount · Description · Full Description · Account · Account # · Institution»
> «Be aware that deletions can only be undone using Google Sheet's Version History tools.»
> «In rare cases, duplication issues cannot be resolved and will persist.»

**Выжимка.**
- **Правило Tiller (Manage Duplicates):** дата в окне **±3 дня** + **точное совпадение** Amount, Description,
  Full Description, Account, Account #, Institution — «if present», то есть отсутствующее поле из сравнения выпадает.
  Это **строже MoneyWiz** (там только сумма + ±3 дня) и **мягче Lunch Money** по дате (там дата точно).
- **Какую копию оставить** — правило есть и полезно нам дословно: по умолчанию **самую старую**; если размечена
  категорией только одна копия — **размеченную, даже если она новее**. То есть сохраняется труд пользователя, а не порядок
  поступления.
- **Двухуровневая диагностика:** одинаковый Transaction ID у пары = сбой заливки (баг, в поддержку); разные ID = один из
  пяти пользовательских/провайдерских сценариев. Колонка **Source** (Yodlee / Plaid / Manual) — провенанс строки в данных
  (совпадает с тем, что Г20 уже записал про Tiller).
- **Автоматики нет:** в основном потоке Tiller дубли **не отбрасывает**; инструмент — «experimental» дополнение, запускается
  руками, подсвечивает, человек снимает/ставит флаги, удаление — пакетом. Провайдерские дубли pending→posted Tiller
  объявляет самоисправляющимися «usually within a week».
- **Для нас:** (1) окно ±3 дня стало индустриальной константой у двух независимых продуктов (MoneyWiz, Tiller) — у нас оно
  нужно для пары «pending в банке → проведённая в выписке», но только вместе с описанием, иначе ложные дубли;
  (2) правило «сохранять размеченную копию» стоит взять в требования к слиянию; (3) отсутствующее поле выпадает из
  сравнения — опасная мягкость для PDF, где описание обрезается по-разному в разных выписках: у нас лучше нормализовать
  описание, чем разрешать ему отсутствовать.

## ИТОГ Г24 (для пунктов 1–2)

| Пункт | Статус | Факт с источником | Что это меняет для продукта |
|---|---|---|---|
| 1а CoinKeeper: импорт файлов, нераспознанное, дубли | **добыто** (дубли — частично) | «Возможности импорта файлов в приложение CoinKeeper пока, к сожалению, нет» (`ruhelp.coinkeeper.me/d0eb…`, 200); идея «Импорт из Excel/CSV» открыта на `roadmap.coinkeeper.me`; импорт только из банка (iOS) / СМС (Android), одновременно нельзя; «Баланс счета в Coinkeeper всегда совпадает с балансом карты в интернет-банке», удаление импортированной операции баланс не меняет (`ck3help.me`, 200). Правило дедупликации не документировано; жалоба на «задваивание сумм» на доске идей | CoinKeeper — не ориентир по файловому импорту. Приём «баланс из банка как якорь, лента может быть неполной/с дублями» подтверждает нашу сверку итогов выписки как защиту |
| 1б MoneyWiz: импорт, нераспознанное, дубли | **добыто** (поведение на битой строке — нет) | Файловый импорт CSV/QIF/OFX/QFX/MT940; при подозрении на дубль «it will ask you what to do» — повтор файла, перекрытие периодов, две стороны перевода (гайд 2021, `assets.wiz.money`, 200); правило совпадения для банка: сумма точно + дата ±3 дня; неопознанная колонка → «Don't import», неопознанная дата → вопрос с примерами; время в CSV выбрасывается (всё 12:00) (`help.wiz.money/a/…-4440549`, 200). Онлайн-статья об импорте удалена (404) | Файловый дубль — решение человека, не молчаливый отброс: совпадает с Lunch Money, расходится с Дзен-мани. Время операции не годится в ключ дедупликации между форматами |
| 2 Tiller: правило сверки полей | **добыто** | Manage Duplicates: дата ±3 дня + точное совпадение Amount, Description, Full Description, Account, Account #, Institution «(if present)»; оставляет самую старую, а если размечена одна — размеченную (`community.tiller.com/t/2971.json`, 200, правка 2022-04-15); справка 21.05.2026: одинаковые Transaction ID = баг заливки, разные = сценарий пользователя/провайдера (`help.tiller.com/en/articles/883554`, 200) | Уточняет наш ключ: окно по дате нужно (pending→posted), но только с нормализованным описанием; правило «сохранять копию с пользовательской разметкой» — в требования к слиянию дублей |

**Сводка по пяти продуктам (дедупликация при импорте):** Lunch Money — (date, payee, amount) точно, отбракованное списком;
Tiller — ±3 дня + сумма + описание + счёт + институт, ручной запуск, подсветка; MoneyWiz — ±3 дня + сумма (банк), при файле
спрашивает; Дзен-мани — только при синхронизации с банком, при файле нет; CoinKeeper — файлов не принимает, правило не
документировано. **Ни один не дедуплицирует файловый импорт молча и автоматически** — везде либо человек, либо ничего.

---

## ДОБОР Г28 (16.09.2026)

**Состояние каналов на начало работы** (замер 16.09.2026, `curl -sk --http1.1`, таймаут 25 с):
`WebSearch` — доступен (бюджетного отказа нет). `Exa` (`mcp__exa__*`) — 🟢 работает, поиск отдаёт результаты.
`r.jina.ai` (без браузерного UA) — **HTTP 200**, 367 б на тестовом адресе. OpenAlex — **200**, 16 851 б.
Crossref — **200**, 2 482 б. EuropePMC — **200**, 1 190 б. **Wayback — 429** (117 б), то есть снова лёг
на момент старта (в задании значился 🟢 — расхождение зафиксировано). `publication.pravo.gov.ru` — **200**,
27 995 б. `consultant.ru` — **200**, 47 360 б (законы, время 13:4x МСК). `rkn.gov.ru` — **403** напрямую
(обход — `r.jina.ai`). `gesetze-im-internet.de/gewo/__34k.html` — **404**, 236 б (см. пункт 7 в файле
`regulation_world_advice_boundary_2026-09-09.md`: параграфа с таким номером в действующей GewO нет).

Область добора: хвосты Г22 по 152-ФЗ, КоАП и РКН (пункты 1–6). Пункт 7 (Германия) — в другом файле.

### Пункт 1. Граница «шифрование как инженерная мера» против «СКЗИ, требующего сертификата»

**Статус: добыто.** Найден документ, который эту границу проводит прямо, — методические рекомендации
ФСБ России. Норма, разъяснение ведомства и надзорная практика разведены ниже отдельно.

#### 1.1. Подзаконный акт: Приказ ФСТЭК России от 18.02.2013 № 21 (ред. 23.03.2017 № 49, 14.05.2020 № 68)

Источник: `https://r.jina.ai/https://fstec.ru/dokumenty/vse-dokumenty/prikazy/prikaz-fstek-rossii-ot-18-fevralya-2013-g-n-21`
— **HTTP 200, 68 977 б, снято 16.09.2026.** (Прямой `curl` на fstec.ru отдаёт 303 на CMS-загрузчик;
через прокси текст приказа получен целиком.)

Пункт 1, абзац третий — **дословно**:

> «В настоящем документе не рассматриваются вопросы обеспечения безопасности персональных данных,
> отнесенных в установленном порядке к сведениям, составляющим государственную тайну, а также меры,
> связанные с применением шифровальных (криптографических) средств защиты информации.»

Пункт 3 — дословно: «Меры по обеспечению безопасности персональных данных реализуются в рамках системы
защиты персональных данных <…> и **должны быть направлены на нейтрализацию актуальных угроз** безопасности
персональных данных.»

Пункт 4 — дословно: «Меры по обеспечению безопасности персональных данных реализуются в том числе
посредством применения в информационной системе средств защиты информации, прошедших в установленном
порядке процедуру оценки соответствия, **в случаях, когда применение таких средств необходимо для
нейтрализации актуальных угроз** безопасности персональных данных.»

Пункт 6 — дословно: «Оценка эффективности реализованных <…> мер <…> проводится **оператором самостоятельно**
или с привлечением на договорной основе юридических лиц и индивидуальных предпринимателей, имеющих лицензию
на осуществление деятельности по технической защите конфиденциальной информации. Указанная оценка проводится
не реже одного раза в 3 года.»

Запись Г22 «Приказ ФСТЭК № 21 п. 1 (криптомеры вне документа)» подтверждена дословно. Плюс добыто новое:
п. 6 вводит **обязанность самооценки эффективности не реже раза в 3 года** — она в Г22 не фигурировала
и относится к нам напрямую.

#### 1.2. Подзаконный акт: ПП РФ от 01.11.2012 № 1119, п. 13

Источник: `https://r.jina.ai/https://base.garant.ru/70252506/` — **HTTP 200, 24 768 б, снято 16.09.2026.**
🔴 **Замер канала:** задание сообщало, что `garant.ru` не открывается ни напрямую, ни через прокси.
**Через `r.jina.ai` без браузерного UA он открылся** — полный текст ПП 1119. Правку канала внести в канон.

Пункт 13 — дословно, подпункты «б» и «г»:

> «б) обеспечение сохранности носителей персональных данных;»
> «г) использование средств защиты информации, прошедших процедуру оценки соответствия требованиям
> законодательства Российской Федерации в области обеспечения безопасности информации, **в случае, когда
> применение таких средств необходимо для нейтрализации актуальных угроз**.»

То есть в базовом наборе УЗ-4 шифрование не названо; обязанность применить средство с оценкой соответствия
условна и включается моделью угроз. Запись Г22 подтверждена.

#### 1.3. Разъяснение ведомства (не норма): Методика оценки угроз безопасности информации, ФСТЭК, 05.02.2021

Источник: `https://fstec.ru/files/495/---5--2021-/891/---5--2021-.pdf` через `curl -skL` (обязателен `-L`:
без него 303, 0 б) → **HTTP 200, 2 744 210 б, PDF 83 с., снято 16.09.2026**; текст извлечён `pdftotext`.

Пункт 1.3 — дословно: Методика «применяется для определения угроз безопасности информации <…> в системах
и сетях, отнесенных к государственным и муниципальным информационным системам, **информационным системам
персональных данных**, значимым объектам критической информационной инфраструктуры <…>». То есть для нашей
ИСПДн она обязательна, а не факультативна.

Пункт 1.4 — дословно и это ключ к вопросу:

> «В документе **не рассматриваются методические подходы по оценке угроз безопасности информации, связанных
> с нарушением безопасности шифровальных (криптографических) средств защиты информации**, а также угроз,
> связанных с техническими каналами утечки информации.»

Вывод по методике: главный обязательный методический документ по моделированию угроз **криптографию
из своего предмета исключает**. Он не может породить «актуальную угрозу, нейтрализуемую только СКЗИ»,
потому что не работает в этом слое вовсе.

#### 1.4. 🔴 Разъяснение ведомства, прямо отвечающее на вопрос: Методические рекомендации ФСБ России от 31.03.2015 № 149/7/2/6-432

Источник-первоисточник: `http://www.fsb.ru/files/PDF/Metodicheskie_recomendacii.pdf` — **HTTP 200, 399 341 б,
PDF 22 с., снято 16.09.2026** (`curl -skL`, текст через `pdftotext`). Дубли текста: КонсультантПлюс
`cons_doc_LAW_185051`, legalacts.ru, normativ.kontur.ru (documentId=270611).

Адресат документа (преамбула, дословно): рекомендации «предназначены для федеральных органов исполнительной
власти <…> которые, в соответствии с частью 5 статьи 19 <…> принимают нормативные правовые акты, в которых
определяют угрозы безопасности персональных данных». И далее — дословно:

> «Настоящими методическими рекомендациями целесообразно также руководствоваться при разработке частных
> моделей угроз **операторам информационных систем персональных данных, ПРИНЯВШИМ РЕШЕНИЕ об использовании
> средств криптографической защиты информации** (далее - СКЗИ) для обеспечения безопасности персональных данных.»

Раздел 2 «Определение актуальности использования СКЗИ для обеспечения безопасности персональных данных» —
дословно:

> «Использование СКЗИ для обеспечения безопасности персональных данных **необходимо в следующих случаях**:
> – если персональные данные подлежат криптографической защите в соответствии с законодательством Российской Федерации;
> – если в информационной системе существуют угрозы, которые могут быть нейтрализованы только с помощью СКЗИ.
> Кроме того, решение о необходимости криптографической защиты персональных данных **может быть принято
> конкретным оператором на основании технико-экономического сравнения** альтернативных вариантов обеспечения
> требуемых характеристик безопасности информации <…>
> К случаям, когда угрозы могут быть нейтрализованы только с помощью СКЗИ, относятся:
> – передача персональных данных по каналам связи, не защищенным от перехвата нарушителем <…> (например,
> при передаче персональных данных по информационно-телекоммуникационным сетям общего пользования);
> – **хранение персональных данных на носителях информации, несанкционированный доступ к которым со стороны
> нарушителя не может быть исключен с помощью некриптографических методов и способов**.»

Там же, дословно, две оговорки, которые бьют по «шифрованию как галочке»:

> «СКЗИ **не предназначены для защиты информации от действий, выполняемых в рамках предоставленных субъекту
> действий полномочий** (например, СКЗИ не предназначены для защиты персональных данных от раскрытия лицами,
> которым предоставлено право на доступ к этой информации)»
> «для обеспечения безопасности персональных данных при их обработке в ИСПДн **должны использоваться СКЗИ,
> прошедшие в установленном порядке процедуру оценки соответствия**. Перечень СКЗИ, сертифицированных
> ФСБ России, опубликован на официальном сайте Центра по лицензированию, сертификации и защите государственной
> тайны ФСБ России (www.clsz.fsb.ru)»
> «СКЗИ являются **как средством защиты персональных данных, так и объектом защиты**.»

#### 1.5. Надзорная и судебная практика

Состав, по которому реально наказывают за несертифицированное средство, — **не ст. 13.11, а ч. 6 ст. 13.12
КоАП РФ** («использование несертифицированных средств, предназначенных для защиты информации…»). Подборка
дел (вторичный источник, автор — Ксения Шудрова, ИБ-практик; `http://shudrova.blogspot.com/2020/06/blog-post_10.html`,
**HTTP 200, 5 957 б через `r.jina.ai`, снято 16.09.2026**):

- Смоленск, 2017: виновен по ч. 6 ст. 13.12 — «Обмен персональными данными при их обработке в информационной
  системе осуществлялся **без применения средств защиты информации, прошедших процедуру оценки соответствия**
  требованиям законодательства в области обеспечения безопасности информации». Это **передача**, не хранение.
- Владикавказ, 2017 (директор филиала УФПС) — виновен по ч. 6 ст. 13.12.
- Краснодар 2019 (госжилинспекция), Сургут (юрисконсульт), Владивосток 2018 (специалист ИБ университета) —
  **НЕвиновны** по ч. 6 ст. 13.12.
- Отдельный сюжет: ООО сдавало налоговые декларации через «СБиС++» с «КриптоПро CSP» **без лицензии** — то есть
  наказание шло по линии лицензирования деятельности со СКЗИ, а не по линии 152-ФЗ.

Все наказанные эпизоды — государственные/муниципальные операторы либо каналы передачи. **Дела, где
коммерческого оператора наказали бы за то, что он не зашифровал хранимые ПДн, в выдаче нет.**
Обратного дела — где наказали бы за шифрование штатным средством без сертификата в ИСПДн УЗ-4 — тоже нет.

⚠️ Оговорка о качестве источника: это блог практика, а не база решений. `kad.arbitr.ru` из этой среды отдаёт
451 (класс 4 аудита № 4), `sudact.ru` по этому запросу через Exa не поднял ни одного релевантного решения
о шифровании хранилища. Первичные тексты решений по этим пяти эпизодам **не добыты**.

#### 1.6. Прямой ответ на вопрос пункта

**Вопрос:** если оператор шифрует хранилище штатным средством СУБД или диска и НЕ заявляет это мерой защиты
ПДн в модели угроз — возникает ли обязанность применять сертифицированные СКЗИ?

**Ответ по совокупности источников: нет, не возникает — при двух условиях.**

1. Обязанность криптозащиты включается **только** одним из двух триггеров ФСБ (МР 149/7/2/6-432, разд. 2):
   прямое требование закона к данному виду данных (к нам не относится — банковской тайной мы не оперируем,
   ГИС не являемся) либо **актуальная угроза, нейтрализуемая только СКЗИ**. Для хранения такая угроза
   определена узко: «несанкционированный доступ <…> **не может быть исключен с помощью некриптографических
   методов и способов**». Наше хранилище — сервер в контролируемой зоне с разграничением доступа, то есть
   некриптографические методы применимы; угроза как «нейтрализуемая только СКЗИ» не квалифицируется.
2. Обратной презумпции — «раз шифруешь, значит применяешь СКЗИ и обязан сертифицировать» — ни в одном
   первоисточнике **нет**. Режим СКЗИ (Приказ ФСБ № 378, ПКЗ-2005, поэкземплярный учёт по ФАПСИ № 152)
   включается от **решения оператора** использовать СКЗИ для обеспечения безопасности ПДн: МР 149/7/2/6-432
   адресует себя операторам, «ПРИНЯВШИМ РЕШЕНИЕ об использовании СКЗИ», а Приказ ФСТЭК № 21 п. 1 криптомеры
   из своего предмета выносит вовсе.

**Но граница острее, чем выглядела в Г22, и вывод надо сузить тремя оговорками:**

- 🔴 **Оговорка первая, решающая для нас.** Если в модели угроз или в любом документе СЗПДн шифрование
  **названо мерой нейтрализации конкретной угрозы**, режим СКЗИ включается автоматически — и тогда штатный
  AES в PostgreSQL/LUKS требование не закрывает: закрыть его можно только сертифицированным ФСБ средством.
  Практическое следствие: **в модели угроз шифрование хранилища упоминать нельзя ни как меру, ни как
  компенсирующий механизм.** Оно должно проходить как инженерное решение вне СЗПДн — например, в разделе
  эксплуатации, — а нейтрализация угрозы НСД должна быть закрыта мерами УПД/ЗНИ/РСБ из приказа № 21.
- **Оговорка вторая.** Вывод держится ровно на том, что **мы сами составляем модель угроз** и в ней
  не объявляем угроз, нейтрализуемых только СКЗИ. Это не автоматическое свойство продукта, а наше решение,
  которое надо задокументировать и защищать перед проверкой.
- **Оговорка третья.** Ч. 6 ст. 13.12 КоАП наказывает за несертифицированные средства защиты и применяется
  на практике. Все найденные обвинительные эпизоды — про **передачу** ПДн по каналам связи. Это подтверждает
  прежний вывод Г22 про почту (ч. 5 ст. 18 и сервер в РФ), но добавляет к нему: **канал доставки выписки
  пользователю — более рискованная точка, чем хранилище**, и там аргумент «некриптографические методы
  применимы» не работает, потому что канал выходит за контролируемую зону.

### Пункт 3. Каким законом и с какой даты введена запретительная редакция ч. 5 ст. 18 152-ФЗ

**Статус: добыто. Гипотеза Г22 подтверждена — это 23-ФЗ, но с уточнением даты вступления.**

Источник нормы: `https://r.jina.ai/https://www.consultant.ru/document/cons_doc_LAW_61801/cbf4e15b7c330f9372e876cdf2bc928bad7950ef/`
— **HTTP 200, 10 196 б, снято 16.09.2026.**

Действующая ч. 5 ст. 18 152-ФЗ — **дословно**:

> «5. При сборе персональных данных, в том числе посредством информационно-телекоммуникационной сети
> "Интернет", запись, систематизация, накопление, хранение, уточнение (обновление, изменение), извлечение
> персональных данных граждан Российской Федерации с использованием баз данных, находящихся за пределами
> территории Российской Федерации, **не допускаются**, за исключением случаев, указанных в пунктах 2, 3, 4,
> 8 части 1 статьи 6 настоящего Федерального закона.»

Ремарка КонсультантПлюс под текстом, дословно: «(часть 5 в ред. Федерального закона **от 28.02.2025 N 23-ФЗ**)».

**Закон-редактор:** Федеральный закон от 28.02.2025 № 23-ФЗ «О внесении изменений в Федеральный закон
"О персональных данных" и отдельные законодательные акты Российской Федерации»
(`https://r.jina.ai/https://www.consultant.ru/document/cons_doc_LAW_499984/` — HTTP 200, 9 806 б).
Его статья 1, пункт 2 — дословно: «часть 5 статьи 18 изложить в следующей редакции: "5. При сборе
персональных данных <…> не допускаются, за исключением случаев, указанных в пунктах 2, 3, 4, 8 части 1
статьи 6 настоящего Федерального закона.";»

**🔴 Дата вступления в силу — 1 июля 2025 года, не 28 февраля 2025.** Статья 10, часть 1 закона 23-ФЗ,
дословно: «Настоящий Федеральный закон вступает в силу с 1 июля 2025 года.»
(`https://r.jina.ai/https://www.consultant.ru/document/cons_doc_LAW_499984/b62da3aeb315547b6915beadea02920bd7dd4c41/`
— HTTP 200, 8 898 б.) Подтверждено и перечнем ГАРАНТ по 152-ФЗ: «Федеральный закон от 28 февраля 2025 г.
№ 23-ФЗ — Изменения вступают в силу с 1 июля 2025 г.»

**Что ещё внёс 23-ФЗ в 152-ФЗ** (ст. 1, пп. 1 и 3): новая ч. 1.2 ст. 6 и новая ч. 15 ст. 19 — обе про
особенности обработки ПДн сотрудников ФСБ, разведки, госохраны, защищаемых судей, потерпевших и свидетелей.
**К нам не относятся**, но записываем, чтобы закрыть закон целиком.

**Что это меняет для продукта:** ничего сверх уже принятого в Г22 — вывод «почтовый сервер только в РФ»
устоял и теперь опирается на точную норму с точной датой, а не на предположение. Дополнительно видно,
что до 01.07.2025 конструкция была «обязан обеспечить <…> с использованием баз данных на территории РФ»,
а с 01.07.2025 стала прямым запретом с закрытым перечнем исключений (пп. 2, 3, 4, 8 ч. 1 ст. 6).
**Ни одно из четырёх исключений нашему кейсу не подходит**: п. 2 — исполнение договора, стороной которого
является субъект (формально близко, но это исключение из локализации сбора, а не из хранения; опираться
на него для размещения базы за рубежом — позиция, которую придётся защищать, и она не нужна, раз мы
и так в РФ); пп. 3, 4, 8 — распространение по ст. 10.1, исследовательские/журналистские цели, правосудие.

### Пункт 4. Принятые, но не вступившие в силу изменения к 152-ФЗ (по состоянию на 16.09.2026)

**Статус: добыто. Ответ: такое изменение ровно одно, и оно нас не касается.**

Источник: перечень изменяющих документов в карточке 152-ФЗ, ГАРАНТ —
`https://r.jina.ai/https://base.garant.ru/12148567/` — **HTTP 200, 45 397 б, снято 16.09.2026.**
Косвенное подтверждение: карточка КонсультантПлюс по 152-ФЗ помечена «Подготовлена редакция документа
**с изменениями, не вступившими в силу**».

Из всего перечня изменяющих законов дата вступления позже 16.09.2026 стоит **только у одного**:

| Закон | Дата вступления | Что меняет |
|---|---|---|
| ФЗ от 07.07.2025 № 200-ФЗ | **1 марта 2027 г.** | п. 7 ч. 2 ст. 10 152-ФЗ |
| ФЗ от 26.07.2026 № 265-ФЗ | 26 июля 2026 г. (уже действует) | ст. 12 — трансграничная передача |

Текст ст. 2 закона 200-ФЗ — **дословно** (`https://r.jina.ai/https://base.garant.ru/412293502/741609f9002bd54a24e5c49cb5af953b/`
— HTTP 200, 18 574 б):

> «Пункт 7 части 2 статьи 10 Федерального закона от 27 июля 2006 года N 152-ФЗ "О персональных данных"
> <…> после слов "о транспортной безопасности," дополнить словами **"о безопасности дорожного движения,"**.»

Полное название закона: «О внесении изменений в Федеральный закон "О безопасности дорожного движения"
и статью 10 Федерального закона "О персональных данных"».

**Вывод:** единственное непришедшее изменение — расширение одного из оснований обработки **специальных
категорий** ПДн (ст. 10) на сферу безопасности дорожного движения. Спецкатегории мы не обрабатываем;
на нас это не влияет никак. **Регуляторного «навеса» на 152-ФЗ, к которому надо готовить продукт, нет.**

⚠️ Отдельно отмечено и НЕ подтверждено первоисточником: обзор AXIOMA AI от 10.09.2026 утверждает, что
Минцифры и РКН готовят требования к ИИ-системам, обрабатывающим ПДн, со статусом «публичное обсуждение
осенью 2026, вступление ориентировочно Q1 2027». Это **прогноз консультанта**, не закон и не законопроект
с номером; в перечнях ГАРАНТ и КонсультантПлюс такого нет. Проверять отдельно, если понадобится.

### Пункт 5. Толкование «идентификатора» в примечании 4 к ст. 13.11 КоАП

**Статус: частично. Норма добыта дословно; официального разъяснения РКН или Пленума ВС по её толкованию
не существует — найдено только применение суда, и оно порог через идентификаторы не считает.**

#### 5.1. Норма — дословно

Источник: `https://r.jina.ai/https://www.consultant.ru/document/cons_doc_LAW_34661/1f421640c6775ff67079ebde06a7d2f6d17b96db/`
— **HTTP 200, 47 043 б, снято 16.09.2026.**

Примечание 4 к ст. 13.11 КоАП РФ — дословно:

> «4. В целях настоящей статьи под идентификатором понимается **уникальное обозначение сведений о физическом
> лице, содержащееся в информационной системе персональных данных оператора и относящееся к такому лицу**.»

Пороги, в которых идентификатор работает альтернативным критерием (дословно, ч. 12–14):

| Часть | Порог по субъектам | **или** порог по идентификаторам |
|---|---|---|
| ч. 12 | от 1 000 до 10 000 субъектов | от 10 000 до 100 000 идентификаторов |
| ч. 13 | от 10 000 до 100 000 субъектов | от 100 000 до 1 000 000 идентификаторов |
| ч. 14 | более 100 000 субъектов | более 1 000 000 идентификаторов |

Конструкция — «и (или)»: достаточно **любого** из двух порогов. Это и есть риск: база на 10 000 человек
с десятком уникальных обозначений на каждого даёт 100 000 идентификаторов и поднимает дело на часть выше.

#### 5.2. Разъяснений ведомства не найдено

Пройденные каналы: `WebSearch` (запрос про прим. 4 и разъяснение РКН), Exa (запрос про толкование
идентификатора — соединение оборвалось, повторено через `WebSearch`), `rkn.gov.ru` напрямую (**403**),
поиск по территориальным управлениям (`74.rkn.gov.ru` через `r.jina.ai` — **HTTP 422**, прокси отказал).
**Ни письма РКН, ни методических разъяснений, ни позиции в обзоре судебной практики не обнаружено.**
Практики толкования нет и у комментаторов: разбор на Хабре (`https://r.jina.ai/https://habr.com/ru/articles/1066582/`
— HTTP 200, 27 887 б) прямо фиксирует проблему, но не решает её, дословно: «Идентификатор по примечанию 4 —
"уникальное обозначение сведений о физическом лице" в вашей системе, и **одна база на десять тысяч человек
может дать в разы больше идентификаторов и утащить дело на часть выше**.»

#### 5.3. Единственное найденное применение нормы судом

Постановление Девятого ААС от 03.06.2026 № 09АП-15707/2026 по делу № А40-351064/2025 (ООО «ЮКИДС»),
получено через `mcp__exa__web_fetch_exa` по адресу КонсультантПлюс `base=MARB&n=3119581`
(🔴 замер: тот же URL через `r.jina.ai` даёт **HTTP 400** — Exa его берёт, прокси нет).

Фабула: утечка из ИСПДн «Битрикс 24»; объём ПДн — «фамилия, имя, отчество, номер телефона, электронная
почта»; оператор сам уведомил РКН 24.06.2025 (номер 9679907). Квалификация — **ч. 14 ст. 13.11 КоАП**,
штраф первой инстанции **400 000 руб.**

🔴 **Ключевое для нашего вопроса:** суд вышел на ч. 14 **по числу субъектов** («около 500 000 записей»,
«более ста тысяч субъектов»), а не по числу идентификаторов. Формулировка постановления дословно:
«Ввиду наличия в скомпрометированной базе данных **более ста тысяч субъектов персональных данных и (или)
более одного миллиона идентификаторов**, указанные действия образуют состав <…> по ч. 14 ст. 13.11 КоАП РФ» —
то есть суд процитировал норму целиком, не разделив критерии и **не посчитав идентификаторы отдельно**.
Отдельно суд признал набор «фамилия, имя, номер телефона, адрес электронной почты» «уникальными
идентифицирующими признаками», но в контексте **доказывания принадлежности базы оператору**, а не в
контексте примечания 4.

#### 5.4. Что это меняет для продукта

- Порог, который нас реально касается, — **по субъектам**, и он далеко: ч. 12 включается от 1 000 субъектов.
  Это же число, кстати, задаёт нижнюю границу вообще всей «утечечной» линейки ч. 12–14.
- 🔴 **Риск по идентификаторам для нас непропорционально выше, чем по субъектам, и его нельзя оценить
  заранее**, потому что толкования нет. Наш продукт хранит на одного пользователя много уникальных
  обозначений: id пользователя, id счёта, id каждой транзакции из выписки, id цели, id долга. Если РКН
  однажды истолкует «уникальное обозначение сведений о физическом лице» широко (любой первичный ключ
  в строке, относящейся к лицу), то **1 000 пользователей с сотней транзакций каждый дают 100 000
  идентификаторов — то есть ч. 12 включается на порядок раньше, чем по числу субъектов.**
- Практический вывод в требования: **минимизировать число долгоживущих уникальных ключей, привязываемых
  к лицу, и не тащить в одну таблицу с ПДн то, что может обойтись суррогатным ключом без связи с субъектом.**
  Плюс — обезличивание/усечение транзакционных идентификаторов при выгрузках и бэкапах.
- ⚠️ Это **наша интерпретация риска, а не позиция ведомства.** Помечено как открытая неопределённость.

### Пункт 6. Опубликование Приказа РКН № 180 и действующая редакция форм

**Статус: добыто.**

**Реквизиты:** Приказ Федеральной службы по надзору в сфере связи, информационных технологий и массовых
коммуникаций **от 28 октября 2022 г. № 180** «Об утверждении форм уведомлений о намерении осуществлять
обработку персональных данных, об изменении сведений, содержащихся в уведомлении о намерении осуществлять
обработку персональных данных, о прекращении обработки персональных данных». Подписал руководитель
**А.Ю. Липов**.

- **Зарегистрирован в Минюсте России 15.12.2022, регистрационный № 71532** (карточка КонсультантПлюс
  `cons_doc_LAW_434375`, снято через `r.jina.ai` — **HTTP 200, 9 157 б, 16.09.2026**; та же запись
  в normativ.kontur.ru documentId=438326 и в тексте PDF-копий приказа).
- **Официально опубликован 15.12.2022** на Официальном интернет-портале правовой информации
  (`pravo.gov.ru`) — подтверждено `WebSearch`; **точный номер опубликования вида `0001202212……` не добыт**:
  поиск по `publication.pravo.gov.ru` через `r.jina.ai` отдаёт только оболочку формы поиска (HTTP 200,
  3 431 б, результаты подгружаются скриптом), точечный перебор номеров за 15–16.12.2022 попал в приказы
  других ведомств.
- **Вступил в силу 26.12.2022** — «по истечении 10 дней после дня официального опубликования»
  (формулировка Контур.Норматив, documentId=45544: «Данная форма вступает в силу (с 26.12.2022)
  по истечении 10 дней после дня официального опубликования Приказа Роскомнадзора от 28.10.2022 N 180»).
- **Основание издания** (преамбула, дословно): «В соответствии с частью 8 статьи 22 Федерального закона
  от 27 июля 2006 г. № 152-ФЗ "О персональных данных" <…>, абзацем вторым пункта 1 Положения о Федеральной
  службе по надзору в сфере связи, информационных технологий и массовых коммуникаций, утвержденного
  постановлением Правительства Российской Федерации от 16 марта 2009 г. № 228 <…>, приказываю».

**Действующая редакция — первоначальная, от 28.10.2022; изменений не вносилось.** Признаки: карточка
КонсультантПлюс в заголовке не содержит пометки «(ред. от …)»; Контур.Норматив помечает документ
«Редакция от 28.10.2022».

**Три формы (приложения № 1–3):** уведомление о намерении осуществлять обработку ПДн; уведомление
об изменении сведений в ранее поданном уведомлении; уведомление о прекращении обработки ПДн.
Состав полей формы № 1 (по тексту приложения): наименование/ФИО и ИНН/ОГРН оператора, адрес; далее
поблочно по каждой цели обработки — цель <2>, категории ПДн <3>, категории субъектов <4>, правовое
основание <5>, перечень действий <6>, способы обработки <7>.

**Что это меняет для продукта:** ничего не меняет, но закрывает процедурный хвост Г22 — при подаче
уведомления до первого пользователя использовать **форму приложения № 1 приказа № 180 в редакции
28.10.2022**, и заполнять её **поблочно по каждой цели** (наша конструкция «анализ выписок» + «расчёт
распределения свободного денежного потока» + «хранение истории» — это разные цели, и в форме они идут
отдельными блоками, а не одной строкой).

### Пункт 2. Прямое письмо или разъяснение РКН о приёме документов и файлов на e-mail

**Статус: не добыто по РКН; но разъяснение 2015 года поднято из пересказа в дословный текст — и оно
оказалось НЕ ответом на наш вопрос. Вывод Г22 требует уточнения.**

#### 2.1. Разъяснения Минкомсвязи от 25.08.2015 — дословно, впервые в этой базе

Г22 опирался на пересказ. Полный текст добыт: `https://r.jina.ai/https://rppa.pro/npa/minkomsvyaz_25.08.2015`
— **HTTP 200, 131 369 б, снято 16.09.2026.** Документ построен как «катехизис» вопрос-ответ; ведомственная
принадлежность и дата подтверждены карточкой NormaCS (`08.normacs.ru/Doclist/doc/24552.html`: «Утвержден:
Минцифры России; Министерство связи и массовых коммуникаций Российской Федерации, **25.08.2015**»,
статус — «Информационный документ») и карточкой ГАРАНТ `base.garant.ru/57385828/`.

**Вопрос, ближайший к нашему, — дословно:**

> «Организация пользуется сервисом электронной почты, чья серверная инфраструктура расположена за рубежом.
> На электронные почтовые ящики могут приходить электронные письма, содержащие персональные данные
> в неструктурированном виде. После получения письма работник осуществляет извлечение и внесение полученных
> персональных данных в базу данных, расположенную в России. То есть, на почтовых серверах могут храниться
> получаемые персональные данные в несистематизированном виде. **Подпадает ли инфраструктура почтового
> сервиса под требования 242-ФЗ?**»

**Ответ министерства — дословно и целиком:**

> «В соответствии с пунктом 1 статьи 3 Федерального закона №152-ФЗ персональные данные - любая информация,
> относящаяся к прямо или косвенно определенному или определяемому физическому лицу (субъекту персональных
> данных).
> Федеральным законом №242-ФЗ внесены изменения в статью 18 Федерального закона №152-ФЗ по ее дополнению
> новой частью 5, устанавливающей обязанность оператора при сборе персональных данных <…> обеспечить запись,
> систематизацию, накопление, хранение, уточнение (обновление, изменение), извлечение персональных данных
> граждан Российской Федерации с использованием баз данных, находящихся на территории Российской Федерации <…>
> Учитывая изложенное, **в случае, если на территории Российской Федерации происходит сбор персональных данных
> гражданина Российской Федерации, за исключением вышеуказанных случаев, оператор персональных данных должен
> будет соблюдать требования Федерального закона №242-ФЗ.**»

🔴 **Это не ответ на заданный вопрос.** Министерство пересказало норму и ушло от главного: считается ли
почтовый ящик «базой данных» в смысле ч. 5 ст. 18. Прямого «почтовый сервер за рубежом нельзя» в тексте
**нет**. Следовательно, запись Г22 «выписки на e-mail — только на почтовый сервер в РФ» опирается не на
позицию ведомства, а на **осторожное толкование**, и это надо называть своим именем.

**Два усиливающих обстоятельства, не отменяющих вывод:**
1. Разъяснение относится к **прежней** редакции ч. 5 ст. 18 («обязан обеспечить <…> с использованием баз
   данных на территории РФ»). С 01.07.2025 действует **запретительная** редакция (см. пункт 3), где
   «не допускаются». Толкование в пользу оператора стало труднее, а не легче.
2. Сам же документ (АЭТП, разбор 2015 г.) фиксирует его юридический вес: разъяснение ведомства — мнение,
   не обязательное для суда; толкование законов — прерогатива суда.

#### 2.2. Позиции самого РКН по e-mail не добыто — с точным перечнем пройденных каналов

| Канал | Что вернул |
|---|---|
| `rkn.gov.ru` прямой `curl` | **HTTP 403** |
| `rkn.gov.ru/personal-data/p197/` с браузерным UA | **HTTP 404**, 2 044 б |
| `pd.rkn.gov.ru/faq/` с браузерным UA | **HTTP 200, 9 682 б, но текста 1 054 знака** — страница на JS, содержания в HTML нет |
| `77.rkn.gov.ru/p3852/p13239/p13309/` с браузерным UA | **HTTP 200, 33 891 б, текста 1 770 знаков** — то же, JS-оболочка |
| `34.rkn.gov.ru/p8959/p15053/` («Часто задаваемые вопросы») с браузерным UA | **HTTP 200, 41 296 б, текста 1 916 знаков** — то же |
| `59.rkn.gov.ru/…/p20914/` («Ответы на вопросы») | **HTTP 404** |
| те же адреса через `r.jina.ai` | **HTTP 422** (прокси отказывается) |
| те же адреса через `mcp__exa__web_fetch_exa` | **CRAWL_LIVECRAWL_TIMEOUT** |
| Wayback | **HTTP 429** на старте работы и **429** при повторе — лежит |
| `WebSearch` (два запроса), Exa `web_search_exa` (один запрос) | поднимают только списки разделов РКН и пересказы консультантов |

🔴 **Замер канала, полезный для канона:** региональные сайты РКН **отдают HTTP 200 прямому `curl`
с браузерным User-Agent**, тогда как головной `rkn.gov.ru` — 403, а `r.jina.ai` по ним — 422.
Но толку мало: содержимое подгружается скриптом, в HTML его нет. **Чтобы взять FAQ РКН, нужен рендеринг
JS — ни одного такого канала в наборе нет.** Это ограничение инструментария, а не отсутствие документа;
записать в класс 2 (нужен другой инструмент), а не в «источника не существует».

#### 2.3. Что при этом установлено твёрдо и на чём держится процедура

Единственный акт РКН, прямо касающийся электронной формы, найден и относится к **направлению уведомлений
оператором в РКН**, а не к приёму файлов от пользователей: Приказ Роскомнадзора от 30.05.2017 № 94
(ред. 30.10.2018), методические рекомендации, п. 3.2 — дословно: «Оператор направляет Уведомление
в ТО Роскомнадзора **в виде документа на бумажном носителе или в форме электронного документа,
подписанного уполномоченным лицом**. Электронная форма Уведомления и порядок ее заполнения размещены
на Портале персональных данных Роскомнадзора.» Там же п. 3.1.7 требует в уведомлении указать
«сведения о наличии шифровальных (криптографических) средств и наименования этих средств» —
🔴 **прямая сцепка с пунктом 1: если мы впишем в уведомление криптосредство, мы своими руками включим
режим СКЗИ.** Источник: `internet-law.ru/documents/dop_documents/66/r_89645/0/prika.html` (через Exa).

#### 2.4. Прямой ответ на вопрос пункта

**Можно ли принимать выписки на e-mail по позиции самого РКН?** — **Позиции самого РКН по этому вопросу
не существует в доступных источниках.** Ближайшее ведомственное высказывание (Минкомсвязь, 25.08.2015)
на прямой вопрос про заграничный почтовый сервер **уклонилось от ответа**. Рабочий вывод остаётся прежним
и осторожным — **почтовый сервер только в РФ**, — но его основание надо переписать: это не «так сказал
регулятор», а «регулятор не сказал ничего, а норма с 01.07.2025 запретительная».

## ИТОГ Г28 (пункты 1–6)

| Пункт | Статус | Норма или разъяснение со ссылкой | Что меняет для продукта |
|---|---|---|---|
| 1. Граница «шифрование как инженерная мера» против «СКЗИ» | **добыто** (практика — частично) | Приказ ФСТЭК № 21 п. 1 абз. 3 («не рассматриваются <…> меры, связанные с применением шифровальных (криптографических) средств»), п. 3, п. 4, п. 6 (`fstec.ru` через `r.jina.ai`, HTTP 200, 68 977 б); ПП 1119 п. 13 «б», «г» (`base.garant.ru/70252506` через прокси, 200, 24 768 б); Методика ФСТЭК 05.02.2021 п. 1.3 и **п. 1.4** («не рассматриваются методические подходы по оценке угроз <…> шифровальных (криптографических) средств») — PDF 2 744 210 б; 🔴 **МР ФСБ 31.03.2015 № 149/7/2/6-432, разд. 2** (`fsb.ru/files/PDF/Metodicheskie_recomendacii.pdf`, 200, 399 341 б) | **Вывод «шифровать не обязаны» держится**, но сужается: (1) в модель угроз шифрование хранилища вписывать нельзя — это включит режим СКЗИ; (2) обязанность **самооценки эффективности мер раз в 3 года** (п. 6 приказа № 21) — новая, в Г22 её не было; (3) канал доставки выписки рискованнее хранилища |
| 2. Позиция РКН о приёме документов на e-mail | **не добыто по РКН; разъяснение 2015 поднято в дословный текст** | Разъяснения Минкомсвязи 25.08.2015, вопрос про заграничный почтовый сервер и ответ целиком (`rppa.pro/npa/minkomsvyaz_25.08.2015`, HTTP 200, 131 369 б; статус по NormaCS — «Информационный документ») | 🔴 **Основание вывода переписывается.** Министерство на прямой вопрос **не ответило**. «Почтовый сервер только в РФ» — наше осторожное толкование запретительной нормы, а не позиция регулятора. Плюс: п. 3.1.7 Приказа РКН № 94 требует указывать в уведомлении криптосредства — вписав их, мы сами включим режим СКЗИ |
| 3. Закон и дата запретительной редакции ч. 5 ст. 18 | **добыто** | ФЗ от 28.02.2025 **№ 23-ФЗ**, ст. 1 п. 2 («часть 5 статьи 18 изложить в следующей редакции»); **ст. 10 ч. 1: вступает в силу с 1 июля 2025 года** (`consultant.ru/document/cons_doc_LAW_499984/…`, HTTP 200) | Гипотеза Г22 подтверждена, дата уточнена: **01.07.2025, не 28.02.2025.** Четыре исключения (пп. 2, 3, 4, 8 ч. 1 ст. 6) нашему кейсу не подходят |
| 4. Принятые, но не вступившие изменения к 152-ФЗ | **добыто** | Перечень изменяющих актов в карточке 152-ФЗ (`base.garant.ru/12148567` через прокси, HTTP 200, 45 397 б); единственный — **ФЗ от 07.07.2025 № 200-ФЗ, в силу с 01.03.2027**, текст ст. 2: в п. 7 ч. 2 ст. 10 добавляются слова «о безопасности дорожного движения,» | **Регуляторного навеса нет.** Изменение касается спецкатегорий ПДн в сфере БДД; нас не затрагивает. Готовить продукт к «будущему 152-ФЗ» не нужно |
| 5. «Идентификатор» в прим. 4 к ст. 13.11 КоАП | **частично** | Прим. 4 дословно: «уникальное обозначение сведений о физическом лице, содержащееся в ИСПДн оператора и относящееся к такому лицу»; пороги ч. 12–14 (`consultant.ru/…/1f421640…`, HTTP 200, 47 043 б). Разъяснений РКН/ВС **нет**. Единственное применение: Постановление 9 ААС 03.06.2026 № 09АП-15707/2026, дело А40-351064/2025 — суд вышел на ч. 14 **по субъектам**, идентификаторы отдельно не считал | 🔴 **Скрытый риск.** У нас на пользователя много уникальных ключей (счета, транзакции, цели, долги). При широком толковании 1 000 пользователей дают >100 000 идентификаторов → ч. 12 включается на порядок раньше порога по субъектам. **В требования: минимизировать долгоживущие ключи, связанные с лицом; усекать транзакционные id в выгрузках и бэкапах.** Толкования нет — риск остаётся открытым |
| 6. Опубликование Приказа РКН № 180 | **добыто** (номер опубликования — нет) | Приказ РКН **от 28.10.2022 № 180**, Минюст **15.12.2022 № 71532**, опубликован на `pravo.gov.ru` **15.12.2022**, в силу **26.12.2022**; действующая редакция — **первоначальная, изменений не вносилось**; основание — ч. 8 ст. 22 152-ФЗ и ПП РФ 16.03.2009 № 228 | Процедурный хвост закрыт: подаём по **форме приложения № 1 в редакции 28.10.2022**, заполняя **поблочно по каждой цели** обработки, а не одной строкой |

### Прямые ответы на вопросы батча

🔴 **Держится ли вывод «шифровать хранимые выписки не обязаны» после проверки практики? — ДА, держится,
но с тремя оговорками.** Обязанность криптозащиты включается только двумя триггерами (МР ФСБ
149/7/2/6-432, разд. 2): прямое требование закона к данному виду данных — к нам не относится; либо
актуальная угроза, «нейтрализуемая только с помощью СКЗИ», а для хранения она определена узко —
«несанкционированный доступ <…> **не может быть исключен с помощью некриптографических методов
и способов**». У нас некриптографические методы применимы. Обратной презумпции «шифруешь — значит
обязан сертифицировать» ни в одном первоисточнике нет: режим СКЗИ включается **решением оператора**
(МР адресованы операторам, «принявшим решение об использовании СКЗИ»), а Приказ ФСТЭК № 21 п. 1
криптомеры выносит из своего предмета. Оговорки: (а) 🔴 шифрование хранилища **нельзя называть мерой
защиты ПДн** ни в модели угроз, ни в уведомлении РКН (п. 3.1.7 Приказа № 94) — иначе штатный AES
требование не закроет и понадобится сертифицированное ФСБ средство; (б) вывод держится на том, что
**мы сами составляем модель угроз** и не объявляем в ней угроз, нейтрализуемых только СКЗИ, — это наше
задокументированное решение, а не свойство продукта; (в) обвинительная практика по ч. 6 ст. 13.12 КоАП
существует и вся касается **передачи** ПДн по каналам связи, а не хранения.

🔴 **Можно ли принимать выписки на e-mail по позиции самого РКН? — Позиции самого РКН нет.**
Ближайшее ведомственное высказывание — Минкомсвязь, 25.08.2015 — на прямо заданный вопрос «подпадает ли
инфраструктура почтового сервиса под 242-ФЗ» **ушло от ответа**, пересказав норму. Сайты РКН из этой
среды не берутся ни одним каналом набора (403 напрямую, 422 через `r.jina.ai`, таймаут через Exa,
429 у Wayback, а при HTTP 200 с браузерным UA содержимое подгружается скриптом и в HTML отсутствует) —
это **ограничение инструментария, класс 2, нужен рендеринг JS**. Рабочее решение не меняется —
**почтовый сервер только в РФ**, — но его основание теперь честное: не «регулятор разрешил/запретил»,
а «регулятор промолчал, а норма с 01.07.2025 запретительная».

### Осталось неизвестным

- Первичные тексты пяти решений по ч. 6 ст. 13.12 КоАП (Смоленск 2017, Владикавказ 2017, Краснодар 2019,
  Сургут, Владивосток 2018) — есть только подборка практика-блогера; `kad.arbitr.ru` отдаёт 451.
- Толкование «идентификатора» — разъяснений не существует в доступных источниках; риск не оценён численно.
- Номер официального опубликования Приказа РКН № 180 на `pravo.gov.ru` (поиск портала — JS-оболочка).
- Любая позиция самого РКН по e-mail — см. выше, класс 2.

### Замеры каналов (в канон добычи)

- 🔴 **`base.garant.ru` открывается через `r.jina.ai` без браузерного UA** — HTTP 200 на ПП 1119, на карточке
  152-ФЗ, на 200-ФЗ. Прежняя запись «garant не открывается ни напрямую, ни через прокси» **опровергнута**.
- 🔴 **`fstec.ru` отдаёт 303 на CMS-загрузчик** — PDF берётся только с `curl -skL` (с `-L`); без него 0 байт.
  Итог: Методика 2021 — 2 744 210 б, 83 страницы, разбирается `pdftotext`.
- 🔴 **Региональные сайты РКН (`34.rkn.gov.ru`, `77.rkn.gov.ru`, `pd.rkn.gov.ru`) отвечают HTTP 200 прямому
  `curl` с браузерным UA**, тогда как головной `rkn.gov.ru` — 403, а `r.jina.ai` по ним — 422. Толку нет:
  контент на JS, в HTML его меньше 2 000 знаков.
- Карточки КонсультантПлюс вида `cons/cgi/online.cgi?base=MARB&n=…` через `r.jina.ai` дают **HTTP 400**,
  а через `mcp__exa__web_fetch_exa` — **читаются целиком**. Обратный случай к обычному порядку каналов.
- `Wayback` был **429 на старте и 429 через час** — в задании значился 🟢; расхождение зафиксировано.
- Собственных `WebSearch` по пунктам 1–6 — 3. Exa `web_search_exa` — 4 (один обрыв сокета, повторён
  через `WebSearch`), `web_fetch_exa` — 1. Остальное — `curl` прямой и через `r.jina.ai`.

---

## ДОБОР Г30.3 — Exa (16.09.2026)

**Каналы на начало работы (16.09.2026, ~21:30 МСК):** Exa `mcp__exa__web_search_exa` — 🟢 работает; `r.jina.ai` без UA → `sec.gov` **HTTP 200**;
OpenAlex **200**; Crossref **200**; `cbr.ru` прямой **200**; Wayback **302** (жив), CDX **503**. `publication.pravo.gov.ru/api/Documents` — **200** (при верных
параметрах; `PageSize=20` и пустой `DocumentTypes` дают **400** — валидатор API, не отказ сервиса).

Сверка с последним упоминанием: Г20 «Приказы ФСТЭК № 21 / ФСБ № 378» — закрыты Г28 (п. 1); «№ 179 опубликование» — закрыто в Г22 (0001202211290008);
«CoinKeeper / MoneyWiz / Tiller» — закрыты Г24 (кроме поведения MoneyWiz на битой строке); Г22 п. 2–5 — закрыты Г28. Открытыми на вход Г30.3 были:
(П1) позиция самого РКН по приёму ПДн на e-mail / зарубежную почту; (П2) первичные тексты решений по ч. 6 ст. 13.12 КоАП; (П3) номер опубликования
Приказа РКН № 180; (П4) толкование «иных организаций» ст. 26 № 395-1; (П5) MoneyWiz — битая строка; (П6) толкование «идентификатора» (прим. 4 к ст. 13.11).

### Г30.3-П1. 🔴 Позиция РКН — СУЩЕСТВУЕТ; «позиции нет» (Г28) было отказом инструмента, а не отсутствием источника — ✅ ДОБЫТО частично первоисточником

**Первоисточник (индивидуальное разъяснение регулятора — не нормативный акт):** Ответ Роскомнадзора от **24.03.2025 № 08-134789** «О рассмотрении запроса по
локализации баз данных», подписан начальником Управления по защите прав субъектов ПДн Ю.Е. Контемировым (ЭП), скан опубликован comply.ru:
`https://storage.yandexcloud.net/comply-publicfiles/public/Otvet_RKN_24.03.2025_lokalizatsija.pdf` — прямой `curl -sL` **HTTP 200, 372 088 б**, `pdftotext`, 376 слов. Найден через Exa. Дословно:
> «В соответствии с ч. 5 ст. 18 Закона (в ред. Федерального закона от 28.02.2025 № 23-ФЗ) при сборе персональных данных, в том числе посредством
> информационно-телекоммуникационной сети «Интернет», запись, систематизацию, накопление, хранение, уточнение (обновление, изменение), извлечение
> персональных данных граждан Российской Федерации с использованием баз данных, находящихся за пределами Российской Федерации, не допускается, за
> исключением случаев, указанных в пп. 2, 3, 4, 8 ч. 1 ст. 6 Закона.
> С учетом изложенного требования ч. 5 ст. 18 Закона (в ред. Федерального закона от 28.02.2025 № 23-ФЗ) распространяются на деятельность операторов,
> осуществляющих сбор персональных данных граждан Российской Федерации.
> Ограничения на осуществление трансграничной передачи персональных данных, ранее собранных с использованием баз данных, находящихся на территории
> Российской Федерации, в случаях, установленных ч. 1 ст. 6 Закона, указанной нормой не устанавливаются.
> Дополнительно обращаем внимание, что трансграничная передача персональных данных подлежит осуществлению в соответствии с требованиями ст. 12 Закона,
> в том числе по подаче уведомления о намерении осуществлять трансграничную передачу персональных данных.»
То же — Минцифры, письмо от **12.05.2025 № П25-44929** (pravo.ppt.ru, сниппет Exa), с добавлением: «уточнение (обновление, изменение), а равно хранение
персональных данных граждан Российской Федерации, в том числе их копий, оператором, осуществляющим сбор … должны осуществляться с использованием баз данных,
расположенных в Российской Федерации»; «использование отдельных метрических программ, в частности "Google Analytics" … является трансграничной передачей».

**Письма РКН именно про мессенджеры/почту — по вторичным (реквизиты есть, сканов в этом заходе нет):**
- **РКН, 13.09.2023 № 08-80104** — цитата у bizstrategii.ru (Exa): «Сбор персональных данных клиентов компании с использованием баз данных, находящихся за
  пределами РФ, будет являться нарушением требований законодательства РФ в области персональных данных. Персональные данные клиентов, содержащиеся в сообщениях
  клиентов, направленных ими в адрес компании через иностранные мессенджеры, включенные в Перечень ч. 10 ст. 10 Федерального закона № 149-ФЗ (Telegram,
  WhatsApp*, Viber, Skype, Discord, Snapchat, Microsoft Teams, Threema, WeChat), не должны приниматься в обработку и должны быть уничтожены компанией».
- Вики privacy-advocates.ru (НКО, 25.03.2026; `r.jina.ai` 200, 37 266 б) сводит: РКН 14.12.2023 № 08-145976 (канал в мессенджере по ссылке — не трансграничная
  передача); **Управление РКН по ПФО 19.08.2025 № 22002-8/52: «переписка между пользователями не обладает признаками формирования базы данных за пределами РФ»**;
  РКН 22.01.2026: запрос ФИО/телефона через чат-бот — сбор ПД, подпадает под ч. 5 ст. 18; «формы, чат-боты и скрипты, передающие данные на иностранные
  серверы до сохранения в базах данных на территории РФ, нарушают 152-ФЗ»; Минцифры 03.07.2025 (обращение № 279841551) — направление ПД через иностранные
  мессенджеры пользователям в РФ не является трансграничной передачей. Сама вики: «мессенджеры и электронная почта в части сообщений, передаваемых между
  пользователями, не обладают признаком систематизированности данных» — это **мнение НКО**, не регулятора.
- Минцифры, 28.06.2023 № П25-1-05-200-202259 (ГАРАНТ, `base.garant.ru/408418617/`, текст из индекса Exa) — первоисточник для ч. 8–10 ст. 10 149-ФЗ:
  «персональные данные российских граждан, направленные ими в адрес организаций посредством иностранных мессенджеров, указанных в перечне Роскомнадзора …
  не должны приниматься в обработку и должны быть уничтожены организацией». РКН, 27.07.2023 № 08ВМ-63651 (pravo.ppt.ru) — то же для банков.
**Выжимка для продукта.** (1) Позиция РКН по сути вопроса есть и совпадает с нашим рабочим решением: **первичная запись ПДн — только в базах в РФ**
(письмо 08-134789). (2) Почтовый ящик, куда пользователь присылает выписку, — это и есть точка «сбора»; иностранный сервер там запрещён по тексту
ч. 5 ст. 18 и по чтению РКН. (3) Канал «через иностранный мессенджер из Перечня» — по письму 08-80104 **принимать нельзя, а полученное — уничтожать**;
запрет ч. 8 ст. 10 149-ФЗ адресован банкам/НФО/госкомпаниям (FINPILOT к ним не относится), но письмо 08-80104 распространяет вывод на «компанию»
вообще через ч. 5 ст. 18. (4) Мягкая позиция Управления РКН по ПФО (2025) о «переписке» — региональная, о межпользовательской переписке, для приёма
документов оператором на неё опираться нельзя. Рабочее решение Г28 «почтовый сервер только в РФ» **теперь опирается на позицию регулятора**, а не только на
осторожное толкование.
**Не добыто:** сканы писем 08-80104, 08-145976, 22002-8/52 и от 22.01.2026 (Exa нашёл только пересказы; `rkn.gov.ru` — 403 по Г28).

### Г30.3-П2. Практика по ч. 6 ст. 13.12 КоАП — ЧАСТИЧНО (новое дело; пять старых решений — нет)

- Лукацкий, блог, 28.10.2022 (`r.jina.ai`, 200, 13 331 б; частный эксперт): ФСТЭК по СФО 24.08.2021 привлекло АНО «Сохнут» по ч. 6 ст. 13.12 КоАП, дословно из
  постановления в пересказе автора: «осуществляли передачу информации, содержащей персональные данные граждан РФ, по каналам связи сети Интернет без
  использования сертифицированных средств криптографической защиты информации (СКЗИ), предназначенные для шифрования передаваемых сообщений электронной
  почты»; штраф 10 000 ₽; судебный акт — «дело №12-696/2021 от 21 октября 2021 года (Омск)». Первичный текст решения суда **не снят** (реквизит есть).
- ВС РФ (`vsrf.ru/lk/practice/stor_pdf/2446160`, сниппет Exa) — ч. 6 ст. 13.12 по **государственной** ИС (аттестация по Приказу ФСТЭК № 17) — к нам не применимо.
- coderf.ru (комментарий): «Нарушение указанных требований влечет административную ответственность в соответствии с комментируемой частью только в случае,
  если речь идет о государственной информационной системе» — **мнение комментатора, противоречит делу «Сохнута»** (там ИСПДн негосударственной организации).
- Пять решений Г28 (Смоленск 2017, Владикавказ 2017, Краснодар 2019, Сургут, Владивосток 2018) — Exa их не нашёл; `kad.arbitr.ru` 451 (Г20). **Не добыто.**
**Выжимка.** Дело «Сохнута» — единственный найденный случай ч. 6 ст. 13.12 **именно за e-mail без СКЗИ** у негосударственного оператора; его вёл ФСТЭК, и
Лукацкий сам называет его «заказным». Для нас — довод держать канал доставки выписок внутри TLS до собственного сервера в РФ и не объявлять e-mail
каналом сбора без защиты; вывод Г28 «обвинительная практика касается передачи, а не хранения» подтверждён ещё одним случаем.

### Г30.3-П3. Номер опубликования Приказа РКН № 180 — ✅ ДОБЫТО (официальный портал)

`http://publication.pravo.gov.ru/api/Documents?Name=уведомлений&PublishDateSearchType=0&PageSize=100&Index=1&DocumentDateFrom=28.10.2022&DocumentDateTo=28.10.2022` —
`curl -sk --http1.1` **HTTP 200, 2 403 б**. Ответ API:
> `eoNumber: 0001202212150022`, `publishDateShort: 2022-12-15`, «Приказ Федеральной службы по надзору в сфере связи, информационных технологий и массовых
> коммуникаций от 28.10.2022 № 180 "Об утверждении форм уведомлений о на…»
Минюст — 15.12.2022 № 71532 (Контур, КонсультантПлюс-Минюст, Exa). **Реквизит для юрблока:** Приказ РКН от 28.10.2022 № 180, рег. Минюст 15.12.2022 № 71532,
опубл. 15.12.2022, **№ 0001202212150022**. 🔴 Замер канала: поиск портала — JS, но **REST API портала открыт** и отвечает без ключа — пригодно для всех реквизитов.

### Г30.3-П4…П6. Не пробовались в Г30.3

- (П4) «иные организации» в ст. 26 № 395-1 — не пробовалось (бюджет ушёл на П1);
- (П5) MoneyWiz, поведение на битой строке — не пробовалось;
- (П6) толкование «идентификатора» (прим. 4 к ст. 13.11) — не пробовалось повторно (Г28 искал с Exa и не нашёл).

### ИТОГ Г30.3 (pdf_statement_parsing_accuracy)

| Пункт | Был статус | Стал | Приём |
|---|---|---|---|
| Позиция РКН по e-mail / зарубежной почте | «позиции нет», класс 2 (JS) | 🔴 **добыто частично**: письмо РКН 24.03.2025 № 08-134789 (скан) + реквизиты и цитаты писем 08-80104, 08-145976, Упр. ПФО 22002-8/52, 22.01.2026; Минцифры П25-44929, П25-1-05-200-202259 | Exa search → `curl` PDF, `r.jina.ai` вики |
| Решения по ч. 6 ст. 13.12 КоАП | только подборка блогера | **частично**: дело «Сохнута» (ФСТЭК 2021, Омск № 12-696/2021, e-mail без СКЗИ) по блогу; пять решений — нет | Exa, `r.jina.ai` |
| Опубликование Приказа РКН № 180 | номер не найден (поиск портала — JS) | **добыто**: 0001202212150022 от 15.12.2022 | REST API `publication.pravo.gov.ru` |
| «Иные организации» ст. 26 № 395-1 | не проверялось | **не пробовалось** | — |
| MoneyWiz — битая строка | нет | **не пробовалось** | — |
| «Идентификатор» (прим. 4 ст. 13.11) | частично | **не пробовалось** | — |


---

# СВОДНЫЙ ИТОГ ПОДБАТЧА Г30.3 (рынок и право, перепрогон через Exa) — 16.09.2026

**Главное число.** Из пунктов «не добыто / осталось неизвестным», открытых на вход в шести файлах, — **14 закрыты полностью, 7 частично**,
**4 остались недобытыми** с точной причиной (Ozon, MaPS FFT, механика «Финтрекера», новое по Совкомбанку), **9 не пробовались** по бюджету
(Stripe/KYC, MD/NV-628A/UK s. 19/CBUAE, информписьма ЦБ о закредитованных, Toya/Spendify, ст. 26 № 395-1, MoneyWiz, «идентификатор»,
Определение ВС 41-КГ22-23-К4). Сверх списка найдено **3 новых пункта**, которых в очереди не было: немецкий SchuBerDG § 2–4, Т-Банк «Тая» + анонс
«вклад или досрочно погасить», FinGPT Финуслуг. Уже закрытое позже (5809-У, маркетплейсы и 39-ФЗ, Известия, hh.ru, конференции, CoinKeeper/MoneyWiz/Tiller,
Monarch, Дзен-мани) — не переоткрывалось.

| Файл | Полностью | Частично | Нет | Не пробовалось |
|---|---|---|---|---|
| `regulation_rf_investment_advice` | 1 (798-П) | — | — | — |
| `monetization_and_graveyard` | 1 (Приказ № 68) | — | 1 (Ozon) | 1 |
| `regulation_world_advice_boundary` | 2 (UDMSA, CFPB) | 3 (SEC/Champion, CCD II, CT) | — | 2 |
| `banks_russia_pfm_advice` | 8 (Сбер, ВТБ, ГПБ, Райф, «досрочно/вклад», РИФГ, финкультура, МПЛ) | 1 (Альфа) | 1 (Совкомбанк) | 1 |
| `competitors_2026_refresh` | 1 (Economic Record) | 1 (KakaoBank) | 2 (MaPS FFT, «Финтрекер») | 1 |
| `pdf_statement_parsing_accuracy` | 1 (№ 180) | 2 (позиция РКН, ч. 6 ст. 13.12) | — | 3 |

**Ошибка прежних доборов «отказ инструмента = нет источника» — найдена шесть раз:**
1. Г28: «позиции самого РКН нет» — есть письмо РКН 24.03.2025 № 08-134789 (скан) и реквизиты ещё четырёх писем РКН.
2. 08.09: «у ВТБ PFM-модуля нет вообще» — вывод по одной странице; у ВТБ категории, лимиты, цели с ежемесячным взносом.
3. Г24: Economic Record «только через браузер человека» — издательский PDF лежит в репозитории Мельбурна (OpenAlex → DSpace REST).
4. Г28: «номер опубликования № 180 не найти, поиск портала — JS» — REST API `publication.pravo.gov.ru` открыт: 0001202212150022.
5. W&L Law Review: `curl` → 403, **Exa fetch → полный текст** (письма SEC Sinclair-deMarinis, Linda Arnold).
6. Канон каналов «Exa и прокси не пробивают российские банковские сайты» — неверен для ВТБ и ГПБ (`r.jina.ai` 200); верен для Сбера (WAF `user_blocked`) и Альфы.
Обратные случаи (отказ подтверждён на всех каналах): Ozon (Exa 307, прокси без UA 403, CDX 503); Wiley для Exa (`CRAWL_UNKNOWN_ERROR`); ILGA для `curl` (000) — взято Exa.

**🔴 Что из добытого меняет красную линию, юрблок или конкурентный вывод**

*Юрблок (L9, выход за рубеж):*
- 🔴 **Германия — SchuBerDG § 4:** «Schuldnerberatungsdienste nach § 2 darf nur erbringen, wer unabhängiger professioneller Anbieter ist»; § 2 по обоснованию
  покрывает «анализ финансового положения и рекомендации по обращению с обязательствами»; § 3 — бесплатно или по себестоимости без прибыли. Закон принят
  Бундестагом, Бундесрат отказал 08.05.2026, Vermittlungsausschuss без даты. Если вступит — коммерческий долговой модуль для потребителей в DE под вопросом
  по существу, а не по лицензии. Это сильнее вывода Г28 (§ 34k GewO не нужен).
- 🔴 **США — Невада, NRS 676A.140/110:** «debt-management services … includes credit counseling», а credit counseling = «education and assistance … concerning
  debts owed» — возможен захват нашего долгового модуля с регистрацией; изъятие «no compensation» платной подписке недоступно. Невада теперь проблемна
  по двум главам (628A + 676A). Модельный UDMSA (UT, CO, DE, RI, TN, VI) и Иллинойс — **не ловят** (комментарий ULC: «does not include services that consist
  solely of counseling or education concerning the management of personal finance»; IL — нужен приём денег должника, а «credit counselor» выведен прямо).
- CFPB: рынка credit counseling среди larger participants нет — планового надзора не будет; UDAAP (Г27) остаётся.
- ЕС: официальных толкований Art. 3(17) нет и по конструкции CCD не ожидается; Ирландия использует дерогацию 16(6) только для юристов/бухгалтеров/PIP/MABS.

*Юрблок (РФ):*
- 🔴 **Канал приёма выписок:** письмо РКН 08-80104 (по вторичному) — ПДн из сообщений через мессенджеры Перечня (Telegram, WhatsApp и др.) «не должны приниматься
  в обработку и должны быть уничтожены». В требования: **не принимать выписки через иностранные мессенджеры**; почтовый приём — только на сервер в РФ
  (теперь с опорой на письмо РКН 08-134789, а не только на толкование).
- Реквизиты для юрблока: Приказ РКН № 68 (Минюст 14.04.2025 № 81842, в силе с 25.04.2025); Приказ РКН № 180 (опубл. 0001202212150022); 798-П в ред. 17.06.2024.
- МПЛ IV кв. 2026 (решение ЦБ 24.07.2026) — наш инвариант ПДН ≤ 0,40 строже любых порогов МПЛ; менять нечего.

*Красная линия (граница «совета»):*
- США, штаб SEC: Champion (1986 WL 68317) — совет о не-ценных бумагах не есть совет о securities; но Linda Arnold (1984) — **даже категории** инвестиций
  («облигации, фонды») в контексте финплана могут сделать советником. В словарь продукта: не называть категорий инструментов в выдаче. Media General (1992):
  критерии выбирает пользователь — не совет; подтверждает разграничитель «вход задаёт пользователь».
- РФ: формулировки FinGPT («не являются индивидуальной рекомендацией», «может ошибаться») — ещё один рыночный образец к Г29; наш зазор по-прежнему держится
  на отсутствии инструментов в выдаче, а не на дисклеймере.

*Конкурентный вывод:*
- 🔴 **Т-Банк публично назвал нашу задачу своей целью** (11.2024: «приложение подскажет, что выгоднее: положить деньги на вклад или досрочно погасить кредит»);
  запуска не найдено; 09.09.2026 — бета ИИ-ассистента «Тая», открытого не-клиентам, с планом «учитывать доходы и кредитную нагрузку». Ближайший российский
  кандидат на пересечение.
- Сбер «Финансовое здоровье» живо (≤03.2025): 4 сферы, 0–100, когорта, советы — продуктово-налоговые; ВТБ — цели с расчётом ежемесячного взноса;
  FinGPT Мосбиржи — бесплатный LLM, «помогает с распределением активов» и «подбирает вклады и кредиты».
- **Зазор FINPILOT по объекту устоял** (долг + резерв + цели одной свёрткой с ранжированием альтернатив — ни у кого), **но окно сужается**: два
  инфраструктурных игрока (Т-Банк, Мосбиржа) идут в LLM-советники, и один из них прямо целится в «вклад vs досрочное погашение».

*Наука о метрике:* Economic Record 2022 (журнальная версия) подтвердил поправку Г7 к Б.3 `bank_patents_wellness_scoring`: ρ = 0,46; 100/19; α 0,92/0,85.

**Процесс — прозрачно.** Тип запроса: breadth-first (шесть файлов, ~35 независимых пунктов). Субагентов — **ноль** (поручение допускало до двух; пункты —
добыча дословных текстов, а правило «писать после каждого пункта» проще держать без передачи контекста). `WebSearch` — 0. Exa `web_search_exa` — 31,
`web_fetch_exa` — 4 (1 полный текст W&L, 1 полный акт ILGA, 2 отказа: Ozon 307, Wiley `CRAWL_UNKNOWN_ERROR`). Остальное — `curl` прямой, `r.jina.ai` без UA,
OpenAlex, DSpace REST, API `publication.pravo.gov.ru`, `pdftotext`. Записей в файлы — 12 дописываний по ходу, до итогового ответа. Канон модели, формулировка
новизны и код продукта не тронуты.


## ДОБОР Г30.3 — второй заход (16.09.2026)

**Каналы:** Exa — 🟢; `r.jina.ai` без UA — 200; Crossref — 200; 🔴 `rkn.gov.ru` — **000** (не отвечает), `pd.rkn.gov.ru` — **403**;
Wayback CDX — **503**; OpenAlex — 429; `publication.pravo.gov.ru/api/Documents` — 200.

### Г30.3-П7. 🔴 Письмо РКН от 13.09.2023 № 08-80104 — ПЕРВОИСТОЧНИК НЕ ДОБЫТ; перечень каналов и что найдено вместо

Пройденные каналы (все — сегодня):
1. Exa-поиск по точному номеру «"08-80104" Роскомнадзор письмо 13.09.2023» — релевантных результатов **ноль** (выдача ушла в посторонние документы с той же цифрой);
2. **Реестр писем РКН на `pravo.ppt.ru/pismo/roskomnadzor`** (`mcp__exa__web_fetch_exa`, полный список за 2019–2026 гг.): письма 08ВМ-63651 (27.07.2023),
   08ВМ-59834 (14.07.2023), 09-6488, 08-85394, 08-80975 и др. — **письма 08-80104 в реестре нет**;
3. `rkn.gov.ru` — соединение **000**, `pd.rkn.gov.ru` — **403** (совпадает с замером Г28);
4. API `publication.pravo.gov.ru` — по конструкции публикует **нормативные акты**, а письмо-разъяснение туда не попадает (проверено на смежном запросе: поиск по
   наименованию даёт приказы, не письма);
5. Wayback — **503**.
**Вывод:** письмо 08-80104 — индивидуальное разъяснение по обращению; в открытые базы оно, судя по реестру, не выкладывалось, и **дословный текст доступен только
в цитате консультанта** (bizstrategii.ru, приведена в первом заходе). 🔴 Требование продукта «не принимать выписки через иностранные мессенджеры» **нельзя опирать
на это письмо как на первоисточник**. Но оно и не нужно: та же позиция есть в первоисточниках, добытых в первом заходе, —
письмо **Минцифры от 28.06.2023 № П25-1-05-200-202259** (ГАРАНТ): «персональные данные российских граждан, направленные ими в адрес организаций посредством
иностранных мессенджеров, указанных в перечне Роскомнадзора … **не должны приниматься в обработку и должны быть уничтожены организацией**»,
и письмо **РКН от 27.07.2023 № 08ВМ-63651** (в реестре писем РКН, текст на pravo.ppt.ru): «при передаче персональных данных и информации, необходимой для
осуществления безналичных переводов и платежей, … **рекомендуется использовать отечественные мессенджеры**». Требование продукта переоформить на эти два реквизита.

### Г30.3-П8. Статья 26 № 395-1, «иные организации» применительно к небанковскому получателю выписки — ❌ НЕ ДОБЫТО

Каналы: Exa-поиск (1 целевой запрос) — выдача ушла в дела о банковской тайне между банком и клиентом (17ААС № А60-40278/2023 и т. п.), в определения КС о
исполнительном производстве и в маркетинговые страницы; `kad.arbitr.ru` — **451** (замер Г20, не повторялся). Практики именно по ситуации «клиент сам передал
свою выписку третьему лицу» не найдено. Оценка: вопрос, вероятно, не возникает в судах, потому что банковскую тайну обязан хранить **банк**, а не получатель
документа от самого клиента; но это рассуждение, а не источник, и так и записано.

### Г30.3-П9. MoneyWiz: поведение при нераспознанной строке — ЧАСТИЧНО (по справке разработчика)

Первоисточник — `help.wiz.money` (статьи 4440549 «How do I format CSV file before importing?», 4440666 «How to import a CSV, QIF, OFX, QFX or MT940 file…»,
4440586 «…transaction code column», тексты из индекса Exa). Дословно:
> «**If MoneyWiz cannot guess what the column contains, it'll default to “Don't import”.** You can click on that button to instruct MoneyWiz what the column is.»
> «MoneyWiz recognizes many date formats but sometimes it might need some help… If MoneyWiz cannot figure out the date format without your help, **it'll show you
> a couple of transactions and ask you to select the correct date format** used throughout the file.»
> «An important rule is not to include time in the same column as the date – it's the single most common reason why date format is not recognised.
> **MoneyWiz cannot parse the date if time is stored in the same column.**»
> «MoneyWiz checks all transactions you wish to import against already existing transactions and in case it finds possible duplicates **it will ask you what to do**.»
**Ответ:** у MoneyWiz проблема решается **на уровне колонки и формата, а не строки**: неопознанная колонка → «Don't import», неоднозначная дата → вопрос пользователю,
дубли → вопрос пользователю. Отдельного описания «что происходит с одной битой строкой внутри корректного файла» в справке **нет** (просмотрены разделы Importing
и Troubleshooting). Вывод Г24 не меняется: молчаливого отбрасывания нет, решение всегда за человеком. Для нас — подтверждение требования: при нераспознанной строке
показывать её пользователю, а не глотать.


---

# СВОДНЫЙ ИТОГ ПОДБАТЧА Г30.3 — ОБНОВЛЁН ПОСЛЕ ВТОРОГО ЗАХОДА (16.09.2026)

**Главное число (пересчитано).** За два захода: **закрыто полностью — 22 пункта**, **частично — 8**, **не добыто с точной причиной — 6**,
**не пробовано — 0**. Сверх очереди найдено **6 новых пунктов**, которых в ней не было (SchuBerDG; Т-Банк «Тая» и анонс «вклад vs досрочное погашение»;
FinGPT Финуслуг; замена закона ОАЭ на DFL 6/2025; дело FCA против компании из фризоны ОАЭ; MCP-сервер Spendify).
Второй заход добавил к первому: **+8 закрытых полностью** (Мэриленд-практика, UK-территориальность, ОАЭ DFL 6/2025, CT-кодификация, письма ЦБ,
Определение ВС 41-КГ22-23-К4, Toya/Spendify, MoneyWiz), **+3 доказанных отрицательных результата** (перечень ULC, письмо РКН 08-80104, ст. 26 № 395-1)
и снял формулировку «не пробовал» полностью.

| Файл | Полностью | Частично | Не добыто (причина) |
|---|---|---|---|
| `regulation_rf_investment_advice` | 1 | — | — |
| `monetization_and_graveyard` | 2 (№ 68; Определение ВС) | — | 1 (Ozon) |
| `regulation_world_advice_boundary` | 6 (UDMSA-состав, CFPB, MD-практика, UK s. 19, ОАЭ DFL 6/2025, CT) | 3 (SEC/Champion, CCD II, Stripe) | 1 (перечень принятий ULC) |
| `banks_russia_pfm_advice` | 9 | 1 (Альфа) | 1 (Совкомбанк — новых фактов нет) |
| `competitors_2026_refresh` | 2 (Economic Record, Toya/Spendify) | 1 (KakaoBank) | 2 (MaPS FFT, «Финтрекер») |
| `pdf_statement_parsing_accuracy` | 2 (№ 180, MoneyWiz-поведение) | 3 (позиция РКН, ч. 6 ст. 13.12, «идентификатор») | 1 (ст. 26 № 395-1) |

**Ошибка «отказ инструмента = нет источника» — итог за два захода: найдена восемь раз.** К шести из первого захода добавились:
(7) «UK s. 19 — практики нет» — практика есть и свежая: FCA против **зарегистрированной в ОАЭ** подписочной платформы (08.06.2026);
(8) «ОАЭ — DFL 14/2018» — закон **заменён** на DFL 6/2025 ещё 16.09.2025, а файл ссылался на старый.
Обратные случаи (отказ подтверждён на всех каналах): страница статуса ULC (HigherLogic-скрипт + Wayback 503), письмо РКН 08-80104 (нет в реестре писем РКН),
Ozon, MaPS (`CRAWL_NOT_FOUND`), ст. 26 № 395-1, Champion (Westlaw).

**🔴 Что из добытого во втором заходе меняет юрблок и красную линию**
1. **UK — самое важное.** Первоисточник FCA (08.06.2026): иск по **ss. 19 и 21 FSMA** против Neil Woodford и **W Four Point Zero FZE LLC (ОАЭ)** за
   подписочную платформу без авторизации. Регистрация вне UK не защищает; по сопутствующему делу HTX критерий для промоушена — «**capable of having an effect
   in the UK**», без доказывания таргетинга. Для L9: по UK работает только фактический геоблок и отказ от британских атрибутов (язык, валюта, ID).
2. **ОАЭ — обновить реквизит.** Действует **Federal Decree-Law No. (6) of 2025** (в силе 16.09.2025), ст. 61 — перечень лицензируемой деятельности,
   совета/консультирования в нём нет (вывод Г21 сохраняется), ст. 60(2) — «in or from within the State», ст. 60(3) — отдельный запрет промоушена.
   🟠 Новое ограничение вывода: «финансовые консультации» в ОАЭ лицензирует **SCA** (категория «Arrangement and advice», активность «Financial Consultations»),
   и этот режим дословно не сверен — `uaelegislation.gov.ae` отдаёт 403 и капчу.
3. **США, Мэриленд — риск снижен.** Функциональная ветка § 11-101(i)(1)(ii)2 в четырёх актах Securities Commissioner **никогда не была единственным основанием**:
   всегда был титул или совет по конкретным бумагам. Статус «вероятно ловит» → «не подтверждено практикой».
4. **США, UDMSA — состав подтверждён первоисточниками штатов** (UT, CO, DE, NV, RI, TN, VI); Висконсин, Гавайи и Миссури вносили, но не приняли;
   Северная Дакота приняла **другой** закон (debt-settlement). Принятия после 2010 г. остаются непроверенными — статус ULC отдаётся скриптом.
5. **РФ, канал приёма выписок — основание переоформлено.** Письмо РКН 08-80104 первоисточником не подтверждается (его нет в реестре писем РКН), поэтому
   требование «не принимать выписки через иностранные мессенджеры» опирается теперь на **письмо Минцифры от 28.06.2023 № П25-1-05-200-202259**
   («не должны приниматься в обработку и должны быть уничтожены организацией») и **письмо РКН от 27.07.2023 № 08ВМ-63651** (рекомендация отечественных мессенджеров).
6. **РФ, оферта.** Определение ВС от 23.08.2022 № 41-КГ22-23-К4 добыто дословно: возврат за неиспользованный период абонентского договора, бремя доказывания
   расходов — на исполнителе. Практический вывод: **помесячная тарификация безопаснее годовой предоплаты**.
7. **Конкуренты.** Toya AI прямо заявляет «**Not just snowball or avalanche**» и оптимизацию порядка погашения по реальным данным — ближайший по методу к нашему
   долговому блоку, но без резерва и целей; Spendify отдаёт свои данные наружу через **MCP с правом записи**. Зазор FINPILOT по объекту (долг + резерв + цели
   одной свёрткой) устоял и во втором заходе.

**Процесс второго захода.** Субагентов — 0. `WebSearch` — 0. Exa `web_search_exa` — 12, `web_fetch_exa` — 3 (ULC + реестр писем РКН — успешно; MaPS — два отказа).
Прочее: прямой `curl -sk --http1.1`, `r.jina.ai` без UA, `publication.pravo.gov.ru` API, `pdftotext`. Записей — 8 дописываний по ходу.
Предыдущая попытка второго захода оборвалась на лимите аккаунта (429) до первой записи; здесь всё выполнено заново. Канон модели, формулировка новизны
и код продукта не тронуты.


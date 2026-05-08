"""
All UI labels and code translations.
NEVER translate raw data — always render codes through this dictionary.
"""

from enums import (
    Language, ShiftType, StructureType, NaturaStatus,
    RebarStatus, RebarDefect, ConcretePlan, ConcreteAvailable,
    ReadinessStatus, PourMethod, PumpType, PumpLogistics
)

# ──────────────────────────────────────────────
# UI LABELS
# ──────────────────────────────────────────────

UI: dict[str, dict[str, str]] = {
    # ── SYSTEM ──
    "welcome": {
        "ru": "👷 Добро пожаловать!\nВыберите язык:",
        "uz": "👷 Xush kelibsiz!\nTilni tanlang:",
        "en": "👷 Welcome!\nChoose your language:",
        "tr": "👷 Hoş geldiniz!\nDil seçin:",
    },
    "lang_saved": {
        "ru": "✅ Язык сохранён. Выберите проект:",
        "uz": "✅ Til saqlandi. Loyihani tanlang:",
        "en": "✅ Language saved. Select project:",
        "tr": "✅ Dil kaydedildi. Proje seçin:",
    },
    "btn_change_lang": {
        "ru": "🌐 Сменить язык",
        "uz": "🌐 Tilni o'zgartirish",
        "en": "🌐 Change language",
        "tr": "🌐 Dili değiştir",
    },

    # ── PROJECT ──
    "select_project": {
        "ru": "📁 Выберите объект:",
        "uz": "📁 Ob'ektni tanlang:",
        "en": "📁 Select project:",
        "tr": "📁 Proje seçin:",
    },
    "select_subproject": {
        "ru": "📂 Выберите подобъект / блок:",
        "uz": "📂 Kichik ob'ekt / blokni tanlang:",
        "en": "📂 Select sub-project / block:",
        "tr": "📂 Alt proje / blok seçin:",
    },
    "no_projects": {
        "ru": "⚠️ Проекты не настроены. Обратитесь к администратору.",
        "uz": "⚠️ Loyihalar sozlanmagan. Admin bilan bog'laning.",
        "en": "⚠️ No projects configured. Contact administrator.",
        "tr": "⚠️ Proje yapılandırılmamış. Yönetici ile iletişime geçin.",
    },

    # ── SHIFT ──
    "select_shift": {
        "ru": "🕐 Выберите тип смены:",
        "uz": "🕐 Navbat turini tanlang:",
        "en": "🕐 Select shift type:",
        "tr": "🕐 Vardiya türünü seçin:",
    },
    "shift_started": {
        "ru": "✅ Смена открыта.\nДобавьте первую конструкцию:",
        "uz": "✅ Navbat ochildi.\nBirinchi konstruktsiyani qo'shing:",
        "en": "✅ Shift started.\nAdd the first structure:",
        "tr": "✅ Vardiya başladı.\nİlk yapıyı ekleyin:",
    },
    "btn_add_structure": {
        "ru": "➕ Добавить конструкцию",
        "uz": "➕ Konstruktsiya qo'shish",
        "en": "➕ Add structure",
        "tr": "➕ Yapı ekle",
    },
    "btn_finish_shift": {
        "ru": "✅ Завершить смену",
        "uz": "✅ Navbatni tugatish",
        "en": "✅ Finish shift",
        "tr": "✅ Vardiyayı bitir",
    },
    "btn_repeat_last": {
        "ru": "🔄 Как вчера",
        "uz": "🔄 Kechadek",
        "en": "🔄 Same as yesterday",
        "tr": "🔄 Dünkü gibi",
    },
    "shift_finished": {
        "ru": "📋 Смена завершена. Генерирую отчёт...",
        "uz": "📋 Navbat tugadi. Hisobot tayyorlanmoqda...",
        "en": "📋 Shift finished. Generating report...",
        "tr": "📋 Vardiya bitti. Rapor oluşturuluyor...",
    },
    "no_entries": {
        "ru": "⚠️ Нет записей. Добавьте хотя бы одну конструкцию.",
        "uz": "⚠️ Yozuvlar yo'q. Kamida bitta konstruktsiya qo'shing.",
        "en": "⚠️ No entries. Add at least one structure.",
        "tr": "⚠️ Kayıt yok. En az bir yapı ekleyin.",
    },

    # ── STRUCTURE ──
    "select_structure_type": {
        "ru": "🏗 Выберите тип конструкции:",
        "uz": "🏗 Konstruktsiya turini tanlang:",
        "en": "🏗 Select structure type:",
        "tr": "🏗 Yapı türünü seçin:",
    },
    "enter_structure_name": {
        "ru": "✏️ Введите название / маркировку конструкции\n(например: К-1, Ос А-Б, Ст-14):",
        "uz": "✏️ Konstruktsiya nomini kiriting\n(masalan: K-1, A-B o'qi, Devol-14):",
        "en": "✏️ Enter structure name / mark\n(e.g. C-1, Axis A-B, W-14):",
        "tr": "✏️ Yapı adı / işareti girin\n(örn. K-1, A-B ekseni, D-14):",
    },

    # ── NATURA ──
    "select_natura": {
        "ru": "📋 НАТУРА (разрешение на работу):",
        "uz": "📋 NATURA (ish ruxsati):",
        "en": "📋 PERMIT TO WORK (natura):",
        "tr": "📋 ÇALIŞMA İZNİ (natura):",
    },
    "warn_natura_not_given": {
        "ru": "⚠️ ВНИМАНИЕ: Натура не дана! Заливка ЗАПРЕЩЕНА.",
        "uz": "⚠️ DIQQAT: Natura berilmagan! Quyish TAQIQLANGAN.",
        "en": "⚠️ WARNING: Permit not issued! Pouring is FORBIDDEN.",
        "tr": "⚠️ UYARI: İzin verilmedi! Döküm YASAK.",
    },
    "warn_natura_night": {
        "ru": "⚠️ Натура будет дана ночью. Заливка возможна только после выдачи.",
        "uz": "⚠️ Natura kechasi beriladi. Quyish faqat berilgandan keyin mumkin.",
        "en": "⚠️ Permit will be issued at night. Pouring only after issuance.",
        "tr": "⚠️ İzin gece verilecek. Döküm yalnızca sonrasında yapılabilir.",
    },

    # ── REBAR ──
    "select_rebar_status": {
        "ru": "🔩 Статус АРМАТУРЫ:",
        "uz": "🔩 ARMATURA holati:",
        "en": "🔩 REBAR status:",
        "tr": "🔩 DONATI durumu:",
    },
    "select_rebar_defects": {
        "ru": "⚠️ Выберите дефекты арматуры (можно несколько):\nНажмите ✅ когда закончите.",
        "uz": "⚠️ Armatura nuqsonlarini tanlang (bir nechtasi mumkin):\n✅ tugmani bosing.",
        "en": "⚠️ Select rebar defects (multiple allowed):\nPress ✅ when done.",
        "tr": "⚠️ Donatı kusurlarını seçin (birden fazla olabilir):\n✅ tıklayın.",
    },
    "btn_defects_done": {
        "ru": "✅ Дефекты выбраны",
        "uz": "✅ Nuqsonlar tanlandi",
        "en": "✅ Defects selected",
        "tr": "✅ Kusurlar seçildi",
    },
    "enter_rebar_comment": {
        "ru": "💬 Доп. комментарий по арматуре (или /skip):",
        "uz": "💬 Armatura bo'yicha qo'shimcha izoh (yoki /skip):",
        "en": "💬 Additional rebar comment (or /skip):",
        "tr": "💬 Ek donatı yorumu (veya /skip):",
    },
    "error_rebar_blocks_pour": {
        "ru": "🚫 Заливка невозможна: арматура не сдана!",
        "uz": "🚫 Quyish mumkin emas: armatura topshirilmagan!",
        "en": "🚫 Pouring blocked: rebar not accepted!",
        "tr": "🚫 Döküm engellidir: donatı teslim edilmedi!",
    },

    # ── CONCRETE ──
    "select_concrete_plan": {
        "ru": "🪣 Планируется ли ЗАЛИВКА БЕТОНА?",
        "uz": "🪣 BETON QUYISH rejalashtirilganmi?",
        "en": "🪣 Is CONCRETE POURING planned?",
        "tr": "🪣 BETON DÖKÜMÜ planlanıyor mu?",
    },
    "check_concrete_available": {
        "ru": "🚛 Бетон заказан / будет на объекте?",
        "uz": "🚛 Beton buyurtma qilinganmi / ob'ektda bo'ladimi?",
        "en": "🚛 Is concrete ordered / available on site?",
        "tr": "🚛 Beton sipariş edildi mi / sahada mevcut mu?",
    },
    "warn_no_concrete": {
        "ru": "🔴 КРИТИЧНО: Бетон отсутствует! Заливка невозможна.",
        "uz": "🔴 MUHIM: Beton yo'q! Quyish mumkin emas.",
        "en": "🔴 CRITICAL: No concrete available! Pouring impossible.",
        "tr": "🔴 KRİTİK: Beton yok! Döküm imkânsız.",
    },
    "check_formwork": {
        "ru": "🔲 Опалубка готова?",
        "uz": "🔲 Qolip tayyor?",
        "en": "🔲 Formwork ready?",
        "tr": "🔲 Kalıp hazır mı?",
    },
    "check_waterproof": {
        "ru": "💧 Гидроизоляция готова?",
        "uz": "💧 Gidroizolyatsiya tayyor?",
        "en": "💧 Waterproofing ready?",
        "tr": "💧 Su yalıtımı hazır mı?",
    },
    "check_rebar_for_pour": {
        "ru": "🔩 Арматура готова к заливке?",
        "uz": "🔩 Armatura quyishga tayyor?",
        "en": "🔩 Rebar ready for pour?",
        "tr": "🔩 Donatı dökmeye hazır mı?",
    },
    "enter_concrete_volume": {
        "ru": "📐 Введите объём бетона (м³):\nПример: 12.5",
        "uz": "📐 Beton hajmini kiriting (m³):\nMasalan: 12.5",
        "en": "📐 Enter concrete volume (m³):\nExample: 12.5",
        "tr": "📐 Beton hacmini girin (m³):\nÖrnek: 12.5",
    },
    "invalid_volume": {
        "ru": "❌ Некорректный объём. Введите число, например: 12.5",
        "uz": "❌ Noto'g'ri hajm. Raqam kiriting, masalan: 12.5",
        "en": "❌ Invalid volume. Enter a number e.g. 12.5",
        "tr": "❌ Geçersiz hacim. Sayı girin örn. 12.5",
    },

    # ── PUMP ──
    "select_pour_method": {
        "ru": "🏗 Способ подачи бетона:",
        "uz": "🏗 Beton uzatish usuli:",
        "en": "🏗 Concrete delivery method:",
        "tr": "🏗 Beton iletim yöntemi:",
    },
    "select_pump_type": {
        "ru": "⚙️ Тип насоса:",
        "uz": "⚙️ Nasos turi:",
        "en": "⚙️ Pump type:",
        "tr": "⚙️ Pompa tipi:",
    },
    "select_pump_logistics": {
        "ru": "🔧 Логистика насоса — требуются работы?",
        "uz": "🔧 Nasos logistikasi — ishlar talab qilinadimi?",
        "en": "🔧 Pump logistics — any work required?",
        "tr": "🔧 Pompa lojistiği — çalışma gerekiyor mu?",
    },

    # ── ENTRY FLOW ──
    "entry_saved": {
        "ru": "✅ Конструкция сохранена!\n\nЧто дальше?",
        "uz": "✅ Konstruktsiya saqlandi!\n\nKeyingi qadam?",
        "en": "✅ Structure saved!\n\nWhat's next?",
        "tr": "✅ Yapı kaydedildi!\n\nSonraki adım?",
    },
    "btn_yes": {
        "ru": "✅ Да",
        "uz": "✅ Ha",
        "en": "✅ Yes",
        "tr": "✅ Evet",
    },
    "btn_no": {
        "ru": "❌ Нет",
        "uz": "❌ Yo'q",
        "en": "❌ No",
        "tr": "❌ Hayır",
    },
    "btn_skip": {
        "ru": "⏭ Пропустить",
        "uz": "⏭ O'tkazib yuborish",
        "en": "⏭ Skip",
        "tr": "⏭ Atla",
    },
    "btn_back": {
        "ru": "◀️ Назад",
        "uz": "◀️ Orqaga",
        "en": "◀️ Back",
        "tr": "◀️ Geri",
    },

    # ── REPORT ──
    "report_header": {
        "ru": "📋 ОТЧЁТ О ПЕРЕДАЧЕ СМЕНЫ",
        "uz": "📋 NAVBAT TOPSHIRISH HISOBOTI",
        "en": "📋 SHIFT HANDOVER REPORT",
        "tr": "📋 VARDİYA DEVIR RAPORU",
    },
    "report_no_entries": {
        "ru": "Нет записей",
        "uz": "Yozuvlar yo'q",
        "en": "No entries",
        "tr": "Kayıt yok",
    },
}

# ──────────────────────────────────────────────
# CODE → LABEL DICTIONARIES
# ──────────────────────────────────────────────

SHIFT_TYPE_LABELS: dict[str, dict[str, str]] = {
    ShiftType.DAY: {
        "ru": "🌅 День", "uz": "🌅 Kun", "en": "🌅 Day", "tr": "🌅 Gündüz"
    },
    ShiftType.NIGHT: {
        "ru": "🌙 Ночь", "uz": "🌙 Kecha", "en": "🌙 Night", "tr": "🌙 Gece"
    },
}

STRUCTURE_TYPE_LABELS: dict[str, dict[str, str]] = {
    StructureType.COLUMN: {
        "ru": "🏛 Колонна", "uz": "🏛 Ustun", "en": "🏛 Column", "tr": "🏛 Kolon"
    },
    StructureType.WALL: {
        "ru": "🧱 Стена", "uz": "🧱 Devor", "en": "🧱 Wall", "tr": "🧱 Duvar"
    },
    StructureType.SLAB: {
        "ru": "⬛ Перекрытие", "uz": "⬛ Tom yopma", "en": "⬛ Slab", "tr": "⬛ Döşeme"
    },
    StructureType.BEAM: {
        "ru": "📐 Балка", "uz": "📐 Balkа", "en": "📐 Beam", "tr": "📐 Kiriş"
    },
    StructureType.FOUNDATION: {
        "ru": "🪨 Фундамент", "uz": "🪨 Poydevor", "en": "🪨 Foundation", "tr": "🪨 Temel"
    },
}

NATURA_LABELS: dict[str, dict[str, str]] = {
    NaturaStatus.GIVEN: {
        "ru": "✅ Дана", "uz": "✅ Berilgan", "en": "✅ Issued", "tr": "✅ Verildi"
    },
    NaturaStatus.NOT_GIVEN: {
        "ru": "🚫 Не дана", "uz": "🚫 Berilmagan", "en": "🚫 Not issued", "tr": "🚫 Verilmedi"
    },
    NaturaStatus.WILL_BE_NIGHT: {
        "ru": "⚠️ Будет ночью", "uz": "⚠️ Kechasi beriladi", "en": "⚠️ Will be at night", "tr": "⚠️ Gece verilecek"
    },
}

REBAR_STATUS_LABELS: dict[str, dict[str, str]] = {
    RebarStatus.ACCEPTED: {
        "ru": "✅ Сдана", "uz": "✅ Topshirildi", "en": "✅ Accepted", "tr": "✅ Teslim edildi"
    },
    RebarStatus.PARTIAL: {
        "ru": "⚠️ Частично", "uz": "⚠️ Qisman", "en": "⚠️ Partial", "tr": "⚠️ Kısmen"
    },
    RebarStatus.NOT_ACCEPTED: {
        "ru": "🚫 Не сдана", "uz": "🚫 Topshirilmagan", "en": "🚫 Not accepted", "tr": "🚫 Teslim edilmedi"
    },
}

DEFECT_LABELS: dict[str, dict[str, str]] = {
    RebarDefect.NO_COVER: {
        "ru": "Нет защитного слоя", "uz": "Himoya qatlami yo'q",
        "en": "No concrete cover", "tr": "Pas payı yok"
    },
    RebarDefect.MISSING_TIES: {
        "ru": "Нехватка хомутов", "uz": "Xomutlar yetishmaydi",
        "en": "Missing stirrups", "tr": "Etriye eksik"
    },
    RebarDefect.MISSING_BOLTS: {
        "ru": "Нехватка шпилек", "uz": "Shpilkalar yetishmaydi",
        "en": "Missing bolts/studs", "tr": "Civata eksik"
    },
    RebarDefect.WRONG_SPACING: {
        "ru": "Нарушение шага", "uz": "Qadam buzilgan",
        "en": "Wrong bar spacing", "tr": "Aralık hatası"
    },
    RebarDefect.FRAME_SHIFT: {
        "ru": "Смещение каркаса", "uz": "Karkasning siljishi",
        "en": "Frame displacement", "tr": "Kafes kayması"
    },
    RebarDefect.BINDING_INCOMPLETE: {
        "ru": "Не завершена вязка", "uz": "Bog'lash tugallanmagan",
        "en": "Binding incomplete", "tr": "Bağlama tamamlanmadı"
    },
    RebarDefect.GEODESY_NOT_READY: {
        "ru": "Не готова геодезия", "uz": "Geodeziya tayyor emas",
        "en": "Geodesy not ready", "tr": "Jeodezi hazır değil"
    },
    RebarDefect.NO_CLEANING: {
        "ru": "Нет очистки (оттирки)", "uz": "Tozalash yo'q",
        "en": "No cleaning done", "tr": "Temizleme yapılmadı"
    },
    RebarDefect.CUSTOM: {
        "ru": "✏️ Свой дефект", "uz": "✏️ Boshqa nuqson",
        "en": "✏️ Custom defect", "tr": "✏️ Özel kusur"
    },
}

POUR_METHOD_LABELS: dict[str, dict[str, str]] = {
    PourMethod.STATIONARY_PUMP: {
        "ru": "🏗 Стационарный насос", "uz": "🏗 Statsionar nasos",
        "en": "🏗 Stationary pump", "tr": "🏗 Sabit pompa"
    },
    PourMethod.MOBILE_PUMP: {
        "ru": "🚛 Мобильный насос", "uz": "🚛 Mobil nasos",
        "en": "🚛 Mobile pump", "tr": "🚛 Mobil pompa"
    },
    PourMethod.MANUAL: {
        "ru": "👷 Вручную / кранами", "uz": "👷 Qo'lda / kranlar",
        "en": "👷 Manual / cranes", "tr": "👷 Elle / vinçler"
    },
    PourMethod.NOT_APPLICABLE: {
        "ru": "➖ Не применимо", "uz": "➖ Qo'llanilmaydi",
        "en": "➖ Not applicable", "tr": "➖ Geçerli değil"
    },
}

PUMP_TYPE_LABELS: dict[str, dict[str, str]] = {
    PumpType.SPIDER_32_4: {
        "ru": "Spider 32+4", "uz": "Spider 32+4", "en": "Spider 32+4", "tr": "Spider 32+4"
    },
    PumpType.PUMP_20_4: {
        "ru": "Насос 20+4", "uz": "Nasos 20+4", "en": "Pump 20+4", "tr": "Pompa 20+4"
    },
    PumpType.OTHER: {
        "ru": "Другой насос", "uz": "Boshqa nasos", "en": "Other pump", "tr": "Diğer pompa"
    },
}

PUMP_LOGISTICS_LABELS: dict[str, dict[str, str]] = {
    PumpLogistics.ASSEMBLY: {
        "ru": "🔧 Монтаж", "uz": "🔧 Montaj", "en": "🔧 Assembly", "tr": "🔧 Montaj"
    },
    PumpLogistics.RELOCATION: {
        "ru": "🔄 Перестановка", "uz": "🔄 Ko'chirish", "en": "🔄 Relocation", "tr": "🔄 Yeniden konumlandırma"
    },
    PumpLogistics.BOTH: {
        "ru": "🔧🔄 Монтаж + Перестановка", "uz": "🔧🔄 Montaj + Ko'chirish",
        "en": "🔧🔄 Assembly + Relocation", "tr": "🔧🔄 Montaj + Yeniden konumlandırma"
    },
    PumpLogistics.NONE: {
        "ru": "➖ Не требуется", "uz": "➖ Talab qilinmaydi",
        "en": "➖ Not required", "tr": "➖ Gerekmiyor"
    },
}

READINESS_LABELS: dict[str, dict[str, str]] = {
    ReadinessStatus.READY: {
        "ru": "✅ Готово", "uz": "✅ Tayyor", "en": "✅ Ready", "tr": "✅ Hazır"
    },
    ReadinessStatus.NOT_READY: {
        "ru": "❌ Не готово", "uz": "❌ Tayyor emas", "en": "❌ Not ready", "tr": "❌ Hazır değil"
    },
}


def t(key: str, lang: str) -> str:
    """Get UI translation. Falls back to RU."""
    return UI.get(key, {}).get(lang, UI.get(key, {}).get("ru", key))


def label(dictionary: dict, code: str, lang: str) -> str:
    """Translate a code using a given label dictionary."""
    return dictionary.get(code, {}).get(lang, code)

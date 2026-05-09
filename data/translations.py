"""
All UI strings in 4 languages.
Data codes are translated via DB lookup — never hardcoded here.
"""

UI: dict[str, dict[str, str]] = {

    # ── LANGUAGE ──
    "welcome": {
        "ru": "👷‍♂️ *HANDOVER BOT*\nСистема передачи смены\n\nВыберите язык:",
        "uz": "👷‍♂️ *HANDOVER BOT*\nNavbat topshirish tizimi\n\nTilni tanlang:",
        "en": "👷‍♂️ *HANDOVER BOT*\nShift handover system\n\nSelect language:",
        "tr": "👷‍♂️ *HANDOVER BOT*\nVardiya devir sistemi\n\nDil seçin:",
    },

    # ── MAIN MENU ──
    "main_menu": {
        "ru": "🏠 *Главное меню*\nЧто делаем?",
        "uz": "🏠 *Asosiy menyu*\nNima qilamiz?",
        "en": "🏠 *Main menu*\nWhat would you like to do?",
        "tr": "🏠 *Ana menü*\nNe yapmak istersiniz?",
    },
    "btn_new_shift": {
        "ru": "📋 Начать смену",
        "uz": "📋 Navbat boshlash",
        "en": "📋 Start shift",
        "tr": "📋 Vardiya başlat",
    },
    "btn_my_reports": {
        "ru": "📊 Мои отчёты",
        "uz": "📊 Mening hisobotlarim",
        "en": "📊 My reports",
        "tr": "📊 Raporlarım",
    },
    "btn_admin": {
        "ru": "⚙️ Администрирование",
        "uz": "⚙️ Boshqaruv",
        "en": "⚙️ Administration",
        "tr": "⚙️ Yönetim",
    },
    "btn_settings": {
        "ru": "🌐 Язык / Настройки",
        "uz": "🌐 Til / Sozlamalar",
        "en": "🌐 Language / Settings",
        "tr": "🌐 Dil / Ayarlar",
    },

    # ── SHIFT ──
    "select_project": {
        "ru": "📁 Выберите объект:",
        "uz": "📁 Ob'ektni tanlang:",
        "en": "📁 Select project:",
        "tr": "📁 Proje seçin:",
    },
    "select_subproject": {
        "ru": "📂 Выберите блок / зону:",
        "uz": "📂 Blok / zonani tanlang:",
        "en": "📂 Select block / zone:",
        "tr": "📂 Blok / bölge seçin:",
    },
    "select_shift_type": {
        "ru": "🕐 Тип смены:",
        "uz": "🕐 Navbat turi:",
        "en": "🕐 Shift type:",
        "tr": "🕐 Vardiya türü:",
    },
    "shift_open": {
        "ru": "✅ Смена открыта.\n\nДобавьте первую конструкцию 👇",
        "uz": "✅ Navbat ochildi.\n\nBirinchi konstruktsiyani qo'shing 👇",
        "en": "✅ Shift started.\n\nAdd the first structure 👇",
        "tr": "✅ Vardiya başladı.\n\nİlk yapıyı ekleyin 👇",
    },

    # ── ENTRY ──
    "select_structure_type": {
        "ru": "🏗 Тип конструкции:",
        "uz": "🏗 Konstruktsiya turi:",
        "en": "🏗 Structure type:",
        "tr": "🏗 Yapı türü:",
    },
    "enter_structure_name": {
        "ru": "✏️ Маркировка конструкции:\n_(например: К-1, Ст-14, Пер-3)_",
        "uz": "✏️ Konstruktsiya markasi:\n_(masalan: K-1, Dev-14, Tom-3)_",
        "en": "✏️ Structure mark:\n_(e.g. C-1, W-14, S-3)_",
        "tr": "✏️ Yapı işareti:\n_(örn. K-1, D-14, D-3)_",
    },
    "select_natura": {
        "ru": "📋 *НАТУРА* — разрешение на производство работ:",
        "uz": "📋 *NATURA* — ishlarni bajarish uchun ruxsat:",
        "en": "📋 *PERMIT TO WORK* (natura):",
        "tr": "📋 *ÇALIŞMA İZNİ* (natura):",
    },
    "select_rebar": {
        "ru": "🔩 *АРМАТУРА* — статус приёмки:",
        "uz": "🔩 *ARMATURA* — qabul holati:",
        "en": "🔩 *REBAR* — acceptance status:",
        "tr": "🔩 *DONATI* — kabul durumu:",
    },
    "select_defects": {
        "ru": "⚠️ *Дефекты арматуры*\nОтметьте все имеющиеся:",
        "uz": "⚠️ *Armatura nuqsonlari*\nBarchasini belgilang:",
        "en": "⚠️ *Rebar defects*\nMark all that apply:",
        "tr": "⚠️ *Donatı kusurları*\nHepsini işaretleyin:",
    },
    "enter_defect_custom": {
        "ru": "✏️ Опишите дефект своими словами:",
        "uz": "✏️ Nuqsonni o'z so'zlaringiz bilan tasvirlab bering:",
        "en": "✏️ Describe the defect in your own words:",
        "tr": "✏️ Kusuru kendi kelimelerinizle açıklayın:",
    },
    "select_concrete": {
        "ru": "🪣 *БЕТОН* — планируется заливка?",
        "uz": "🪣 *BETON* — quyish rejalashtirilganmi?",
        "en": "🪣 *CONCRETE* — is pouring planned?",
        "tr": "🪣 *BETON* — döküm planlanıyor mu?",
    },
    "select_pour_method": {
        "ru": "🚛 Способ подачи бетона:",
        "uz": "🚛 Beton uzatish usuli:",
        "en": "🚛 Concrete delivery method:",
        "tr": "🚛 Beton iletim yöntemi:",
    },
    "select_pump_type": {
        "ru": "⚙️ Тип насоса:",
        "uz": "⚙️ Nasos turi:",
        "en": "⚙️ Pump type:",
        "tr": "⚙️ Pompa türü:",
    },
    "select_pump_logistics": {
        "ru": "🔧 Логистика насоса:",
        "uz": "🔧 Nasos logistikasi:",
        "en": "🔧 Pump logistics:",
        "tr": "🔧 Pompa lojistiği:",
    },
    "enter_volume": {
        "ru": "📐 Объём бетона (м³):\n_Введите число, например: 12.5_",
        "uz": "📐 Beton hajmi (m³):\n_Raqam kiriting, masalan: 12.5_",
        "en": "📐 Concrete volume (m³):\n_Enter number, e.g. 12.5_",
        "tr": "📐 Beton hacmi (m³):\n_Sayı girin, örn. 12.5_",
    },
    "enter_comment": {
        "ru": "💬 Доп. комментарий по конструкции:\n_/skip — пропустить_",
        "uz": "💬 Konstruktsiya bo'yicha qo'shimcha izoh:\n_/skip — o'tkazish_",
        "en": "💬 Additional comment on structure:\n_/skip — skip_",
        "tr": "💬 Yapı hakkında ek yorum:\n_/skip — atla_",
    },
    "invalid_volume": {
        "ru": "❌ Введите корректное число. Например: 12.5",
        "uz": "❌ To'g'ri raqam kiriting. Masalan: 12.5",
        "en": "❌ Enter a valid number. Example: 12.5",
        "tr": "❌ Geçerli bir sayı girin. Örnek: 12.5",
    },

    # ── ENTRY DONE ──
    "entry_saved": {
        "ru": "✅ *Конструкция сохранена!*",
        "uz": "✅ *Konstruktsiya saqlandi!*",
        "en": "✅ *Structure saved!*",
        "tr": "✅ *Yapı kaydedildi!*",
    },
    "entry_menu": {
        "ru": "Что дальше?",
        "uz": "Keyingi qadam?",
        "en": "What's next?",
        "tr": "Sonraki adım?",
    },
    "btn_add_structure": {
        "ru": "➕ Добавить конструкцию",
        "uz": "➕ Konstruktsiya qo'shish",
        "en": "➕ Add structure",
        "tr": "➕ Yapı ekle",
    },
    "btn_finish_shift": {
        "ru": "🏁 Завершить смену → Отчёт",
        "uz": "🏁 Navbatni tugatish → Hisobot",
        "en": "🏁 Finish shift → Report",
        "tr": "🏁 Vardiyayı bitir → Rapor",
    },
    "btn_cancel_entry": {
        "ru": "🗑 Отменить последнюю",
        "uz": "🗑 Oxirgisini bekor qilish",
        "en": "🗑 Cancel last entry",
        "tr": "🗑 Son girişi iptal et",
    },

    # ── WARNINGS ──
    "warn_natura_not_given": {
        "ru": "‼️ ВНИМАНИЕ: Натура НЕ ДАНА — заливка ЗАПРЕЩЕНА",
        "uz": "‼️ DIQQAT: Natura BERILMAGAN — quyish TAQIQLANGAN",
        "en": "‼️ WARNING: Permit NOT ISSUED — pouring FORBIDDEN",
        "tr": "‼️ UYARI: İzin VERİLMEDİ — döküm YASAK",
    },
    "warn_natura_night": {
        "ru": "⚠️ Натура будет дана ночью — заливка только после выдачи",
        "uz": "⚠️ Natura kechasi beriladi — quyish faqat keyin",
        "en": "⚠️ Permit at night — pouring only after issuance",
        "tr": "⚠️ İzin gece verilecek — döküm yalnızca sonrasında",
    },
    "warn_rebar_blocks": {
        "ru": "‼️ Арматура НЕ СДАНА — заливка ЗАПРЕЩЕНА",
        "uz": "‼️ Armatura TOPSHIRILMAGAN — quyish TAQIQLANGAN",
        "en": "‼️ Rebar NOT ACCEPTED — pouring FORBIDDEN",
        "tr": "‼️ Donatı TESLİM EDİLMEDİ — döküm YASAK",
    },

    # ── REPORT ──
    "generating_report": {
        "ru": "⏳ Генерирую отчёт...",
        "uz": "⏳ Hisobot tayyorlanmoqda...",
        "en": "⏳ Generating report...",
        "tr": "⏳ Rapor oluşturuluyor...",
    },
    "no_entries": {
        "ru": "⚠️ Нет записей. Добавьте хотя бы одну конструкцию.",
        "uz": "⚠️ Yozuvlar yo'q. Kamida bitta konstruktsiya qo'shing.",
        "en": "⚠️ No entries. Add at least one structure.",
        "tr": "⚠️ Kayıt yok. En az bir yapı ekleyin.",
    },

    # ── ADMIN ──
    "admin_menu": {
        "ru": "⚙️ *Администрирование*\nУправление справочниками:",
        "uz": "⚙️ *Boshqaruv*\nMa'lumotnomalarni boshqarish:",
        "en": "⚙️ *Administration*\nManage reference data:",
        "tr": "⚙️ *Yönetim*\nReferans verileri yönetin:",
    },
    "btn_manage_projects": {
        "ru": "🏗 Объекты и подобъекты",
        "uz": "🏗 Ob'ektlar va kichik ob'ektlar",
        "en": "🏗 Projects & subprojects",
        "tr": "🏗 Projeler ve alt projeler",
    },
    "btn_manage_structures": {
        "ru": "🏛 Типы конструкций",
        "uz": "🏛 Konstruktsiya turlari",
        "en": "🏛 Structure types",
        "tr": "🏛 Yapı türleri",
    },
    "btn_manage_defects": {
        "ru": "⚠️ Список дефектов",
        "uz": "⚠️ Nuqsonlar ro'yxati",
        "en": "⚠️ Defect list",
        "tr": "⚠️ Kusur listesi",
    },
    "btn_manage_pour_methods": {
        "ru": "🚛 Способы подачи бетона",
        "uz": "🚛 Beton uzatish usullari",
        "en": "🚛 Pour methods",
        "tr": "🚛 Döküm yöntemleri",
    },
    "btn_manage_pump_types": {
        "ru": "⚙️ Типы насосов",
        "uz": "⚙️ Nasos turlari",
        "en": "⚙️ Pump types",
        "tr": "⚙️ Pompa türleri",
    },
    "btn_back": {
        "ru": "◀️ Назад",
        "uz": "◀️ Orqaga",
        "en": "◀️ Back",
        "tr": "◀️ Geri",
    },
    "btn_add_new": {
        "ru": "➕ Добавить",
        "uz": "➕ Qo'shish",
        "en": "➕ Add new",
        "tr": "➕ Yeni ekle",
    },
    "enter_name_ru": {
        "ru": "✏️ Введите название на русском:",
        "uz": "✏️ Rus tilida nom kiriting:",
        "en": "✏️ Enter name in Russian:",
        "tr": "✏️ Rusça ad girin:",
    },
    "item_added": {
        "ru": "✅ Добавлено успешно",
        "uz": "✅ Muvaffaqiyatli qo'shildi",
        "en": "✅ Added successfully",
        "tr": "✅ Başarıyla eklendi",
    },
    "item_deleted": {
        "ru": "🗑 Удалено",
        "uz": "🗑 O'chirildi",
        "en": "🗑 Deleted",
        "tr": "🗑 Silindi",
    },
    "confirm_delete": {
        "ru": "❓ Удалить этот элемент?",
        "uz": "❓ Bu elementni o'chirasizmi?",
        "en": "❓ Delete this item?",
        "tr": "❓ Bu öğeyi silelim mi?",
    },
    "btn_confirm_yes": {
        "ru": "✅ Да, удалить",
        "uz": "✅ Ha, o'chirish",
        "en": "✅ Yes, delete",
        "tr": "✅ Evet, sil",
    },
    "btn_cancel": {
        "ru": "❌ Отмена",
        "uz": "❌ Bekor qilish",
        "en": "❌ Cancel",
        "tr": "❌ İptal",
    },

    # ── COMMON ──
    "btn_yes": {"ru": "✅ Да", "uz": "✅ Ha", "en": "✅ Yes", "tr": "✅ Evet"},
    "btn_no": {"ru": "❌ Нет", "uz": "❌ Yo'q", "en": "❌ No", "tr": "❌ Hayır"},
    "btn_done": {"ru": "✅ Готово", "uz": "✅ Tayyor", "en": "✅ Done", "tr": "✅ Tamam"},
    "btn_skip": {"ru": "⏭ Пропустить", "uz": "⏭ O'tkazish", "en": "⏭ Skip", "tr": "⏭ Atla"},
    "btn_ready": {"ru": "✅ Готово", "uz": "✅ Tayyor", "en": "✅ Ready", "tr": "✅ Hazır"},
    "btn_not_ready": {"ru": "❌ Не готово", "uz": "❌ Tayyor emas", "en": "❌ Not ready", "tr": "❌ Hazır değil"},
    "not_applicable": {"ru": "—", "uz": "—", "en": "—", "tr": "—"},
    "access_denied": {
        "ru": "🚫 Доступ запрещён",
        "uz": "🚫 Kirish taqiqlangan",
        "en": "🚫 Access denied",
        "tr": "🚫 Erişim engellendi",
    },
}

# ── CODE LABEL DICTIONARIES (for DB-stored codes) ──

SHIFT_LABELS = {
    "DAY": {"ru": "🌅 День", "uz": "🌅 Kun", "en": "🌅 Day", "tr": "🌅 Gündüz"},
    "NIGHT": {"ru": "🌙 Ночь", "uz": "🌙 Kecha", "en": "🌙 Night", "tr": "🌙 Gece"},
}

NATURA_LABELS = {
    "NATURA_GIVEN": {"ru": "✅ Дана", "uz": "✅ Berilgan", "en": "✅ Issued", "tr": "✅ Verildi"},
    "NATURA_NOT_GIVEN": {"ru": "🚫 Не дана", "uz": "🚫 Berilmagan", "en": "🚫 Not issued", "tr": "🚫 Verilmedi"},
    "NATURA_WILL_BE_NIGHT": {"ru": "⚠️ Будет ночью", "uz": "⚠️ Kechasi", "en": "⚠️ At night", "tr": "⚠️ Gece"},
}

REBAR_LABELS = {
    "REBAR_ACCEPTED": {"ru": "✅ Сдана", "uz": "✅ Topshirildi", "en": "✅ Accepted", "tr": "✅ Teslim"},
    "REBAR_PARTIAL": {"ru": "⚠️ Частично", "uz": "⚠️ Qisman", "en": "⚠️ Partial", "tr": "⚠️ Kısmen"},
    "REBAR_NOT_ACCEPTED": {"ru": "🚫 Не сдана", "uz": "🚫 Topshirilmagan", "en": "🚫 Not accepted", "tr": "🚫 Teslim yok"},
}

PUMP_LOGISTICS_LABELS = {
    "LOGISTICS_ASSEMBLY": {"ru": "🔧 Монтаж", "uz": "🔧 Montaj", "en": "🔧 Assembly", "tr": "🔧 Montaj"},
    "LOGISTICS_RELOCATION": {"ru": "🔄 Перестановка", "uz": "🔄 Ko'chirish", "en": "🔄 Relocation", "tr": "🔄 Taşıma"},
    "LOGISTICS_BOTH": {"ru": "🔧🔄 Монтаж+Перестановка", "uz": "🔧🔄 Montaj+Ko'chirish", "en": "🔧🔄 Both", "tr": "🔧🔄 İkisi"},
    "LOGISTICS_NONE": {"ru": "➖ Не требуется", "uz": "➖ Kerak emas", "en": "➖ Not required", "tr": "➖ Gerekmez"},
}


def t(key: str, lang: str) -> str:
    return UI.get(key, {}).get(lang) or UI.get(key, {}).get("ru") or key


def lbl(dictionary: dict, code: str, lang: str) -> str:
    return dictionary.get(code, {}).get(lang) or dictionary.get(code, {}).get("ru") or code

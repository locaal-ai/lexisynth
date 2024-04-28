class LanguageCodes:
    ENGLISH = "en"
    FRENCH = "fr"
    SPANISH = "es"
    GERMAN = "de"
    ITALIAN = "it"
    DUTCH = "nl"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    TURKISH = "tr"
    GREEK = "el"
    HEBREW = "he"
    POLISH = "pl"
    UKRAINIAN = "uk"
    CZECH = "cs"
    SLOVAK = "sk"
    BULGARIAN = "bg"
    ROMANIAN = "ro"
    HUNGARIAN = "hu"
    FINNISH = "fi"
    SWEDISH = "sv"
    DANISH = "da"
    NORWEGIAN = "no"
    ICELANDIC = "is"
    ESTONIAN = "et"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    MALTESE = "mt"
    CROATIAN = "hr"
    SERBIAN = "sr"
    BOSNIAN = "bs"
    SLOVENIAN = "sl"
    ALBANIAN = "sq"
    MACEDONIAN = "mk"
    MONTENEGRIN = "me"
    KURDISH = "ku"
    PERSIAN = "fa"
    PASHTO = "ps"
    URDU = "ur"
    BENGALI = "bn"
    TAMIL = "ta"
    TELUGU = "te"
    MARATHI = "mr"
    GUJARATI = "gu"
    PUNJABI = "pa"
    NEPALI = "ne"
    SINHALA = "si"
    BURMESE = "my"
    KHMER = "km"
    LAO = "lo"
    THAI = "th"
    VIETNAMESE = "vi"
    INDONESIAN = "id"
    MALAY = "ms"
    FILIPINO = "fil"
    JAVANESE = "jv"

    def getLanguageName(code):
        if code == LanguageCodes.ENGLISH:
            return "English"
        elif code == LanguageCodes.FRENCH:
            return "French"
        elif code == LanguageCodes.SPANISH:
            return "Spanish"
        elif code == LanguageCodes.GERMAN:
            return "German"
        elif code == LanguageCodes.ITALIAN:
            return "Italian"
        elif code == LanguageCodes.DUTCH:
            return "Dutch"
        elif code == LanguageCodes.PORTUGUESE:
            return "Portuguese"
        elif code == LanguageCodes.RUSSIAN:
            return "Russian"
        elif code == LanguageCodes.CHINESE:
            return "Chinese"
        elif code == LanguageCodes.JAPANESE:
            return "Japanese"
        elif code == LanguageCodes.KOREAN:
            return "Korean"
        elif code == LanguageCodes.ARABIC:
            return "Arabic"
        elif code == LanguageCodes.HINDI:
            return "Hindi"
        elif code == LanguageCodes.TURKISH:
            return "Turkish"
        elif code == LanguageCodes.GREEK:
            return "Greek"
        elif code == LanguageCodes.HEBREW:
            return "Hebrew"
        elif code == LanguageCodes.POLISH:
            return "Polish"
        elif code == LanguageCodes.UKRAINIAN:
            return "Ukrainian"
        elif code == LanguageCodes.CZECH:
            return "Czech"
        elif code == LanguageCodes.SLOVAK:
            return "Slovak"
        elif code == LanguageCodes.BULGARIAN:
            return "Bulgarian"
        elif code == LanguageCodes.ROMANIAN:
            return "Romanian"
        elif code == LanguageCodes.HUNGARIAN:
            return "Hungarian"
        elif code == LanguageCodes.FINNISH:
            return "Finnish"
        elif code == LanguageCodes.SWEDISH:
            return "Swedish"
        elif code == LanguageCodes.DANISH:
            return "Danish"
        elif code == LanguageCodes.NORWEGIAN:
            return "Norwegian"
        elif code == LanguageCodes.ICELANDIC:
            return "Icelandic"
        elif code == LanguageCodes.ESTONIAN:
            return "Estonian"
        elif code == LanguageCodes.LATVIAN:
            return "Latvian"
        elif code == LanguageCodes.LITHUANIAN:
            return "Lithuanian"
        elif code == LanguageCodes.MALTESE:
            return "Maltese"
        elif code == LanguageCodes.CROATIAN:
            return "Croatian"
        elif code == LanguageCodes.SERBIAN:
            return "Serbian"
        elif code == LanguageCodes.BOSNIAN:
            return "Bosnian"
        elif code == LanguageCodes.SLOVENIAN:
            return "Slovenian"
        elif code == LanguageCodes.ALBANIAN:
            return "Albanian"
        elif code == LanguageCodes.MACEDONIAN:
            return "Macedonian"
        elif code == LanguageCodes.MONTENEGRIN:
            return "Montenegrin"
        elif code == LanguageCodes.KURDISH:
            return "Kurdish"
        elif code == LanguageCodes.PERSIAN:
            return "Persian"
        elif code == LanguageCodes.PASHTO:
            return "Pashto"
        elif code == LanguageCodes.URDU:
            return "Urdu"
        elif code == LanguageCodes.BENGALI:
            return "Bengali"
        elif code == LanguageCodes.TAMIL:
            return "Tamil"
        elif code == LanguageCodes.TELUGU:
            return "Telugu"
        elif code == LanguageCodes.MARATHI:
            return "Marathi"
        elif code == LanguageCodes.GUJARATI:
            return "Gujarati"
        elif code == LanguageCodes.PUNJABI:
            return "Punjabi"
        elif code == LanguageCodes.NEPALI:
            return "Nepali"
        elif code == LanguageCodes.SINHALA:
            return "Sinhala"
        elif code == LanguageCodes.BURMESE:
            return "Burmese"
        elif code == LanguageCodes.KHMER:
            return "Khmer"
        elif code == LanguageCodes.LAO:
            return "Lao"
        elif code == LanguageCodes.THAI:
            return "Thai"
        elif code == LanguageCodes.VIETNAMESE:
            return "Vietnamese"
        elif code == LanguageCodes.INDONESIAN:
            return "Indonesian"
        elif code == LanguageCodes.MALAY:
            return "Malay"
        elif code == LanguageCodes.FILIPINO:
            return "Filipino"
        elif code == LanguageCodes.JAVANESE:
            return "Javanese"
        else:
            return "Unknown"

    def getLanguageCode(name) -> str:
        if name == "English":
            return LanguageCodes.ENGLISH
        elif name == "French":
            return LanguageCodes.FRENCH
        elif name == "Spanish":
            return LanguageCodes.SPANISH
        elif name == "German":
            return LanguageCodes.GERMAN
        elif name == "Italian":
            return LanguageCodes.ITALIAN
        elif name == "Dutch":
            return LanguageCodes.DUTCH
        elif name == "Portuguese":
            return LanguageCodes.PORTUGUESE
        elif name == "Russian":
            return LanguageCodes.RUSSIAN
        elif name == "Chinese":
            return LanguageCodes.CHINESE
        elif name == "Japanese":
            return LanguageCodes.JAPANESE
        elif name == "Korean":
            return LanguageCodes.KOREAN
        elif name == "Arabic":
            return LanguageCodes.ARABIC
        elif name == "Hindi":
            return LanguageCodes.HINDI
        elif name == "Turkish":
            return LanguageCodes.TURKISH
        elif name == "Greek":
            return LanguageCodes.GREEK
        elif name == "Hebrew":
            return LanguageCodes.HEBREW
        elif name == "Polish":
            return LanguageCodes.POLISH
        elif name == "Ukrainian":
            return LanguageCodes.UKRAINIAN
        elif name == "Czech":
            return LanguageCodes.CZECH
        elif name == "Slovak":
            return LanguageCodes.SLOVAK
        elif name == "Bulgarian":
            return LanguageCodes.BULGARIAN
        elif name == "Romanian":
            return LanguageCodes.ROMANIAN
        elif name == "Hungarian":
            return LanguageCodes.HUNGARIAN
        elif name == "Finnish":
            return LanguageCodes.FINNISH
        elif name == "Swedish":
            return LanguageCodes.SWEDISH
        elif name == "Danish":
            return LanguageCodes.DANISH
        elif name == "Norwegian":
            return LanguageCodes.NORWEGIAN
        elif name == "Icelandic":
            return LanguageCodes.ICELANDIC
        elif name == "Estonian":
            return LanguageCodes.ESTONIAN
        elif name == "Latvian":
            return LanguageCodes.LATVIAN
        elif name == "Lithuanian":
            return LanguageCodes.LITHUANIAN
        elif name == "Maltese":
            return LanguageCodes.MALTESE
        elif name == "Croatian":
            return LanguageCodes.CROATIAN
        elif name == "Serbian":
            return LanguageCodes.SERBIAN
        elif name == "Bosnian":
            return LanguageCodes.BOSNIAN
        elif name == "Slovenian":
            return LanguageCodes.SLOVENIAN
        elif name == "Albanian":
            return LanguageCodes.ALBANIAN
        elif name == "Macedonian":
            return LanguageCodes.MACEDONIAN
        elif name == "Montenegrin":
            return LanguageCodes.MONTENEGRIN
        elif name == "Kurdish":
            return LanguageCodes.KURDISH
        elif name == "Persian":
            return LanguageCodes.PERSIAN
        elif name == "Pashto":
            return LanguageCodes.PASHTO
        elif name == "Urdu":
            return LanguageCodes.URDU
        elif name == "Bengali":
            return LanguageCodes.BENGALI
        elif name == "Tamil":
            return LanguageCodes.TAMIL
        elif name == "Telugu":
            return LanguageCodes.TELUGU
        elif name == "Marathi":
            return LanguageCodes.MARATHI
        elif name == "Gujarati":
            return LanguageCodes.GUJARATI
        elif name == "Punjabi":
            return LanguageCodes.PUNJABI
        elif name == "Nepali":
            return LanguageCodes.NEPALI
        elif name == "Sinhala":
            return LanguageCodes.SINHALA
        elif name == "Burmese":
            return LanguageCodes.BURMESE
        elif name == "Khmer":
            return LanguageCodes.KHMER
        elif name == "Lao":
            return LanguageCodes.LAO
        elif name == "Thai":
            return LanguageCodes.THAI
        elif name == "Vietnamese":
            return LanguageCodes.VIETNAMESE
        elif name == "Indonesian":
            return LanguageCodes.INDONESIAN
        elif name == "Malay":
            return LanguageCodes.MALAY
        elif name == "Filipino":
            return LanguageCodes.FILIPINO
        elif name == "Javanese":
            return LanguageCodes.JAVANESE
        else:
            return "Unknown"

    def getLanguageCodes():
        return [
            LanguageCodes.ENGLISH,
            LanguageCodes.FRENCH,
            LanguageCodes.SPANISH,
            LanguageCodes.GERMAN,
            LanguageCodes.ITALIAN,
            LanguageCodes.DUTCH,
            LanguageCodes.PORTUGUESE,
            LanguageCodes.RUSSIAN,
            LanguageCodes.CHINESE,
            LanguageCodes.JAPANESE,
            LanguageCodes.KOREAN,
            LanguageCodes.ARABIC,
            LanguageCodes.HINDI,
            LanguageCodes.TURKISH,
            LanguageCodes.GREEK,
            LanguageCodes.HEBREW,
            LanguageCodes.POLISH,
            LanguageCodes.UKRAINIAN,
            LanguageCodes.CZECH,
            LanguageCodes.SLOVAK,
            LanguageCodes.BULGARIAN,
            LanguageCodes.ROMANIAN,
            LanguageCodes.HUNGARIAN,
            LanguageCodes.FINNISH,
            LanguageCodes.SWEDISH,
            LanguageCodes.DANISH,
            LanguageCodes.NORWEGIAN,
            LanguageCodes.ICELANDIC,
            LanguageCodes.ESTONIAN,
            LanguageCodes.LATVIAN,
            LanguageCodes.LITHUANIAN,
            LanguageCodes.MALTESE,
            LanguageCodes.CROATIAN,
            LanguageCodes.SERBIAN,
            LanguageCodes.BOSNIAN,
            LanguageCodes.SLOVENIAN,
            LanguageCodes.ALBANIAN,
            LanguageCodes.MACEDONIAN,
            LanguageCodes.MONTENEGRIN,
            LanguageCodes.KURDISH,
            LanguageCodes.PERSIAN,
            LanguageCodes.PASHTO,
            LanguageCodes.URDU,
            LanguageCodes.BENGALI,
            LanguageCodes.TAMIL,
            LanguageCodes.TELUGU,
            LanguageCodes.MARATHI,
            LanguageCodes.GUJARATI,
            LanguageCodes.PUNJABI,
            LanguageCodes.NEPALI,
            LanguageCodes.SINHALA,
            LanguageCodes.BURMESE,
            LanguageCodes.KHMER,
            LanguageCodes.LAO,
            LanguageCodes.THAI,
            LanguageCodes.VIETNAMESE,
            LanguageCodes.INDONESIAN,
            LanguageCodes.MALAY,
            LanguageCodes.FILIPINO,
            LanguageCodes.JAVANESE,
        ]

    def getLanguageNames():
        return [
            "English",
            "French",
            "Spanish",
            "German",
            "Italian",
            "Dutch",
            "Portuguese",
            "Russian",
            "Chinese",
            "Japanese",
            "Korean",
            "Arabic",
            "Hindi",
            "Turkish",
            "Greek",
            "Hebrew",
            "Polish",
            "Ukrainian",
            "Czech",
            "Slovak",
            "Bulgarian",
            "Romanian",
            "Hungarian",
            "Finnish",
            "Swedish",
            "Danish",
            "Norwegian",
            "Icelandic",
            "Estonian",
            "Latvian",
            "Lithuanian",
            "Maltese",
            "Croatian",
            "Serbian",
            "Bosnian",
            "Slovenian",
            "Albanian",
            "Macedonian",
            "Montenegrin",
            "Kurdish",
            "Persian",
            "Pashto",
            "Urdu",
            "Bengali",
            "Tamil",
            "Telugu",
            "Marathi",
            "Gujarati",
            "Punjabi",
            "Nepali",
            "Sinhala",
            "Burmese",
            "Khmer",
            "Lao",
            "Thai",
            "Vietnamese",
            "Indonesian",
            "Malay",
            "Filipino",
            "Javanese",
        ]

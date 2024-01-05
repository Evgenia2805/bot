from text2ipa import get_IPA

def get_transcription(input_text: str) -> str:
    text = input_text.lower()
    language: str = 'fr'
    ipa = get_IPA(text, language)
    return ipa

# Пример использования:
user_input = input("Введите фразу или слово: ")
transcription_result = get_transcription(user_input)
print("Транскрипция:", transcription_result)


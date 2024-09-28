from chatbot.Audio import Audio

text= 'السلام عليكم ورحمة الله وبركاته, أنا مساعدك الشخصي اسألني اي سوأل تريده.'
chat = Audio()

# recording, sampling_rate = chat.record_audio()

# chat.write_audio(recording, "voice_records/recording1.mp3")

# text = chat.voice_to_text("./voice_records/recording1.mp3")

# chat.printAr(text)

# chat.text_to_voice(text, "./voice_records/t_recording1.mp3")
# chat.play_sound("./voice_records/t_recording1.mp3")
# chat.play_sound("./voice_records/recording1.mp3")

# chat.text_to_voice(text, "./voice_records/speech.mp3")

chat.play_sound('./voice_records/speech.mp3')

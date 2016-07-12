__author__ = 'JP'

from time import sleep
from AppKit import NSSpeechSynthesizer
import Cocoa

TEXT = "Good-bye! Nice to know you."

# TTS variables
RATE = 170    # Value in words per minute; human 180-220
VOLUME = 0.5  # Floating point value in the range of 0.0 to 1.0, inclusive.
VOICE = 'com.apple.speech.synthesis.voice.Agnes'  # String identifier of the active voice.
              ### RUN showcase_voices.py TO SEE ALL AVAILABLE VOICES IN YOUR SYSTEM ###

if __name__ == '__main__':

    ## Initialise voice synthesizer
    # synth = [[NSSpeechSynthesizer alloc] initWithVoice:nil];
    synth = NSSpeechSynthesizer.alloc().initWithVoice_(None)

    ## Fetch all system voices available
    voices = NSSpeechSynthesizer.availableVoices()

    ## Set voice values
    synth.setVolume_(VOLUME)
    synth.setRate_(RATE)
    # synth.setPitch_(PITCH)

    ## Print out all system voices available
    for voice in voices:
        print voice

    for voice in voices:
        # synth = NSSpeechSynthesizer.alloc().initWithVoice_(voice)
        synth.setVoice_(voice)
        RATE += 10
        synth.setRate_(RATE)
        v = voice.split('voice.')[-1]
        synth.startSpeakingString_(v)
        while synth.isSpeaking():
            sleep(2)

        synth.startSpeakingString_(TEXT)
        while synth.isSpeaking():
            sleep(1)

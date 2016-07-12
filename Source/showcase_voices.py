__author__ = 'JP'

from time import sleep
from AppKit import NSSpeechSynthesizer

TEXT = "Hello, dear. Nice to finally meet you!"

if __name__ == '__main__':
    # synth = [[NSSpeechSynthesizer alloc] initWithVoice:nil];
    synth = NSSpeechSynthesizer.alloc().initWithVoice_(None)
    # synth.startSpeakingString_('Hi! Nice to meet you!')
    while synth.isSpeaking():
        sleep(1)
    voices = NSSpeechSynthesizer.availableVoices()

    for voice in voices:
        print voice

    for voice in voices:
        synth = NSSpeechSynthesizer.alloc().initWithVoice_(voice)
        v = voice.split('.')[-1]
        synth.startSpeakingString_(v)
        while synth.isSpeaking():
            sleep(2)

        synth.startSpeakingString_(TEXT)
        while synth.isSpeaking():
            sleep(1)

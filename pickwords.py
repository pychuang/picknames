#!/usr/bin/env python3

import csv
import os
import pickle
import Pmw
import tkinter

class WordController(object):

    def __init__(self, parent_view, column, word):
        self.word = word
        self.button = tkinter.Button(parent_view, text=word, command=self.toggle_word_button)
        self.button.grid(row=0, column=column)
        self.selected = False


    def toggle_word_button(self):
        if self.selected:
            self.deselect_word_button()
        else:
            self.select_word_button()


    def select_word_button(self):
        self.selected = True
        self.button.config(relief=tkinter.SUNKEN)


    def deselect_word_button(self):
        self.selected = False
        self.button.config(relief=tkinter.RAISED)

    def destroy(self):
        self.button.destroy()


class SoundController(object):

    def __init__(self, parent_view, row, sound, words):
        self.sound = sound
        self.candidate_words = words

        self.sound_label = tkinter.Label(parent_view, text=sound)
        self.sound_label.grid(row=row, column=0, sticky=tkinter.NW+tkinter.SE)
        self.words_frame = tkinter.Frame(parent_view)
        self.words_frame.grid(row=row, column=1, sticky=tkinter.NW)

        self.word_controllers = []
        for i, word in enumerate(self.candidate_words):
            try:
                wc = WordController(self.words_frame, i, word)
                self.word_controllers.append(wc)
            except Exception as e:
                print(e)


    def load_state(self, selected_words):
        if not selected_words:
            return

        for wc in self.word_controllers:
            if wc.word in selected_words:
                wc.select_word_button()


    def get_selected_words(self):
        selected_words = []
        for wc in self.word_controllers:
            if wc.selected:
                 selected_words.append(wc.word)

        return selected_words


    def deselect_sound(self):
        for wc in self.word_controllers:
            wc.destroy()
        self.word_controllers = []


    def destroy(self):
        self.deselect_sound()
        self.sound_label.destroy()
        self.words_frame.destroy()


class SpellingController(object):

    def __init__(self, parent_view, row, spelling, chewing, sound_words_pairs):
        self.spelling = spelling
        self.chewing = chewing
        self.sound_words_pairs = sound_words_pairs
        self.selected = False

        display_text = "%s %s" % (chewing, spelling)
        self.spelling_button = tkinter.Button(parent_view, text=display_text, command=self.toggle_spelling_button)
        self.spelling_button.grid(row=row, column=0, sticky=tkinter.NW+tkinter.SE)
        self.sounds_frame = tkinter.Frame(parent_view)
        self.sounds_frame.grid(row=row, column=1, sticky=tkinter.NW)

        self.sound_controllers = []


    def load_state(self, selected_sound_words_mapping):
        if not selected_sound_words_mapping:
            return

        self.toggle_spelling_button()

        for sc in self.sound_controllers:
            if sc.sound in selected_sound_words_mapping:
                selected_words = selected_sound_words_mapping[sc.sound]
                sc.load_state(selected_words)


    def get_selected_sounds_state(self):
        if not self.selected:
            return None

        selected_sound_words_mapping = {}
        for sc in self.sound_controllers:
            selected_words = sc.get_selected_words()
            if not selected_words:
                continue

            selected_sound_words_mapping[sc.sound] = selected_words

        return selected_sound_words_mapping


    def toggle_spelling_button(self):
        if self.selected:
            self.spelling_button.config(relief=tkinter.RAISED)
            self.deselect_spelling()
        else:
            self.spelling_button.config(relief=tkinter.SUNKEN)
            self.select_spelling()

        self.selected = not self.selected


    def select_spelling(self):
        for i, (sound, words) in enumerate(self.sound_words_pairs):
            try:
                sc = SoundController(self.sounds_frame, i, sound, words)
                self.sound_controllers.append(sc)
            except Exception as e:
                print(e)


    def deselect_spelling(self):
        for sc in self.sound_controllers:
            sc.destroy()
        self.sound_controllers = []


class WordSelectController(object):

    STATE_FILE_NAME = 'words-selected.pkl'


    def __init__(self, parent_view):
        self.sf = Pmw.ScrolledFrame(parent_view, labelpos=tkinter.N, label_text='音 & 字')
        self.sf.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.spelling_controllers = []

        data = None
        with open('pickwords-data.pkl', 'rb') as f:
            data = pickle.load(f)

        # [
        #   ("Pan", "ㄅㄢ", [
        #               ( "ㄅㄢˋ", [
        #                           "半", "辦"]
        #               ),
        #               ...
        #           ]
        #   ),
        #   ...
        # ]

        for i, (spelling, chewing, sound_words_pairs) in enumerate(data):
            spc = SpellingController(self.sf.interior(), i, spelling, chewing, sound_words_pairs)
            self.spelling_controllers.append(spc)
        self.load_state()


    def load_state(self):
        saved_state = {}
        if os.path.exists(self.STATE_FILE_NAME):
            with open(self.STATE_FILE_NAME, 'rb') as f:
                saved_state = pickle.load(f)
        #print('LOAD:', saved_state)

        for spc in self.spelling_controllers:
            if spc.spelling in saved_state:
                selected_sound_words_mapping = saved_state[spc.spelling]
                spc.load_state(selected_sound_words_mapping)


    def save_state(self):
        state = {}
        for spc in self.spelling_controllers:
            selected_sounds_state = spc.get_selected_sounds_state()
            if not selected_sounds_state:
                continue

            state[spc.spelling] = selected_sounds_state

        #print('SAVE:', state)
        with open(self.STATE_FILE_NAME, 'wb') as f:
            pickle.dump(state, f)


class App(object):

    def __init__(self, root):
        self.root = root

        self.wsc = WordSelectController(root)

        self.button = tkinter.Button(root, text='離開', fg="red", command=self.quit)
        self.button.pack(side=tkinter.RIGHT)

        self.button = tkinter.Button(root, text='儲存後離開', fg="red", command=self.save_and_quit)
        self.button.pack(side=tkinter.RIGHT)

        self.button = tkinter.Button(root, text='儲存', fg="red", command=self.save)
        self.button.pack(side=tkinter.RIGHT)


    def save(self):
        self.wsc.save_state()


    def save_and_quit(self):
        self.wsc.save_state()
        self.root.quit()


    def quit(self):
        self.root.quit()


def main():
    root = tkinter.Tk()
    root.option_readfile('.pickwords.tkinter.options')
    root.wm_title('選字')
    Pmw.initialise()
    app = App(root)
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    main()

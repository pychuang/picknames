#!/usr/bin/env python3

import csv
import os
import pickle
import Pmw
import tkinter


class NameSelectController(object):

    SELECTED_WORDS_FILE_NAME = 'words-selected.pkl'
    SELECTED_NAMES_FILE_NAME = 'names-selected.txt'
    REFUSED_NAMES_FILE_NAME = 'names-refused.txt'


    def __init__(self, parent_view):
        self.candidate_words = set()
        self.word1_selected_count = {}
        self.word2_selected_count = {}
        self.word1_refused_count = {}
        self.word2_refused_count = {}
        self.refused_names = set()  # (w1, w2)
        self.selected_names = set() # (w1, w2)

        self.candidate_names = []   # (w1, w2, score)
        self.candidate_name = None  # (w,1 w2)

        self.frame = tkinter.Frame(parent_view)
        self.frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # selected names
        self.selected_slb = Pmw.ScrolledListBox(self.frame, labelpos=tkinter.N, label_text='還不錯')
        self.selected_slb.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # refused names
        #self.refused_slb = Pmw.ScrolledListBox(self.frame, labelpos=tkinter.N, label_text='不要的')
        #self.refused_slb.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # candidate
        self.num_candidates_label = tkinter.Label(self.frame)
        self.num_candidates_label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        self.candidate_label = tkinter.Label(self.frame)
        self.candidate_label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        choice_bb = Pmw.ButtonBox(self.frame)
        choice_bb.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.select_button = choice_bb.add('✔', state=tkinter.DISABLED, command=self.select_current_candidate_name)
        self.refuse_button = choice_bb.add( '✖', state=tkinter.DISABLED, command=self.refuse_current_candidate_name)

        # restore state
        self.load_state()

    def load_state(self):
        selected_spelling_sound_words_mapping = {}
        if os.path.exists(self.SELECTED_WORDS_FILE_NAME):
            with open(self.SELECTED_WORDS_FILE_NAME, 'rb') as f:
                selected_spelling_sound_words_mapping = pickle.load(f)
        print('LOAD:', selected_spelling_sound_words_mapping)

        for spelling in selected_spelling_sound_words_mapping:
            for sound, words in selected_spelling_sound_words_mapping[spelling].items():
                self.candidate_words.update(words)

        if os.path.exists(self.SELECTED_NAMES_FILE_NAME):
            with open(self.SELECTED_NAMES_FILE_NAME, 'r', encoding='utf-8') as f:
                for line in f:
                    w1 = line[0]
                    w2 = line[1]
                    self.add_selected_name(w1, w2)
                #print('LOAD selected_names:', self.selected_names)

        if os.path.exists(self.REFUSED_NAMES_FILE_NAME):
            with open(self.REFUSED_NAMES_FILE_NAME, 'r', encoding='utf-8') as f:
                for line in f:
                    w1 = line[0]
                    w2 = line[1]
                    self.add_refused_name(w1, w2)
                #print('LOAD refused_names:', self.refused_names)

        self.update_selected_names_view()

        #names = [w1 + w2 for (w1, w2) in self.refused_names]
        #self.refused_slb.setlist(names)

    def save_state(self):
        with open(self.SELECTED_NAMES_FILE_NAME, 'w', encoding='utf-8') as f:
            names = sorted([w1 + w2 for (w1, w2) in self.selected_names])
            for name in names:
                f.write(name + '\n')

        with open(self.REFUSED_NAMES_FILE_NAME, 'w', encoding='utf-8') as f:
            names = sorted([w1 + w2 for (w1, w2) in self.refused_names])
            for name in names:
                f.write(name + '\n')

    def add_selected_name(self, w1, w2):
        self.selected_count_sanity_check(w1, w2)
        self.word1_selected_count[w1] += 1
        self.word2_selected_count[w2] += 1
        self.selected_names.add((w1, w2))

    def add_refused_name(self, w1, w2):
        self.refused_count_sanity_check(w1, w2)
        self.word1_refused_count[w1] += 1
        self.word2_refused_count[w2] += 1
        self.refused_names.add((w1, w2))

    def selected_count_sanity_check(self, w1, w2):
        if w1 not in self.word1_selected_count:
            self.word1_selected_count[w1] = 0
        if w2 not in self.word2_selected_count:
            self.word2_selected_count[w2] = 0

    def refused_count_sanity_check(self, w1, w2):
        if w1 not in self.word1_refused_count:
            self.word1_refused_count[w1] = 0
        if w2 not in self.word2_refused_count:
            self.word2_refused_count[w2] = 0

    def score_name(self, w1, w2):
        self.selected_count_sanity_check(w1, w2)
        self.refused_count_sanity_check(w1, w2)

        if not self.selected_names and w1 == w2:
            return -1.0

        score = 0
        if self.selected_names:
            score += float(self.word1_selected_count[w1]) / len(self.selected_names)
            score += float(self.word2_selected_count[w2]) / len(self.selected_names)
        if self.refused_names:
            score -= float(self.word1_refused_count[w1]) / len(self.refused_names)
            score -= float(self.word2_refused_count[w2]) / len(self.refused_names)
        return score

    def update_candidate_names(self):
        names = []
        for w1 in self.candidate_words:
            for w2 in self.candidate_words:
                if (w1, w2) in self.refused_names or (w1, w2) in self.selected_names:
                    continue
                score = self.score_name(w1, w2)
                names.append((w1, w2, score))
        self.candidate_names = sorted(names, key=lambda tup: tup[2])
        #print(self.candidate_names)
        self.num_candidates_label.config(text=len(self.candidate_names))
        self.update_name_for_selection()

    def update_name_for_selection(self):
        if self.candidate_names:
            (w1, w2, score) = self.candidate_names.pop()
            self.candidate_name = (w1, w2)
            name = w1 + w2
            self.candidate_label.config(text=name)
            self.select_button.config(state=tkinter.NORMAL)
            self.refuse_button.config(state=tkinter.ACTIVE)
        else:
            self.candidate_name = None
            self.candidate_label.config(text='')
            self.select_button.config(state=tkinter.DISABLED)
            self.refuse_button.config(state=tkinter.DISABLED)

    def select_current_candidate_name(self):
        (w1, w2) = self.candidate_name
        self.add_selected_name(w1, w2)
        self.update_selected_names_view()
        #self.update_name_for_selection()
        self.update_candidate_names()

    def update_selected_names_view(self):
        names = sorted([w1 + w2 for (w1, w2) in self.selected_names])
        self.selected_slb.setlist(names)

    def refuse_current_candidate_name(self):
        (w1, w2) = self.candidate_name
        self.add_refused_name(w1, w2)
        #names = [w1 + w2 for (w1, w2) in self.refused_names]
        #self.refused_slb.setlist(names)
        #self.update_name_for_selection()
        self.update_candidate_names()


class App(object):
    def __init__(self, root):
        self.root = root

        self.nsc = NameSelectController(root)

        self.button = tkinter.Button(root, text='離開', fg="red", command=self.quit)
        self.button.pack(side=tkinter.RIGHT)

        self.button = tkinter.Button(root, text='儲存後離開', fg="red", command=self.save_and_quit)
        self.button.pack(side=tkinter.RIGHT)

        self.button = tkinter.Button(root, text='儲存', fg="red", command=self.save)
        self.button.pack(side=tkinter.RIGHT)

        self.nsc.update_candidate_names()

    def save(self):
        self.nsc.save_state()

    def save_and_quit(self):
        self.nsc.save_state()
        self.root.quit()

    def quit(self):
        self.root.quit()


def main():
    root = tkinter.Tk()
    root.option_readfile('.picknames.tkinter.options')
    root.wm_title('取名字')
    Pmw.initialise()
    app = App(root)
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    main()

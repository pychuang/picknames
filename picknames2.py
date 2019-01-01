#!/usr/bin/env python3

import csv
import os
import pickle
import Pmw
import tkinter


class SpellingPairController(object):

    def __init__(self, parent_view, delegate, row, column, spelling1, words1, spelling2, words2):
        self.delegate = delegate
        self.spelling1 = spelling1
        self.spelling2 = spelling2
        self.selected = False

        self.word_pairs = []
        for w1 in words1:
            for w2 in words2:
                self.word_pairs.append((w1, w2))

        displayed_text = "%s-%s" % (spelling1.capitalize(), spelling2.capitalize())

        self.button = tkinter.Button(parent_view, text=displayed_text, command=self.toggle_spelling_pair_button)
        self.button.grid(row=row, column=column, sticky=tkinter.NW+tkinter.SE)


    def toggle_spelling_pair_button(self):
        if self.selected:
            self.deselect_spelling_pair_button()
        else:
            self.select_spelling_pair_button()

        self.delegate.update_candidate_names_with_score()


    def select_spelling_pair_button(self):
        self.selected = True
        self.button.config(relief=tkinter.SUNKEN, fg="red")


    def deselect_spelling_pair_button(self):
        self.selected = False
        self.button.config(relief=tkinter.RAISED, fg="black")


    def get_candidate_names(self):
        if self.selected:
            return self.word_pairs
        else:
            return None


class NameSelectController(object):

    STATE_FILE_NAME = '.picknames2.state.pkl'
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

        self.candidate_names_with_score = []   # (w1, w2, score)
        self.candidate_name = None  # (w,1 w2)

        self.frame = tkinter.Frame(parent_view)
        self.frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.upper_frame = tkinter.Frame(self.frame)
        self.upper_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.spelling_pairs_sf = Pmw.ScrolledFrame(self.upper_frame, labelpos=tkinter.N, label_text='音')
        self.spelling_pairs_sf.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # selected names
        self.selected_slb = Pmw.ScrolledListBox(self.upper_frame, labelpos=tkinter.N, label_text='還不錯', listbox_height=5)
        self.selected_slb.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=False)

        # refused names
        #self.refused_slb = Pmw.ScrolledListBox(self.upper_frame, labelpos=tkinter.N, label_text='不要的')
        #self.refused_slb.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.lower_frame = tkinter.Frame(self.frame)
        self.lower_frame.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=False)

        # candidate
        self.num_candidates_label = tkinter.Label(self.lower_frame)
        self.num_candidates_label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        self.candidate_label = tkinter.Label(self.lower_frame)
        self.candidate_label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        choice_bb = Pmw.ButtonBox(self.lower_frame)
        choice_bb.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.select_button = choice_bb.add('✔', state=tkinter.DISABLED, command=self.select_current_candidate_name)
        self.refuse_button = choice_bb.add( '✖', state=tkinter.DISABLED, command=self.refuse_current_candidate_name)

        self.spelling_pair_controllers = []

        # restore state
        self.load_state()

    def load_state(self):
        selected_spelling_sound_words_mapping = {}
        if os.path.exists(self.SELECTED_WORDS_FILE_NAME):
            with open(self.SELECTED_WORDS_FILE_NAME, 'rb') as f:
                selected_spelling_sound_words_mapping = pickle.load(f)
        #print('LOAD:', selected_spelling_sound_words_mapping)

        for i, spelling1 in enumerate(selected_spelling_sound_words_mapping):
            words1 = set()
            for sound, words in selected_spelling_sound_words_mapping[spelling1].items():
                words1.update(words)

            for j, spelling2 in enumerate(selected_spelling_sound_words_mapping):
                words2 = set()
                for sound, words in selected_spelling_sound_words_mapping[spelling2].items():
                    words2.update(words)

                #print("pair %d %d: %s, %s" % (i, j, words1, words2))
                spc = SpellingPairController(self.spelling_pairs_sf.interior(), self, i, j, spelling1, words1, spelling2, words2)
                self.spelling_pair_controllers.append(spc)

        if os.path.exists(self.STATE_FILE_NAME):
            with open(self.STATE_FILE_NAME, 'rb') as f:
                selected_spelling_pairs = pickle.load(f)

            for spc in self.spelling_pair_controllers:
                pair = (spc.spelling1, spc.spelling2)
                if pair in selected_spelling_pairs:
                    spc.select_spelling_pair_button()

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
        with open(self.STATE_FILE_NAME, 'wb') as f:
            selected_spelling_pairs = []
            for spc in self.spelling_pair_controllers:
                if not spc.selected:
                    continue
                pair = (spc.spelling1, spc.spelling2)
                selected_spelling_pairs.append(pair)

            pickle.dump(selected_spelling_pairs, f)

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


    def update_candidate_names_with_score(self):
        names_with_scores = []
        for spc in self.spelling_pair_controllers:
            names = spc.get_candidate_names()
            if not names:
                continue

            for w1, w2 in names:
                if (w1, w2) in self.refused_names or (w1, w2) in self.selected_names:
                    continue
                score = self.score_name(w1, w2)
                names_with_scores.append((w1, w2, score))

        self.candidate_names_with_score = sorted(names_with_scores, key=lambda tup: tup[2])
        #print(self.candidate_names_with_score)
        self.num_candidates_label.config(text=len(self.candidate_names_with_score))
        self.update_current_candidate_name()


    def update_current_candidate_name(self):
        if self.candidate_names_with_score:
            (w1, w2, score) = self.candidate_names_with_score.pop()
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
        #self.update_current_candidate_name()
        self.update_candidate_names_with_score()


    def update_selected_names_view(self):
        names = sorted([w1 + w2 for (w1, w2) in self.selected_names])
        self.selected_slb.setlist(names)


    def refuse_current_candidate_name(self):
        (w1, w2) = self.candidate_name
        self.add_refused_name(w1, w2)
        #names = [w1 + w2 for (w1, w2) in self.refused_names]
        #self.refused_slb.setlist(names)
        #self.update_current_candidate_name()
        self.update_candidate_names_with_score()


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

        self.nsc.update_candidate_names_with_score()

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

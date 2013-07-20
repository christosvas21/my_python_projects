#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Console Hangman by christosvas 

import random, os, sys


class FileHelper:
    def wordslists_files(self, folder):
		files = os.listdir( './' + folder)
		if len(files) < 1:
			print 'No words files in folder: ', folder
			sys.exit()
		return files
		
    def open_file(self, file_name, mode):
        '''Tries to open a file in the specified mode.
        If the file does not exist, opens it in a+ mode'''
        try:
            the_file = open(file_name, mode)
        except IOError:
            print 'Dependent file:', file_name, 'is missing'
            sys.exit()
        return the_file

    def load_words(self, subfolder, category):
        '''Load the word list from the file'''
        file = self.open_file('./'+ subfolder + '/' + category, "r")
        words = file.read()
        word_list = words.split(',')
        file.close()
        return word_list


class State:
	def __init__(self):
		self.nextState = None

	def start(self):
		pass

	def quit(self):
		sys.exit()

	def my_setup(self, frame):
		pass

	def draw(self, canvas):
		pass
        
	def format_category(self, category):
		return (category[0].upper() + category[1:-4])[:13]

	def get_next_state(self):
		return self.nextState

	def transition(self):
		next_state = self.get_next_state()
		if next_state <> None:
			switch_to = next_state()
			switch_to.start()


class GameStart(State):
	def __init__(self, number_of_categories = 4, subfolder = 'word_lists'):
		State.__init__(self)
		self.nextState = lambda: Playing(self.hidden, self.category)
		self.num_categories = number_of_categories
		self.allowed_input = [''+str(i+1) for i in range(number_of_categories+1)]
		self.subfolder = subfolder
		self.categories = FileHelper().wordslists_files('word_lists')
		random.shuffle(self.categories)
        
	def start(self):
		i = self.draw()
		self.play(i)
		self.get_random_word()
		#print self.hidden # reveals the hidden word/phrase
		self.transition()
		
	def draw(self):
		print '\n\n\t Welcome to HangMan'
		print '\t', 20*'-'
		print '\n\tSelect a category:'
		for i in range(self.num_categories):
			print ' \t', (i+1), self.format_category(self.categories[i])
		print ' \t', (i+2), "Random"
		return i
		
	def play(self, i):
		inp = ''
		while inp not in self.allowed_input :
			inp = raw_input('\n  Please input only a number from 1 to ' + str(i+2) + ' and press Enter: ')
			if inp:
				inp = inp[0]
		inp = int(inp)
		if inp == i + 2:
			category_chosen = random.randrange(0, self.num_categories)
		else:
			category_chosen = inp - 1
		self.category = self.categories[category_chosen]
		self.word_list = FileHelper().load_words(self.subfolder, self.category)
		self.category = self.format_category(self.categories[category_chosen])
		#print self.category # reveals chosen/random category
		
	def get_random_word(self):
		self.hidden = self.word_list[random.randrange(0, len(self.word_list))] 


class Playing(State):
	def __init__(self, hidden, category, guesses = 10):
		State.__init__(self)
		self.nextState = None
		self.hidden = hidden
		self.category = category
		self.max_wrong_guesses = guesses
		self.allowed_input = [''+chr(97+i) for i in range(26)]
		self.allowed_input.append(' ')
		self.guessed = [] # or '' here for list or string (list prints guessed letters prettier though)
        
	def display_word(self, hidden, guessed):
		'returns a string of the word with dashes substituted for unguessed letters'
		word_to_display = ''
		for i in hidden:
			if i in guessed:
				ch = i + ' '
			else:
				ch = '_ '
			word_to_display += ch
		return word_to_display
    
	def character_validate(self, guess, guessed):
		guess = list(guess)
		for i in list(guess):
			if i not in self.allowed_input:
				print "\nOnly letters and space are allowed. You entered a(n): ", i
				guess.remove(i)
			elif i in guessed:
				print "\nYou already guessed that letter: ", i, " before"
				guess.remove(i)
		return guess

	def get_guess(self, guessed, hidden):
		'processes players guess and returns result'
		guess = raw_input('Enter one or more letters or space and press Enter: ')
		if guess:
			guess = self.character_validate(set(guess.lower()), guessed) # erase doubles from input and turns it to lowercase
			guessed += guess
			guessed.sort()
			for i in guess:
				if i in hidden:
					print "\nGreat you found the letter: ", i
				else:
					print "\nSorry, the letter: ", i, " is not in the word"
		return guessed 
	
	def display_left(self, hidden, guessed, max_guesses):
		'returns a message (string) of how many guesses the player has left'
		wrong_guesses = 0
		for i in guessed:
			if i not in hidden:
				wrong_guesses += 1
		return max_guesses - wrong_guesses

	def start(self):
		guesses_left = self.max_wrong_guesses
		while guesses_left > 0:
			print "\nThe secret word to find is: ", self.display_word(self.hidden, self.guessed)
			print "You have: ", guesses_left, " guesses left"
			print "Letters guessed so far: ", self.guessed
			self.guessed = self.get_guess(self.guessed, self.hidden)
			if not '_' in self.display_word(self.hidden, self.guessed):
				#hidden word found - take action
				self.nextState = lambda: GameOver(["\n\tGreat you found the secret word.", 
			              "It was: "+self.hidden, "from category: "+self.category+" and ", 
			              "found it in totally: "+str(len(self.guessed))+" guesses"])
				self.transition()
			guesses_left = self.display_left(self.hidden, self.guessed, self.max_wrong_guesses)
		if '_' in self.display_word(self.hidden, self.guessed):
			#not found after all guesses run out - take action
			self.nextState = lambda: GameOver(["\nSorry you ran out of guesses.", 
				"The secret word was: "+self.hidden, "from category: "+self.category])
			self.transition()

		
class GameOver(State):
	def __init__(self, messages):
		State.__init__(self)
		self.nextState = lambda: GameStart()
		self.messages = messages
		self.allowed_input = ['yes', 'y', 'no', 'n']

	def yes(self):
		self.transition()

	def no(self):
		self.quit()
		
	def start(self):
		self.draw()
		self.play()
		
	def draw(self):
		for i in self.messages:
			print '\t', i
		print '\n\tPlay Again? '
					
	def play(self):
		inp = ''
		while inp not in self.allowed_input:
			inp = raw_input('\t(yes/no) <yes>')
			if not inp:
				inp = 'yes'
			else:
				inp = inp.lower()
		if inp in ['yes', 'y']:
			self.yes()
		else:
			self.no()
			

ascii_art = ["__________________                  ",
			 "||  //                              ",
			 "|| //                               ",
			 "||//                                ",
			 "||                                  ",
			 "||                                  ",
			 "||                                  ",
			 "||__________________              ||",
			 "||  //                            ||",
			 "|| //                             ||",
			 "||//______________________________||"]


new_game = GameStart()
new_game.start()

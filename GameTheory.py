#================
#written by SoapDictator
#================

import operator
import random

#cheat&cheat, cheat&coop, coop&cheat, coop&coop
global SCORE_RESPONSE, GAMES_NUM, TURNS_NUM, PLAYER_NUM, PLAYER_CUTOFF
SCORE_RESPONSE = [0, -1, 3, 2]
TURNS_NUM = 10
GAMES_NUM = 5
PLAYER_NUM = 20
PLAYER_CUTOFF = 3

#fucking broken
class Main(object):
	player_avalible = ["Cooperative", "Cheater", "Copycat"]
	player_queue = []
	player_score = {}
	
	def __init__(self):
		self.playersCreate("Cheater", 10)
		self.playersCreate("Cooperative", 5)
		self.playersCreate("Copycat", 5)
		
		self.playersInfo(0)
		for i in range(0, GAMES_NUM):
			self.playersResetScore()
			self.playersPlay()
			self.playersEvolve()
		self.playersInfo()
		
	def playersCreate(self, player_name, num=1):
		if player_name not in self.player_avalible:
			return None
			
		for i in range(0, num):
			targetPlayer = getattr(Players, player_name)
			new_player = targetPlayer()
			
			self.player_queue.append(new_player)
			new_player.setQueuePos(self.player_queue.index(new_player))
	
	def playersResetScore(self):
		for player in self.player_queue:
			player.setScore(0)
	
	def playersPlay(self):
		for player1 in self.player_queue:
			for player2 in self.player_queue:
				if player1 == player2:
					continue
					
				player1.reset()
				player1.reset()
				for i in range(0, TURNS_NUM):				
					player1.play()
					player2.play()
					
					player1.response(player2.getActionSelf())
					player2.response(player1.getActionSelf())
				
	def playersInfo(self, gamesNum = GAMES_NUM):
		print("Turn: %s" % gamesNum)
		print("===========")
		for player in self.player_queue:
			index = self.player_queue.index(player)
			name = player.getName()
			score = player.getScore()
			print("%s) %s: %s" % (index, name, score))
		print("===========")
			
	def playersEvolve(self):
		for player in self.player_queue:
			index = player.getQueuePos()
			score = player.getScore()
			self.player_score[index] = score
			
		sorted_score = sorted(self.player_score.items(), key=operator.itemgetter(1))
		for i in range(0, PLAYER_CUTOFF):
			for player in self.player_queue:
				if player.getQueuePos() == sorted_score[i][0]:
					del self.player_queue[self.player_queue.index(player)]
			
		for player in self.player_queue:
			if len(self.player_queue) < PLAYER_NUM:
				if player.getQueuePos() == sorted_score[len(sorted_score)-1][0]:
					self.playersCreate(player.getName(), PLAYER_CUTOFF)
			player.setQueuePos(self.player_queue.index(player))
		
class Players(object):
	
	class Player(object):
		name = "Prototype"
		queue_pos = 0
		action_self = True
		action_opp = True
		score = 0
		
		def reset(self):
			pass
		
		def play(self):
			pass
			
		def cheat(self):
			self.action_self = False
			
		def cooperate(self):
			self.action_self = True
			
		def response(self, action_opp):
			self.action_opp = action_opp
			if not self.action_self and not self.action_opp:
				self.score += SCORE_RESPONSE[0]
			elif self.action_self and not self.action_opp:
				self.score += SCORE_RESPONSE[1]
			elif not self.action_self and self.action_opp:
				self.score += SCORE_RESPONSE[2]
			elif self.action_self and self.action_opp:
				self.score += SCORE_RESPONSE[3]
				
		#---------------------------------------
		
		def getActionSelf(self):
			return self.action_self
		
		def setScore(self, score):
			self.score = score
		
		def getScore(self):
			return self.score
		
		def getName(self):
			return self.name
			
		def setQueuePos(self, queue_pos):
			self.queue_pos = queue_pos
			
		def getQueuePos(self):
			return self.queue_pos
			
	#this player will always cooperate
	class Cooperative(Player):
		name = "Cooperative"
		
		def reset(self):
			super(Players.Cooperative, self).reset()
		
		def play(self):
			super(Players.Cooperative, self).play()
			self.cooperate()
			
	#this player will always cheat
	class Cheater(Player):
		name = "Cheater"
		
		def reset(self):
			super(Players.Cheater, self).reset()
		
		def play(self):
			super(Players.Cheater, self).play()
			self.cheat()
			
	class Copycat(Player):
		name = "Copycat"
		
		def __init__(self):
			self.action_opp = True
		
		def reset(self):
			super(Players.Copycat, self).reset()
			self.action_opp = True
		
		def play(self):
			super(Players.Copycat, self).play()
			if self.action_opp:
				self.cooperate()
			else:
				self.cheat()
			
main = Main()